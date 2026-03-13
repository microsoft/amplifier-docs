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
| `session` | `AmplifierSession` | Parent session reference |
| `session_id` | `str` | Current session ID |
| `parent_id` | `str \| None` | Parent session ID for child sessions |
| `config` | `dict` | Session configuration/mount plan |
| `hooks` | `HookRegistry` | Hook registry for event emission |
| `mount_points` | `dict` | All mount points (orchestrator, providers, tools, context, hooks) |

### Methods

#### `mount(mount_point, module, name=None)`

Mount a module at a specific mount point.

```python
await coordinator.mount("tools", my_tool, name="my-tool")
await coordinator.mount("providers", my_provider, name="anthropic")
await coordinator.mount("orchestrator", my_orchestrator)  # Single module, no name needed
```

#### `unmount(mount_point, name=None)`

Unmount a module from a mount point.

```python
await coordinator.unmount("tools", "my-tool")
```

#### `get(mount_point, name=None)`

Get a mounted module or dict of modules.

```python
# Get single-module mount points
orchestrator = coordinator.get("orchestrator")
context = coordinator.get("context")

# Get all modules at a mount point
all_providers = coordinator.get("providers")  # Returns dict[str, Provider]
all_tools = coordinator.get("tools")          # Returns dict[str, Tool]

# Get specific module by name
provider = coordinator.get("providers", "anthropic")
tool = coordinator.get("tools", "bash")
```

#### `register_cleanup(cleanup_fn)`

Register a cleanup function to be called on shutdown.

#### `register_capability(name, value)`

Register a capability for inter-module communication.

```python
coordinator.register_capability("agents.list", list_agents_fn)
```

#### `get_capability(name)`

Get a registered capability.

```python
list_agents = coordinator.get_capability("agents.list")
```

#### `register_contributor(channel, name, callback)`

Register a contributor for a contribution channel.

```python
coordinator.register_contributor(
    "observability.events",
    "tool-filesystem",
    lambda: ["filesystem:read", "filesystem:write"]
)
```

#### `collect_contributions(channel) -> list[Any]`

Collect contributions from all registered contributors for a channel.

```python
events = await coordinator.collect_contributions("observability.events")
```

### Emitting Events

Events are emitted via the hook registry:

```python
await coordinator.hooks.emit("tool:pre", {"name": "bash", "input": "ls"})
```

### Module Loading

Modules are loaded via the mount plan during session initialization:

```python
# Mount plan specifies modules to load
config = {
    "session": {
        "orchestrator": "loop-basic",
        "context": "context-simple"
    },
    "providers": [{"module": "provider-anthropic"}],
    "tools": [{"module": "tool-bash"}]
}

# Session initialization loads and mounts all modules
async with AmplifierSession(config=config) as session:
    # All modules are now mounted and accessible via coordinator
    orchestrator = session.coordinator.get("orchestrator")
    tools = session.coordinator.get("tools")
```
