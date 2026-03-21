---
title: Module System
description: Module loading, coordination, and lifecycle
---

# Module System

The module system enables discovery, loading, and coordination of Amplifier components.

## Overview

Modules are swappable implementations of kernel contracts:

| Module Type | Contract | Mount Point | Purpose |
|-------------|----------|-------------|---------|
| **Provider** | `Provider` | `providers` | LLM backends |
| **Tool** | `Tool` | `tools` | Agent capabilities |
| **Orchestrator** | `Orchestrator` | `orchestrator` | Execution loops |
| **Context** | `ContextManager` | `context` | Memory management |
| **Hook** | `HookHandler` | (registered) | Observability |
| **Resolver** | `ModuleSourceResolver` | `module-source-resolver` | Module sources |

## Module Discovery

Modules are discovered via three methods:

### 1. Python Entry Points

Standard Python entry points in `pyproject.toml`:

```toml
[project.entry-points."amplifier.modules"]
tool-filesystem = "amplifier_module_tool_filesystem:mount"
provider-anthropic = "amplifier_module_provider_anthropic:mount"
```

### 2. Environment Variables

```bash
export AMPLIFIER_MODULES=/path/to/modules:/other/path
```

### 3. Explicit Search Paths

```python
loader = ModuleLoader(search_paths=[Path("/custom/modules")])
```

**Priority**: Entry points → Search paths → Environment variables

## Module Loading

### ModuleLoader

**Source**: `amplifier_core/loader.py`

```python
from amplifier_core.loader import ModuleLoader

# Create loader with coordinator for resolver injection
loader = ModuleLoader(
    coordinator=session.coordinator,  # For source resolver
    search_paths=[Path("/custom/modules")]  # Optional
)

# Discover available modules
modules = await loader.discover()

# Load specific module
mount_fn = await loader.load(
    module_id="provider-anthropic",
    config={"api_key": "..."},
    source_hint="git+https://github.com/...",  # Optional
    coordinator=session.coordinator  # For polyglot dispatch
)

# Initialize the module
cleanup = await mount_fn(session.coordinator)
```

### Module Loading Flow

```
1. Resolve module source
   ├─ Try source resolver (if mounted)
   └─ Fall back to entry point discovery

2. Validate module (Python modules only)
   ├─ Check package structure
   ├─ Verify protocol implementation
   └─ Validate configuration

3. Load module
   ├─ Python: Import and call mount()
   ├─ WASM: Load via Rust engine
   └─ gRPC: Connect to remote service

4. Initialize
   ├─ Call mount(coordinator, config)
   ├─ Register with coordinator
   └─ Return cleanup function
```

## Module Types

### Type Declaration

Modules declare their type via `__amplifier_module_type__`:

```python
# In your module's __init__.py
__amplifier_module_type__ = "tool"  # or "provider", "orchestrator", etc.
```

The kernel uses this to determine the mount point:

| Type | Mount Point |
|------|-------------|
| `orchestrator` | `orchestrator` |
| `provider` | `providers` |
| `tool` | `tools` |
| `hook` | `hooks` |
| `context` | `context` |
| `resolver` | `module-source-resolver` |

**No explicit mount point needed** - it's derived from the type.

### Type Validation

The loader validates modules before loading:

```python
from amplifier_core.loader import ModuleValidationError

try:
    mount_fn = await loader.load("my-module")
except ModuleValidationError as e:
    print(f"Module validation failed: {e}")
```

Validation includes:
- Protocol implementation check
- Entry point verification
- Configuration schema validation (if provided)
- Type compatibility

## Module Coordination

### ModuleCoordinator

**Source**: `amplifier_core/coordinator.py`

The coordinator manages module lifecycles and inter-module communication:

```python
from amplifier_core import ModuleCoordinator

coordinator = ModuleCoordinator()

# Mount a module
await coordinator.mount("tools", my_tool, name="my-tool")

# Get mounted modules
tools = coordinator.get_mounted("tools")

# Get specific module
tool = coordinator.get("tools", "my-tool")

# Register contribution channels
coordinator.register_contributor(
    "observability.events",
    "my-module",
    lambda: ["my-module:event1", "my-module:event2"]
)
```

### Mount Points

Each module type has a designated mount point:

```python
# Providers: dict of Provider instances
providers = coordinator.get_mounted("providers")
provider = coordinator.get("providers", "anthropic")

# Tools: dict of Tool instances
tools = coordinator.get_mounted("tools")
tool = coordinator.get("tools", "filesystem")

# Orchestrator: single instance
orchestrator = coordinator.get("orchestrator")

# Context: single instance
context = coordinator.get("context")

# Hooks: HookRegistry instance
hooks = coordinator.hooks
```

## Polyglot Module Loading

Amplifier supports modules in multiple languages:

### Python Modules

Standard Python modules with `mount()` function:

```python
async def mount(coordinator, config):
    module = MyModule(config)
    await coordinator.mount("tools", module, name="my-tool")
    return cleanup_function
```

### WASM Modules

WebAssembly modules loaded via Rust engine:

