# Docs CI Automation Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Fix the docs-sync setup step, convert docs-regenerate to v5.0.0 (flat, no approval gate), and create a daily GitHub Actions workflow that runs both recipes and files GitHub issues for three categories of source warning.

**Architecture:** Three file changes. `docs-sync.yaml` gets a single one-line setup fix (add `mkdir -p` for the repos directory). `docs-regenerate.yaml` is structurally converted from a staged recipe with an approval gate to a flat recipe with an unconditional cleanup step — the evidence validator and semantic diff filter replace the human gate. A new GitHub Actions workflow (`docs-regenerate.yml`) owns all environment concerns — install, auth, git identity, issue filing — and invokes the two recipes as black boxes. Recipes contain zero GitHub-specific logic and run identically locally and in CI.

**Tech Stack:** Amplifier recipe YAML, GitHub Actions YAML, Python 3 (inline script in GH Actions step), `gh` CLI, `amplifier tool invoke`, `yamllint`, `actionlint`.

---

## Pre-flight: Orient Yourself

Before starting Task 1, run these to confirm your environment:

```bash
cd /Users/samule/repo/amplifier-docs
git status           # Should be: working directory clean, branch main
ls recipes/          # Should show: docs-sync.yaml, docs-regenerate.yaml
ls .github/workflows/ # Should show: docs.yml (pre-existing, don't touch it)
```

**CRITICAL RULE: Every task ends with `git commit`. Never `git push`. When the plan says commit, stop there.**

---

## Task 1: Fix docs-sync.yaml — Add `mkdir -p` for repos_dir

**File to modify:** `recipes/docs-sync.yaml`

The `setup` step currently creates the output directories but not the repos directory. When CI runs on a fresh Ubuntu runner, `~/repo/amplifier-sources` doesn't exist yet, and the `sync-repos` step will fail trying to clone into it. Fix: create the directory in the setup step.

### Step 1: Open the file and find the setup step

Read `recipes/docs-sync.yaml`. Find the `setup` step — it's the first step in the file, around line 15. The current `command` line looks like this:

```yaml
    command: "mkdir -p {{output_dir}}/reports {{output_dir}}/cache && echo 'Setup complete'"
```

### Step 2: Replace the single-line command with a multi-line block

Make this exact change — replace the entire `setup` step's `command:` line:

**Find this (exact text):**
```yaml
  - id: "setup"
    type: "bash"
    command: "mkdir -p {{output_dir}}/reports {{output_dir}}/cache && echo 'Setup complete'"
    output: "setup_result"
    timeout: 30
```

**Replace with:**
```yaml
  - id: "setup"
    type: "bash"
    command: |
      mkdir -p {{repos_dir}}
      mkdir -p {{output_dir}}/reports {{output_dir}}/cache
      echo 'Setup complete'
    output: "setup_result"
    timeout: 30
```

> **Why `repos_dir` first?** `context.repos_dir` is already defined in the recipe as `~/repo/amplifier-sources`. The `sync-repos` step clones into it. In CI, the runner starts with a blank home directory, so the path doesn't exist yet.

### Step 3: Verify the change looks right

```bash
head -30 recipes/docs-sync.yaml
```

Expected: the `setup` step shows a multi-line `command:` block with three lines. No other changes to the file.

---

## Task 2: Validate docs-sync.yaml

Run the recipe schema validator:

```bash
cd /Users/samule/repo/amplifier-docs
amplifier tool invoke recipes operation=validate recipe_path=recipes/docs-sync.yaml
```

**PASS looks like:** Output says validation passed, no errors listed. May show warnings about unknown fields — warnings are OK, errors are not.

**FAIL looks like:** Error messages referencing field names, line numbers, or YAML parse errors. If it fails: re-read the file, check that the indentation is exactly 2 spaces for step-level fields (`command:`, `output:`, `timeout:`), and 6 spaces for the command content lines.

---

## Task 3: Commit docs-sync.yaml

```bash
cd /Users/samule/repo/amplifier-docs
git add recipes/docs-sync.yaml
git commit -m "fix: ensure repos_dir exists before cloning in docs-sync setup step"
```

Expected: git reports 1 file changed. **Stop here. Do not push.**

---

