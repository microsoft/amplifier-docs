---
title: Libraries
description: Supporting libraries in the Amplifier ecosystem
---

# Libraries

Amplifier's supporting libraries provide higher-level functionality on top of the kernel. These are **application-layer concerns**, not kernel mechanisms.

## Library Overview

| Library | Purpose | Repository |
|---------|---------|------------|
| **amplifier-profiles** | Profile loading and inheritance | [GitHub](https://github.com/microsoft/amplifier-profiles) |
| **amplifier-config** | Three-scope configuration | [GitHub](https://github.com/microsoft/amplifier-config) |
| **amplifier-module-resolution** | Module source resolution | [GitHub](https://github.com/microsoft/amplifier-module-resolution) |

## Architecture Position

```
┌─────────────────────────────────────────────────────────────┐
│  Application (amplifier-app-cli)                            │
│      Uses libraries to resolve configuration                │
└──────┬────────────────────────────────┬─────────────────────┘
       │                                │
       ▼                                ▼
┌──────────────────┐          ┌──────────────────┐
│ amplifier-       │          │ amplifier-       │
│ profiles         │          │ config           │
└──────────────────┘          └──────────────────┘
       │                                │
       └────────────────┬───────────────┘
                        │
                        ▼
               ┌──────────────────┐
               │ amplifier-       │
               │ module-resolution│
               └──────────────────┘
                        │
                        └───────────────┐
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

<div class="grid">

<div class="card">
<h3><a href="profiles/">Profiles Library</a></h3>
<p>Load and compile profiles to Mount Plans. Handles inheritance, overlays, and @mentions.</p>
</div>

<div class="card">
<h3><a href="config/">Config Library</a></h3>
<p>Three-scope configuration management. Deep merge semantics.</p>
</div>

<div class="card">
<h3><a href="module_resolution/">Module Resolution</a></h3>
<p>Resolve module IDs to sources. Git, file, and package strategies.</p>
</div>

</div>

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