```toml
# amplifier.toml
[module]
name = "my-wasm-tool"
type = "tool"
transport = "wasm"

[wasm]
file = "tool.wasm"
```

The loader detects `transport = "wasm"` and dispatches to the WASM loader.

### gRPC Modules

Remote modules accessed via gRPC:

```toml
# amplifier.toml
[module]
name = "my-grpc-tool"
type = "tool"
transport = "grpc"

[grpc]
endpoint = "localhost:50051"
service = "tool.v1.ToolService"
```

The loader detects `transport = "grpc"` and sets up the gRPC channel.

## Module Configuration

Modules receive configuration via the `config` parameter:

```python
async def mount(coordinator, config):
    """
    Args:
        coordinator: ModuleCoordinator instance
        config: dict with module-specific configuration
    """
    api_key = config.get("api_key")
    max_retries = config.get("max_retries", 3)
    
    module = MyModule(api_key=api_key, max_retries=max_retries)
    await coordinator.mount("providers", module, name="my-provider")
    
    return cleanup_function
```

Configuration comes from:
- Bundle YAML files
- Mount Plan specifications
- Runtime overrides

## Module Lifecycle

### 1. Discovery

```python
modules = await loader.discover()
# Returns list of ModuleInfo with id, type, mount_point
```

### 2. Loading

```python
mount_fn = await loader.load(
    module_id="provider-anthropic",
    config={"api_key": "..."}
)
```

### 3. Initialization

```python
cleanup = await mount_fn(coordinator)
```

### 4. Operation

Modules are accessed via the coordinator:

```python
provider = coordinator.get("providers", "anthropic")
response = await provider.complete(request)
```

### 5. Cleanup

```python
if cleanup:
    await cleanup()
```

## Module Source Resolution

The `ModuleSourceResolver` handles finding and downloading modules:

```python
from amplifier_core.module_sources import ModuleSourceResolver

resolver = ModuleSourceResolver()

# Resolve module source
source = resolver.resolve(
    module_id="provider-anthropic",
    source_hint="git+https://github.com/microsoft/amplifier-module-provider-anthropic@main"
)

# Get local path
module_path = source.resolve()
```

### Source Types

- **Git repositories**: `git+https://github.com/org/repo@branch`
- **Local paths**: `/absolute/path/to/module`
- **Python packages**: Package names (via entry points)

## Contribution Channels

Modules can contribute to system-wide registries:

```python
# Register events this module emits
coordinator.register_contributor(
    "observability.events",
    "my-module",
    lambda: ["my-module:started", "my-module:completed"]
)

# Register capabilities
coordinator.register_contributor(
    "capabilities",
    "my-provider",
    lambda: ["streaming", "tool_use", "vision"]
)
```

Available channels:
- `observability.events` - Event names
- `capabilities` - Provider capabilities
- Custom channels defined by applications

## Best Practices

### Module Development

1. **Declare type explicitly**: Use `__amplifier_module_type__`
2. **Validate configuration**: Check required config in `mount()`
3. **Return cleanup**: Always return cleanup function (or None)
4. **Register events**: Use contribution channels
5. **Follow contracts**: Implement full protocol

### Module Loading

1. **Use source resolver**: Delegate to `ModuleSourceResolver`
2. **Handle failures gracefully**: Return None from mount() if config missing
3. **Validate before loading**: Use loader's validation
4. **Track cleanup functions**: Call them on shutdown

### Module Coordination

1. **Use typed access**: `coordinator.get("tools", "name")`
2. **Check availability**: Handle missing modules gracefully
3. **Register contributions**: Make capabilities discoverable
4. **Emit lifecycle events**: Help observability

## Example: Custom Module

```python
# my_module/__init__.py
__amplifier_module_type__ = "tool"

from amplifier_core import ToolResult

class MyTool:
    @property
    def name(self) -> str:
        return "my-tool"
    
    @property
    def description(self) -> str:
        return "My custom tool"
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            },
            "required": ["input"]
        }
    
    async def execute(self, input: dict) -> ToolResult:
        result = f"Processed: {input['input']}"
        return ToolResult(success=True, output=result)

async def mount(coordinator, config):
    """Module entry point."""
    tool = MyTool()
    await coordinator.mount("tools", tool, name=tool.name)
    
    # Register events
    coordinator.register_contributor(
        "observability.events",
        "my-tool",
        lambda: ["my-tool:executed"]
    )
    
    # Return cleanup (if needed)
    return None
```

```toml
# pyproject.toml
[project.entry-points."amplifier.modules"]
my-tool = "my_module:mount"
```

## Related Documentation

- **[Contracts](../developer/contracts/)** - Module protocol specifications
- **[Module Development Guide](../developer/module_development.md)** - Building modules
- **[Mount Plan Specification](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/MOUNT_PLAN_SPECIFICATION.md)** - Configuration format
- **[Module Source Protocol](https://github.com/microsoft/amplifier-core/blob/main/docs/MODULE_SOURCE_PROTOCOL.md)** - Source resolution
