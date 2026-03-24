---
title: Architecture Overview
description: High-level architecture of Amplifier
---

# Architecture Overview

Amplifier is built on a modular architecture inspired by the Linux kernel model. This page provides a comprehensive overview of how all the pieces fit together.

## The Linux Kernel Analogy

Amplifier mirrors Linux kernel concepts:

| Linux Concept | Amplifier Analog | Purpose |
|---------------|------------------|---------|
| Ring 0 kernel | `amplifier-core` | Mechanisms only, never policy |
| Syscalls | Session operations | Few, sharp APIs |
| Loadable drivers | Modules | Compete at edges |
| Signals/Netlink | Event bus / hooks | Observe and control |
| /proc & dmesg | JSONL logs | Single canonical stream |
| Capabilities | Approval system | Deny-by-default |
| Scheduler | Orchestrator modules | Swap execution strategies |
| VM/Memory | Context manager | Conversation memory |

## System Layers

### Layer 1: Application

The application layer (e.g., `amplifier-app-cli`) handles:

- User interaction (CLI, REPL)
- Configuration resolution (bundles, profiles, settings)
- Mount Plan creation
- Approval and display systems

```python
# Application defines configuration (mount plan)
config = {
    "session": {"orchestrator": "loop-basic", "context": "context-simple"},
    "providers": [{"module": "provider-anthropic"}],
    "tools": [{"module": "tool-filesystem"}, {"module": "tool-bash"}],
}

# Application creates and runs session
async with AmplifierSession(config) as session:
    response = await session.execute(prompt)
```

### Layer 2: Kernel

The kernel (`amplifier-core`, ~2,600 lines) provides:

- Mount Plan validation
- Module discovery and loading
- Session lifecycle management
- Event emission
- Coordinator infrastructure

```python
# Kernel validates config and loads modules
session = AmplifierSession(config)  # Validates required fields
await session.initialize()  # Discovers and loads all modules

# Modules mount via coordinator
await coordinator.mount("tools", tool_instance)
coordinator.hooks.register("tool:pre", hook_function)

# Events flow through the kernel
await hooks.emit("tool:pre", {...})
```

### Layer 3: Modules

Modules implement policies using kernel mechanisms:

```python
# Provider module
class AnthropicProvider:
    async def complete(self, request: ChatRequest) -> ChatResponse:
        # Decide: which model, what parameters, how to call API
        ...

# Tool module
class BashTool:
    async def execute(self, input: dict) -> ToolResult:
        # Decide: safety checks, command execution, result formatting
        ...

# Hook module
async def logging_hook(event: str, data: dict) -> HookResult:
    # Decide: what to log, where to log, how to redact
    ...
```

## Data Flow

### 1. Session Initialization

```
Application
    ↓ (Mount Plan)
Kernel validates config
    ↓ (Discovers modules via entry points / filesystem)
ModuleLoader
    ↓ (Calls mount() for each module)
Modules register with Coordinator
    ↓
Session ready
```

### 2. Request Execution

```
User prompt
    ↓
Application → Session.execute(prompt)
    ↓
Kernel → Orchestrator.execute()
    ↓
Orchestrator:
    ├─ Get messages from Context
    ├─ Call Provider.complete()
    ├─ Parse tool calls
    ├─ Execute Tools (via Tool.execute())
    ├─ Add results to Context
    └─ Repeat until final response
    ↓
Return response to Application
```

### 3. Event Flow

```
Module emits event
    ↓
Kernel → Hooks.emit(event, data)
    ↓
Hook Registry dispatches to all registered hooks
    ↓
Each Hook returns HookResult
    ↓
Kernel processes results (deny, modify, inject context, etc.)
```

## Module Contracts

All modules use Python `Protocol` (structural typing):

```python
# No inheritance required - just implement the interface
class MyTool:
    @property
    def name(self) -> str: ...
    
    @property
    def description(self) -> str: ...
    
    @property
    def input_schema(self) -> dict: ...
    
    async def execute(self, input: dict) -> ToolResult: ...
```

### Module Types

| Type | Protocol | Required Methods | Purpose |
|------|----------|------------------|---------|
| Provider | `Provider` | `name`, `complete()`, `parse_tool_calls()`, `get_info()`, `list_models()` | LLM backends |
| Tool | `Tool` | `name`, `description`, `input_schema`, `execute()` | Agent capabilities |
| Orchestrator | `Orchestrator` | `execute()` | Execution loops |
| ContextManager | `ContextManager` | `add_message()`, `get_messages()`, `compact()` | Memory |
| Hook | Callable | `__call__(event, data) -> HookResult` | Observability |

## Coordinator

The `ModuleCoordinator` provides infrastructure to modules:

