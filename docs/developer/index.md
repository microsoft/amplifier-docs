---
title: Developer Guide
description: Building modules and extending Amplifier
---

# Developer Guide

**Start here for building Amplifier modules.**

This guide covers creating custom modules that extend Amplifier's capabilities: providers, tools, hooks, orchestrators, and context managers.

## Module Types

| Module Type | Contract | Purpose |
|-------------|----------|---------|
| **Provider** | [Provider Contract](contracts/provider.md) | LLM backend integration |
| **Tool** | [Tool Contract](contracts/tool.md) | Agent capabilities |
| **Hook** | [Hook Contract](contracts/hook.md) | Lifecycle observation and control |
| **Orchestrator** | [Orchestrator Contract](contracts/orchestrator.md) | Agent loop execution strategy |
| **Context** | [Context Contract](contracts/context.md) | Conversation memory management |

## Quick Start Pattern

All modules follow this pattern:

```python
# 1. Implement the Protocol from interfaces.py
class MyModule:
    # ... implement required methods
    pass

# 2. Provide mount() function
async def mount(coordinator, config):
    """Initialize and register module."""
    instance = MyModule(config)
    await coordinator.mount("category", instance, name="my-module")
    return instance  # or cleanup function

# 3. Register entry point in pyproject.toml
# [project.entry-points."amplifier.modules"]
# my-module = "my_package:mount"
```

## Source of Truth

**Protocols are in code**, not docs:

- **Protocol definitions**: `python/amplifier_core/interfaces.py`
- **Data models**: `python/amplifier_core/models.py`
- **Message models**: `python/amplifier_core/message_models.py` (Pydantic models for request/response envelopes)
- **Content models**: `python/amplifier_core/content_models.py` (dataclass types for events and streaming)
- **Rust traits**: `crates/amplifier-core/src/traits.rs` (Rust-side trait definitions)
- **Rust/Python type mapping**: [CONTRACTS.md](https://github.com/microsoft/amplifier-core/blob/main/CONTRACTS.md) (authoritative cross-boundary reference)

These contract documents provide **guidance** that code cannot express. Always read the code docstrings first.

## Related Documentation

- [Mount Plan Specification](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/MOUNT_PLAN_SPECIFICATION.md) - Configuration contract
- [Module Source Protocol](https://github.com/microsoft/amplifier-core/blob/main/docs/MODULE_SOURCE_PROTOCOL.md) - Module loading mechanism
- [Contribution Channels](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/CONTRIBUTION_CHANNELS.md) - Module contribution pattern
- [Design Philosophy](https://github.com/microsoft/amplifier-core/blob/main/docs/DESIGN_PHILOSOPHY.md) - Kernel design principles

## Validation

Verify your module before release:

```bash
# Structural validation
amplifier module validate ./my-module
```

See individual contract documents for type-specific validation requirements.

**For ecosystem overview**: [amplifier](https://github.com/microsoft/amplifier)
