---
title: API Reference
description: Complete API documentation for amplifier-foundation
---

# API Reference

The amplifier-foundation API is fully documented via Python docstrings and type hints. This overview lists what's exported; for details, read the source files directly.

**Why this approach?** Documentation that duplicates code becomes context poisoning when it drifts. The code IS the authoritative reference.

## Quick Import

```python
from amplifier_foundation import Bundle, BundleRegistry, load_bundle
```

## Core Classes

| Export | Source | Purpose |
|--------|--------|---------|
| `Bundle` | `bundle.py` | Composable unit with mount plan config |
| `BundleRegistry` | `registry.py` | Named bundle management and loading |
| `BundleValidator` | `validator.py` | Bundle structure validation |
| `ValidationResult` | `validator.py` | Validation result with errors/warnings |
| `BundleState` | `registry.py` | Tracked state for loaded bundles |
| `UpdateInfo` | `registry.py` | Available update information |

## Convenience Functions

| Export | Source | Purpose |
|--------|--------|---------|
| `load_bundle` | `registry.py` | Load bundle from URI |
| `validate_bundle` | `validator.py` | Validate bundle, return result |
| `validate_bundle_or_raise` | `validator.py` | Validate bundle, raise on error |

## Exceptions

| Export | Source | Purpose |
|--------|--------|---------|
| `BundleError` | `exceptions.py` | Base exception |
| `BundleNotFoundError` | `exceptions.py` | Bundle not found |
| `BundleLoadError` | `exceptions.py` | Bundle load/parse failed |
| `BundleValidationError` | `exceptions.py` | Validation failed |
| `BundleDependencyError` | `exceptions.py` | Dependency resolution failed |

## Protocols

| Export | Source | Purpose |
|--------|--------|---------|
| `MentionResolverProtocol` | `mentions/protocol.py` | @mention resolution contract |
| `SourceResolverProtocol` | `sources/protocol.py` | URI resolution contract |
| `SourceHandlerProtocol` | `sources/protocol.py` | Source type handler contract |
| `SourceHandlerWithStatusProtocol` | `sources/protocol.py` | Source handler with status checking |
| `SourceStatus` | `sources/protocol.py` | Source status (local, cached, remote, etc.) |
| `CacheProviderProtocol` | `cache/protocol.py` | Cache provider contract |

## Reference Implementations

| Export | Source | Purpose |
|--------|--------|---------|
| `BaseMentionResolver` | `mentions/resolver.py` | Default @mention resolver |
| `SimpleSourceResolver` | `sources/resolver.py` | Git/file source resolver |
| `SimpleCache` | `cache/simple.py` | In-memory cache |
| `DiskCache` | `cache/disk.py` | Persistent disk cache |

## Mentions

| Export | Source | Purpose |
|--------|--------|---------|
| `parse_mentions` | `mentions/parser.py` | Extract @mentions from text |
| `load_mentions` | `mentions/loader.py` | Load @mention content (async) |
| `ContentDeduplicator` | `mentions/deduplicator.py` | SHA-256 content deduplication |
| `ContextFile` | `mentions/models.py` | Loaded context file data |
| `MentionResult` | `mentions/models.py` | Mention resolution result |

## Agents

| Export | Source | Purpose |
|--------|--------|---------|
| `AgentResolver` | `agents/resolver.py` | Resolve agent names to paths |
| `AgentLoader` | `agents/loader.py` | Load and parse agent files |
| `Agent` | `agents/models.py` | Agent definition with metadata |
| `AgentMeta` | `agents/models.py` | Agent metadata (description, model_role) |
| `SystemConfig` | `agents/models.py` | System configuration for agents |

## Provider Preferences

| Export | Source | Purpose |
|--------|--------|---------|
| `ProviderPreference` | `providers/models.py` | Provider/model preference for routing |
| `resolve_provider_preferences` | `providers/resolver.py` | Resolve preferences to concrete provider |

## Sources

| Export | Source | Purpose |
|--------|--------|---------|
| `GitSource` | `sources/git.py` | Git URL source handler |
| `FileSource` | `sources/file.py` | Local file source handler |
| `resolve_source` | `sources/resolver.py` | Resolve URI to local path |

## Usage Examples

### Loading a Bundle

```python
from amplifier_foundation import load_bundle

# Load from git URL
bundle = await load_bundle("git+https://github.com/org/bundle@main")

# Load from local file
bundle = await load_bundle("./bundle.md")
```

### Using the Registry

```python
from amplifier_foundation import BundleRegistry

registry = BundleRegistry()
registry.register({
    "foundation": "git+https://github.com/microsoft/amplifier-foundation@main"
})

bundle = await registry.load("foundation")
state = registry.get_state("foundation")
```

### Bundle Composition

```python
from amplifier_foundation import load_bundle

base = await load_bundle("foundation")
overlay = await load_bundle("./overrides.md")
composed = base.compose(overlay)
```

### Validation

```python
from amplifier_foundation import validate_bundle_or_raise

bundle = await load_bundle("./bundle.md")
await validate_bundle_or_raise(bundle)  # Raises on validation errors
```

### Preparation and Session Creation

```python
from amplifier_foundation import load_bundle

bundle = await load_bundle("./bundle.md")
prepared = await bundle.prepare()

async with prepared.create_session() as session:
    response = await session.execute("Hello!")
```

## Type Hints

All APIs use type hints. Use your IDE's type checker (mypy, pyright) for full API documentation:

```python
from amplifier_foundation import Bundle

# Your IDE will show:
# - Method signatures
# - Parameter types
# - Return types
# - Docstrings
```

## Source Code

The authoritative API documentation is in the source code:

- **`amplifier_foundation/__init__.py`** - Public API exports
- **`amplifier_foundation/bundle.py`** - Bundle class implementation
- **`amplifier_foundation/registry.py`** - BundleRegistry implementation
- **`amplifier_foundation/validator.py`** - Validation logic
- **`amplifier_foundation/mentions/`** - @mention resolution
- **`amplifier_foundation/sources/`** - Source resolution
- **`amplifier_foundation/agents/`** - Agent loading
- **`amplifier_foundation/providers/`** - Provider preferences

## Related Documentation

- [Core Concepts](concepts.md) - Mental model and terminology
- [Bundle System](bundle_system.md) - Loading, composition, validation
- [Common Patterns](patterns.md) - Code examples and recipes
