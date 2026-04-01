#!/usr/bin/env python3
"""
apply_placements.py - Apply source-discovery judge verdicts to the doc mapping.

Reads verdicts.json (output from the judge step of the source-discovery recipe)
and applies each verdict:

  AGREE  + add_to_existing  → append source to existing row in CSV and manifest
  AGREE  + new_page         → add new CSV row, new manifest page entry, create
                              placeholder .md file at the target path
  DISAGREE                  → file a GitHub issue via `gh issue create`

After all CSV changes, regenerates the outline by running csv_to_outline.py.

Usage:
    python3 scripts/apply_placements.py \\
        --verdicts path/to/verdicts.json \\
        --csv docs/DOC_SOURCE_MAPPING.csv \\
        --manifest docs/site-manifest.yaml \\
        [--repo microsoft/amplifier-docs] \\
        [--dry-run]

Dependencies: Python stdlib only + the `gh` CLI (for DISAGREE verdicts).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

CSV_FIELDNAMES = ["Documentation Page", "Source Files", "Relationship Type", "Notes"]


def load_csv(path: Path) -> list[dict]:
    """Load the mapping CSV into a list of row dicts."""
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def save_csv(path: Path, rows: list[dict]) -> None:
    """Write rows back to the CSV, preserving the canonical column order."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _csv_source_key(repo: str, path: str) -> str:
    """Format a source entry as it appears in the CSV: ``repo/path``."""
    return f"{repo}/{path}"


def csv_add_source_to_row(
    rows: list[dict], target_page: str, repo: str, path: str
) -> bool:
    """
    Append ``repo/path`` to the pipe-delimited Source Files column of the row
    whose Documentation Page matches *target_page*.

    Returns True if the row was modified, False if the source was already
    present or the page was not found.
    """
    source = _csv_source_key(repo, path)
    for row in rows:
        if row["Documentation Page"] == target_page:
            existing = row["Source Files"]
            if existing == "N/A":
                parts: list[str] = []
            else:
                parts = [s.strip() for s in existing.split("|")]
            if source in parts:
                return False  # already present — idempotent
            parts.append(source)
            row["Source Files"] = "|".join(parts)
            return True
    return False  # page not found in CSV


def csv_add_new_row(
    rows: list[dict],
    page: str,
    sources: list[tuple[str, str]],
    scope: str,
) -> bool:
    """
    Append a brand-new DERIVED row for *page*.

    Returns True if the row was added, False if the page already exists.
    """
    for row in rows:
        if row["Documentation Page"] == page:
            return False  # already present
    source_str = "|".join(_csv_source_key(r, p) for r, p in sources) or "N/A"
    rows.append(
        {
            "Documentation Page": page,
            "Source Files": source_str,
            "Relationship Type": "DERIVED",
            "Notes": scope or "",
        }
    )
    return True


# ---------------------------------------------------------------------------
# YAML manifest helpers (text-surgical — preserves comments & formatting)
# ---------------------------------------------------------------------------
#
# The manifest uses a consistent structure:
#
#   pages:
#
#     - path: docs/some/page.md          ← 2-space indent + "- path:"
#       scope: >
#         ...
#       accepts:
#         - "..."
#       relationship: DERIVED
#       priority: medium
#       sources:                         ← 4-space "sources:" key
#         - repo: some-repo             ← 6-space "- repo:"
#           path: some/file.py          ← 8-space "path:"
#
#   (blank line between page entries)
#
# Pages with "sources: []" (inline empty list) are manually maintained and are
# never valid placement targets — we skip them gracefully.
# ---------------------------------------------------------------------------

# Patterns used across the YAML helpers
_PAGE_PAT = re.compile(r"^  - path: (.+)$")
_SOURCES_BLOCK_PAT = re.compile(r"^    sources:\s*$")
_REPO_ENTRY_PAT = re.compile(r"^      - repo:\s*(.+)$")
_PATH_ENTRY_PAT = re.compile(r"^        path:\s*(.+)$")
_SOURCE_LINE_PAT = re.compile(r"^      ")  # any line inside sources block
_SOURCES_INLINE_PAT = re.compile(
    r"^    sources:"
)  # catches both "sources:" and "sources: []"


def yaml_page_exists(lines: list[str], target_page: str) -> bool:
    """Return True if a page entry for *target_page* exists in the manifest."""
    for line in lines:
        m = _PAGE_PAT.match(line)
        if m and m.group(1).strip() == target_page:
            return True
    return False