## Task 4: Convert docs-regenerate.yaml to v5.0.0

**File to modify:** `recipes/docs-regenerate.yaml`

This is the most complex task. The current file (v4.1.0) uses a `stages:` structure with two stages and an approval gate between them. v5.0.0 flattens this into a single `steps:` list and adds an unconditional `cleanup-sources` step after `update-baseline`.

### What the structure looks like now (v4.1.0):

```
stages:
  - name: "regenerate-and-apply"        ← stage 1 wrapper (remove)
    steps:
      - id: "setup"
      - id: "select-docs"
      - id: "check-selection"
      - id: "read-existing-docs"
      - id: "regenerate-docs"
      - id: "evidence-validation"
      - id: "semantic-diff-filter"
      - id: "validate-output"
      - id: "apply-to-docs"
      - id: "show-diff"
    approval:                           ← approval gate (remove entirely)
      required: true
      ...

  - name: "commit"                      ← stage 2 wrapper (remove)
    steps:
      - id: "commit-changes"
      - id: "update-baseline"
      - id: "generate-report"
```

### What the structure should look like after (v5.0.0):

```
steps:
  - id: "setup"
  - id: "select-docs"
  - id: "check-selection"
  - id: "read-existing-docs"
  - id: "regenerate-docs"
  - id: "evidence-validation"
  - id: "semantic-diff-filter"
  - id: "validate-output"
  - id: "apply-to-docs"
  - id: "show-diff"
  - id: "commit-changes"
  - id: "update-baseline"
  - id: "cleanup-sources"              ← NEW step (add here)
  - id: "generate-report"
```

### Step 1: Update the version and description

**Find this exact text** (around line 28–31 of the file):

```yaml
name: "docs-regenerate"
description: "Regenerate documentation using source hash diffs for incremental updates, with evidence validation and approval-gated commit"
version: "4.1.0"
```

**Replace with:**

```yaml
name: "docs-regenerate"
description: "Regenerate documentation incrementally using source hash diffs, with evidence validation and unconditional cleanup"
version: "5.0.0"
```

### Step 2: Add a changelog entry

The top of the file has a changelog comment block. Find the end of the existing v4.1.0 entry. It ends with a line like:

```
#       creates a window where docs and baseline were out of sync.
#     * FIX: Commit prompt now contains an explicit IMPORTANT block instructing
#       git-ops to run `git add baseline-hashes.json` before committing.
#
```

Insert the new changelog entry AFTER the existing v4.1.0 block (before the `name:` line):

```
# v5.0.0 (2026-02-20):
#   - Breaking: converted from staged recipe to flat recipe
#   - Removed: approval gate (evidence validation + semantic diff filter are
#     the quality gates; no human approval needed for CI)
#   - Removed: ci_mode context variable (not needed; recipe is identical locally
#     and in CI)
#   - Added: cleanup-sources step (unconditional; removes cloned repos +
#     staging dir after every run, including runs with 0 changed sections)
#
```

### Step 3: Run the structural transformation script

This script rewrites the file in place. It removes the stage wrappers, removes the approval block, dedents all steps by 4 spaces, and inserts the new `cleanup-sources` step.

Save the following as a temporary file `_transform.py` in the project root:

```python
#!/usr/bin/env python3
"""
Transform docs-regenerate.yaml from staged (v4.1.0) to flat (v5.0.0).

What this does:
  1. Passes lines before 'stages:' through unchanged.
  2. Replaces 'stages:' with 'steps:'.
  3. Skips the stage-1 name wrapper lines.
  4. Emits all stage-1 step lines, dedented by 4 spaces.
  5. Skips the approval block and stage-2 name wrapper.
  6. Emits commit-changes + update-baseline, dedented by 4 spaces.
  7. Inserts the new cleanup-sources step.
  8. Emits generate-report, dedented by 4 spaces.
"""

from pathlib import Path

CLEANUP_STEP = '''
  - id: "cleanup-sources"
    type: "bash"
    command: |
      echo "Cleaning up cloned source repos..."
      rm -rf {{repos_dir}} && echo "Removed {{repos_dir}}" || echo "Warning: could not remove {{repos_dir}}"
      echo "Cleaning up staging output..."
      rm -rf {{output_dir}}/staging && echo "Removed staging dir" || echo "Warning: staging dir not found"
      echo "Cleanup complete"
    output: "cleanup_result"
    on_error: "continue"
    timeout: 60
'''

path = Path("recipes/docs-regenerate.yaml")
lines = path.read_text().splitlines(keepends=True)

output = []
i = 0
in_stages = False
skip_until_first_step = False
skip_approval = False
cleanup_inserted = False

while i < len(lines):
    line = lines[i]
    stripped = line.rstrip("\n")

    # ── Before stages block: pass through unchanged ────────────────────────
    if not in_stages:
        if stripped == "stages:":
            output.append("steps:\n")
            in_stages = True
            skip_until_first_step = True
            i += 1
            continue
        else:
            output.append(line)
            i += 1
            continue

    # ── Skip stage-1 name wrapper until we hit the first step ─────────────
    if skip_until_first_step:
        if stripped.startswith("      - id:"):  # 6-space indent = first step
            skip_until_first_step = False
            # fall through to normal processing below
        else:
            i += 1
            continue

    # ── Skip approval block + stage-2 name wrapper ────────────────────────
    if skip_approval:
        if stripped == "    steps:":  # stage-2 steps: at 4-space indent
            skip_approval = False
            i += 1
            continue
        else:
            i += 1
            continue

    # ── Detect start of approval block ────────────────────────────────────
    if stripped.startswith("    # Approval gate:") or stripped == "    approval:":
        skip_approval = True
        i += 1
        continue

    # ── Insert cleanup-sources before generate-report ─────────────────────
    if not cleanup_inserted and '- id: "generate-report"' in stripped:
        output.append(CLEANUP_STEP)
        cleanup_inserted = True
        # fall through — also emit the generate-report line below

    # ── Emit line, dedented by 4 spaces ───────────────────────────────────
    if line.startswith("    "):      # 4+ spaces → remove 4
        output.append(line[4:])
    else:
        output.append(line)

    i += 1

path.write_text("".join(output))
print("Transformation complete.")
print("Run 'head -80 recipes/docs-regenerate.yaml' to inspect the header.")
print("Run 'grep -n \"^  - id:\" recipes/docs-regenerate.yaml' to see all step IDs.")
```

Run it:

```bash
cd /Users/samule/repo/amplifier-docs
python3 _transform.py
```

Expected output:
```
Transformation complete.
Run 'head -80 recipes/docs-regenerate.yaml' to inspect the header.
Run 'grep -n "^  - id:" recipes/docs-regenerate.yaml' to see all step IDs.
```

### Step 4: Verify the transformation

Run the verification commands the script suggested:

```bash
# Check that 'stages:' is gone and 'steps:' is present
grep -n "^stages:\|^steps:" recipes/docs-regenerate.yaml
```
Expected: one line showing `steps:`. If `stages:` appears, the script didn't run correctly.

```bash
# Check step order — should show exactly these 14 IDs in this order
grep -n "^  - id:" recipes/docs-regenerate.yaml
```
Expected output (14 lines):
```
  - id: "setup"
  - id: "select-docs"
  - id: "check-selection"
  - id: "read-existing-docs"
  - id: "regenerate-docs"
  - id: "evidence-validation"
  - id: "semantic-diff-filter"
  - id: "validate-output"
  - id: "apply-to-docs"
  - id: "show-diff"
  - id: "commit-changes"
  - id: "update-baseline"
  - id: "cleanup-sources"
  - id: "generate-report"
```

```bash
# Check that approval gate is gone
grep -n "approval:" recipes/docs-regenerate.yaml
```
Expected: no output (no matches). If any line appears, the approval block wasn't removed.

```bash
# Check version was updated
grep "^version:" recipes/docs-regenerate.yaml
```
Expected: `version: "5.0.0"`

```bash
# Inspect the cleanup-sources step
grep -A 12 'id: "cleanup-sources"' recipes/docs-regenerate.yaml
```
Expected: shows the full cleanup step with `on_error: "continue"` and `timeout: 60`.

```bash
# Inspect the file header
head -80 recipes/docs-regenerate.yaml
```
Expected: shows the v5.0.0 changelog entry and updated description.

### Step 5: Clean up the temporary script

