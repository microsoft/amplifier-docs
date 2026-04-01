#!/usr/bin/env python3
"""
discover_sources.py
===================
Scan source repositories and discover new files that match acceptance
protocols but are **not** currently tracked in the site manifest.

Usage
-----
    python3 scripts/discover_sources.py \
        --repos-dir ~/repo/amplifier-sources \
        --manifest docs/site-manifest.yaml \
        --output sync-output/candidates.json

The script is intentionally dependency-free: it uses only Python stdlib
(pathlib, json, re, ast, argparse, datetime).  It is safe to run repeatedly;
it never modifies any source repo or the manifest.

Exit codes
----------
0  – success (output file written)
1  – fatal error (bad arguments, unwritable output path, etc.)
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Acceptance protocol definitions
# ---------------------------------------------------------------------------
# Each entry maps a protocol name to a configuration dict with the keys:
#
#   include_globs   – list of POSIX glob patterns; a file must match ≥1.
#                     Patterns are matched against the POSIX path *relative
#                     to the repository root* (e.g. "python/foo/bar.py").
#   exclude_globs   – list of glob patterns matched against the *filename
#                     only* (the last path component).  A match disqualifies
#                     the file.
#   exclude_parts   – list of strings; if any path component contains one of
#                     these substrings the file is disqualified.
#   exclude_init_rule – when True the ``_*.py`` exclude_glob is NOT applied
#                     to ``__init__.py`` (which starts with ``_`` but is
#                     explicitly public).
#   min_lines       – minimum non-empty-line count.  0 means "always accept".
#
# Protocols are evaluated in insertion order.  "contracts_and_specs" is
# declared before "documentation" so that files in docs/contracts/ or
# docs/specs/ receive the more specific label.
# ---------------------------------------------------------------------------

DEFAULT_PROTOCOLS: dict[str, dict] = {
    "contracts_and_specs": {
        "include_globs": [
            "docs/contracts/*.md",
            "docs/specs/*.md",
        ],
        "exclude_globs": [],
        "exclude_parts": [],
        "exclude_init_rule": False,
        "min_lines": 0,  # always accept
    },
    "public_python_api": {
        "include_globs": [
            "python/**/*.py",
            "amplifier_foundation/**/*.py",
        ],
        "exclude_globs": [
            "_*.py",  # private modules — but NOT __init__.py (see below)
            "test_*.py",  # test files
        ],
        "exclude_parts": [
            "__pycache__",
            "_grpc_gen",
        ],
        "exclude_init_rule": True,  # _*.py exclusion skipped for __init__.py
        "min_lines": 20,
    },
    "documentation": {
        "include_globs": [
            "docs/**/*.md",
        ],
        "exclude_globs": [
            "docs/plans/**",  # matched against full relative path for this one
        ],
        "exclude_parts": [],
        "exclude_init_rule": False,
        "min_lines": 30,
    },
    "examples": {
        "include_globs": [
            "examples/*.py",
        ],
        "exclude_globs": [],
        "exclude_parts": [],
        "exclude_init_rule": False,
        "min_lines": 20,
    },
    "rust_crates": {
        "include_globs": [
            "crates/*/src/*.rs",
        ],
        "exclude_globs": [],
        "exclude_parts": [
            "generated",
            "bridges",
        ],
        "exclude_init_rule": False,
        "min_lines": 50,
    },
}

# ---------------------------------------------------------------------------
# Glob → regex helpers
# ---------------------------------------------------------------------------


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Compile a POSIX glob pattern to a regex.

    Supported wildcards::

        **   any characters, including ``/``  (multi-segment wildcard)
        *    any characters except ``/``       (single-segment wildcard)
        ?    any single character except ``/``

    The returned regex is anchored (``^…$``) and matches the full string.
    """
    # Split on the special tokens, preserving them in the list.
    tokens = re.split(r"(\*\*|\*|\?)", pattern)
    parts: list[str] = []
    for tok in tokens:
        if tok == "**":
            parts.append(".*")
        elif tok == "*":
            parts.append("[^/]*")
        elif tok == "?":
            parts.append("[^/]")
        else:
            parts.append(re.escape(tok))
    return re.compile("^" + "".join(parts) + "$")


