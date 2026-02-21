# Nav / Structural Fixes Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Consolidate the MkDocs nav from 9 top-level tabs to 6, fix a conflicting feature flag, rename a confusing section label, and add audience signposting to two developer landing pages.

**Architecture:** Four independent file edits applied in order. No Python code changes — every verification step is a clean `mkdocs build`. Tasks must run sequentially because Task 1 removes noise from the build output before Task 2 restructures the nav.

**Tech Stack:** MkDocs Material, awesome-nav plugin (`docs/.nav.yml`), YAML config (`mkdocs.yaml`), Markdown.

---

## Build Verification Command

The "test" for every task is a clean build. Run this after each change:

```bash
cd /Users/samule/repo/amplifier-docs && uv run mkdocs build 2>&1 | grep -E "ERROR|WARNING|built in"
```

**Pass:** output contains only `INFO - Documentation built in X.Xs` — no ERROR or WARNING lines.  
**Fail:** any `ERROR` or `WARNING` about missing files, broken links, or bad YAML.

---

## Task 1 — Remove `navigation.expand` from `mkdocs.yaml`

**File:** `mkdocs.yaml`  
**Lines affected:** line 44

### The problem

`navigation.expand` and `navigation.prune` are in the features list together. They conflict:

- `navigation.expand` auto-opens every sidebar section on every page
- `navigation.prune` only renders active sidebar sections in the DOM

With expand on, every section is always active, so prune can never collapse anything. Result: 4-level deep auto-expand on every page load, and prune does nothing useful.

Fix: remove `navigation.expand`. Prune then works as intended — only the active branch renders.

### Step 1 — Read the file to confirm current state

```bash
grep -n "navigation.expand\|navigation.prune" /Users/samule/repo/amplifier-docs/mkdocs.yaml
```

Expected output:
```
38:    - navigation.prune
44:    - navigation.expand
```

### Step 2 — Make the edit

In `mkdocs.yaml`, find and remove **exactly this line** (line 44):

```yaml
    - navigation.expand
```

The `features:` block before the change (lines 34–50):
```yaml
  features:
    - navigation.instant
    - navigation.instant.progress
    - navigation.indexes
    - navigation.prune
    - content.code.copy
    - content.code.annotate
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.expand
    - navigation.path
    - navigation.top
    - navigation.footer
    - search.highlight
    - search.suggest
    - toc.follow
```

The `features:` block after the change (navigation.expand removed):
```yaml
  features:
    - navigation.instant
    - navigation.instant.progress
    - navigation.indexes
    - navigation.prune
    - content.code.copy
    - content.code.annotate
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.path
    - navigation.top
    - navigation.footer
    - search.highlight
    - search.suggest
    - toc.follow
```

### Step 3 — Verify the build passes

```bash
cd /Users/samule/repo/amplifier-docs && uv run mkdocs build 2>&1 | grep -E "ERROR|WARNING|built in"
```

Expected: `INFO - Documentation built in X.Xs` — no errors.

### Step 4 — Commit

```bash
cd /Users/samule/repo/amplifier-docs && git add mkdocs.yaml && git commit -m "fix: remove navigation.expand to fix conflict with navigation.prune"
```

---

## Task 2 — Restructure `docs/.nav.yml`: 9 tabs → 6 tabs

**File:** `docs/.nav.yml`

### The changes

| What | Before | After |
|---|---|---|
| Tab rename | `Getting Started` | `Get Started` |
| New grouping | `User Guide` (top-level tab) | nested under new `Learn` tab |
| New grouping | `Architecture` (top-level tab) | nested under new `Learn` tab |
| New grouping | `Developer Guides` (top-level tab) | nested under new `Build` tab |
| New grouping | `API Reference` (top-level tab) | nested under new `Build` tab |
| Section rename | `Modules:` inside Developer Guides | `Module Development:` |
| Showcase absorbed | `Showcase` (top-level tab, 1 page) | moved under `Community` |

Result: 9 tabs → 6 tabs: **Home · Get Started · Learn · Build · Ecosystem · Community**