def yaml_source_already_in_page(
    lines: list[str], target_page: str, repo: str, path: str
) -> bool:
    """
    Return True if ``{repo}/{path}`` is already listed under *target_page*'s
    sources block in the manifest.
    """
    in_target = False
    in_sources = False
    current_repo: str | None = None

    for line in lines:
        m = _PAGE_PAT.match(line)
        if m:
            if in_target:
                break  # moved past the target page
            if m.group(1).strip() == target_page:
                in_target = True
            continue

        if not in_target:
            continue

        if not in_sources:
            if _SOURCES_BLOCK_PAT.match(line):
                in_sources = True
            continue

        # Inside the sources block
        if not line.strip():
            continue  # blank separator line — still skip
        if not _SOURCE_LINE_PAT.match(line):
            break  # dedented out of sources block

        m_repo = _REPO_ENTRY_PAT.match(line)
        if m_repo:
            current_repo = m_repo.group(1).strip()
            continue
        m_path = _PATH_ENTRY_PAT.match(line)
        if m_path and current_repo == repo and m_path.group(1).strip() == path:
            return True

    return False


def yaml_find_sources_insert_point(lines: list[str], target_page: str) -> int:
    """
    Locate the line index at which new ``- repo/path`` pairs should be
    inserted for *target_page*'s sources block.

    The insert point is the first line *after* all existing source entries —
    typically the blank line that separates pages, or the start of the next
    page entry, or end-of-file.

    Returns -1 if the page or its sources block was not found, or if the
    sources key is an inline empty list (``sources: []``), which cannot be
    safely extended with line-based insertion.
    """
    in_target = False
    in_sources = False

    for i, line in enumerate(lines):
        m = _PAGE_PAT.match(line)
        if m:
            if in_target and in_sources:
                # Hit the next page entry — insert just before it
                return i
            if in_target and not in_sources:
                # Page found but no sources block before next page — bail out
                return -1
            if m.group(1).strip() == target_page:
                in_target = True
            continue

        if not in_target:
            continue

        if not in_sources:
            # Check for inline empty list — cannot extend
            if _SOURCES_INLINE_PAT.match(line) and not _SOURCES_BLOCK_PAT.match(line):
                return -1  # "sources: []" — skip
            if _SOURCES_BLOCK_PAT.match(line):
                in_sources = True
            continue

        # Inside the sources block: a non-blank line that is NOT indented at
        # least 6 spaces signals the end of the block.
        if line.strip() and not _SOURCE_LINE_PAT.match(line):
            return i

        # Blank line (page separator) — insert before it
        if not line.strip():
            return i

    # Reached end-of-file while still inside the sources block
    if in_target and in_sources:
        return len(lines)

    return -1


def yaml_add_source_to_page(
    lines: list[str], target_page: str, repo: str, path: str
) -> tuple[list[str], bool]:
    """
    Insert a new ``- repo / path`` source entry into *target_page*'s sources
    block, preserving all surrounding formatting.

    Returns *(new_lines, was_modified)*.
    """
    if yaml_source_already_in_page(lines, target_page, repo, path):
        return lines, False

    insert_idx = yaml_find_sources_insert_point(lines, target_page)
    if insert_idx == -1:
        return lines, False

    new_entries = [
        f"      - repo: {repo}\n",
        f"        path: {path}\n",
    ]
    new_lines = lines[:insert_idx] + new_entries + lines[insert_idx:]
    return new_lines, True


def yaml_build_new_page_block(
    page: str,
    scope: str,
    accepts: list[str],
    relationship: str,
    priority: str,
    sources: list[tuple[str, str]],
) -> list[str]:
    """
    Build the YAML lines for a brand-new page entry to be appended to the
    manifest's ``pages:`` section.
    """
    block: list[str] = ["\n"]
    block.append(f"  - path: {page}\n")

    # scope as a block scalar (>)
    block.append("    scope: >\n")
    wrapped = textwrap.fill(scope.strip(), width=72)
    for text_line in wrapped.splitlines():
        block.append(f"      {text_line}\n")

    # accepts
    if accepts:
        block.append("    accepts:\n")
        for item in accepts:
            # Escape any embedded double-quotes
            safe = item.replace('"', '\\"')
            block.append(f'      - "{safe}"\n')
    else:
        block.append("    accepts: []\n")

    block.append(f"    relationship: {relationship}\n")
    block.append(f"    priority: {priority}\n")

    block.append("    sources:\n")
    for src_repo, src_path in sources:
        block.append(f"      - repo: {src_repo}\n")
        block.append(f"        path: {src_path}\n")

    return block