def _matches_any_glob(subject: str, globs: list[str]) -> bool:
    """Return True if *subject* matches at least one pattern in *globs*."""
    return any(_glob_to_regex(g).match(subject) for g in globs)


# ---------------------------------------------------------------------------
# Minimal YAML manifest reader  (stdlib-only)
# ---------------------------------------------------------------------------
# site-manifest.yaml is expected to contain ``sources`` blocks with
# ``repo:`` and ``path:`` sibling keys, for example:
#
#   pages:
#     - id: architecture-kernel
#       sources:
#         - repo: amplifier-core
#           path: python/amplifier_core/session.py
#
# Because Python stdlib has no YAML parser, we use a conservative
# line-level state machine.  We collect every (repo, path) pair whose
# YAML scalar lines appear within five lines of each other, which is
# always true for the two-key source objects in this codebase.
#
# False inclusions (picking up stray repo:/path: pairs from non-source
# sections) are benign: they cause us to treat the item as already
# tracked, which is the safe direction.
# ---------------------------------------------------------------------------


def _strip_yaml_scalar(raw: str) -> str:
    """Remove optional surrounding quotes from a YAML scalar value."""
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] in ('"', "'") and raw[-1] == raw[0]:
        return raw[1:-1]
    return raw


def load_manifest_sources(manifest_path: Path) -> set[str]:
    """Parse *manifest_path* and return a set of ``"repo/path"`` strings.

    Each string identifies a source file currently tracked by the site,
    e.g. ``"amplifier-core/python/amplifier_core/session.py"``.

    Returns an empty set if the manifest does not exist or cannot be read,
    after printing a warning to *stderr*.
    """
    if not manifest_path.exists():
        print(
            f"[discover] Warning: manifest not found at {manifest_path} — "
            "treating all discovered files as untracked.",
            file=sys.stderr,
        )
        return set()

    try:
        text = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(
            f"[discover] Warning: cannot read manifest ({exc}) — "
            "treating all discovered files as untracked.",
            file=sys.stderr,
        )
        return set()

    tracked: set[str] = set()

    # State for pairing repo: and path: lines.
    pending_repo: str | None = None
    pending_path: str | None = None
    repo_lineno: int = -100
    path_lineno: int = -100

    # Patterns that match   ``  - repo: value``  and  ``  - path: value``
    # (with an optional leading ``-`` for list items).
    re_repo = re.compile(r"^-?\s*repo:\s*(.+)$")
    re_path = re.compile(r"^-?\s*path:\s*(.+)$")

    for lineno, raw_line in enumerate(text.splitlines()):
        line = raw_line.strip()

        m = re_repo.match(line)
        if m:
            pending_repo = _strip_yaml_scalar(m.group(1))
            repo_lineno = lineno

        m = re_path.match(line)
        if m:
            pending_path = _strip_yaml_scalar(m.group(1))
            path_lineno = lineno

        # Commit a pair when both halves are within 5 lines of each other.
        if (
            pending_repo is not None
            and pending_path is not None
            and abs(repo_lineno - path_lineno) <= 5
        ):
            tracked.add(f"{pending_repo}/{pending_path}")
            pending_repo = None
            pending_path = None
            repo_lineno = -100
            path_lineno = -100

    return tracked


# ---------------------------------------------------------------------------
# Protocol matching
# ---------------------------------------------------------------------------


