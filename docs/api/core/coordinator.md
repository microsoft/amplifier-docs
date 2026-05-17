---
title: Coordinator API
description: ModuleCoordinator class reference
---

# Coordinator API

The `ModuleCoordinator` manages module lifecycle and provides access to loaded modules.

**Source**: [amplifier_core/coordinator.py](https://github.com/microsoft/amplifier-core/blob/main/python/amplifier_core/coordinator.py)

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

Query a registered capability. Returns `None` if the capability has not been registered.

```python
value = coordinator.get_capability("my.capability")
if value is None:
    # Capability not registered
    pass
```

#### `register_capability(name, value)`

Register a capability that other modules can query. Calling again with the same name overwrites the previous value.

```python
coordinator.register_capability("my.capability", some_value)
```

## Capability Registry

The capability registry enables loose coupling between modules:

```python
# Module A registers a capability
coordinator.register_capability("agents.list", get_agent_list)

# Module B queries it
agents_fn = coordinator.get_capability("agents.list")
if agents_fn:
    agents = agents_fn()
```