# ---------------------------------------------------------------------------
# Placeholder doc-file creation
# ---------------------------------------------------------------------------


def create_placeholder_doc(
    repo_root: Path, page_path: str, scope: str, dry_run: bool
) -> bool:
    """
    Create a minimal placeholder Markdown file at ``{repo_root}/{page_path}``.

    The file contains YAML frontmatter noting it is auto-generated and a
    human-readable stub body.  Does not overwrite an existing file.

    Returns True if the file was (or would be, in dry-run mode) created.
    """
    full_path = repo_root / page_path
    if full_path.exists():
        return False  # don't overwrite

    title = full_path.stem.replace("_", " ").replace("-", " ").title()

    content = textwrap.dedent(f"""\
        ---
        # AUTO-GENERATED PLACEHOLDER
        # Source: source-discovery pipeline
        # Scope: {scope.strip()}
        ---

        # {title}

        > **This page will be generated** from the source files assigned by the
        > source-discovery pipeline.  Run the doc-generation step to populate it.
    """)

    if not dry_run:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    return True


# ---------------------------------------------------------------------------
# GitHub issue filing
# ---------------------------------------------------------------------------


def _build_issue_body(
    candidate: dict,
    placement: dict,
    judge_reasoning: str,
) -> str:
    """Render the Markdown body for a DISAGREE issue."""
    cand_repo = candidate.get("repo", "unknown")
    cand_path = candidate.get("path", "unknown")
    cand_lines = candidate.get("lines", "?")
    protocol = candidate.get("protocol_matched", "")
    summary = candidate.get("summary", "")

    action = placement.get("action", "")
    target_page = placement.get("target_page", "")
    prop_reasoning = placement.get("reasoning", "")
    prop_scope = placement.get("scope", "")
    prop_accepts = placement.get("accepts", [])

    parts = [
        "## Source Candidate\n",
        f"- **Repo**: `{cand_repo}`",
        f"- **Path**: `{cand_path}`",
        f"- **Lines**: {cand_lines}",
    ]
    if protocol:
        parts.append(f"- **Protocol matched**: `{protocol}`")
    if summary:
        parts.append(f"- **Summary**: {summary}")

    parts += [
        "",
        "## Proposed Placement",
        f"- **Action**: `{action}`",
        f"- **Target page**: `{target_page}`",
        f"- **Reasoning**: {prop_reasoning}",
    ]
    if prop_scope:
        parts.append(f"- **Scope**: {prop_scope}")
    if prop_accepts:
        accepts_str = ", ".join(f"`{a}`" for a in prop_accepts)
        parts.append(f"- **Accepts**: {accepts_str}")

    parts += [
        "",
        "## Judge's Disagreement",
        judge_reasoning,
        "",
        "---",
        "_Filed automatically by `scripts/apply_placements.py`_",
    ]

    return "\n".join(parts)


