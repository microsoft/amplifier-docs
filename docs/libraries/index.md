---
title: Libraries
description: Amplifier library layer overview
---

# Libraries

The Amplifier ecosystem includes supporting libraries that sit between the kernel (`amplifier-core`) and applications:

```
┌──────────────────────────────────────────────────────────────┐
│  Application (amplifier-app-cli)                            │
│      Uses libraries to resolve configuration                │
└──────┬───────────────────────────────────┬──────────────────┘
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

- Configuration scope resolution
- Module source resolution strategies

## Quick Reference

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
