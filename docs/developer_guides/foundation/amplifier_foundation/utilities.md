---
title: Utilities Reference
description: I/O, dicts, paths, mentions, and caching utilities
---

# Utilities Reference

Reference for utility modules included in amplifier-foundation. The API is fully documented via Python docstrings and type hints; this page provides an overview of what's exported.

**Why this approach?** Documentation that duplicates code becomes context poisoning when it drifts. The code IS the authoritative reference.

## Quick Import

```python
from amplifier_foundation import Bundle, BundleRegistry, load_bundle
```

## I/O Utilities

YAML reading/writing, frontmatter parsing, and file I/O with cloud-sync retry logic.

| Export | Source | Purpose |
|--------|--------|---------|
| `read_yaml` | `io/yaml.py` | Read YAML file (async) |
| `write_yaml` | `io/yaml.py` | Write YAML file (async) |
| `parse_frontmatter` | `io/frontmatter.py` | Parse YAML frontmatter from markdown |
| `read_with_retry` | `io/files.py` | Read with cloud sync retry (async) |
| `write_with_retry` | `io/files.py` | Write with cloud sync retry (async) |

## Dict Utilities

Deep merge for bundle composition and nested dict navigation.

| Export | Source | Purpose |
|--------|--------|---------|
| `deep_merge` | `dicts/merge.py` | Deep merge dictionaries |
| `merge_module_lists` | `dicts/merge.py` | Merge module lists by ID |
| `get_nested` | `dicts/navigation.py` | Get nested dict value by path |
| `set_nested` | `dicts/navigation.py` | Set nested dict value by path |

## Path Utilities

URI parsing, path normalization, file discovery, and path construction for agents and context files.

| Export | Source | Purpose |
|--------|--------|---------|
| `parse_uri` | `paths/resolution.py` | Parse source URI |
| `ParsedURI` | `paths/resolution.py` | Parsed URI dataclass |
| `normalize_path` | `paths/resolution.py` | Normalize/resolve path |
| `construct_agent_path` | `paths/construction.py` | Build agent file path |
| `construct_context_path` | `paths/construction.py` | Build context file path |
| `find_files` | `paths/discovery.py` | Find files by pattern (async) |
| `find_bundle_root` | `paths/discovery.py` | Find bundle root upward (async) |

## @Mention System

Parsing, resolution, loading, and deduplication of `@namespace:path` references in bundle instructions.

### Core Functions

| Export | Source | Purpose |
|--------|--------|---------|
| `parse_mentions` | `mentions/parser.py` | Extract @mentions from text |
| `load_mentions` | `mentions/loader.py` | Load @mention content (async) |

### Models

| Export | Source | Purpose |
|--------|--------|---------|
| `ContextFile` | `mentions/models.py` | Loaded context file data |
| `MentionResult` | `mentions/models.py` | @mention resolution result |
| `ContentDeduplicator` | `mentions/deduplicator.py` | SHA-256 content deduplication |

### Protocols and Implementations

| Export | Source | Purpose |
|--------|--------|---------|
| `MentionResolverProtocol` | `mentions/protocol.py` | @mention resolution contract |
| `BaseMentionResolver` | `mentions/resolver.py` | Default @mention resolver |

### Usage Example

```python
from amplifier_foundation import load_mentions, BaseMentionResolver

resolver = BaseMentionResolver(bundles={"foundation": foundation_bundle})
results = await load_mentions("See @foundation:context/guidelines.md", resolver)
```

## Caching

In-memory and persistent disk caching with protocol-based extensibility.

| Export | Source | Purpose |
|--------|--------|---------|
| `CacheProviderProtocol` | `cache/protocol.py` | Cache provider contract |
| `SimpleCache` | `cache/simple.py` | In-memory cache |
| `DiskCache` | `cache/disk.py` | Persistent disk cache |

## Source Resolution

URI resolution and source handling for loading bundles from git URLs and local paths.

| Export | Source | Purpose |
|--------|--------|---------|
| `SourceResolverProtocol` | `sources/protocol.py` | URI resolution contract |
| `SourceHandlerProtocol` | `sources/protocol.py` | Source type handler contract |
| `SimpleSourceResolver` | `sources/resolver.py` | Git/file source resolver |

## Session Capabilities

Utilities for session working directory management, registered as coordinator capabilities.

| Export | Source | Purpose |
|--------|--------|---------|
| `get_working_dir` | `session/capabilities.py` | Get session working directory from coordinator |
| `set_working_dir` | `session/capabilities.py` | Update session working directory dynamically |
| `WORKING_DIR_CAPABILITY` | `session/capabilities.py` | Capability name constant (`"session.working_dir"`) |

```python
from amplifier_foundation import get_working_dir

# In mount() or tool execute()
working_dir = get_working_dir(coordinator)  # Returns Path
```

## Spawn Utilities

Utilities for spawning sub-sessions with provider/model preferences.

| Export | Source | Purpose |
|--------|--------|---------|
| `ProviderPreference` | `spawn_utils.py` | Dataclass for provider/model preference (supports glob patterns) |
| `apply_provider_preferences` | `spawn_utils.py` | Apply ordered preferences to mount plan |
| `resolve_model_pattern` | `spawn_utils.py` | Resolve glob patterns (e.g., `claude-haiku-*`) to concrete model names |
| `is_glob_pattern` | `spawn_utils.py` | Check if model string contains glob characters |

## Exceptions

| Export | Source | Purpose |
|--------|--------|---------|
| `BundleError` | `exceptions.py` | Base exception |
| `BundleNotFoundError` | `exceptions.py` | Bundle not found |
| `BundleLoadError` | `exceptions.py` | Bundle load/parse failed |
| `BundleValidationError` | `exceptions.py` | Validation failed |
| `BundleDependencyError` | `exceptions.py` | Dependency resolution failed |

## Reading the Source

Each source file has comprehensive docstrings. To read them:

```bash
# In your editor
code amplifier_foundation/bundle.py

# Or via Python
python -c "from amplifier_foundation import Bundle; help(Bundle)"

# Or via pydoc
python -m pydoc amplifier_foundation.Bundle
```

## Common Patterns

### Load and Use a Bundle

```python
from amplifier_foundation import load_bundle

bundle = await load_bundle("git+https://github.com/org/my-bundle@main")
mount_plan = bundle.to_mount_plan()
```

### Compose Bundles

```python
from amplifier_foundation import load_bundle

base = await load_bundle("foundation")
overlay = await load_bundle("./local-overlay.md")
composed = base.compose(overlay)
```

### Registry Management

```python
from amplifier_foundation import BundleRegistry

registry = BundleRegistry()
registry.register({"my-bundle": "git+https://github.com/org/bundle@main"})
bundle = await registry.load("my-bundle")
```