### Step 1 — Read the current file to confirm structure

```bash
cat /Users/samule/repo/amplifier-docs/docs/.nav.yml
```

Confirm: top-level keys are `Home`, `Getting Started`, `User Guide`, `Developer Guides`, `Architecture`, `Ecosystem`, `API Reference`, `Showcase`, `Community` (9 tabs). The inner `Modules:` label under Developer Guides is on line 35.

### Step 2 — Replace the entire file contents

Write the following as the complete new content of `docs/.nav.yml` (every character matters — YAML indentation is two spaces throughout):

```yaml
nav:
  - Home: index.md
  - Get Started:
      - getting_started/index.md
      - Installation Options: getting_started/installation.md
      - Provider Setup: getting_started/providers.md
  - Learn:
      - User Guide:
          - user_guide/index.md
          - CLI Reference: user_guide/cli.md
          - Profiles: user_guide/profiles.md
          - Agents: user_guide/agents.md
          - Sessions: user_guide/sessions.md
          - Collections: user_guide/collections.md
      - Architecture:
          - architecture/index.md
          - Overview: architecture/overview.md
          - Kernel Philosophy: architecture/kernel.md
          - Module System: architecture/modules.md
          - Mount Plans: architecture/mount_plans.md
          - Event System: architecture/events.md
  - Build:
      - Developer Guides:
          - Foundation:
              - developer_guides/foundation/index.md
              - amplifier-foundation Library:
                  - developer_guides/foundation/amplifier_foundation/index.md
                  - Getting Started: developer_guides/foundation/amplifier_foundation/getting_started.md
                  - Core Concepts: developer_guides/foundation/amplifier_foundation/concepts.md
                  - Bundle System: developer_guides/foundation/amplifier_foundation/bundle_system.md
                  - Utilities: developer_guides/foundation/amplifier_foundation/utilities.md
                  - Patterns: developer_guides/foundation/amplifier_foundation/patterns.md
                  - Examples:
                      - developer_guides/foundation/amplifier_foundation/examples/index.md
                      - Hello World: developer_guides/foundation/amplifier_foundation/examples/hello_world.md
                      - Custom Configuration: developer_guides/foundation/amplifier_foundation/examples/custom_configuration.md
                      - Custom Tool: developer_guides/foundation/amplifier_foundation/examples/custom_tool.md
                      - CLI Application: developer_guides/foundation/amplifier_foundation/examples/cli_application.md
                      - Multi-Agent System: developer_guides/foundation/amplifier_foundation/examples/multi_agent_system.md
                  - API Reference: developer_guides/foundation/amplifier_foundation/api_reference.md
          - Applications:
              - developer_guides/applications/index.md
              - CLI Case Study: developer_guides/applications/cli_case_study.md
          - Module Development:
              - developer/index.md
              - Module Development: developer/module_development.md
              - Contracts:
                  - developer/contracts/index.md
                  - Provider Contract: developer/contracts/provider.md
                  - Tool Contract: developer/contracts/tool.md
                  - Hook Contract: developer/contracts/hook.md
                  - Orchestrator Contract: developer/contracts/orchestrator.md
                  - Context Contract: developer/contracts/context.md
      - API Reference:
          - api/index.md
          - Core:
              - api/core/index.md
              - Session: api/core/session.md
              - Coordinator: api/core/coordinator.md
              - Hooks: api/core/hooks.md
              - Models: api/core/models.md
              - Events: api/core/events.md
          - CLI:
              - api/cli/index.md
  - Ecosystem:
      - ecosystem/index.md
      - Modules:
          - modules/index.md
          - Providers:
              - modules/providers/index.md
              - Anthropic: modules/providers/anthropic.md
              - OpenAI: modules/providers/openai.md
              - Azure OpenAI: modules/providers/azure.md
              - Ollama: modules/providers/ollama.md
              - vLLM: modules/providers/vllm.md
              - Mock: modules/providers/mock.md
          - Tools:
              - modules/tools/index.md
              - Filesystem: modules/tools/filesystem.md
              - Bash: modules/tools/bash.md
              - Web: modules/tools/web.md
              - Search: modules/tools/search.md
              - Task: modules/tools/task.md
              - Todo: modules/tools/todo.md
          - Orchestrators:
              - modules/orchestrators/index.md
              - Basic: modules/orchestrators/loop_basic.md
              - Streaming: modules/orchestrators/loop_streaming.md
              - Events: modules/orchestrators/loop_events.md
          - Contexts:
              - modules/contexts/index.md
              - Simple: modules/contexts/simple.md
              - Persistent: modules/contexts/persistent.md
          - Hooks:
              - modules/hooks/index.md
              - Logging: modules/hooks/logging.md
              - Approval: modules/hooks/approval.md
              - Redaction: modules/hooks/redaction.md
              - Backup: modules/hooks/backup.md
              - Cost-Aware Scheduler: modules/hooks/scheduler_cost_aware.md
              - Heuristic Scheduler: modules/hooks/scheduler_heuristic.md
              - Status Context: modules/hooks/status_context.md
              - Streaming UI: modules/hooks/streaming_ui.md
              - Todo Reminder: modules/hooks/todo_reminder.md
      - Libraries:
          - libraries/index.md
          - Profiles: libraries/profiles.md
          - Collections: libraries/collections.md
          - Config: libraries/config.md
          - Module Resolution: libraries/module_resolution.md
  - Community:
      - community/index.md
      - Contributing: community/contributing.md
      - Roadmap: community/roadmap.md
      - Showcase: showcase/index.md
```

