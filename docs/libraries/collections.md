---
title: Collections Library
---

# Collections Library

The `amplifier-collections` library provides convention-based collection discovery, resolution, and installation for Amplifier applications.

## Collection Structure

Collections use directory conventions for resource discovery:

```
my-collection/
├── profiles/       # Auto-discovered as profiles
├── agents/         # Auto-discovered as agents
├── context/        # Auto-discovered as context
├── modules/        # Auto-discovered as modules
└── pyproject.toml  # Collection metadata
```

No manifest file needed — the directory structure IS the configuration.

### First-Match-Wins Resolution

Collections are resolved from:

1. `.amplifier/collections/` (project)
2. `~/.amplifier/collections/` (user)
3. Bundled collections

First match wins, enabling project-level overrides.

## Key APIs

### CollectionResolver

```python
from amplifier_collections import CollectionResolver

resolver = CollectionResolver(search_paths=[
    Path(".amplifier/collections"),
    Path("~/.amplifier/collections"),
])

# Resolve collection name to path
path = resolver.resolve("foundation")

# Check if collection exists
if resolver.exists("my-collection"):
    ...
```

### discover_collection_resources

```python
from amplifier_collections import discover_collection_resources

resources = discover_collection_resources(collection_path)
# Returns:
# {
#     "profiles": ["analyst.md", "writer.md"],
#     "agents": ["researcher.md"],
#     "context": ["guidelines.md"],
#     "modules": []
# }
```

### Collection Installation

```python
from amplifier_collections import install_collection, uninstall_collection

# Install from git
await install_collection(
    name="my-collection",
    source="git+https://github.com/org/my-collection@main",
    target_dir=Path("~/.amplifier/collections")
)

# Uninstall
await uninstall_collection(
    name="my-collection",
    target_dir=Path("~/.amplifier/collections")
)
```

### CollectionLock

Track installed collections:

```python
from amplifier_collections import CollectionLock

lock = CollectionLock(Path("~/.amplifier/collections.lock"))

# Add entry
lock.add("my-collection", source="git+...", commit="abc123")

# Check installation
info = lock.get("my-collection")
```

## Collection Metadata

Collections define metadata in `pyproject.toml`:

```toml
[project]
name = "my-collection"
version = "1.0.0"
description = "My awesome collection"

[tool.amplifier.collection]
name = "my-collection"
description = "Collection description"
```

## Integration with Profiles

The collections library integrates with profiles via protocol:

```python
# Profiles library accepts CollectionResolver
from amplifier_profiles import ProfileLoader

loader = ProfileLoader(
    search_paths=[...],
    collection_resolver=collection_resolver
)

# Now profiles can extend collection profiles
# extends: collection:foundation/base
```

## Pluggable Sources

Collection installation supports pluggable sources:

```python
from amplifier_collections import InstallSourceProtocol

class CustomSource(InstallSourceProtocol):
    async def install(self, source: str, target: Path) -> None:
        # Custom installation logic
        ...
```

Built-in sources:

- **GitSource**: Git repositories
- **FileSource**: Local directories

## References

- **→ [amplifier-collections Repository](https://github.com/microsoft/amplifier-collections)** - Full documentation
- **→ [Collection Guide](https://github.com/microsoft/amplifier-collections/blob/main/docs/COLLECTION_GUIDE.md)** - Creating collections