def match_protocol(
    rel_posix: str,
    line_count: int,
    protocols: dict[str, dict],
) -> str | None:
    """Return the name of the first protocol that accepts this file, or None.

    Args:
        rel_posix:   POSIX-style path relative to the repository root,
                     e.g. ``"python/amplifier_core/testing.py"``.
        line_count:  Non-empty line count for the file.
        protocols:   Protocol configuration dict (see ``DEFAULT_PROTOCOLS``).
    """
    filename = rel_posix.rsplit("/", 1)[-1]

    for name, cfg in protocols.items():
        # ── 1. Must match at least one include_glob ──────────────────────
        if not _matches_any_glob(rel_posix, cfg["include_globs"]):
            continue

        # ── 2. Must not match any exclude_glob (applied to filename) ─────
        # Special case: the ``exclude_init_rule`` flag means _*.py should
        # NOT exclude ``__init__.py`` — it is always considered public.
        skipped = False
        for excl in cfg.get("exclude_globs", []):
            if cfg.get("exclude_init_rule") and filename == "__init__.py":
                # The _*.py pattern must not veto __init__.py.
                if excl.startswith("_") and not excl.startswith("__"):
                    continue
            # For the documentation protocol the exclude list contains a
            # full-path glob ("docs/plans/**"); match against rel_posix.
            subject = rel_posix if "/" in excl else filename
            if _glob_to_regex(excl).match(subject):
                skipped = True
                break
        if skipped:
            continue

        # ── 3. Must not contain any disqualified path component ──────────
        segments = rel_posix.split("/")
        if any(ep in seg for ep in cfg.get("exclude_parts", []) for seg in segments):
            continue

        # ── 4. Must meet minimum non-empty line count ────────────────────
        if line_count < cfg.get("min_lines", 0):
            continue

        return name

    return None


# ---------------------------------------------------------------------------
# Summary extraction
# ---------------------------------------------------------------------------

_SUMMARY_MAX_CHARS = 100


