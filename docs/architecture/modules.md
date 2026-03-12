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

# Initialize (mount into coordinator)
cleanup = await loader.initialize(mount_fn, session.coordinator)
```

### Mount Function Pattern

Every module exports a `mount` function:

```python
async def mount(
    coordinator: ModuleCoordinator,
    config: dict[str, Any] | None = None
) -> Callable | None:
    """
    Initialize and register module with coordinator.

    Returns:
        Optional cleanup function to unregister
    """
    config = config or {}
    
    # Create module instance
    instance = MyModule(config)
    
    # Mount into coordinator
    await coordinator.mount("tools", instance, name=instance.name)
    
    # Return cleanup function
    def cleanup():
        # Unregister handlers, close connections, etc.
        pass
    
    return cleanup
```

## Module Coordination

### ModuleCoordinator

**Source**: `amplifier_core/coordinator.py` (Rust-backed via PyO3)

The coordinator manages mount points and provides access to mounted modules:

```python
from amplifier_core.coordinator import ModuleCoordinator

coordinator = ModuleCoordinator()

# Mount module
await coordinator.mount("tools", tool_instance, name="my-tool")

# Get mounted module
tool = coordinator.get("tools", "my-tool")

# Get all modules at mount point
all_tools = coordinator.get("tools")

# Check if mount point exists
has_tools = coordinator.has("tools")
```

### Mount Points

Standard mount points:

| Mount Point | Type | Cardinality | Purpose |
|-------------|------|-------------|---------|
| `orchestrator` | Single | Required | Execution loop |
| `context` | Single | Required | Memory management |
| `providers` | Dictionary | Optional | LLM backends by name |
| `tools` | Dictionary | Optional | Tools by name |
| `module-source-resolver` | Single | Optional | Module sources |

**Key pattern**: Session-scoped modules (orchestrator, context) are singular. Capability modules (providers, tools) are dictionaries.

## Type-to-Mount Point Mapping

**Source**: `amplifier_core/loader.py` lines 29-38

The kernel derives mount points from module types via a stable mapping:

```python
TYPE_TO_MOUNT_POINT = {
    "orchestrator": "orchestrator",
    "provider": "providers",
    "tool": "tools",
    "hook": "hooks",
    "context": "context",
    "resolver": "module-source-resolver",
}
```

**Design principle**: Modules declare type via `__amplifier_module_type__` attribute. The kernel derives the mount point. This is mechanism (kernel), not policy (module).

**Fallback**: If no type is declared, the loader uses naming conventions (e.g., "provider" in module ID → "provider" type).

## Module Validation

Modules are validated before loading:

```python
from amplifier_core.validation import (
    ProviderValidator,
    ToolValidator,
    HookValidator,
    OrchestratorValidator,
    ContextValidator
)

validator = ToolValidator()
result = await validator.validate(package_path, config=config)

if not result.passed:
    raise ModuleValidationError(result.summary())
```

**Validation checks**:
- Required protocol methods exist
- Mount function signature is correct
- Entry point is registered
- Package structure is valid

## Module Source Resolution

Modules can be loaded from multiple sources:

### ModuleSourceResolver Protocol

```python
class ModuleSourceResolver(Protocol):
    def resolve(
        self,
        module_id: str,
        source_hint: str | dict | None = None,
        profile_hint: str | dict | None = None  # Deprecated
    ) -> ModuleSource:
        """Resolve module ID to a filesystem path."""
        ...
    
    async def async_resolve(
        self,
        module_id: str,
        source_hint: str | dict | None = None,
        profile_hint: str | dict | None = None  # Deprecated
    ) -> ModuleSource:
        """Async resolution for lazy activation."""
        ...
```

### Source Types

- **Entry points**: Installed Python packages
- **Git repositories**: `git+https://github.com/org/repo@tag`
- **Local paths**: `/path/to/module`
- **Package registries**: PyPI, private registries

### Resolution Flow

```
1. Check if resolver mounted in coordinator
2. If yes: resolver.resolve(module_id, source_hint)
3. If no: Fall back to direct entry-point discovery
4. Add resolved path to sys.path
5. Validate module structure
6. Load via entry point or filesystem import
```

**Source**: `amplifier_core/loader.py` lines 176-338

## Polyglot Modules (WASM, gRPC)

The loader supports non-Python modules via transport dispatch:

### Transport Detection

**Source**: `amplifier_core/loader.py` lines 262-289

