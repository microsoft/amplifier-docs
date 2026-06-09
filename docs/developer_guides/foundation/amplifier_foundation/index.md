---
title: Amplifier Foundation
description: Foundational library for bundle composition, module resolution, and shared utilities
---

# Amplifier Foundation

> **Repository**: [`amplifier-foundation`](https://github.com/microsoft/amplifier-foundation)

Foundational library for the Amplifier ecosystem: bundle composition, utilities, and reference content.

Foundation provides:
- **Bundle System** — Load, compose, validate, and resolve bundles from local and remote sources
- **@Mention System** — Parse and resolve `@namespace:path` references in instructions
- **Utilities** — YAML/frontmatter I/O, dict merging, path handling, caching
- **Reference Content** — Reusable providers, agents, behaviors, and context files

## Quick Start

```bash
pip install git+https://github.com/microsoft/amplifier-foundation
```

```python
import asyncio
from amplifier_foundation import load_bundle

async def main():
    # Load foundation bundle and a provider
    foundation = await load_bundle("git+https://github.com/microsoft/amplifier-foundation@main")
    provider = await load_bundle("./providers/anthropic.yaml")

    # Compose bundles (later overrides earlier)
    composed = foundation.compose(provider)

    # Prepare: resolves module sources, downloads if needed
    prepared = await composed.prepare()

    # Create session and execute
    async with await prepared.create_session() as session:
        response = await session.execute("Hello! What can you help me with?")
        print(response)

asyncio.run(main())
```

## Core Concepts

### Bundles

A **bundle** is the fundamental unit of composition in Amplifier. A bundle is a YAML/Markdown file that specifies:

- Which modules to mount (orchestrator, providers, tools, hooks, context manager)
- System instructions and agent behavior
- References to other bundles via `includes:`

```yaml
---
bundle:
  name: my-assistant
  version: 1.0.0

session:
  orchestrator: {module: loop-streaming}
  context: {module: context-simple}

providers:
  - module: provider-anthropic
    source: git+https://github.com/microsoft/amplifier-module-provider-anthropic@main
    config:
      default_model: claude-sonnet-4-5

tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
---

You are a helpful assistant with file system access.
```

### Composition

Bundles compose via the `compose()` method. Later bundles override earlier ones using deep-merge rules:

```python
base = await load_bundle("./base.md")
overlay = await load_bundle("./dev-overlay.md")
composed = base.compose(overlay)
```

The `includes:` key provides declarative composition directly in YAML:

```yaml
includes:
  - ./base.md
  - ./dev-overlay.md
```

### Mount Plans

After composition, a bundle is converted to a **mount plan** — a resolved configuration that `AmplifierSession` consumes to load modules. `prepare()` resolves all source URIs and installs module packages.

```python
prepared = await composed.prepare()
mount_plan = composed.to_mount_plan()  # Inspect before preparing
```

## What's Included

### Bundle System

| Export | Source | Purpose |
|--------|--------|---------| 
| `Bundle` | `bundle.py` | Composable unit with mount plan config |
| `BundleRegistry` | `registry.py` | Named bundle management and loading |
| `BundleValidator` | `validator.py` | Bundle structure validation |
| `ValidationResult` | `validator.py` | Validation result with errors/warnings |
| `load_bundle` | `registry.py` | Load bundle from URI |
| `validate_bundle` | `validator.py` | Validate bundle, return result |
| `validate_bundle_or_raise` | `validator.py` | Validate bundle, raise on error |

### @Mention System

| Export | Source | Purpose |
|--------|--------|---------| 
| `parse_mentions` | `mentions/parser.py` | Extract `@namespace:path` references from text |
| `load_mentions` | `mentions/loader.py` | Load @mention content (async) |
| `BaseMentionResolver` | `mentions/resolver.py` | Default @mention resolver |
| `ContentDeduplicator` | `mentions/deduplicator.py` | SHA-256 content deduplication |
| `MentionResolverProtocol` | `mentions/protocol.py` | @mention resolution contract |

### Utilities

| Module | Exports | Purpose |
|--------|---------|---------|
| `io/` | `read_yaml`, `write_yaml`, `parse_frontmatter`, `read_with_retry`, `write_with_retry` | File I/O with cloud sync retry |
| `dicts/` | `deep_merge`, `merge_module_lists`, `get_nested`, `set_nested` | Dict manipulation |
| `paths/` | `parse_uri`, `normalize_path`, `find_files`, `find_bundle_root` | Path and URI handling |
| `cache/` | `SimpleCache`, `DiskCache` | In-memory and disk caching |

### Session Capabilities

| Export | Source | Purpose |
|--------|--------|---------| 
| `get_working_dir` | `session/capabilities.py` | Get session working directory from coordinator |
| `set_working_dir` | `session/capabilities.py` | Update session working directory dynamically |
| `WORKING_DIR_CAPABILITY` | `session/capabilities.py` | Capability name constant (`"session.working_dir"`) |

### Spawn Utilities

Utilities for spawning sub-sessions with provider/model preferences.

| Export | Source | Purpose |
|--------|--------|---------| 
| `ProviderPreference` | `spawn_utils.py` | Dataclass for provider/model preference (supports glob patterns) |
| `apply_provider_preferences` | `spawn_utils.py` | Apply ordered preferences to mount plan |
| `resolve_model_pattern` | `spawn_utils.py` | Resolve glob patterns (e.g., `claude-haiku-*`) to concrete model names |
| `is_glob_pattern` | `spawn_utils.py` | Check if model string contains glob characters |

### Cost Bridge Utilities

Utilities for propagating child-session costs to parent coordinators in app-layer spawn wrappers.

| Export | Source | Purpose |
|--------|--------|---------| 
| `bridge_child_cost` | `bundle/_prepared.py` | Collect child session's `session.cost` contributions and register them as a single contributor on the parent coordinator. Never raises — errors are logged as warnings. |
| `sum_cost_usd` | `bundle/_prepared.py` | Sum a list of `collect_contributions()` results into a single `Decimal \| None`. Returns `None` when no cost data is present. Tolerates both `Decimal` and `str` values. |

### Exceptions

| Export | Purpose |
|--------|---------|
| `BundleError` | Base exception |
| `BundleNotFoundError` | Bundle not found |
| `BundleLoadError` | Bundle load/parse failed |
| `BundleValidationError` | Validation failed |
| `BundleDependencyError` | Dependency resolution failed |

## Reference Content

The repository co-locates reusable bundle content:

| Path | Content |
|------|---------|
| `bundle.md` | Main foundation bundle — provider-agnostic base with streaming, tools, behaviors |
| `providers/` | Provider configurations (anthropic, openai, azure-openai, gemini, ollama) |
| `agents/` | Reusable agent definitions |
| `behaviors/` | Behavioral configurations (logging, redaction, status, etc.) |
| `context/` | Shared context files |
| `bundles/` | Complete bundle examples |

## Examples

| Example | Description |
|---------|-------------|
| `examples/01_hello_world.py` | Minimal working example |
| `examples/04_load_and_inspect.py` | Loading bundles from various sources |
| `examples/05_composition.py` | Bundle composition and merge rules |
| `examples/06_sources_and_registry.py` | Git URLs and BundleRegistry |
| `examples/07_full_workflow.py` | Complete: prepare → create_session → execute |
| `examples/08_cli_application.py` | Building a production CLI tool |

See [`examples/README.md`](https://github.com/microsoft/amplifier-foundation/blob/main/examples/README.md) for the full catalog of 20+ examples.

## Documentation

| Document | Description |
|----------|-------------|
| [BUNDLE_GUIDE.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md) | Complete bundle authoring guide |
| [AGENT_AUTHORING.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/AGENT_AUTHORING.md) | Agent creation and context sink pattern |
| [Concepts](./concepts.md) | Mental model: bundles, composition, mount plans |
| [Patterns](./patterns.md) | Common patterns with code examples |
| [API Reference](https://github.com/microsoft/amplifier-foundation/blob/main/docs/API_REFERENCE.md) | API index pointing to source files |

## Philosophy

Foundation follows Amplifier's core principles:

- **Mechanism, not policy**: Provides loading/composition mechanisms. Apps decide which bundles to use.
- **Ruthless simplicity**: One concept (bundle), one mechanism (`includes:` + `compose()`).
- **Text-first**: YAML/Markdown formats are human-readable, diffable, versionable.
- **Composable**: Small bundles compose into larger configurations.

This library is pure mechanism. It doesn't know about specific bundles. The co-located reference content is just content — discovered and loaded like any other bundle.
