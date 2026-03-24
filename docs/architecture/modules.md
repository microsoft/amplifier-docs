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

# Initialize module (mount it to coordinator)
cleanup = await loader.initialize(mount_fn, coordinator)
```

### Module Loading Flow

```
1. Resolve module source
   ├─ Use ModuleSourceResolver if available
   ├─ Or discover via entry points/filesystem
   └─ Returns: module_path

2. Check transport type (polyglot)
   ├─ python: Direct import
   ├─ rust: Sidecar or native link
   ├─ wasm: In-process WASM runtime
   └─ grpc: External service

3. Validate module (Python only)
   ├─ Check required fields
   ├─ Verify protocol compliance
   └─ Run type-specific validator

4. Load mount function
   ├─ Import module
   ├─ Get mount() function
   └─ Return closure with config

5. Initialize
   ├─ Call mount(coordinator, config)
   ├─ Module registers with coordinator
   └─ Return cleanup function
```

## Module Metadata

Modules declare their type via module-level attribute:

```python
# In module's __init__.py
__amplifier_module_type__ = "tool"  # or "provider", "hook", etc.
```

The kernel derives the mount point from this type using `TYPE_TO_MOUNT_POINT` mapping.

## Module Contracts

### Mount Function

Every module provides a `mount()` function:

```python
async def mount(coordinator: ModuleCoordinator, config: dict[str, Any]) -> Callable | None:
    """Initialize and register module.
    
    Args:
        coordinator: Infrastructure context (session_id, config, hooks, mount points)
        config: Module configuration from Mount Plan
        
    Returns:
        Optional cleanup function to call on session end
    """
    # Create module instance
    instance = MyModule(config)
    
    # Register with coordinator
    await coordinator.mount("tools", instance, name="my-tool")
    
    # Return cleanup function (optional)
    async def cleanup():
        await instance.close()
    
    return cleanup
```

### Module Protocols

Modules implement protocols without inheritance:

```python
# Tool protocol
class MyTool:
    @property
    def name(self) -> str:
        return "my-tool"
    
    @property
    def description(self) -> str:
        return "Does something useful"
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {...}
        }
    
    async def execute(self, input: dict) -> ToolResult:
        # Implementation
        return ToolResult(output="...", error=None)
```

See [Module Contracts](../../reference/contracts/) for complete protocol specifications.

## Polyglot Module Loading

Modules can be written in any language. The transport type determines integration:

### Transport Types

| Transport | Description | Usage |
|-----------|-------------|-------|
| `python` | Direct Python import | Default, native performance |
| `rust` | Native library or gRPC sidecar | Compiled Rust binaries |
| `wasm` | In-process WASM runtime | Sandboxed execution |
| `grpc` | External gRPC service | Remote/microservices |

### How It Works

1. **Module declares transport** in `amplifier.toml`:
   ```toml
   [module]
   transport = "rust"  # or "python", "wasm", "grpc"
   ```

2. **Host selects loading strategy**:
   - Rust host + `transport=rust` → Native link
   - Python host + `transport=rust` → gRPC sidecar
   - Any host + `transport=grpc` → Remote endpoint

3. **Module works transparently** - no code changes needed

### Example: Rust Sidecar

```toml
# amplifier.toml
[module]
transport = "rust"
crate_name = "amplifier_module_my_tool"
```

Python host automatically:
1. Finds compiled binary (`./target/release/amplifier_module_my_tool`)
2. Spawns as sidecar process
3. Connects via gRPC
4. Mounts module normally

## Module Validation

The `ModuleLoader` validates modules before loading (Python modules only):

```python
# Validation happens automatically during load()
await loader.load(
    module_id="tool-bash",
    config={...}
)
# ✓ Checks package structure
# ✓ Verifies required fields (__amplifier_module_type__)
# ✓ Runs type-specific validator (ToolValidator, ProviderValidator, etc.)
# ✓ Validates protocol compliance
```

### Validators by Type

| Type | Validator | Checks |
|------|-----------|--------|
| Provider | `ProviderValidator` | Required methods, protocol compliance |
| Tool | `ToolValidator` | name, description, input_schema, execute() |
| Hook | `HookValidator` | Callable signature |
| Orchestrator | `OrchestratorValidator` | execute() method |
| Context | `ContextValidator` | add_message(), get_messages(), compact() |

## Coordinator Integration

Modules interact via the `ModuleCoordinator`:

### Mounting Modules

```python
# In mount() function
await coordinator.mount("tools", tool_instance, name="bash")
await coordinator.mount("providers", provider_instance, name="anthropic")
```

### Accessing Other Modules

```python
# Get specific module
provider = coordinator.get("providers", name="anthropic")

