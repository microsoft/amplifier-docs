---
title: Coordinator API
description: ModuleCoordinator class reference
---

# Coordinator API

The `ModuleCoordinator` manages module lifecycle and provides access to loaded modules.

**Source**: [amplifier_core/coordinator.py](https://github.com/microsoft/amplifier-core/blob/main/amplifier_core/coordinator.py)

## ModuleCoordinator

The coordinator is created by `AmplifierSession` and provides infrastructure context to all modules including:

- Mount points for module attachment
- Infrastructure context (session ID, parent ID, config)
- Capability registry for inter-module communication
- Contribution channels for pull-based aggregation
- Event system with hook registry

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `hooks` | `HookRegistry` | Hook registry for event emission |
| `cancellation` | `CancellationToken` | Cancellation token for graceful shutdown |

### Methods

#### `mount(mount_point, module, name=None)`

Mount a module at a specific mount point.

```python
await coordinator.mount("tools", my_tool, name="my-tool")
await coordinator.mount("providers", my_provider, name="anthropic")
await coordinator.mount("orchestrator", my_orchestrator)  # Single module, no name needed
```

#### `get_capability(name)`

Query a registered capability.

```python
events = coordinator.get_capability("observability.events") or []
working_dir = coordinator.get_capability("session.working_dir")
```

#### `register_capability(name, value)`

Register a capability that other modules can query.

```python
coordinator.register_capability("session.working_dir", "/path/to/project")
```

#### `register_contributor(channel, source, fn)`

Register a contributor function for pull-based aggregation.

```python
coordinator.register_contributor(
    "observability.events",
    "my-module",
    lambda: ["my:event:1", "my:event:2"]
)
```

#### `process_hook_result(result, event, source)`

Process hook results and apply actions.

```python
result = await coordinator.process_hook_result(
    hook_result, "tool:pre", tool_name
)
if result.action == "deny":
    return f"Operation denied: {result.reason}"
```

## Capability Registry

The capability registry enables loose coupling between modules:

```python
# Provider registers model info
coordinator.register_capability("provider.model_info", {
    "context_window": 200_000,
    "max_output_tokens": 8192
})

# Context manager queries it
model_info = coordinator.get_capability("provider.model_info")
if model_info:
    budget = model_info["context_window"] - model_info["max_output_tokens"]
```

## Contribution Channels

Contribution channels enable pull-based aggregation:

```python
# Multiple modules register contributors
coordinator.register_contributor("observability.events", "mod-a", 
    lambda: ["event:a1", "event:a2"])
coordinator.register_contributor("observability.events", "mod-b",
    lambda: ["event:b1"])

# Consumer pulls all contributions
all_events = coordinator.get_capability("observability.events")
# Result: ["event:a1", "event:a2", "event:b1"]
```
