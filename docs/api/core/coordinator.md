---
title: Coordinator API
description: ModuleCoordinator class reference
---

# Coordinator API

The `ModuleCoordinator` manages module lifecycle and provides access to loaded modules.

**Source**: [amplifier_core/coordinator.py](https://github.com/microsoft/amplifier-core/blob/main/amplifier_core/coordinator.py)

!!! note "Implementation Location"
    The coordinator implementation lives in the Rust kernel (`amplifier_core._engine.RustCoordinator`). The Python module re-exports it for backward compatibility:
    ```python
    from amplifier_core.coordinator import ModuleCoordinator
    ```

## ModuleCoordinator

The coordinator is created by `AmplifierSession` and provides infrastructure context to all modules including:

- Mount points for module attachment
- Infrastructure context (session ID, parent ID, config)
- Capability registry for inter-module communication
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