# Get default module (first mounted)
orchestrator = coordinator.get("orchestrator")

# Get all modules of a type
tools = coordinator.get_all("tools")
```

### Using Hooks

```python
# Register hook
coordinator.hooks.register("tool:pre", my_hook_function)

# Emit event
await coordinator.hooks.emit("tool:post", {
    "tool_name": "bash",
    "result": {...}
})
```

### Checking Capabilities

```python
# Check if capability exists
if coordinator.check_capability("session.working_dir"):
    working_dir = coordinator.get_capability("session.working_dir")
```

## Module Source Resolution

The `ModuleSourceResolver` handles flexible module sourcing:

```python
# Modules can come from:
# - git+https://github.com/org/repo@branch
# - Local paths: /path/to/module
# - Python packages: amplifier-module-tool-bash

source_resolver = coordinator.get("module-source-resolver")
source = await source_resolver.async_resolve(
    "tool-bash",
    source_hint="git+https://github.com/microsoft/amplifier-module-tool-bash@main"
)
module_path = source.resolve()
```

See [Module Source Protocol](../specs/module_source_protocol.md) for details.

## Module Lifecycle

```
┌─────────────────────────────────────────┐
│ 1. Discovery                            │
│    - Entry points                       │
│    - Filesystem search                  │
│    - Environment variables              │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│ 2. Resolution                           │
│    - ModuleSourceResolver (if available)│
│    - Direct discovery (fallback)        │
│    - Returns: module_path               │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│ 3. Transport Check (polyglot)           │
│    - Read amplifier.toml                │
│    - Select: python/rust/wasm/grpc      │
│    - Dispatch to appropriate loader     │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│ 4. Validation (Python only)             │
│    - Package structure                  │
│    - Module metadata                    │
│    - Protocol compliance                │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│ 5. Loading                              │
│    - Import module                      │
│    - Get mount() function               │
│    - Create closure with config         │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│ 6. Mounting                             │
│    - Call mount(coordinator, config)    │
│    - Module registers capabilities      │
│    - Return cleanup function            │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│ 7. Active (during session)              │
│    - Module responds to calls           │
│    - Emits events via hooks             │
│    - Accesses other modules             │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│ 8. Cleanup                              │
│    - Call cleanup function              │
│    - Module releases resources          │
│    - Remove from coordinator            │
└─────────────────────────────────────────┘
```

## Module Isolation

Modules operate in isolation:

- **No shared state**: Each module instance is independent
- **No direct imports**: Modules don't import each other
- **Coordinator-mediated**: All communication via coordinator
- **Error isolation**: Module failures don't crash kernel
- **Resource cleanup**: Cleanup functions release resources

## Best Practices

### 1. Use Module Metadata

Always declare your module type:

```python
__amplifier_module_type__ = "tool"
```

### 2. Handle Configuration

Validate and provide defaults:

```python
async def mount(coordinator, config):
    timeout = config.get("timeout", 30)  # Default
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    ...
```

### 3. Return Cleanup Functions

Release resources properly:

```python
async def mount(coordinator, config):
    connection = await create_connection(config)
    
    async def cleanup():
        await connection.close()
    
    return cleanup
```

### 4. Use Coordinator APIs

Don't bypass the coordinator:

```python
# ✓ Good
provider = coordinator.get("providers", name="anthropic")

# ✗ Bad
from amplifier_module_provider_anthropic import AnthropicProvider
```

### 5. Emit Events

Make your module observable:

```python
await coordinator.hooks.emit("tool:pre", {
    "tool_name": self.name,
    "tool_input": input
})
```

## See Also

- [Module Contracts](../../reference/contracts/) - Protocol specifications
- [Module Source Protocol](../specs/module_source_protocol.md) - Source resolution
- [DESIGN_PHILOSOPHY.md](https://github.com/microsoft/amplifier-core/blob/main/docs/DESIGN_PHILOSOPHY.md) - Kernel vs module boundaries
