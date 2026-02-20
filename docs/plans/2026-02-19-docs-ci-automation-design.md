# Docs CI Automation Design

**Date:** 2026-02-19
**Status:** Draft

---

## What This Enables

A daily GitHub Actions workflow that runs the full `docs-sync → docs-regenerate` pipeline without human intervention. Docs stay current with their source repositories. Warnings surface as tracked GitHub issues. Nothing commits unless content actually changed.

---

## Goal

Automate the docs-sync + docs-regenerate pipeline as a daily GitHub Actions workflow. Reliability over convenience — evidence-validated, content-change-only, self-healing via GitHub issues for warnings.

---

## Background

The `docs-sync` and `docs-regenerate` recipes currently require manual invocation. Documentation drifts as source repositories evolve. The pipeline already has the right quality gates (evidence validation, semantic diff filtering, baseline hashing) — it just needs a reliable trigger and an operator to surface problems as trackable work items rather than silent failures.

---

## Approach

Run both recipes sequentially from GitHub Actions on a daily schedule. GitHub Actions handles environment concerns (secrets, install, git identity, permissions). Recipes own all documentation workflow logic. The two layers share no logic — recipes work identically locally and in CI.

Reliability mechanisms:
- **Evidence validation** inside `docs-regenerate` catches regressions before anything is committed
- **Semantic diff filter** rejects cosmetic-only changes (< 5% meaningful delta)
- **Content-change-only commits** — zero changed sections means zero commits
- **Warning issues** surface missing sources, expired secrets, and other soft failures as tracked GitHub issues rather than build failures

---

## Architecture

```
GitHub Actions (daily @ 6 AM UTC)
│
├── Preflight: check ANTHROPIC_API_KEY
├── Install: UV + Amplifier
├── amplifier init --yes
├── Configure git identity
│
├── amplifier tool invoke recipes docs-sync.yaml
│       └── Clone/update sources, compute hashes, diff against baseline,
│           write freshness report, write source-hashes.json
│
├── Parse sync output → file GitHub issues for warnings
│       └── Missing sources → "docs-warning" issues (idempotent)
│
└── amplifier tool invoke recipes docs-regenerate.yaml
        └── Select changed sections → AI regenerate → evidence validate
            → semantic diff filter → apply → commit → update baseline → cleanup
```

---

## Components

### GitHub Actions Workflow (`.github/workflows/docs-regenerate.yml`)

Owns all environment and orchestration concerns. Invokes recipes as black boxes.

```yaml
name: Daily Docs Regeneration

on:
  schedule:
    - cron: '0 6 * * *'   # 6 AM UTC daily
  workflow_dispatch:

concurrency:
  group: docs-regenerate
  cancel-in-progress: false  # let current run finish, queue next

jobs:
  regenerate:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    permissions:
      contents: write
      issues: write

    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      NO_COLOR: 1

    steps:
      - uses: actions/checkout@v4

      - name: Preflight — check required secrets
        id: preflight
        run: |
          if [ -z "$ANTHROPIC_API_KEY" ]; then
            echo "::warning::ANTHROPIC_API_KEY not set — skipping run"
            echo "skip=true" >> $GITHUB_OUTPUT
          else
            echo "skip=false" >> $GITHUB_OUTPUT
          fi

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

      - name: Init Amplifier (detects ANTHROPIC_API_KEY, writes settings.yaml)
        if: steps.preflight.outputs.skip != 'true'
        run: amplifier init --yes

      - name: Ensure docs-warning label exists
        if: steps.preflight.outputs.skip != 'true'
        run: |
          gh label create "docs-warning" --color "#e4e669" \
            --description "Automated warning from docs sync" 2>/dev/null || true
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Configure git identity
        if: steps.preflight.outputs.skip != 'true'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Sync sources
        if: steps.preflight.outputs.skip != 'true'
        run: |
          amplifier tool invoke recipes \
            operation=execute \
            recipe_path=recipes/docs-sync.yaml

      - name: File issues for warnings
        if: steps.preflight.outputs.skip != 'true'
        run: |
          python3 << 'EOF'
          import json, subprocess, sys
          from pathlib import Path

          report = Path("sync-output/reports/freshness-report.md")
          hashes = Path("sync-output/cache/source-hashes.json")

          if not hashes.exists():
              print("No source-hashes.json found, skipping issue filing")
              sys.exit(0)

          with open(hashes) as f:
              data = json.load(f)

          for section_id, section in data.get("sections", {}).items():
              for source in section.get("sources", []):
                  if not source.get("exists", True):
                      repo = source["repo"]
                      path = source["path"]
                      title = f"[docs-warning] Missing source: {repo}/{path}"

                      result = subprocess.run(
                          ["gh", "issue", "list", "--search", title,
                           "--state", "open", "--json", "number,url,title"],
                          capture_output=True, text=True
                      )
                      issues = json.loads(result.stdout or "[]")
                      match = next((i for i in issues if i["title"] == title), None)

                      if match:
                          print(f"Issue already exists: {title} — {match['url']}")
                      else:
                          doc_path = section.get("doc_path", "unknown")
                          body = f"""## Missing Source File

**Section:** `{section_id}`
**Affected doc:** `{doc_path}`
**Missing:** `{repo}/{path}`

The source file referenced in `outlines/amplifier-docs-outline.json` no longer exists in the repository.

**Suggested action:** Update `docs/DOC_SOURCE_MAPPING.csv` to remove or fix this entry, then regenerate the outline.
"""
                          subprocess.run([
                              "gh", "issue", "create",
                              "--title", title,
                              "--body", body,
                              "--label", "docs-warning"
                          ])
                          print(f"Created issue: {title}")
          EOF
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Regenerate docs
        if: steps.preflight.outputs.skip != 'true'
        run: |
          amplifier tool invoke recipes \
            operation=execute \
            recipe_path=recipes/docs-regenerate.yaml
```

