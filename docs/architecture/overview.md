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
await coordinator.mount("tools", tool_instance, name="my-tool")

# Session executes
response = await session.execute(prompt)
```

The kernel is implemented in **Rust** with Python bindings via PyO3:
- Same API for Python consumers
- Type-safe session management
- Fast event dispatch
- Efficient hook processing

### Layer 3: Modules

Modules implement specific functionality:

| Module Type | Examples | Mount Point |
|-------------|----------|-------------|
| **Providers** | Anthropic, OpenAI, Azure | `providers` |
| **Tools** | Filesystem, Bash, Web | `tools` |
| **Orchestrators** | Basic loop, Streaming | `orchestrator` |
| **Contexts** | Simple, Persistent | `context` |
| **Hooks** | Logging, Approval | (registered) |

```python
# Modules discovered via entry points
[project.entry-points."amplifier.modules"]
tool-filesystem = "amplifier_module_tool_filesystem:mount"

# Module implements protocol
class MyTool:
    @property
    def name(self) -> str: return "my_tool"
    
    @property
    def description(self) -> str: return "Does X"
    
    async def execute(self, input: dict) -> ToolResult: ...
```

## Data Flow

```
User Prompt
    ↓
Application Layer
    ↓ (mount plan)
Kernel (AmplifierSession)
    ↓ (load modules)
Coordinator
    ↓ (orchestrator.execute())
Orchestrator Module
    ↓ (context.get_messages())
Context Manager
    ↓ (provider.complete())
Provider Module
    ↓ (tool.execute())
Tool Modules
    ↓ (hooks.emit())
Hook Modules
    ↓
Final Response
```

## Event Flow

The kernel emits lifecycle events through the hook system:

```
session:start → execution:start → provider:request → provider:response
    ↓
tool:pre → tool:post (repeat for each tool)
    ↓
execution:end → orchestrator:complete → session:end
```

**Hook modules observe events**:
- Log to files (hooks-logging)
- Request approval (hooks-approval)
- Redact secrets (hooks-redaction)
- Custom observability (your hooks)

## Module Contracts

Modules communicate via stable protocols:

```python
# Provider Protocol
class Provider(Protocol):
    @property
    def name(self) -> str: ...
    def get_info(self) -> ProviderInfo: ...
    async def list_models(self) -> list[ModelInfo]: ...
    async def complete(self, request: ChatRequest) -> ChatResponse: ...
    def parse_tool_calls(self, response: ChatResponse) -> list[ToolCall]: ...

# Tool Protocol
class Tool(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def description(self) -> str: ...
    async def execute(self, input: dict[str, Any]) -> ToolResult: ...

# Orchestrator Protocol
class Orchestrator(Protocol):
    async def execute(
        self, prompt: str, context: ContextManager,
        providers: dict[str, Provider], tools: dict[str, Tool],
        hooks: HookRegistry
    ) -> str: ...

# ContextManager Protocol
class ContextManager(Protocol):
    async def add_message(self, message: dict[str, Any]) -> None: ...
    async def get_messages_for_request(
        self, token_budget: int | None = None,
        provider: Any | None = None
    ) -> list[dict[str, Any]]: ...
    async def get_messages(self) -> list[dict[str, Any]]: ...
    async def set_messages(self, messages: list[dict[str, Any]]) -> None: ...
    async def clear(self) -> None: ...

# HookHandler Protocol
class HookHandler(Protocol):
    async def __call__(self, event: str, data: dict[str, Any]) -> HookResult: ...
```

Protocols use structural subtyping (duck typing) - no inheritance required.

## Configuration Flow

```
User Settings (~/.amplifier/settings.yaml)
    ↓ (profile selection)
Profile Config
    ↓ (bundle loading)
Bundle Config
    ↓ (CLI overrides)
Mount Plan
    ↓ (validation)
AmplifierSession(config)
    ↓ (module loading)
Running Session
```

## The Rust Kernel

amplifier-core is implemented in Rust with Python bindings:

```
┌─────────────────────────────────────────────────┐
│  RUST KERNEL (crates/amplifier-core/)           │
│  * Session lifecycle   * Event system           │
│  * Coordinator         * Hook registry          │
│  * Type-safe contracts * Cancellation tokens    │
└────────────────────┬────────────────────────────┘
                     │ PyO3 bridge
                     ▼
┌─────────────────────────────────────────────────┐
│  PYTHON BINDINGS (python/amplifier_core/)       │
│  * Same public API    * Pydantic models         │
│  * Module loader      * Backward-compatible     │
└────────────────────┬────────────────────────────┘
                     │ protocols
                     ▼
┌─────────────────────────────────────────────────┐
│  MODULES (Python, WASM, gRPC)                   │
│  * Providers, Tools, Orchestrators, Contexts... │
└─────────────────────────────────────────────────┘
```

**Key features**:
- Zero changes for Python consumers
- Type-safe core with Protocol-based modules
- Fast event dispatch
- Efficient hook processing
- Cancellation primitives

## Design Principles

### Mechanism vs Policy

The kernel provides **mechanisms** (capabilities), modules provide **policies** (decisions):

| Mechanism (Kernel) | Policy (Modules) |
|-------------------|------------------|
| Load modules | Which modules to load |
| Emit events | What to log, where |
| Manage sessions | Orchestration strategy |
| Register hooks | Security policies |

### Stable Contracts

- **Backward compatible**: Old modules work with new kernel
- **Protocol-based**: Duck typing, no inheritance
- **Additive evolution**: Add features, don't break existing
- **Documented**: Clear expectations and examples

### Event-First Observability

- If it's important → emit a canonical event
- If it's not observable → it didn't happen
- One JSONL stream = single source of truth
- Hooks observe without blocking

## Session Lifecycle

```python
# Create session
session = AmplifierSession(
    config=config,
    session_id=None,           # Auto-generated
    parent_id=None,            # None for top-level
    approval_system=None,      # App-layer policy
    display_system=None,       # App-layer policy
    is_resumed=False           # Controls event emission
)

# Initialize (load modules)
await session.initialize()

# Execute prompt
response = await session.execute(prompt)

# Cleanup
await session.cleanup()
```

**Session states**:
- `created` - Initialized but not yet executed
- `running` - Currently executing
- `completed` - Finished successfully
- `failed` - Encountered error
- `cancelled` - User cancelled

**Lifecycle events**:
- `session:start` - New session begins
- `session:resume` - Session resumed
- `session:fork` - Child session created
- `session:end` - Session cleanup

## Child Sessions (Forking)

Sessions can spawn child sessions for agent delegation:

```python
child_session = AmplifierSession(
    config=child_config,
    session_id="child-id",
    parent_id=parent_session.session_id,  # Links to parent
    approval_system=parent_approval,
    display_system=parent_display
)
```

**W3C Trace Context pattern**:
- Root session ID becomes the `trace_id`
- All children inherit the same `trace_id`
- Enables distributed tracing across agent hierarchies

## See Also

- [Kernel Philosophy](kernel.md) - Design principles
- [Module System](modules.md) - Module loading and coordination
- [Module Contracts](../developer/contracts/index.md) - Protocol specifications
- [Design Philosophy](https://github.com/microsoft/amplifier-core/blob/main/docs/DESIGN_PHILOSOPHY.md) - Complete philosophy
