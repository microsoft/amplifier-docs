---
title: Libraries
description: Amplifier library layer overview
---

# Libraries

The Amplifier ecosystem includes several supporting libraries that sit between the kernel (`amplifier-core`) and applications:

```
┌──────────────────────────────────────────────────────────────┐
│  Application (amplifier-app-cli)                            │
│      Uses libraries to resolve configuration                │
└──────┬──────────────────────────────┬──────────────────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│ amplifier-       │          │ amplifier-       │
│ profiles         │◄────────►│ collections      │
└──────────────────┘          └──────────────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│ amplifier-       │          │ amplifier-       │
│ config           │          │ module-resolution│
└──────────────────┘          └──────────────────┘
       │                              │
       └────────────────┬─────────────┘
                        │
                        ▼
               ┌──────────────────┐
               │ amplifier-core   │
               │ (kernel)         │
               └──────────────────┘
```

Libraries are **not part of the kernel**. They implement application-layer policies for:

- Where to find profiles
- How inheritance works
- Configuration scope resolution
- Module source resolution strategies

## Quick Reference

### [Profiles Library](profiles.md)

Load and compile profiles to Mount Plans. Handles inheritance, overlays, and @mentions.

### [Collections Library](collections.md)

Discover and manage collections. Convention-based resource discovery.

### [Config Library](config.md)

Three-scope configuration management. Deep merge semantics.

### [Module Resolution](module_resolution.md)

Resolve module IDs to sources. Git, file, and package strategies.

## Design Philosophy

These libraries follow the same principles as the kernel:

1. **Mechanism, not policy**: Provide APIs; apps decide how to use them
2. **Composable**: Libraries can be used independently
3. **Swappable**: Apps can provide their own implementations
4. **Testable**: Clear interfaces enable mocking

## Shared Utilities

Some utilities are shared across libraries:

### Deep Merge

```python
from amplifier_profiles import merge_profile_dicts

result = merge_profile_dicts(base, overlay)
```

### Module List Merge

```python
from amplifier_profiles import merge_module_lists

merged = merge_module_lists(base_modules, overlay_modules)
```

These are canonical implementations used consistently across the ecosystem.
