---
title: Modules
description: Amplifier module catalog
---

# Modules

Amplifier's functionality is provided by swappable modules. Each module type has a specific purpose and contract.

## Module Types

| Type | Purpose | Mount Point |
|------|---------|-------------|
| **[Providers](providers/index.md)** | LLM backend integration | `providers` |
| **[Tools](tools/index.md)** | Agent capabilities | `tools` |
| **[Orchestrators](orchestrators/index.md)** | Agent loop execution strategy | `orchestrator` |
| **[Contexts](contexts/index.md)** | Conversation memory management | `context` |
| **[Hooks](hooks/index.md)** | Lifecycle observation and control | (registered) |

## Module Catalog

<!-- MODULE_CATALOG -->

## Using Modules

### In Profiles

```yaml
---
name: my-profile
---

providers:
  - module: provider-anthropic
    source: git+https://github.com/microsoft/amplifier-module-provider-anthropic@main
    config:
      default_model: claude-sonnet-4-5

tools:
  - module: tool-filesystem
  - module: tool-bash
```

### In Mount Plans

```python
mount_plan = {
    "session": {
        "orchestrator": "loop-streaming",
        "context": "context-simple"
    },
    "providers": [
        {"module": "provider-anthropic", "source": "git+..."}
    ],
    "tools": [
        {"module": "tool-filesystem"},
        {"module": "tool-bash"}
    ]
}
```

## Creating Modules

See the [Module Development Guide](../developer/module_development.md) for creating your own modules.