```python
class ModuleCoordinator:
    # Session context
    session_id: str
    config: dict[str, Any]
    
    # Module registration
    async def mount(category: str, module: Any, name: str) -> None
    def get(category: str, name: str | None = None) -> Any
    
    # Hook system
    hooks: HookRegistry
    
    # Capability checks
    def check_capability(name: str) -> bool
    def get_capability(name: str) -> Any
```

Modules receive the coordinator when mounted and use it to:
- Register themselves
- Access other modules
- Emit events via hooks
- Check capabilities

## Mount Plan Specification

Mount Plans are simple dictionaries:

```python
{
    "session": {
        "orchestrator": "loop-streaming",  # Module ID
        "context": "context-simple"         # Module ID
    },
    "providers": [
        {
            "module": "provider-anthropic",  # Required
            "name": "claude",                # Optional
            "source": "git+https://...",     # Optional
            "config": {...}                  # Optional
        }
    ],
    "tools": [...],
    "hooks": [...]
}
```

The kernel validates structure and loads referenced modules.

## Event System

Canonical events flow through the `HookRegistry`:

```python
# Kernel emits events
await hooks.emit("tool:pre", {
    "tool_name": "bash",
    "tool_input": {"command": "ls -la"}
})

# Hooks observe and optionally control
async def approval_hook(event: str, data: dict) -> HookResult:
    if requires_approval(data):
        if not await get_user_approval(data):
            return HookResult(action="deny", reason="User denied")
    return HookResult(action="continue")
```

Events include:
- `execution:start`, `execution:end`
- `prompt:submit`, `prompt:complete`
- `provider:request`, `provider:response`, `provider:error`
- `tool:pre`, `tool:post`, `tool:error`
- `content_block:start`, `content_block:end`
- Custom events from modules

## Module Discovery

Three discovery methods (priority order):

1. **Python Entry Points**
   ```toml
   [project.entry-points."amplifier.modules"]
   tool-bash = "amplifier_module_tool_bash:mount"
   ```

2. **Explicit Search Paths**
   ```python
   loader = ModuleLoader(search_paths=[Path("/custom/modules")])
   ```

3. **Environment Variables**
   ```bash
   export AMPLIFIER_MODULES=/path/to/modules:/other/path
   ```

## Polyglot Module Loading

Modules can be written in any language via four transport types:

| Transport | Usage | Integration |
|-----------|-------|-------------|
| `python` | Direct Python import | Native performance |
| `rust` | Native linking (Rust host) or gRPC sidecar (Python host) | Compiled binary |
| `wasm` | In-process WASM runtime | Sandboxed execution |
| `grpc` | External service | Remote/microservices |

The module declares its transport in `amplifier.toml`. The host runtime decides how to load it.

## Session Lifecycle

```
┌─────────────────────────────────────────────────┐
│ 1. Creation: AmplifierSession(config)           │
│    - Validates Mount Plan                       │
│    - Creates Coordinator                        │
└────────────┬────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────┐
│ 2. Initialization: await session.initialize()  │
│    - Discovers modules                          │
│    - Loads and mounts modules                   │
│    - Registers hooks                            │
└────────────┬────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────┐
│ 3. Execution: await session.execute(prompt)    │
│    - Orchestrator drives agent loop             │
│    - Modules interact via Coordinator           │
│    - Events flow through hooks                  │
└────────────┬────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────┐
│ 4. Cleanup: await session.cleanup()            │
│    - Modules clean up resources                 │
│    - Final events emitted                       │
└─────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. Dependency Injection

Modules receive all dependencies via the `coordinator`:

```python
async def mount(coordinator: ModuleCoordinator, config: dict) -> None:
    # No global state or imports of other modules
    tool = MyTool(config)
    await coordinator.mount("tools", tool, name="my-tool")
```

### 2. Event-Driven Communication

Modules communicate via events, not direct calls:

```python
# Module emits event
await coordinator.hooks.emit("custom:event", {"data": "..."})

# Other modules observe
coordinator.hooks.register("custom:event", my_handler)
```

### 3. Protocol-Based Contracts

No inheritance required - just implement the interface:

```python
# This works without extending any base class
class MyOrchestrator:
    async def execute(self, prompt, context, providers, tools, hooks):
        # Implementation
        ...
```

### 4. Configuration Over Code

Behavior changes via configuration, not code changes:

```yaml
# Change orchestrator without touching code
session:
  orchestrator: loop-streaming  # Was: loop-basic
```

## Backward Compatibility

The kernel maintains strict backward compatibility:

- **Stable APIs**: Session, Coordinator, Module contracts
- **Additive changes**: New optional fields, capabilities
- **Deprecation windows**: Long sunset periods
- **Version detection**: Modules can check kernel version

Modules can break their own APIs - they compete at the edges.

## Next Steps

- **[Kernel Philosophy](../kernel/)** - Learn kernel design principles
- **[Module System](../modules/)** - Understand module loading
- **[Mount Plans](../mount_plans/)** - Configuration specification
- **[Event System](../events/)** - Canonical events reference