```bash
rm _transform.py
```

---

## Task 5: Validate docs-regenerate.yaml

```bash
cd /Users/samule/repo/amplifier-docs
amplifier tool invoke recipes operation=validate recipe_path=recipes/docs-regenerate.yaml
```

**PASS looks like:** Validation passes, no errors. The recipe has 14 flat steps with no stage wrappers.

**FAIL — "unknown field 'stages'":** The transformation didn't remove `stages:`. Re-run `_transform.py` (you'll need to restore the original first with `git checkout recipes/docs-regenerate.yaml` and redo Tasks 4.1–4.4).

**FAIL — "unknown field 'approval'":** The approval block wasn't removed. Same remediation.

**FAIL — YAML parse error:** Indentation is wrong somewhere. Run `python3 -c "import yaml; yaml.safe_load(open('recipes/docs-regenerate.yaml'))"` to get a more precise error with a line number, then fix the indentation at that location.

---

## Task 6: Local Smoke Test — Run docs-sync

This verifies that docs-sync still works after the setup step change (Task 1).

```bash
cd /Users/samule/repo/amplifier-docs
amplifier tool invoke recipes operation=execute recipe_path=recipes/docs-sync.yaml
```

This will take several minutes — it clones ~34 repositories. Watch for:

- The `setup` step should complete and print `Setup complete`
- The `sync-repos` step will clone/pull from GitHub (requires internet)
- The `compute-hashes` step should print a summary of found vs missing sources
- The recipe should end with `=== DOCS SYNC COMPLETE ===`

**PASS:** Recipe completes. Verify these files were written:

```bash
ls sync-output/cache/source-hashes.json
ls sync-output/reports/freshness-report.md
cat sync-output/reports/freshness-report.md
```

Note how many sections show as **Changed** — that's how many docs-regenerate will process in Task 7.

