---
title: amplifier-foundation Library
description: Bundle composition and utilities for building Amplifier applications
---

# amplifier-foundation Library

**amplifier-foundation** is a Python library that simplifies building applications with Amplifier by providing bundle composition, utilities, and reference content.

## What is amplifier-foundation?

While **amplifier-core** provides the kernel (session lifecycle, module loading, coordination), **amplifier-foundation** provides the **application-layer tooling** to make working with Amplifier easier:

- **Bundle System**: Load, compose, validate, and resolve bundles from local and remote sources
- **@Mention System**: Parse and resolve `@namespace:path` references in instructions
- **Utilities**: YAML/frontmatter I/O, dict merging, path handling, caching
- **Reference Content**: Reusable providers, agents, behaviors, and context files

## Why Use amplifier-foundation?

**Without amplifier-foundation** (using amplifier-core directly):

```python
from amplifier_core import AmplifierSession

# You manually create mount plans (dicts)
mount_plan = {
    "session": {"orchestrator": "loop-basic", "context": "context-simple"},
    "providers": [{"module": "provider-anthropic", "source": "git+...", "config": {...}}],
    "tools": [{"module": "tool-bash", "source": "git+..."}]
}

session = await AmplifierSession(mount_plan)
```

**With amplifier-foundation**:

```python
from amplifier_foundation import load_bundle

# Load and compose human-readable bundles
foundation = await load_bundle("git+https://github.com/microsoft/amplifier-foundation@main")
provider = await load_bundle("./providers/anthropic.yaml")
composed = foundation.compose(provider)

# Prepare handles module downloads automatically
prepared = await composed.prepare()
session = await prepared.create_session()
```

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

For the complete workflow with provider selection and advanced features, see [`examples/04_full_workflow/`](https://github.com/microsoft/amplifier-foundation/tree/main/examples/04_full_workflow/).

## What's Included

### Bundle System (`bundle.py`, `registry.py`, `validator.py`)

| Export | Purpose |
|--------|---------|
| `Bundle` | Core class - load, compose, validate bundles |
| `load_bundle(uri)` | Load bundle from local path or git URL |
| `BundleRegistry` | Track loaded bundles, check for updates |
| `validate_bundle()` | Validate bundle structure |

### @Mention System (`mentions/`)

| Export | Purpose |
|--------|---------|
| `parse_mentions(text)` | Extract `@namespace:path` references |
| `load_mentions(text, resolver)` | Resolve and load mentioned files |
| `BaseMentionResolver` | Base class for custom resolvers |
| `ContentDeduplicator` | Prevent duplicate content loading |

### Utilities

| Module | Exports | Purpose |
|--------|---------|---------|
| `io/` | `read_yaml`, `write_yaml`, `parse_frontmatter`, `read_with_retry`, `write_with_retry` | File I/O with cloud sync retry |
| `dicts/` | `deep_merge`, `merge_module_lists`, `get_nested`, `set_nested` | Dict manipulation |
| `paths/` | `parse_uri`, `normalize_path`, `find_files`, `find_bundle_root` | Path and URI handling |
| `cache/` | `SimpleCache`, `DiskCache` | In-memory and disk caching (apps can extend with TTL) |

### Session Capabilities

| Export | Purpose |
|--------|---------|
| `get_working_dir` | Get session working directory from coordinator |
| `set_working_dir` | Update session working directory dynamically |
| `WORKING_DIR_CAPABILITY` | Capability name constant (`"session.working_dir"`) |

### Spawn Utilities

| Export | Purpose |
|--------|---------|
| `ProviderPreference` | Dataclass for provider/model preference (supports glob patterns) |
| `apply_provider_preferences` | Apply ordered preferences to mount plan |
| `resolve_model_pattern` | Resolve glob patterns (e.g., `claude-haiku-*`) to concrete model names |
| `is_glob_pattern` | Check if model string contains glob characters |

### Reference Content (Co-located)

This repo also contains reference bundle content for common configurations:

| Path | Content |
|------|---------|
| `bundle.md` | **Main foundation bundle** - provider-agnostic base with streaming, tools, behaviors |
| `providers/` | Provider configurations (anthropic, openai, azure-openai, gemini, ollama) |
| `agents/` | Reusable agent definitions |
| `behaviors/` | Behavioral configurations (logging, redaction, status, etc.) |
| `context/` | Shared context files |
| `bundles/` | Complete bundle examples |

**Note**: This content is just files - discovered and loaded like any other bundle. See [Common Patterns](patterns.md) for usage examples.

## Examples

| Example | Description |
|---------|-------------|
| `examples/01_hello_world.py` | Minimal working example |
| `examples/04_load_and_inspect.py` | Loading bundles from various sources |
| `examples/05_composition.py` | Bundle composition and merge rules |
| `examples/06_sources_and_registry.py` | Git URLs and BundleRegistry |
| `examples/07_full_workflow.py` | Complete: prepare → create_session → execute |

See [`examples/README.md`](https://github.com/microsoft/amplifier-foundation/blob/main/examples/README.md) for the full catalog of 20+ examples.

## Documentation

| Document | Description |
|----------|-------------|
| [BUNDLE_GUIDE.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md) | Complete bundle authoring guide |
| [AGENT_AUTHORING.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/AGENT_AUTHORING.md) | Agent creation and context sink pattern |
| [CONCEPTS.md](concepts.md) | Mental model: bundles, composition, mount plans |
| [PATTERNS.md](patterns.md) | Common patterns with code examples |
| [URI_FORMATS.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/URI_FORMATS.md) | Source URI quick reference |
| [API_REFERENCE.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/API_REFERENCE.md) | API index pointing to source files |

**Code is authoritative**: Each source file has comprehensive docstrings. Use `help(ClassName)` or read source directly.

## For Bundle Authors

This README covers the Python library API. **For bundle authoring guidance:**

- **[BUNDLE_GUIDE.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md)** - Complete authoring guide (thin bundle pattern, behaviors, composition)
- **[AGENT_AUTHORING.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/AGENT_AUTHORING.md)** - Agent creation and the context sink pattern
- **`foundation:foundation-expert`** - Expert agent for guidance when building bundles
- **Canonical example**: [amplifier-bundle-recipes](https://github.com/microsoft/amplifier-bundle-recipes) - demonstrates proper structure

## Philosophy

Foundation follows Amplifier's core principles:

- **Mechanism, not policy**: Provides loading/composition mechanisms. Apps decide which bundles to use.
- **Ruthless simplicity**: One concept (bundle), one mechanism (`includes:` + `compose()`).
- **Text-first**: YAML/Markdown formats are human-readable, diffable, versionable.
- **Composable**: Small bundles compose into larger configurations.

This library is pure mechanism. It doesn't know about specific bundles. The co-located reference content is just content - discovered and loaded like any other bundle.

## See Also

- [Getting Started](getting_started.md) - Installation and your first bundle-based application
- [Core Concepts](concepts.md) - Mental model for amplifier-foundation's design
- [Common Patterns](patterns.md) - Best practices and common usage patterns
- [Example: Hello World](examples/hello_world.md) - Your first Amplifier agent in ~15 lines of code
