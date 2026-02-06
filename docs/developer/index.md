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

| Source | Description |
|--------|-------------|
| `amplifier_core/interfaces.py` | Protocol definitions |
| `amplifier_core/models.py` | Data models |
| `amplifier_core/message_models.py` | Pydantic models for request/response |
| `amplifier_core/content_models.py` | Dataclass types for events and streaming |

These contract documents provide **guidance** that code cannot express. Always read the code docstrings first.

## Configuration

Modules receive configuration from Mount Plans:

```yaml
tools:
  - module: my-tool
    source: git+https://github.com/org/my-tool@main
    config:
      option1: value1
      debug: true
```

Configuration options should be documented in your module's README.

## Validation

Verify your module before release:

```bash
# Structural validation
amplifier module validate ./my-module
```

See individual contract documents for type-specific validation requirements.

## Streaming Support

Modules can participate in streaming:

```python
# Provider streaming
async for chunk in provider.stream_complete(request):
    await hooks.emit("provider:stream", {"chunk": chunk})

# Hook handles streaming display
async def streaming_hook(event, data):
    if event == "provider:stream":
        print(data["chunk"].get("text", ""), end="", flush=True)
    return HookResult(action="continue")
```

## Module Development Guide

For detailed guidance on building each module type:

<div class="grid">

<div class="card">
<h3><a href="module_development/">Module Development</a></h3>
<p>Complete guide to creating Amplifier modules.</p>
</div>

<div class="card">
<h3><a href="contracts/provider/">Provider Contract</a></h3>
<p>Integrate LLM backends.</p>
</div>

<div class="card">
<h3><a href="contracts/tool/">Tool Contract</a></h3>
<p>Add agent capabilities.</p>
</div>

<div class="card">
<h3><a href="contracts/hook/">Hook Contract</a></h3>
<p>Observe and control operations.</p>
</div>

</div>

## Related Documentation

- **[Mount Plan Specification](../architecture/mount_plans.md)** - Configuration contract
- **[Event System](../architecture/events.md)** - Observability patterns
- **[Design Philosophy](../architecture/overview.md)** - Kernel design principles

## Best Practices

### Graceful Degradation

Modules should handle missing dependencies gracefully:

```python
async def mount(coordinator, config=None):
    config = config or {}
    api_key = config.get("api_key") or os.environ.get("MY_API_KEY")
    
    if not api_key:
        # Return None - don't block other modules
        return None
    
    module = MyModule(config)
    await coordinator.mount("providers", module, name="my-provider")
    return module.cleanup
```

### Error Handling

Return structured errors instead of raising exceptions:

```python
async def execute(self, input: dict) -> ToolResult:
    try:
        result = await self._do_work(input)
        return ToolResult(success=True, output=result)
    except ValueError as e:
        return ToolResult(
            success=False,
            error={"message": str(e), "type": "ValueError"}
        )
```

### Testing

Include comprehensive tests:

```python
import pytest

@pytest.mark.asyncio
async def test_mount():
    coordinator = MockCoordinator()
    cleanup = await mount(coordinator, {"api_key": "test"})
    
    assert "my-module" in coordinator.modules
    assert cleanup is not None
```

## Authoritative Reference

**→ [Module Contracts](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/README.md)** - Complete contract documentation

**→ [amplifier-core](https://github.com/microsoft/amplifier-core)** - Kernel source code