### Recipe: `docs-sync.yaml`

Unchanged from current version. Responsible for:
- Clone/update source repositories
- Compute content hashes per section
- Diff against baseline hashes
- Write `sync-output/cache/source-hashes.json`
- Write `sync-output/reports/freshness-report.md`

### Recipe: `docs-regenerate.yaml` (v5.0.0)

Converted from staged (approval-gated) to flat (no gate). The evidence validation and semantic diff filter are the quality gates — no human approval needed in CI.

**Breaking changes from v4.1.0:**
- Approval gate removed entirely
- `ci_mode` context variable removed — recipe is identical everywhere
- `cleanup-sources` step runs unconditionally as the final step

**Step sequence:**

```
setup
→ select-docs
→ check-selection
→ read-existing-docs
→ regenerate-docs
→ evidence-validation
→ semantic-diff-filter
→ validate-output
→ apply-to-docs
→ show-diff
→ commit-changes
→ update-baseline
→ cleanup-sources      ← rm -rf ~/repo/amplifier-sources + sync-output/regenerated/
→ generate-report
```

---

## Separation of Concerns

**GitHub Actions owns** (environment + orchestration):
- Schedule trigger, concurrency, timeout, permissions
- UV + Amplifier installation and caching
- `amplifier init --yes`
- Git identity configuration
- Pre-flight secret checks
- Sequential recipe invocation
- Warning output parsing → GitHub issue filing

**Recipes own** (documentation workflow logic):
- Source cloning, hashing, baseline diffing (docs-sync)
- Section selection, AI regeneration, evidence validation, semantic filtering, commit, cleanup (docs-regenerate)

No GitHub-specific logic lives inside recipes. Recipes run identically locally and in CI.

---

## Data Flow

```
Source repos (GitHub)
        │
        ▼ docs-sync
sync-output/
  cache/source-hashes.json     ← per-section content hashes
  reports/freshness-report.md  ← human-readable sync report
        │
        ├──▶ GitHub Actions parses source-hashes.json
        │           └──▶ missing sources → GitHub Issues (docs-warning label)
        │
        ▼ docs-regenerate
outlines/amplifier-docs-outline.json   ← section selection input
        │
        ▼ AI regeneration (changed sections only)
        │
        ▼ evidence-validation (claim verification)
        │
        ▼ semantic-diff-filter (< 5% delta → reject)
        │
        ▼ apply-to-docs → git commit → update baseline-hashes.json
        │
        ▼ cleanup: rm -rf ~/repo/amplifier-sources + sync-output/regenerated/
```

---

## Error Handling

| Category | Case | Behavior |
|---|---|---|
| Pre-flight | No `ANTHROPIC_API_KEY` | Skip run (green), log warning |
| Pre-flight | Invalid/expired key | `amplifier init --yes` fails → red run |
| Pre-flight | Amplifier install fails | Fail fast → red run |
| docs-sync | One repo clone fails | Warning issue filed, continue with remaining repos |
| docs-sync | Private repo (403) | Warning issue filed, continue |
| docs-sync | All repos fail | Warning issue filed, skip docs-regenerate |
| docs-regenerate | 0 changed sections | `check-selection` exits cleanly, green run, no commit |
| docs-regenerate | All changes cosmetic (< 5%) | Semantic filter rejects all, clean exit, no commit |
| docs-regenerate | LLM rate limit / timeout | Step fails → red run, retriable via `workflow_dispatch` |
| docs-regenerate | Evidence removes everything | Regression caught by semantic filter, doc skipped |
| Git | Push race (concurrent runs) | `cancel-in-progress: false` queues runs |
| Git | Branch protection blocks push | 403 → red run with clear error |
| Issues | `docs-warning` label missing | Created idempotently before filing |
| Issues | `issues: write` permission missing | Log error, don't fail run (docs still committed) |
| Issues | Issue already exists | Log "Issue already exists: \<title\> — \<url\>", skip |
| Cleanup | `rm -rf` fails | Log warning, don't fail the run |

---

## Testing Strategy

- **Local smoke test:** Run `docs-sync` then `docs-regenerate` locally before merging the workflow file
- **`workflow_dispatch` dry run:** Trigger manually on a branch; verify issue filing, commit, and cleanup all behave correctly with real secrets
- **No-op verification:** Confirm a run with 0 changed sections produces a green build and no commit
- **Cosmetic-change verification:** Confirm a run where all diffs are < 5% delta produces no commit
- **Idempotent issue test:** Trigger two consecutive runs with a known missing source; confirm only one issue is filed

---

## Known Gaps (Tracked Separately)

Two behaviors are intentionally not addressed here:

1. **Remove outdated mapping entries** — when a source file disappears, a warning issue is filed but `docs/DOC_SOURCE_MAPPING.csv` and the outline are never updated automatically. Manual remediation is required.

2. **Discover new source files** — no mechanism exists to detect new files that should be added to the mapping. The outline is treated as read-only ground truth.

Both gaps surface as `docs-warning` GitHub issues and require human action. Automating them is deferred.

---

## Required Setup

1. Add `ANTHROPIC_API_KEY` as a repository secret (`Settings → Secrets and variables → Actions`)
2. No additional GitHub token configuration needed — `GITHUB_TOKEN` is automatically available with the `contents: write` and `issues: write` permissions declared in the workflow
