---
title: Profiles Library
---

# Profiles Library

The `amplifier-profiles` library handles profile loading, inheritance resolution, and compilation to Mount Plans for `AmplifierSession`.

## Key APIs

### ProfileLoader

```python
from amplifier_profiles import ProfileLoader

loader = ProfileLoader(search_paths=[
    Path(".amplifier/profiles"),
    Path("~/.amplifier/profiles"),
])

# Discover available profiles
profiles = loader.discover()

# Load a specific profile
profile = loader.load("dev")
```

### compile_profile_to_mount_plan

```python
from amplifier_profiles import compile_profile_to_mount_plan

profile = loader.load("dev")
mount_plan = compile_profile_to_mount_plan(profile)

# mount_plan is now ready for AmplifierSession
session = AmplifierSession(mount_plan)
```

### AgentResolver

```python
from amplifier_profiles import AgentResolver

resolver = AgentResolver(
    profile=profile,
    search_paths=[...],
    collection_resolver=collection_resolver
)

# Resolve agent by name
agent_config = resolver.resolve("explorer")
```

## Profile Inheritance

Profiles support multi-level inheritance:

```yaml
---
name: my-profile
extends: dev  # Inherits from dev profile
---
```

Inheritance chain:

```
foundation → base → dev → my-profile
```

### Merge Behavior

| Field | Merge Strategy |
|-------|----------------|
| `session` | Deep merge |
| `providers` | List merge by module ID |
| `tools` | List merge by module ID |
| `hooks` | List merge by module ID |
| `agents` | Deep merge by agent name |
| Markdown content | Concatenated |

### List Merge by Module ID

```yaml
# base profile
tools:
  - module: tool-filesystem
    config:
      read_only: false

# child profile
tools:
  - module: tool-filesystem
    config:
      read_only: true  # Overrides base

# Result: single tool-filesystem with read_only: true
```

## @Mention Expansion

Profiles can reference context files:

```yaml
---
name: my-profile
---

Follow these guidelines:

@project:context/coding-standards.md
@collection:foundation/context/philosophy.md
```

### Mention Syntax

| Syntax | Resolves To |
|--------|-------------|
| `@project:path` | `.amplifier/path` |
| `@user:path` | `~/.amplifier/path` |
| `@collection:name/path` | Collection resource |
| `@path` | Relative to current file |

## Collection Integration

Profiles can extend collection profiles:

```yaml
---
name: my-profile
extends: collection:foundation/base
---
```

The library supports pluggable collection resolution via `CollectionResolver` protocol.

## Search Paths

Default search order:

1. `.amplifier/profiles/` (project)
2. `~/.amplifier/profiles/` (user)
3. Installed collections
4. Bundled profiles

First match wins.

## Error Handling

```python
from amplifier_profiles import ProfileNotFoundError, ProfileCycleError

try:
    profile = loader.load("nonexistent")
except ProfileNotFoundError as e:
    print(f"Profile not found: {e.profile_name}")
except ProfileCycleError as e:
    print(f"Inheritance cycle: {e.cycle}")
```

## References

- **→ [amplifier-profiles Repository](https://github.com/microsoft/amplifier-profiles)** - Full documentation
- **→ [Profile Authoring Guide](https://github.com/microsoft/amplifier-profiles/blob/main/docs/PROFILE_AUTHORING.md)** - Creating profiles
- **→ [Agent Authoring Guide](https://github.com/microsoft/amplifier-profiles/blob/main/docs/AGENT_AUTHORING.md)** - Creating agents
