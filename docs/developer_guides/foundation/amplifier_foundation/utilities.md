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
| `get_amplifier_home` | `paths/resolution.py` | Get Amplifier home directory |
| `construct_agent_path` | `paths/construction.py` | Build agent file path |
| `construct_context_path` | `paths/construction.py` | Build context file path |
| `find_files` | `paths/discovery.py` | Find files by pattern (async) |
| `find_bundle_root` | `paths/discovery.py` | Find bundle root upward (async) |

## Mention Utilities

@mention parsing, resolution, and content loading with deduplication.

| Export | Source | Purpose |
|--------|--------|---------|
| `parse_mentions` | `mentions/parser.py` | Extract @mentions from text |
| `load_mentions` | `mentions/loader.py` | Load @mention content (async) |
| `ContentDeduplicator` | `mentions/deduplicator.py` | SHA-256 content deduplication |
| `ContextFile` | `mentions/models.py` | Loaded context file data |
| `MentionResult` | `mentions/models.py` | @mention resolution result |
| `BaseMentionResolver` | `mentions/resolver.py` | Default @mention resolver |
| `MentionResolverProtocol` | `mentions/protocol.py` | @mention resolution contract |

## Cache Utilities

Caching providers for performance optimization.

| Export | Source | Purpose |
|--------|--------|---------|
| `SimpleCache` | `cache/simple.py` | In-memory cache |
| `DiskCache` | `cache/disk.py` | Persistent disk cache |
| `CacheProviderProtocol` | `cache/protocol.py` | Cache provider contract |

## Session Capabilities

Utilities for session-level capabilities and working directory management.

| Export | Source | Purpose |
|--------|--------|---------|
| `get_working_dir` | `session/capabilities.py` | Get session working directory from coordinator |
| `set_working_dir` | `session/capabilities.py` | Update session working directory dynamically |
| `WORKING_DIR_CAPABILITY` | `session/capabilities.py` | Capability name constant (`"session.working_dir"`) |

## Spawn Utilities

Utilities for spawning sub-sessions with provider/model preferences.

| Export | Source | Purpose |
|--------|--------|---------|
| `ProviderPreference` | `spawn_utils.py` | Dataclass for provider/model preference (supports glob patterns) |
| `apply_provider_preferences` | `spawn_utils.py` | Apply ordered preferences to mount plan |
| `resolve_model_pattern` | `spawn_utils.py` | Resolve glob patterns (e.g., `claude-haiku-*`) to concrete model names |
| `is_glob_pattern` | `spawn_utils.py` | Check if model string contains glob characters |

## Source Utilities

URI resolution and source handling.

| Export | Source | Purpose |
|--------|--------|---------|
| `SimpleSourceResolver` | `sources/resolver.py` | Git/file source resolver |
| `SourceResolverProtocol` | `sources/protocol.py` | URI resolution contract |
| `SourceHandlerProtocol` | `sources/protocol.py` | Source type handler contract |

## Reading the Source

Each utility module has comprehensive docstrings. To read them:

```bash
# In your editor
code amplifier_foundation/io/yaml.py

# Or via Python
python -c "from amplifier_foundation.io import read_yaml; help(read_yaml)"

# Or via pydoc
python -m pydoc amplifier_foundation.io.yaml
```

## Usage Examples

### Deep Merge

```python
from amplifier_foundation import deep_merge

base = {"a": 1, "b": {"c": 2}}
overlay = {"b": {"d": 3}, "e": 4}
result = deep_merge(base, overlay)
# Result: {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}
```

### Path Resolution

```python
from amplifier_foundation import parse_uri, normalize_path

# Parse git URI
uri = parse_uri("git+https://github.com/org/repo@main#subdirectory=foo")
# uri.scheme = "git+https"
# uri.host = "github.com"
# uri.ref = "main"
# uri.subdirectory = "foo"

# Normalize path
path = normalize_path("./relative/path", base_path="/base")
# Returns absolute path
```

### @Mention Loading

```python
from amplifier_foundation import load_mentions, BaseMentionResolver

resolver = BaseMentionResolver(bundles={"foundation": foundation_bundle})
results = await load_mentions("See @foundation:context/guidelines.md", resolver)

for result in results:
    print(f"Loaded: {result.mention} -> {result.content[:100]}...")
```

### Working Directory Management

```python
from amplifier_foundation import get_working_dir, set_working_dir

# Get current working directory
working_dir = get_working_dir(coordinator)  # Returns Path

# Update working directory mid-session
set_working_dir(coordinator, Path("/new/working/dir"))
```

## Next Steps

- [API Reference](api_reference.md) - Complete API documentation
- [Core Concepts](concepts.md) - Understanding the bundle system
- [Common Patterns](patterns.md) - Practical usage patterns