def _normalise_and_truncate(text: str, max_len: int = _SUMMARY_MAX_CHARS) -> str:
    """Collapse whitespace and truncate to *max_len* characters."""
    text = " ".join(text.split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def _python_summary(source: str) -> str:
    """Return the module-level docstring from Python *source*.

    Falls back to the first non-shebang ``#`` comment if no docstring exists.
    """
    try:
        tree = ast.parse(source)
        docstring = ast.get_docstring(tree)
        if docstring:
            first_line = docstring.strip().splitlines()[0].rstrip(".")
            return _normalise_and_truncate(first_line)
    except SyntaxError:
        pass

    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") and not stripped.startswith("#!"):
            return _normalise_and_truncate(stripped.lstrip("#").strip())
        if stripped and not stripped.startswith("#"):
            break
    return ""


def _markdown_summary(source: str) -> str:
    """Return the first Markdown heading plus the first paragraph."""
    heading = ""
    para_lines: list[str] = []
    in_para = False

    for line in source.splitlines():
        stripped = line.strip()
        if not heading:
            m = re.match(r"^#{1,6}\s+(.+)$", stripped)
            if m:
                heading = m.group(1).strip()
            continue
        # Past the heading: collect first paragraph.
        if stripped and not stripped.startswith("#"):
            in_para = True
            para_lines.append(stripped)
        elif in_para:
            break  # blank line ends the paragraph

    if heading and para_lines:
        raw = f"{heading} — {' '.join(para_lines)}"
    elif heading:
        raw = heading
    else:
        raw = " ".join(para_lines)
    return _normalise_and_truncate(raw)


def _rust_summary(source: str) -> str:
    """Return the ``//!`` module-doc block from Rust *source*."""
    lines: list[str] = []
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("//!"):
            content = stripped[3:].strip()
            if content:
                lines.append(content)
        elif lines:
            break  # first non-//! line ends the block
    return _normalise_and_truncate(" ".join(lines)) if lines else ""


def extract_summary(file_path: Path, source: str) -> str:
    """Dispatch to the right summary extractor based on file extension."""
    match file_path.suffix.lower():
        case ".py":
            return _python_summary(source)
        case ".md":
            return _markdown_summary(source)
        case ".rs":
            return _rust_summary(source)
        case _:
            return ""


# ---------------------------------------------------------------------------
# Python export detection
# ---------------------------------------------------------------------------


def extract_python_exports(source: str) -> list[str]:
    """Return the list of public names exported by a Python module.

    Resolution order:
    1. If an ``__all__`` list/tuple literal is present, use it verbatim.
    2. Otherwise, collect top-level ``def`` / ``async def`` / ``class``
       names that do not start with ``_``.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    # ── 1. Honour explicit __all__ ────────────────────────────────────────
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        return [
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant)
                            and isinstance(elt.value, str)
                        ]

    # ── 2. Public top-level definitions ──────────────────────────────────
    return [
        node.name
        for node in ast.iter_child_nodes(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and not node.name.startswith("_")
    ]


# ---------------------------------------------------------------------------
# __init__.py bonus signal detection
# ---------------------------------------------------------------------------


def check_init_bonus(file_path: Path) -> list[str]:
    """Return bonus signal strings for a Python source file.

    Currently checks whether the module's name is explicitly re-exported
    from the sibling ``__init__.py`` via a relative import or ``__all__``.

    Returns an empty list for ``__init__.py`` itself or if no signals fire.
    """
    signals: list[str] = []
    module_stem = file_path.stem  # "testing" from "testing.py"

    if module_stem == "__init__":
        return signals

    init_file = file_path.parent / "__init__.py"
    if not init_file.exists():
        return signals

    try:
        init_src = init_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return signals

    # Patterns that indicate the module is explicitly published:
    #   from . import testing
    #   from .testing import SomeClass
    #   __all__ = ["testing", ...]  or  __all__ = [..., "testing", ...]
    patterns = [
        rf"from\s+\.\s+import\s+[^\n]*\b{re.escape(module_stem)}\b",
        rf"from\s+\.{re.escape(module_stem)}\s+import\b",
        rf"""["']{re.escape(module_stem)}["']""",
    ]
    for pat in patterns:
        if re.search(pat, init_src):
            signals.append("exported in __init__.py")
            break

    return signals


# ---------------------------------------------------------------------------
# Repository scanner
# ---------------------------------------------------------------------------


def scan_repo(
    repo_path: Path,
    tracked_sources: set[str],
    protocols: dict[str, dict],
) -> tuple[list[dict], int]:
    """Walk *repo_path* and return ``(candidates, total_files_scanned)``.

    A file becomes a *candidate* when it:
    - passes at least one acceptance protocol, **and**
    - its ``"repo/path"`` key is absent from *tracked_sources*.

    Args:
        repo_path:       Absolute path to the repository root directory.
        tracked_sources: Set of ``"repo/path"`` strings from the manifest.
        protocols:       Protocol configuration dict.

    Returns:
        A 2-tuple of (list-of-candidate-dicts, integer count of files examined).
    """
    repo_name = repo_path.name
    candidates: list[dict] = []
    total_scanned = 0

    for file_path in sorted(repo_path.rglob("*")):
        if not file_path.is_file():
            continue

        # Derive POSIX-style path relative to the repo root.
        try:
            rel_posix = file_path.relative_to(repo_path).as_posix()
        except ValueError:
            continue

        # Skip hidden directories and dotfiles (e.g. .git, .tox, .venv).
        if any(part.startswith(".") for part in rel_posix.split("/")):
            continue

        total_scanned += 1

        # ── Read source ───────────────────────────────────────────────────
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(
                f"[discover] Warning: cannot read {file_path}: {exc}",
                file=sys.stderr,
            )
            continue

        # Non-empty line count is the quality signal for min_lines checks.
        line_count = sum(1 for ln in source.splitlines() if ln.strip())

        # ── Protocol check ────────────────────────────────────────────────
        protocol = match_protocol(rel_posix, line_count, protocols)
        if protocol is None:
            continue

        # ── Already tracked? ──────────────────────────────────────────────
        canonical = f"{repo_name}/{rel_posix}"
        if canonical in tracked_sources:
            continue

        # ── Extract metadata ──────────────────────────────────────────────
        summary = extract_summary(file_path, source)
        exports: list[str] = []
        bonus_signals: list[str] = []

        if file_path.suffix.lower() == ".py":
            exports = extract_python_exports(source)
            bonus_signals = check_init_bonus(file_path)

        candidate: dict = {
            "repo": repo_name,
            "path": rel_posix,
            "protocol_matched": protocol,
            "lines": line_count,
            "summary": summary,
        }
        # Omit empty lists to keep the JSON clean.
        if exports:
            candidate["exports"] = exports
        if bonus_signals:
            candidate["bonus_signals"] = bonus_signals

        candidates.append(candidate)

    return candidates, total_scanned


# ---------------------------------------------------------------------------
# Manifest protocol overrides (stub — requires YAML parser)
# ---------------------------------------------------------------------------


def _try_load_protocols_from_manifest(manifest_path: Path) -> dict[str, dict] | None:
    """Attempt to load an ``acceptance_protocols:`` block from the manifest.

    Returns *None* when the block is absent or cannot be parsed without an
    external YAML library.  Callers should fall back to ``DEFAULT_PROTOCOLS``.

    This function is a hook for future extension: if the project ever adds
    a JSON-format protocol override file (``--protocols-json``) or moves to
    TOML config, the loading logic goes here.
    """
    if not manifest_path.exists():
        return None

    try:
        text = manifest_path.read_text(encoding="utf-8")
    except OSError:
        return None

    if "acceptance_protocols:" not in text:
        return None

    # Full YAML parsing requires PyYAML/ruamel, which is not in stdlib.
    # Signal the presence of the block so operators know it was detected
    # but explain that defaults are being used instead.
    print(
        "[discover] Info: 'acceptance_protocols:' block detected in manifest "
        "but cannot be parsed without a YAML library.  Using built-in defaults.",
        file=sys.stderr,
    )
    return None


# ---------------------------------------------------------------------------
# CLI argument parser
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="discover_sources",
        description=(
            "Scan source repositories and discover new files that match "
            "acceptance protocols but are not yet tracked in the site manifest."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  # Standard run
  python3 scripts/discover_sources.py \\
      --repos-dir ~/repo/amplifier-sources \\
      --manifest docs/site-manifest.yaml \\
      --output sync-output/candidates.json

  # Scan a single repo only
  python3 scripts/discover_sources.py \\
      --repos-dir ~/repo/amplifier-sources \\
      --manifest docs/site-manifest.yaml \\
      --output sync-output/candidates.json \\
      --include-repo amplifier-core

  # Limit to one protocol
  python3 scripts/discover_sources.py \\
      --repos-dir ~/repo/amplifier-sources \\
      --manifest docs/site-manifest.yaml \\
      --output sync-output/candidates.json \\
      --protocol public_python_api
""",
    )
    parser.add_argument(
        "--repos-dir",
        required=True,
        metavar="PATH",
        help=(
            "Directory whose immediate sub-directories are cloned source "
            "repositories.  Each sub-directory name is used as the repo name."
        ),
    )
    parser.add_argument(
        "--manifest",
        required=True,
        metavar="PATH",
        help=(
            "Path to docs/site-manifest.yaml.  "
            "Tracked source files are read from this file so that already-covered "
            "files are excluded from the candidates list.  "
            "The file is optional: if absent, all matching files are reported."
        ),
    )
    parser.add_argument(
        "--output",
        required=True,
        metavar="PATH",
        help="Path to write the candidates.json output file.",
    )
    parser.add_argument(
        "--include-repo",
        metavar="REPO",
        action="append",
        dest="include_repos",
        default=[],
        help=(
            "Only scan this repository (may be repeated).  "
            "Default: scan all sub-directories of --repos-dir."
        ),
    )
    parser.add_argument(
        "--exclude-repo",
        metavar="REPO",
        action="append",
        dest="exclude_repos",
        default=[],
        help="Skip this repository (may be repeated).",
    )
    parser.add_argument(
        "--protocol",
        metavar="NAME",
        action="append",
        dest="protocols",
        default=[],
        help=(
            "Limit scanning to this acceptance protocol (may be repeated).  "
            f"Available: {', '.join(DEFAULT_PROTOCOLS)}.  "
            "Default: all protocols."
        ),
    )
    return parser


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """Parse arguments, run the scan, and write candidates.json.

    Returns 0 on success, 1 on fatal error.
    """
    parser = _build_arg_parser()
    args = parser.parse_args()

    repos_dir = Path(args.repos_dir).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    # ── Validate repos directory ──────────────────────────────────────────
    if not repos_dir.exists():
        print(
            f"[discover] Error: --repos-dir does not exist: {repos_dir}",
            file=sys.stderr,
        )
        return 1
    if not repos_dir.is_dir():
        print(
            f"[discover] Error: --repos-dir is not a directory: {repos_dir}",
            file=sys.stderr,
        )
        return 1

    # ── Resolve protocols ─────────────────────────────────────────────────
    protocols = _try_load_protocols_from_manifest(manifest_path) or dict(
        DEFAULT_PROTOCOLS
    )

    if args.protocols:
        unknown = set(args.protocols) - set(protocols)
        if unknown:
            print(
                f"[discover] Error: unknown protocol(s): {', '.join(sorted(unknown))}.  "
                f"Available: {', '.join(protocols)}.",
                file=sys.stderr,
            )
            return 1
        protocols = {k: v for k, v in protocols.items() if k in args.protocols}

    # ── Load tracked sources ──────────────────────────────────────────────
    tracked_sources = load_manifest_sources(manifest_path)
    print(
        f"[discover] Manifest: {len(tracked_sources)} tracked source(s) loaded.",
        file=sys.stderr,
    )

    # ── Discover repository directories ──────────────────────────────────
    repo_dirs: list[Path] = []
    for entry in sorted(repos_dir.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if args.include_repos and entry.name not in args.include_repos:
            continue
        if entry.name in args.exclude_repos:
            print(
                f"[discover] Skipping repo (excluded by --exclude-repo): {entry.name}",
                file=sys.stderr,
            )
            continue
        repo_dirs.append(entry)

    if not repo_dirs:
        print(
            "[discover] Warning: no repositories found to scan in "
            f"{repos_dir}.  Check --repos-dir / --include-repo flags.",
            file=sys.stderr,
        )

    # ── Scan each repository ──────────────────────────────────────────────
    all_candidates: list[dict] = []
    total_files_scanned = 0
    repos_scanned: list[str] = []

    for repo_path in repo_dirs:
        print(f"[discover] Scanning: {repo_path.name} …", file=sys.stderr)
        try:
            candidates, n_scanned = scan_repo(repo_path, tracked_sources, protocols)
        except Exception as exc:  # noqa: BLE001 — surface any unexpected errors
            print(
                f"[discover] Warning: unexpected error scanning "
                f"{repo_path.name}: {exc}",
                file=sys.stderr,
            )
            continue

        repos_scanned.append(repo_path.name)
        total_files_scanned += n_scanned
        all_candidates.extend(candidates)
        print(
            f"[discover]   {n_scanned} files scanned, "
            f"{len(candidates)} candidate(s) found.",
            file=sys.stderr,
        )

    # ── Build output document ─────────────────────────────────────────────
    output: dict = {
        "scan_date": datetime.now(timezone.utc).isoformat(),
        "repos_scanned": repos_scanned,
        "total_files_scanned": total_files_scanned,
        "total_candidates": len(all_candidates),
        "candidates": all_candidates,
    }

    # ── Write output ──────────────────────────────────────────────────────
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output_path.open("w", encoding="utf-8") as fh:
            json.dump(output, fh, indent=2, ensure_ascii=False)
            fh.write("\n")  # POSIX-friendly trailing newline
    except OSError as exc:
        print(
            f"[discover] Error: cannot write output to {output_path}: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        f"[discover] Done — {len(all_candidates)} candidate(s) written to "
        f"{output_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