### Step 3 — Verify the build passes

```bash
cd /Users/samule/repo/amplifier-docs && uv run mkdocs build 2>&1 | grep -E "ERROR|WARNING|built in"
```

Expected: `INFO - Documentation built in X.Xs` — no errors.

If you see `WARNING - A reference to 'showcase/index.md' is included in the 'nav' but is not found in the docs directory`, check that `docs/showcase/index.md` exists:

```bash
ls /Users/samule/repo/amplifier-docs/docs/showcase/
```

If missing, that's a pre-existing issue — the WARNING is acceptable; do not stop on it. An ERROR (not a WARNING) about missing files means the YAML path is wrong.

### Step 4 — Commit

```bash
cd /Users/samule/repo/amplifier-docs && git add docs/.nav.yml && git commit -m "feat: consolidate nav from 9 tabs to 6 and rename Modules to Module Development"
```

---

## Task 3 — Add audience labels to two developer landing pages

**Files:**
- `docs/developer_guides/foundation/index.md`
- `docs/developer/index.md`

### Why

Both pages cover "developer" topics but for different audiences. The tab rename (Task 2) helps, but users arriving via search or direct links still land on the wrong page and have to figure out where to go. A prominent callout at the top of each page points them to the other section immediately.

---

### File 1: `docs/developer_guides/foundation/index.md`

#### Step 1 — Read the file to confirm the insertion point

```bash
head -15 /Users/samule/repo/amplifier-docs/docs/developer_guides/foundation/index.md
```

Expected output (lines 6–10):
```
# Foundation Developer Guide

This guide is for developers who want to **work with the Amplifier foundation** - the core kernel, libraries, and architectural components that power all Amplifier applications.

## Who This Guide Is For
```

#### Step 2 — Insert the audience callout

The callout goes **between** the opening paragraph (line 8) and the `## Who This Guide Is For` heading (line 10). There is one blank line between them — the edit replaces that blank line + heading with the callout + blank line + heading.

Find this exact string in the file:

```
This guide is for developers who want to **work with the Amplifier foundation** - the core kernel, libraries, and architectural components that power all Amplifier applications.

## Who This Guide Is For
```

Replace it with:

```
This guide is for developers who want to **work with the Amplifier foundation** - the core kernel, libraries, and architectural components that power all Amplifier applications.

!!! note "Audience"
    Building an application on top of Amplifier? You're in the right place. For building a pluggable module (Provider, Tool, Hook), see [Module Development](../../developer/index.md).

## Who This Guide Is For
```

#### Step 3 — Verify the insertion visually