```python
# Loader checks amplifier.toml for transport field
from amplifier_core._engine import resolve_module

manifest = resolve_module(str(module_path))
transport = manifest.get("transport", "python")

if transport == "wasm":
    return self._make_wasm_mount(module_path, coordinator)

if transport == "grpc":
    return await self._make_grpc_mount(module_path, module_id, config, coordinator)

# Default: Python modules
```

### WASM Modules

**Source**: `amplifier_core/loader.py` lines 627-658

```python
def _make_wasm_mount(self, module_path: Path, coordinator: ModuleCoordinator):
    """Load WASM module via Rust load_and_mount_wasm()."""
    from amplifier_core._engine import load_and_mount_wasm
    
    async def wasm_mount(coord: ModuleCoordinator) -> Callable | None:
        result = load_and_mount_wasm(coord, str(module_path))
        logger.info(f"[module:mount] WASM mounted: {result}")
        return None  # No cleanup function for WASM modules
    
    return wasm_mount
```

### gRPC Modules

**Source**: `amplifier_core/loader.py` lines 660-697

```python
async def _make_grpc_mount(
    self, module_path: Path, module_id: str,
    config: dict[str, Any] | None, coordinator: ModuleCoordinator
):
    """Load gRPC module via gRPC loader bridge."""
    from .loader_grpc import load_grpc_module
    
    # Read amplifier.toml for gRPC config
    toml_path = module_path / "amplifier.toml"
    meta = {}
    if toml_path.exists():
        with open(toml_path, "rb") as f:
            meta = tomli.load(f)
    
    return await load_grpc_module(module_id, config, meta, coordinator)
```

## Module Lifecycle

### 1. Discovery

```python
loader = ModuleLoader(coordinator=coordinator)
modules = await loader.discover()
```

Scans entry points, search paths, and environment variables.

### 2. Resolution

```python
mount_fn = await loader.load(
    module_id="provider-anthropic",
    source_hint="git+https://github.com/...",
    coordinator=coordinator
)
```

Resolves module location via resolver or direct discovery.

### 3. Validation

Before loading, modules are validated for contract compliance.

### 4. Loading

Module code is imported and mount function is extracted.

### 5. Mounting

```python
cleanup = await loader.initialize(mount_fn, coordinator)
```

Mount function registers module with coordinator.

### 6. Cleanup

```python
if cleanup:
    cleanup()  # Unregister handlers, close connections
```

Cleanup function (if returned) is called during session cleanup.

## Module Metadata

Modules declare metadata via module attributes:

```python
# In module's __init__.py
__amplifier_module_type__ = "tool"  # Required
__version__ = "1.0.0"                # Optional
__description__ = "Tool description" # Optional
```

**Type is REQUIRED** - the kernel uses `__amplifier_module_type__` to derive the mount point via `TYPE_TO_MOUNT_POINT` mapping.

## Error Handling

### ModuleValidationError

Raised when a module fails validation:

```python
from amplifier_core.loader import ModuleValidationError

try:
    await loader.load("my-module")
except ModuleValidationError as e:
    print(f"Validation failed: {e}")
```

### ModuleNotFoundError

Raised when source resolution fails:

```python
from amplifier_core.module_sources import ModuleNotFoundError

try:
    mount_fn = await loader.load("unknown-module")
except ModuleNotFoundError as e:
    print(f"Module not found: {e}")
```

## Testing

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import MockCoordinator

@pytest.mark.asyncio
async def test_module_loading():
    coordinator = MockCoordinator()
    loader = ModuleLoader(coordinator=coordinator)
    
    # Load module
    mount_fn = await loader.load("my-module")
    
    # Mount into coordinator
    cleanup = await loader.initialize(mount_fn, coordinator)
    
    # Verify mounting
    module = coordinator.get("tools", "my-tool")
    assert module is not None
    
    # Cleanup
    if cleanup:
        cleanup()
```

## Cleanup Pattern

**Source**: `amplifier_core/loader.py` lines 719-728

The loader tracks sys.path additions and cleans them up:

```python
def cleanup(self) -> None:
    """Remove all sys.path entries added by this loader."""
    for path in reversed(self._added_paths):
        try:
            sys.path.remove(path)
            logger.debug(f"Removed '{path}' from sys.path")
        except ValueError:
            logger.debug(f"Path '{path}' already removed from sys.path")
    self._added_paths.clear()
```

**Key pattern**: Loader adds module paths to sys.path during loading, tracks them, and removes them during cleanup to avoid polluting the Python environment.

## See Also

- [Module Contracts](../developer/contracts/index.md) - Protocol specifications
- [Kernel Philosophy](kernel.md) - Design principles
- [Architecture Overview](overview.md) - High-level architecture