def file_github_issue(
    gh_repo: str,
    candidate: dict,
    placement: dict,
    judge_reasoning: str,
    dry_run: bool,
) -> str:
    """
    File a GitHub issue for a DISAGREE verdict using the ``gh`` CLI.

    Returns a human-readable reference string such as ``#79`` or the full
    URL returned by ``gh``.  On dry-run or error, returns a descriptive
    placeholder.
    """
    cand_repo = candidate.get("repo", "unknown")
    cand_path = candidate.get("path", "unknown")
    title = f"[source-discovery] Placement disagreement: {cand_repo}/{cand_path}"
    body = _build_issue_body(candidate, placement, judge_reasoning)

    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        gh_repo,
        "--title",
        title,
        "--body",
        body,
        "--label",
        "docs-warning",
    ]

    if dry_run:
        print(f"    [dry-run] Would file issue: {title}")
        return "#dry-run"

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        url = result.stdout.strip()
        # gh outputs the issue URL; extract the number for the summary line
        m = re.search(r"/issues/(\d+)$", url)
        return f"#{m.group(1)}" if m else url
    except subprocess.CalledProcessError as exc:
        print(
            f"    ERROR filing issue for {cand_repo}/{cand_path}: {exc.stderr.strip()}",
            file=sys.stderr,
        )
        return "#error"
    except FileNotFoundError:
        print(
            "    ERROR: 'gh' CLI not found. "
            "Install the GitHub CLI (https://cli.github.com/) to file issues.",
            file=sys.stderr,
        )
        return "#no-gh-cli"


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--verdicts",
        required=True,
        metavar="PATH",
        help="Path to verdicts.json (output from the judge step)",
    )
    p.add_argument(
        "--csv",
        required=True,
        metavar="PATH",
        help="Path to docs/DOC_SOURCE_MAPPING.csv",
    )
    p.add_argument(
        "--manifest",
        required=True,
        metavar="PATH",
        help="Path to docs/site-manifest.yaml",
    )
    p.add_argument(
        "--repo",
        default="microsoft/amplifier-docs",
        metavar="OWNER/REPO",
        help=(
            "GitHub repo for filing disagreement issues "
            "(default: microsoft/amplifier-docs)"
        ),
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without writing any files or filing issues",
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_args()

    verdicts_path = Path(args.verdicts).resolve()
    csv_path = Path(args.csv).resolve()
    manifest_path = Path(args.manifest).resolve()
    dry_run = args.dry_run

    # The repo root is the directory that contains the docs/ folder.
    # csv_path is docs/DOC_SOURCE_MAPPING.csv → parent → docs/ → parent → root
    repo_root = csv_path.parent.parent
    scripts_dir = Path(__file__).resolve().parent

    # ------------------------------------------------------------------
    # Validate inputs
    # ------------------------------------------------------------------
    for label, fpath in [
        ("verdicts", verdicts_path),
        ("CSV", csv_path),
        ("manifest", manifest_path),
    ]:
        if not fpath.exists():
            print(f"ERROR: {label} file not found: {fpath}", file=sys.stderr)
            sys.exit(1)

    with open(verdicts_path, encoding="utf-8") as fh:
        verdicts_data = json.load(fh)

    placements: list[dict] = verdicts_data.get("placements", [])
    if not placements:
        print("No placements found in verdicts file — nothing to do.")
        return

    # ------------------------------------------------------------------
    # Load mutable state
    # ------------------------------------------------------------------
    csv_rows = load_csv(csv_path)
    manifest_lines = manifest_path.read_text(encoding="utf-8").splitlines(keepends=True)

    csv_modified = False
    manifest_modified = False

    # Accumulators for the summary
    agreements_applied: list[str] = []
    new_pages_created: list[str] = []
    disagreements_filed: list[tuple[str, str]] = []  # (issue_ref, candidate_label)
    skipped: list[str] = []

    # ------------------------------------------------------------------
    # Process each verdict
    # ------------------------------------------------------------------
    for entry in placements:
        candidate = entry.get("candidate", {})
        placement = entry.get("placement", {})
        verdict = entry.get("verdict", "").upper().strip()
        judge_reasoning = entry.get("judge_reasoning", "")

        cand_repo = candidate.get("repo", "")
        cand_path = candidate.get("path", "")
        action = placement.get("action", "")
        target_page = placement.get("target_page", "")
        cand_label = f"{cand_repo}/{cand_path}"

        # ---- AGREE ---------------------------------------------------
        if verdict == "AGREE":
            if action == "add_to_existing":
                # -- CSV --
                csv_changed = csv_add_source_to_row(
                    csv_rows, target_page, cand_repo, cand_path
                )
                if csv_changed:
                    csv_modified = True

                # -- Manifest --
                manifest_lines, mani_changed = yaml_add_source_to_page(
                    manifest_lines, target_page, cand_repo, cand_path
                )
                if mani_changed:
                    manifest_modified = True

                if not csv_changed and not mani_changed:
                    reason = "already present in CSV and manifest"
                    skipped.append(f"{cand_label} → {target_page}  ({reason})")
                elif dry_run:
                    print(f"  [dry-run] add_to_existing: {cand_label} → {target_page}")
                    agreements_applied.append(f"{cand_label} -> {target_page}")
                else:
                    agreements_applied.append(f"{cand_label} -> {target_page}")

                # Warn if manifest update silently failed (e.g. inline sources: [])
                if csv_changed and not mani_changed:
                    already = yaml_source_already_in_page(
                        manifest_lines, target_page, cand_repo, cand_path
                    )
                    if not already:
                        print(
                            f"  WARNING: CSV updated but manifest could not be "
                            f"updated for {target_page} — sources block may use "
                            f"inline 'sources: []' syntax. Update manually.",
                            file=sys.stderr,
                        )

            elif action == "new_page":
                scope = placement.get(
                    "scope", f"Documentation derived from {cand_path}"
                )
                accepts = placement.get("accepts", [])

                # -- CSV --
                csv_added = csv_add_new_row(
                    csv_rows, target_page, [(cand_repo, cand_path)], scope
                )
                if csv_added:
                    csv_modified = True

                # -- Manifest --
                if not yaml_page_exists(manifest_lines, target_page):
                    new_block = yaml_build_new_page_block(
                        page=target_page,
                        scope=scope,
                        accepts=accepts,
                        relationship="DERIVED",
                        priority="medium",
                        sources=[(cand_repo, cand_path)],
                    )
                    manifest_lines = manifest_lines + new_block
                    manifest_modified = True

                # -- Placeholder doc file --
                doc_created = create_placeholder_doc(
                    repo_root, target_page, scope, dry_run
                )

                if not csv_added and not doc_created:
                    skipped.append(
                        f"{cand_label} → {target_page}  (page already exists)"
                    )
                elif dry_run:
                    print(
                        f"  [dry-run] new_page: {target_page}  (source: {cand_label})"
                    )
                    agreements_applied.append(f"{cand_label} -> {target_page}")
                    new_pages_created.append(target_page)
                else:
                    agreements_applied.append(f"{cand_label} -> {target_page}")
                    new_pages_created.append(target_page)

            else:
                print(
                    f"  WARNING: Unknown placement action '{action}' for "
                    f"AGREE verdict on {cand_label} — skipping.",
                    file=sys.stderr,
                )
                skipped.append(f"{cand_label}  (unknown action: {action})")

        # ---- DISAGREE ------------------------------------------------
        elif verdict == "DISAGREE":
            issue_ref = file_github_issue(
                gh_repo=args.repo,
                candidate=candidate,
                placement=placement,
                judge_reasoning=judge_reasoning,
                dry_run=dry_run,
            )
            disagreements_filed.append((issue_ref, cand_label))

        # ---- Unknown -------------------------------------------------
        else:
            print(
                f"  WARNING: Unknown verdict '{verdict}' for {cand_label} — skipping.",
                file=sys.stderr,
            )
            skipped.append(f"{cand_label}  (unknown verdict: {verdict})")

    # ------------------------------------------------------------------
    # Write outputs (skip in dry-run)
    # ------------------------------------------------------------------
    if not dry_run:
        if csv_modified:
            save_csv(csv_path, csv_rows)
        if manifest_modified:
            manifest_path.write_text("".join(manifest_lines), encoding="utf-8")

    # ------------------------------------------------------------------
    # Regenerate outline
    # ------------------------------------------------------------------
    outline_script = scripts_dir / "csv_to_outline.py"

    if csv_modified and not dry_run:
        if outline_script.exists():
            try:
                subprocess.run(
                    [sys.executable, str(outline_script)],
                    check=True,
                    cwd=str(repo_root),
                )
            except subprocess.CalledProcessError as exc:
                print(
                    f"WARNING: csv_to_outline.py exited with code {exc.returncode}.",
                    file=sys.stderr,
                )
        else:
            print(
                f"WARNING: {outline_script} not found — skipping outline regeneration.",
                file=sys.stderr,
            )
    elif csv_modified and dry_run:
        print(
            f"  [dry-run] Would regenerate outline: "
            f"python3 {outline_script.relative_to(repo_root)}"
        )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n=== Source Discovery Results ===")

    n_agree = len(agreements_applied)
    n_new = len(new_pages_created)
    n_disagree = len(disagreements_filed)

    print(f"Agreements applied: {n_agree}")
    for item in agreements_applied:
        print(f"  - {item}")

    if n_new:
        print(f"New pages created: {n_new}")
        for page in new_pages_created:
            print(f"  - {page}")

    print(f"Disagreements filed: {n_disagree}")
    for issue_ref, label in disagreements_filed:
        print(f"  - {issue_ref}: {label}")

    if skipped:
        print(f"Skipped (no-op): {len(skipped)}")
        for item in skipped:
            print(f"  - {item}")

    if dry_run:
        print("\n(dry-run — no files written, no issues filed)")


if __name__ == "__main__":
    main()