```bash
head -20 /Users/samule/repo/amplifier-docs/docs/developer_guides/foundation/index.md
```

Expected: the `!!! note "Audience"` block appears between the intro paragraph and `## Who This Guide Is For`.

---

### File 2: `docs/developer/index.md`

#### Step 1 — Read the file to confirm the insertion point

```bash
head -15 /Users/samule/repo/amplifier-docs/docs/developer/index.md
```

Expected output (lines 6–12):
```
# Developer Guide

**Start here for building Amplifier modules.**

This guide covers creating custom modules that extend Amplifier's capabilities: providers, tools, hooks, orchestrators, and context managers.

## Module Types
```

#### Step 2 — Insert the audience callout

The callout goes **between** the intro paragraph (line 10) and the `## Module Types` heading (line 12). There is one blank line between them — the edit replaces that blank line + heading with the callout + blank line + heading.

Find this exact string in the file:

```
This guide covers creating custom modules that extend Amplifier's capabilities: providers, tools, hooks, orchestrators, and context managers.

## Module Types
```

Replace it with:

```
This guide covers creating custom modules that extend Amplifier's capabilities: providers, tools, hooks, orchestrators, and context managers.

!!! note "Audience"
    Building a module that plugs into Amplifier (Provider, Tool, Hook, Orchestrator, Context)? You're in the right place. For building an application with Amplifier, see [Foundation Guide](../developer_guides/foundation/index.md).

## Module Types
```

#### Step 3 — Verify the insertion visually

```bash
head -20 /Users/samule/repo/amplifier-docs/docs/developer/index.md
```

Expected: the `!!! note "Audience"` block appears between the intro paragraph and `## Module Types`.

---

### Step 4 — Build verify (both files together)

```bash
cd /Users/samule/repo/amplifier-docs && uv run mkdocs build 2>&1 | grep -E "ERROR|WARNING|built in"
```

Expected: `INFO - Documentation built in X.Xs` — no errors.

### Step 5 — Commit

```bash
cd /Users/samule/repo/amplifier-docs && git add docs/developer_guides/foundation/index.md docs/developer/index.md && git commit -m "docs: add audience labels to developer guide landing pages"
```

---

## Task 4 — Final verification and push

This task confirms all three prior changes work together end-to-end, then pushes to origin.

### Step 1 — Run full build with verbose warning output

```bash
cd /Users/samule/repo/amplifier-docs && uv run mkdocs build 2>&1 | tail -30
```

Expected: build completes with `INFO - Documentation built in X.Xs`. No `ERROR` lines. Any `WARNING` lines should only be pre-existing ones (not introduced by this work).

### Step 2 — Spot-check nav structure in the built site

```bash
grep -r "Get Started\|Module Development" /Users/samule/repo/amplifier-docs/site/ --include="*.html" -l | head -5
```

Expected: several `.html` files found — confirms the new tab names rendered into the built site.

### Step 3 — Confirm navigation.expand is gone

```bash
grep "navigation.expand" /Users/samule/repo/amplifier-docs/mkdocs.yaml
```

Expected: no output (the line is gone).

### Step 4 — Push

```bash
cd /Users/samule/repo/amplifier-docs && git push origin main
```

Expected: push succeeds. GitHub Actions will pick up the three commits and deploy the updated site.

---

## Summary

| Task | File | Change | Commit message |
|---|---|---|---|
| 1 | `mkdocs.yaml` | Remove `navigation.expand` | `fix: remove navigation.expand to fix conflict with navigation.prune` |
| 2 | `docs/.nav.yml` | 9 tabs → 6 tabs + "Module Development" rename | `feat: consolidate nav from 9 tabs to 6 and rename Modules to Module Development` |
| 3 | `docs/developer_guides/foundation/index.md` + `docs/developer/index.md` | Audience callouts | `docs: add audience labels to developer guide landing pages` |
| 4 | — | Final verify + push | — |

**Run order is fixed.** Task 1 before Task 2 (cleaner build output during dev). Tasks 1–3 before Task 4 (nothing to verify until all edits are done).
