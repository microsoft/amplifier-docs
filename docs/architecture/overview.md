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
await coordinator.mount("providers", provider, name="anthropic")
await coordinator.hooks.emit("session:start", data)
```

### Layer 3: Modules

Modules implement specific functionality:

- **Providers**: LLM API integrations (Anthropic, OpenAI, Azure, Ollama)
- **Tools**: Agent capabilities (filesystem, bash, web, search)
- **Orchestrators**: Execution strategies (basic, streaming, events)
- **Contexts**: ContextManager implementations for memory management (simple, persistent)
- **Hooks**: Observability and control (logging, approval, redaction, streaming)
- **Agents**: Configuration overlays for specialized sub-sessions

```python
# Module implements contract
class AnthropicProvider:
    async def complete(self, request: ChatRequest) -> ChatResponse:
        # Provider-specific implementation
        ...
```

## Component Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                        Application                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Bundles   │  │   Config    │  │  Collections│             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                      │
│         └────────────────┼────────────────┘                      │
│                          │                                       │
│                          ▼                                       │
│                   ┌─────────────┐                                │
│                   │ Mount Plan  │                                │
│                   └──────┬──────┘                                │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────┼──────────────────────────────────────┐
│                        Kernel                                    │
│                   ┌─────────────┐                                │
│                   │   Session   │                                │
│                   └──────┬──────┘                                │
│                          │                                       │
│                          ▼                                       │
│                   ┌─────────────┐                                │
│                   │ Coordinator │                                │
│                   └──────┬──────┘                                │
│         ┌────────────────┼────────────────┐                      │
│         ▼                ▼                ▼                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Loader    │  │    Hooks    │  │   Events    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────┼──────────────────────────────────────┐
│                       Modules                                    │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│  │ Providers │ │   Tools   │ │Orchestrator│ │  Context  │       │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
│                                                                  │
│  ┌───────────────────────────────────────────────────────┐      │
│  │                        Hooks                           │      │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │      │
│  │  │ Logging │ │ Approval│ │Redaction│ │Streaming│     │      │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘     │      │
│  └───────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Session Execution Flow

```
User Prompt
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. Session receives prompt                                       │
│    emit("prompt:submit", {prompt})                              │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Orchestrator takes control                                    │
│    orchestrator.execute(prompt, context, providers, tools)      │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Add prompt to context                                         │
│    context.add_message({role: "user", content: prompt})         │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Call provider                                                 │
│    emit("provider:request", {...})                              │
│    response = provider.complete(messages)                        │
│    emit("provider:response", {...})                             │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Process tool calls (if any)                                   │
│    for tool_call in response.tool_calls:                        │
│        emit("tool:pre", {...})                                  │
│        result = tool.execute(input)                             │
│        emit("tool:post", {...})                                 │
│        context.add_message({role: "tool", ...})                 │
│    → Loop back to step 4 if more tool calls                     │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Return final response                                         │
│    emit("orchestrator:complete", {...})                         │
│    emit("prompt:complete", {...})                               │
│    return response.text                                          │
└─────────────────────────────────────────────────────────────────┘
```

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Kernel** | Ultra-thin core providing mechanisms only (~2,600 lines) |
| **Module** | Swappable component implementing a contract (Protocol) |
| **Mount Plan** | Configuration specifying which modules to load |
| **Event** | Observable occurrence in the system |
| **Hook** | Module that observes/controls events |
| **Session** | Single conversation lifecycle |
| **Coordinator** | Infrastructure context for modules |
| **Context Manager** | Memory management with compaction |
| **Agent** | Configuration overlay for specialized sub-sessions |

## Key Design Decisions

### Why a Tiny Kernel?

1. **Stability**: Fewer changes = fewer breaking changes
2. **Auditability**: Can be reviewed in an afternoon
3. **Maintainability**: Single-throat-to-choke ownership
4. **Flexibility**: All innovation happens at edges

### Why Module Contracts?

1. **Independence**: Modules develop independently
2. **Swappability**: Replace any module without touching others
3. **Testing**: Mock modules for isolated testing
4. **Competition**: Multiple implementations can compete

### Why Events?

1. **Observability**: Everything important is observable
2. **Decoupling**: Emitters don't know about observers
3. **Debugging**: Complete audit trail
4. **Extensions**: Add behavior via hooks, not code changes

### Why Directness Over Abstraction?

1. **Simplicity**: Fewer layers to understand
2. **Maintenance**: Clear code paths
3. **Debugging**: Easy to trace execution
4. **Performance**: No unnecessary indirection

### Decision Framework

When faced with implementation decisions, apply these questions:

1. **Necessity**: "Do we actually need this right now?"
2. **Simplicity**: "What's the simplest way to solve this?"
3. **Directness**: "Can we solve this more directly?"
4. **Value**: "Does the complexity add proportional value?"
5. **Maintenance**: "How easy will this be to understand later?"

## Libraries

Supporting libraries provide higher-level functionality:

| Library | Purpose |
|---------|---------|
| `amplifier-foundation` | Bundle loading, composition, configuration, module resolution, and session management |

These libraries are **not part of the kernel**—they're application-layer concerns.

## For Different Audiences

Now that you understand the architecture, here's where to go based on what you want to do:

### I Want to Use Amplifier
→ Start with [Getting Started](../getting_started/)  
→ Read [CLI User Guide](../user_guide/) for the amplifier-app-cli application

### I Want to Extend Amplifier with Modules
→ Read this Architecture section to understand the system  
→ Follow [Module Developer Guide](../developer/) for creating custom providers, tools, hooks

### I Want to Build Applications on Amplifier
→ Read this Architecture section to understand the foundation  
→ Follow [Application Developer Guide](../developer_guides/applications/) for building apps on amplifier-core  
→ Study [Foundation Guide](../developer_guides/foundation/) for using the core and libraries

### I Want to Contribute to Amplifier Core
→ Read this Architecture section + [Kernel Philosophy](kernel.md)  
→ Follow [Foundation Developer Guide](../developer_guides/foundation/) for working with the kernel and libraries  
→ See [Contributing](../community/contributing.md) for contribution guidelines

## Next Steps

- [Kernel Philosophy](kernel.md) - Deep dive into kernel design
- [Module System](modules.md) - How modules work
- [Mount Plans](mount_plans.md) - Configuration contract
- [Event System](events.md) - Observability

## References

- **→ [Design Philosophy](https://github.com/microsoft/amplifier-core/blob/main/docs/DESIGN_PHILOSOPHY.md)** - Kernel design principles and Linux kernel inspiration