**FAIL — setup step fails:** Check that `mkdir -p {{repos_dir}}` is in the setup command. The `{{repos_dir}}` template variable must match the context key exactly (it's `repos_dir` in the context block).

**FAIL — sync-repos fails on all repos:** Likely a network issue or GitHub rate limit. Retry.

---

## Task 7: Local Smoke Test — Run docs-regenerate

This verifies the v5.0.0 flat recipe works end-to-end.

```bash
cd /Users/samule/repo/amplifier-docs
amplifier tool invoke recipes operation=execute recipe_path=recipes/docs-regenerate.yaml
```

This will take 10–30 minutes depending on how many sections changed. Both of these outcomes are a **PASS**:

**PASS — Zero changed sections:** The `check-selection` step exits with `"nothing_to_do"` and the recipe halts cleanly (green). This is correct when docs are current with their sources.

**PASS — Sections regenerated:** The recipe runs all 14 steps, applies changes, commits, updates `baseline-hashes.json`, runs cleanup, and prints the final report.

**Either way, verify cleanup ran:**

```bash
ls ~/repo/amplifier-sources 2>/dev/null && echo "PROBLEM: sources dir still exists" || echo "OK: sources dir cleaned up"
```

Expected: `OK: sources dir cleaned up`

**FAIL — recipe errors during regenerate-docs or evidence-validation:** These are AI steps and can fail due to LLM timeouts. Retry the recipe — it will pick up changed sections again. If it fails consistently, note the error but proceed with the plan (the recipe logic itself is not what changed in this plan).

**FAIL — cleanup-sources step errors:** The step has `on_error: "continue"` so it won't fail the run. Check the `cleanup_result` output in the logs. A warning here is acceptable.

---

## Task 8: Commit docs-regenerate.yaml

```bash
cd /Users/samule/repo/amplifier-docs
git add recipes/docs-regenerate.yaml
git commit -m "feat: convert docs-regenerate to v5.0.0 — flat recipe, no approval gate, cleanup always runs"
```

Expected: git reports 1 file changed (docs-regenerate.yaml). **Stop here. Do not push.**

---

## Task 9: Create .github/workflows/docs-regenerate.yml

**File to create:** `.github/workflows/docs-regenerate.yml`

> **Note:** `.github/workflows/` already exists in this repo (there's a `docs.yml` there). Do NOT modify `docs.yml`. Just create the new file alongside it.

> **Note on the issue-filing script:** It handles three warning types:
> - **Type 1 — Missing sources:** A file is referenced in the outline but doesn't exist in the cloned repo (`exists: false` in `source-hashes.json`)
> - **Type 2 — Outdated sections:** Every source for a section is missing (the whole section mapping is stale)
> - **Type 3 — New undocumented files:** A file exists in a cloned repo but isn't referenced anywhere in the outline
>
> All three types go through the same deduplication logic: if an issue with that exact title already exists as an open issue, log a link and skip creation.

Create the file with this exact content:

```yaml
name: Daily Docs Regeneration

on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM UTC daily
  workflow_dispatch:       # allow manual trigger

concurrency:
  group: docs-regenerate
  cancel-in-progress: false  # let the current run finish; queue the next one

jobs:
  regenerate:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    permissions:
      contents: write  # git push
      issues: write    # gh issue create

    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      NO_COLOR: 1

    steps:
      - uses: actions/checkout@v4

      # ── Preflight ──────────────────────────────────────────────────────────
      - name: Preflight — check required secrets
        id: preflight
        run: |
          if [ -z "$ANTHROPIC_API_KEY" ]; then
            echo "::warning::ANTHROPIC_API_KEY secret not configured — skipping run"
            echo "skip=true" >> $GITHUB_OUTPUT
          else
            echo "skip=false" >> $GITHUB_OUTPUT
          fi

      # ── Cache + Install ────────────────────────────────────────────────────
      - name: Cache UV + Amplifier modules
        if: steps.preflight.outputs.skip != 'true'
        uses: actions/cache@v4
        with:
          path: |
            ~/.local/share/uv
            ~/.amplifier/cache
            ~/.amplifier/bundles
          key: amplifier-${{ runner.os }}-v1
          restore-keys: amplifier-${{ runner.os }}-

      - name: Install UV + Amplifier
        if: steps.preflight.outputs.skip != 'true'
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          export PATH="$HOME/.local/bin:$PATH"
          echo "$HOME/.local/bin" >> $GITHUB_PATH
          uv tool install git+https://github.com/microsoft/amplifier

      - name: Init Amplifier
        if: steps.preflight.outputs.skip != 'true'
        run: amplifier init --yes

      # ── One-time setup ─────────────────────────────────────────────────────
      - name: Ensure docs-warning label exists
        if: steps.preflight.outputs.skip != 'true'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh label create "docs-warning" \
            --color "#e4e669" \
            --description "Automated warning from docs-sync" \
            2>/dev/null || true

      - name: Configure git identity
        if: steps.preflight.outputs.skip != 'true'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      # ── docs-sync ──────────────────────────────────────────────────────────
      - name: Sync sources
        if: steps.preflight.outputs.skip != 'true'
        run: |
          amplifier tool invoke recipes \
            operation=execute \
            recipe_path=recipes/docs-sync.yaml

      # ── Issue filing ───────────────────────────────────────────────────────
      - name: File issues for warnings
        if: steps.preflight.outputs.skip != 'true'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python3 << 'PYEOF'
          import json, subprocess, sys
          from pathlib import Path

          HASHES  = Path("sync-output/cache/source-hashes.json")
          OUTLINE = Path("outlines/amplifier-docs-outline.json")
          REPOS_DIR = Path.home() / "repo" / "amplifier-sources"

          def find_existing_issue(title):
              """Return the existing open issue dict, or None."""
              result = subprocess.run(
                  ["gh", "issue", "list",
                   "--search", title,
                   "--state", "open",
                   "--json", "number,url,title"],
                  capture_output=True, text=True
              )
              issues = json.loads(result.stdout or "[]")
              return next((i for i in issues if i["title"] == title), None)

          def file_or_skip(title, body):
              existing = find_existing_issue(title)
              if existing:
                  print(f"Issue already exists: {title} — {existing['url']}")
              else:
                  subprocess.run([
                      "gh", "issue", "create",
                      "--title", title,
                      "--body", body,
                      "--label", "docs-warning"
                  ])
                  print(f"Created issue: {title}")

          if not HASHES.exists():
              print("No source-hashes.json — skipping issue filing")
              sys.exit(0)

          with open(HASHES) as f:
              hashes_data = json.load(f)

          # Build set of (repo, path) tuples referenced in the outline
          outlined_sources = set()
          if OUTLINE.exists():
              with open(OUTLINE) as f:
                  outline_data = json.load(f)
              for section in outline_data.get("content_sections", []):
                  for src in section.get("sources", []):
                      outlined_sources.add((src.get("repo", ""), src.get("path", "")))

          # ── Type 1: Missing sources (in outline, not found in repo) ─────────
          for section_id, section in hashes_data.get("sections", {}).items():
              for source in section.get("sources", []):
                  if not source.get("exists", True):
                      repo = source["repo"]
                      path = source["path"]
                      title = f"[docs-warning] Missing source: {repo}/{path}"
                      body = f"""## Missing Source File

          **Section:** `{section_id}`
          **Affected doc:** `{section.get('doc_path', 'unknown')}`
          **Missing file:** `{repo}/{path}`

          The source file referenced in `outlines/amplifier-docs-outline.json` no longer exists in the repository.

          **Suggested action:** Update `docs/DOC_SOURCE_MAPPING.csv` to remove or fix this entry, then regenerate the outline with `python3 scripts/csv_to_outline.py`.
          """
                      file_or_skip(title, body)

          # ── Type 2: Outdated sections (every source for a section is missing) ─
          for section_id, section in hashes_data.get("sections", {}).items():
              sources = section.get("sources", [])
              if sources and all(not s.get("exists", True) for s in sources):
                  doc_path = section.get("doc_path", "unknown")
                  title = f"[docs-warning] Outdated mapping section: {section_id}"
                  body = f"""## Outdated Mapping Section

          **Section:** `{section_id}`
          **Doc:** `{doc_path}`
          **All {len(sources)} source file(s) are missing.**

          Every source file for this section is gone. The section mapping is entirely stale.

          **Suggested action:** Remove the `{section_id}` entry from `docs/DOC_SOURCE_MAPPING.csv`, delete `{doc_path}` if it is no longer relevant, then regenerate the outline.
          """
                  file_or_skip(title, body)

          # ── Type 3: New undocumented files (in repo, not in outline) ─────────
          if REPOS_DIR.exists():
              for repo_dir in sorted(REPOS_DIR.iterdir()):
                  if not repo_dir.is_dir():
                      continue
                  repo_name = repo_dir.name
                  # README.md and package __init__.py are signals a module may need docs
                  candidates = (
                      list(repo_dir.glob("README.md")) +
                      list(repo_dir.glob("*/__init__.py"))
                  )
                  for candidate in candidates:
                      rel_path = str(candidate.relative_to(repo_dir))
                      if (repo_name, rel_path) not in outlined_sources:
                          title = f"[docs-warning] Potential new source: {repo_name}/{rel_path}"
                          body = f"""## Potential New Source File

          **Repo:** `{repo_name}`
          **File:** `{rel_path}`

          This file exists in the cloned repository but is not referenced in any section of `outlines/amplifier-docs-outline.json`.

          **Suggested action:** If this file should be documented, add an entry to `docs/DOC_SOURCE_MAPPING.csv` and regenerate the outline with `python3 scripts/csv_to_outline.py`.
          """
                          file_or_skip(title, body)

          print("Issue filing complete.")
          PYEOF

      # ── docs-regenerate ────────────────────────────────────────────────────
      - name: Regenerate docs
        if: steps.preflight.outputs.skip != 'true'
        run: |
          amplifier tool invoke recipes \
            operation=execute \
            recipe_path=recipes/docs-regenerate.yaml
```

### Verify the file was created

```bash
ls -la .github/workflows/docs-regenerate.yml
wc -l .github/workflows/docs-regenerate.yml
```

Expected: file exists, somewhere around 150–180 lines.

```bash
# Confirm docs.yml was not touched
git diff --name-only
```

Expected: only `.github/workflows/docs-regenerate.yml` shows as changed.

---

## Task 10: Validate Workflow YAML with yamllint

```bash
cd /Users/samule/repo/amplifier-docs

# Install yamllint if not present
pip install yamllint 2>/dev/null || pip3 install yamllint 2>/dev/null || true

yamllint \
  -d "{extends: default, rules: {line-length: {max: 200}, truthy: {check-keys: false}}}" \
  .github/workflows/docs-regenerate.yml
```

**PASS looks like:** No output, or only lines prefixed with `warning:`. Warnings about line length are acceptable.

**FAIL looks like:** Lines prefixed with `error:`. Common causes:
- Tab characters instead of spaces → check your editor didn't insert tabs
- Inconsistent indentation → check the `run: |` blocks are indented 2 spaces under the step
- Duplicate keys → check for typos in step/field names

If yamllint is not installable (restricted environment), skip to Task 11.

---

## Task 11: Validate Workflow YAML with actionlint

`actionlint` understands GitHub Actions schema specifically — it catches things yamllint misses (wrong action versions, invalid `if:` expressions, wrong output references).

```bash
# Try to get actionlint
which actionlint 2>/dev/null || brew install actionlint 2>/dev/null || \
  (curl -s https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash | bash -s -- latest . && mv actionlint /usr/local/bin/ 2>/dev/null || true)

# Run it
actionlint .github/workflows/docs-regenerate.yml
```

**PASS looks like:** No output. Actionlint is silent on success.

**FAIL — "shellcheck reported issues":** These are warnings about the inline shell scripts. Review them — most are benign (like quoting warnings in Python heredocs). Fix any that are actual logic errors.

**FAIL — "property 'skip' is not defined":** This would mean the `steps.preflight.outputs.skip` reference is wrong. Check the `id: preflight` step and the `echo "skip=..."` line.

**If actionlint is not installable:** Skip this task and note it. yamllint from Task 10 is sufficient to proceed.

---

## Task 12: Commit the Workflow File

```bash
cd /Users/samule/repo/amplifier-docs
git add .github/workflows/docs-regenerate.yml
git commit -m "feat: add daily docs regeneration GitHub Actions workflow

- Daily cron at 6 AM UTC, plus workflow_dispatch for manual runs
- Preflight check: skips gracefully (green) if ANTHROPIC_API_KEY not set
- Installs UV + Amplifier via uv tool install, runs amplifier init --yes
- Caches ~/.local/share/uv, ~/.amplifier/cache, ~/.amplifier/bundles
- Runs docs-sync then docs-regenerate via amplifier tool invoke
- Files GitHub issues (docs-warning label) for three warning types:
    1. Missing sources: in outline but not found in cloned repo
    2. Outdated sections: all sources for a section are gone
    3. New undocumented files: in cloned repo but not in outline
- Issue deduplication: logs existing issue URL, skips re-creation
- concurrency: cancel-in-progress: false (queue runs, don't cancel)
- timeout-minutes: 60"
```

Expected: git reports 1 file changed. **Stop here. Do not push.**

---

## Final Verification

After all 12 tasks, confirm the commit log looks right:

```bash
cd /Users/samule/repo/amplifier-docs
git log --oneline -5
```

Expected (newest first):
```
<hash>  feat: add daily docs regeneration GitHub Actions workflow
<hash>  feat: convert docs-regenerate to v5.0.0 — flat recipe, no approval gate, cleanup always runs
<hash>  fix: ensure repos_dir exists before cloning in docs-sync setup step
<hash>  docs: add design document for docs CI automation via GitHub Actions
...
```

```bash
# Confirm nothing is staged or unstaged
git status
```

Expected: `working directory clean`. No pending changes. No push.

---

## What Was NOT Done (Out of Scope)

- **Auto-updating `DOC_SOURCE_MAPPING.csv`** — the issue filing script flags problems but does not modify the CSV or outline. Human action required.
- **`git push`** — all commits are local only. Push manually after review.
- **`workflow_dispatch` end-to-end test** — requires `ANTHROPIC_API_KEY` to be configured as a repo secret and a branch to be pushed to. Deferred to post-review.

---

## Required Setup Before First Real CI Run

Once the branch is pushed and reviewed:

1. In the GitHub repo → Settings → Secrets and variables → Actions → **New repository secret**
2. Name: `ANTHROPIC_API_KEY`, Value: your Anthropic API key
3. `GITHUB_TOKEN` is automatically available — no setup needed
4. Trigger manually via Actions → Daily Docs Regeneration → Run workflow to verify end-to-end
