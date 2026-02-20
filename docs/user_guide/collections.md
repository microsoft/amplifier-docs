---
title: Collections
description: Convention-based collection discovery and management for Amplifier applications
---

# Collections

Collections are git repositories with a well-known directory structure that bundle profiles, agents, context files, scenario tools, and modules together. The `amplifier-collections` library provides collection lifecycle management through filesystem conventions — discovering resources by convention, resolving collection names to paths, managing installation, and tracking installed collections via lock files.

## Overview

Collections let you package and share Amplifier resources as a unit. A single collection can include:

- **Profiles** — pre-configured capability sets
- **Agents** — specialized agent definitions
- **Context files** — shared reference material
- **Scenario tools** — task-specific tool packages
- **Modules** — Amplifier modules

## Collection Structure

Collections use **directory structure** to define resources — no manifest file is required. The library auto-discovers resources by checking for well-known directories:

```
my-collection/
├── pyproject.toml          # Collection metadata (required)
├── profiles/               # Profile .md files
│   ├── base.md
│   └── production.md
├── agents/                 # Agent .md files
│   ├── analyzer.md
│   └── optimizer.md
├── context/                # Context .md files (recursive)
│   └── guidelines.md
├── scenario-tools/         # Tool packages (subdirs with pyproject.toml)
│   └── my-tool/
│       └── pyproject.toml
└── modules/                # Amplifier modules (subdirs with pyproject.toml)
    └── my-module/
        └── pyproject.toml
```

Profiles and agents must start with YAML front matter. Configuration inside code fences is ignored.

## Installation

```bash
# From PyPI (when published)
uv pip install amplifier-collections

# From git (development)
uv pip install git+https://github.com/microsoft/amplifier-collections@main

# For local development
cd amplifier-collections
uv pip install -e .
```

## Quick Start

```python
from amplifier_collections import (
    CollectionResolver,
    discover_collection_resources,
    install_collection,
    CollectionLock,
)
from pathlib import Path

# Define search paths for your application
search_paths = [
    Path("/var/amplifier/system/collections"),  # Bundled (lowest)
    Path.home() / ".amplifier" / "collections",  # User
    Path(".amplifier/collections"),              # Project (highest)
]

# Create resolver
resolver = CollectionResolver(search_paths=search_paths)

# Resolve collection name to path
foundation_path = resolver.resolve("foundation")

# Discover resources
resources = discover_collection_resources(foundation_path)
print(f"Found {len(resources.profiles)} profiles")
print(f"Found {len(resources.agents)} agents")
```

## Search Path Precedence

Collections resolve using **first-match-wins** in precedence order:

```
1. PROJECT (highest)    .amplifier/collections/
   → Workspace-specific, overrides everything

2. USER                 ~/.amplifier/collections/
   → User-installed, overrides bundled

3. BUNDLED (lowest)     <app>/data/collections/
   → Application-provided defaults
```

Applications define search paths; the library provides the resolution mechanism.

## Installing Collections

Install a collection from a git source using the CLI or the `install_collection` API:

```python
from amplifier_collections import install_collection
from pathlib import Path

await install_collection(
    name="my-collection",
    source="git+https://github.com/org/my-collection@main",
    target_dir=Path("~/.amplifier/collections")
)
```

To uninstall:

```python
from amplifier_collections import uninstall_collection

await uninstall_collection(
    name="my-collection",
    target_dir=Path("~/.amplifier/collections")
)
```

## Error Handling

| Exception | Raised When |
|-----------|-------------|
| `CollectionError` | Base exception for all collection operations |
| `CollectionInstallError` | Installation or uninstallation fails |
| `CollectionMetadataError` | Invalid or missing collection metadata |
| `CollectionNotFoundError` | Collection not found in search paths |

## Design Philosophy

The library follows **mechanism, not policy**:

- **Library provides mechanism**: How to discover resources, resolve names, install collections, and track state
- **Applications provide policy**: Where to search, what source types to use, when to install

**Convention over configuration** — directory structure IS the configuration. No manifest file is required, which eliminates maintenance burden, drift risk, and duplication.

## See Also

- [Profiles](profiles.md) - Using profiles from collections
- **→ [Collections Library](../libraries/collections.md)** - Full API reference
