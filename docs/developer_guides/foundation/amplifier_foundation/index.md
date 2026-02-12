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

## Core Concepts

<div class="grid cards" markdown>

-   :material-cube-outline: __Bundle__

    ---

    A composable configuration unit containing providers, tools, hooks, orchestrator, context manager, and system instruction.
    
    Bundles are markdown files with YAML frontmatter.

-   :material-layers: __Composition__

    ---

    Layer bundles to build your desired configuration:
    ```python
    foundation.compose(provider).compose(tools)
    ```
    
    Later bundles override earlier ones.

-   :material-cog: __Preparation__

    ---

    Downloads modules from git sources and caches them locally:
    ```python
    prepared = await bundle.prepare()
    ```
    
    First run: downloads. Subsequent runs: uses cache.

-   :material-account-group: __Mount Plan__

    ---

    The final configuration dict consumed by AmplifierSession:
    ```python
    mount_plan = bundle.to_mount_plan()
    session = AmplifierSession(mount_plan)
    ```

</div>

## What's Included

### Bundle System

| Export | Purpose |
|--------|---------|
| `Bundle` | Core class - load, compose, validate bundles |
| `load_bundle(uri)` | Load bundle from local path or git URL |
| `BundleRegistry` | Track loaded bundles, check for updates |
| `validate_bundle()` | Validate bundle structure |

### @Mention System

| Export | Purpose |
|--------|---------|
| `parse_mentions(text)` | Extract `@namespace:path` references |
| `load_mentions(text, resolver)` | Resolve and load mentioned files |
| `BaseMentionResolver` | Base class for custom resolvers |
| `ContentDeduplicator` | Prevent duplicate content loading |

### Utilities

| Module | Purpose |
|--------|---------|
| `io/` | YAML/frontmatter I/O, retry logic |
| `dicts/` | Deep merge, nested get/set |
| `paths/` | URI parsing, path normalization |
| `cache/` | SimpleCache, DiskCache |
| `session/` | Session capabilities (working directory) |
| `spawn_utils` | Provider preferences for sub-sessions |

### Reference Content

The amplifier-foundation repository also includes reference content:

| Path | Content |
|------|---------| 
| `bundle.md` | Main foundation bundle (provider-agnostic) |
| `providers/` | Provider configurations (Anthropic, OpenAI, Azure OpenAI, Gemini, Ollama) |
| `agents/` | Reusable agent definitions |
| `behaviors/` | Behavioral configurations (logging, redaction, status, etc.) |
| `context/` | Shared context files |
| `bundles/` | Complete bundle examples |

## Architecture Position

```
┌─────────────────────────────────────┐
│  Your Application                   │
│  (CLI, Web UI, Script)             │
└──────────────┬──────────────────────┘
               │ uses
               ▼
┌─────────────────────────────────────┐
│  amplifier-foundation               │
│  • Bundle loading & composition     │
│  • @Mention resolution              │
│  • Utilities (I/O, paths, cache)    │
└──────────────┬──────────────────────┘
               │ produces
               ▼
┌─────────────────────────────────────┐
│  Mount Plan (Dict)                  │
└──────────────┬──────────────────────┘
               │ passed to
               ▼
┌─────────────────────────────────────┐
│  amplifier-core (Kernel)           │
│  • Session lifecycle                │
│  • Module loading                   │
│  • Coordination                     │
└─────────────────────────────────────┘
```

**Key Insight**: amplifier-foundation sits **above** amplifier-core, providing convenient APIs for building mount plans. You can use amplifier-core directly (with manual mount plans) or use amplifier-foundation for a higher-level API.

## When to Use Each

### Use amplifier-foundation when:

- ✅ Building applications with reusable configurations
- ✅ You want human-readable YAML + Markdown bundles
- ✅ You need bundle composition (base + overlays)
- ✅ You want automatic module downloading
- ✅ You benefit from built-in utilities

### Use amplifier-core directly when:

- ✅ You have your own configuration system
- ✅ You generate mount plans programmatically
- ✅ You want minimal dependencies
- ✅ You're building a framework on top of Amplifier

## Documentation Structure

<div class="grid cards" markdown>

-   :material-rocket-launch: __[Getting Started](getting_started.md)__

    ---

    Installation, hello world, and basic workflow

-   :material-book-open-variant: __[Core Concepts](concepts.md)__

    ---

    Bundles, composition, mount plans, and philosophy

-   :material-cube-outline: __[Bundle System](bundle_system.md)__

    ---

    Deep dive: load, compose, validate, prepare

-   :material-tools: __[Utilities](utilities.md)__

    ---

    I/O, dicts, paths, mentions, caching utilities

-   :material-code-braces: __[Patterns](patterns.md)__

    ---

    Common patterns and best practices

-   :material-code-json: __[Examples](examples/)__

    ---

    Progressive examples from hello world to production

-   :material-api: __[API Reference](api_reference.md)__

    ---

    Complete API documentation

</div>

## Repository

**GitHub**: [microsoft/amplifier-foundation](https://github.com/microsoft/amplifier-foundation)

## Philosophy

amplifier-foundation follows Amplifier's core principles:

- **Mechanism, not policy**: Provides loading/composition mechanisms. Apps decide which bundles to use.
- **Ruthless simplicity**: One concept (bundle), one mechanism (`includes:` + `compose()`).
- **Text-first**: YAML/Markdown formats are human-readable, diffable, versionable.
- **Composable**: Small bundles compose into larger configurations.

## Next Steps

<div class="grid cards" markdown>

-   :material-play: __Quick Start__

    ---

    [Getting Started →](getting_started.md)
    
    Get your first bundle-based agent running

-   :material-school: __Learn by Example__

    ---

    [Examples Gallery →](examples/)
    
    Progressive examples from beginner to advanced

-   :material-book: __Understand Deeply__

    ---

    [Core Concepts →](concepts.md)
    
    Mental model for bundle composition

</div>
