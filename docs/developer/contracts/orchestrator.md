---
title: Orchestrator Contract
description: Execution loop strategy contract
---

# Orchestrator Contract

Orchestrators control how agents execute: the loop structure, tool handling, and response generation.

## Purpose

Orchestrators define the execution strategy:

- **Basic**: Simple request/response loop
- **Streaming**: Real-time token streaming via hooks
- **Events**: Event-driven architecture with callbacks

## Protocol

```python
from typing import Protocol, runtime_checkable
from amplifier_core.interfaces import ContextManager, Provider, Tool
from amplifier_core.hooks import HookRegistry

@runtime_checkable
class Orchestrator(Protocol):
    async def execute(
        self,
        prompt: str,
        context: ContextManager,
        providers: dict[str, Provider],
        tools: dict[str, Tool],
        hooks: HookRegistry,
    ) -> str:
        """Execute the orchestration loop."""
        ...
```

## Mount Function

```python
async def mount(coordinator, config=None):
    config = config or {}
    orchestrator = MyOrchestrator(config)
    await coordinator.mount("session", orchestrator, name="orchestrator")
    return None
```

## Execution Flow

Typical orchestrator flow:

```
1. Add user prompt to context
2. Loop:
   a. Get messages from context (with dynamic token budget)
   b. Emit provider:request
   c. Call provider.complete()
   d. Emit provider:response
   e. Add response to context
   f. Parse tool calls
   g. If no tools: return response
   h. For each tool:
      - Emit tool:pre
      - Execute tool
      - Emit tool:post
      - Add result to context
   i. Continue loop
3. Emit orchestrator:complete (REQUIRED)
4. Return final response
```

## Events

Orchestrators **MUST** emit these events:

| Event | When | Data |
|-------|------|------|
| `prompt:submit` | Received prompt | prompt |
| `provider:request` | Before LLM call | messages, model |
| `provider:stream` | During streaming (optional) | chunk |
| `provider:response` | After LLM call | response, usage |
| `tool:pre` | Before tool execution | tool_name, tool_input |
| `tool:post` | After successful tool execution | tool_name, tool_result |
| `tool:error` | Tool execution failed | tool_name, error |
| `orchestrator:complete` | Execution finished | orchestrator, turn_count, status |

### Required: orchestrator:complete Event

**All orchestrators MUST emit `orchestrator:complete`** at the end of their `execute()` method:

```python
await hooks.emit("orchestrator:complete", {
    "orchestrator": "my-orchestrator",  # Your orchestrator name
    "turn_count": iteration_count,       # Number of LLM turns
    "status": "success"                  # "success", "incomplete", or "cancelled"
})
```

### Required: execution:start and execution:end Events

**All orchestrators MUST emit `execution:start` and `execution:end`** to mark execution boundaries:

```python
async def execute(self, prompt, context, providers, tools, hooks, coordinator=None):
    # REQUIRED: Emit at the very start of execute()
    await hooks.emit("execution:start", {"prompt": prompt})

    try:
        # ... agent loop logic ...

        # REQUIRED: Emit on successful completion
        await hooks.emit("execution:end", {
            "response": final_response,
            "status": "completed"
        })
        return final_response

    except CancelledError:
        # REQUIRED: Emit on cancellation
        await hooks.emit("execution:end", {
            "response": "",
            "status": "cancelled"
        })
        raise

    except Exception:
        # REQUIRED: Emit on error
        await hooks.emit("execution:end", {
            "response": "",
            "status": "error"
        })
        raise
```

## Hook Processing

Handle HookResult actions:

```python
# Before tool execution
pre_result = await hooks.emit("tool:pre", data)

if pre_result.action == "deny":
    # Don't execute tool
    return ToolResult(is_error=True, output=pre_result.reason)

if pre_result.action == "modify":
    # Use modified data
    data = pre_result.data

if pre_result.action == "inject_context":
    # Add feedback to context
    await context.add_message({
        "role": pre_result.context_injection_role,
        "content": pre_result.context_injection
    })

if pre_result.action == "ask_user":
    # Request approval (requires approval provider)
    approved = await request_approval(pre_result)
    if not approved:
        return ToolResult(is_error=True, output="User denied")
```

## Context Management

Manage conversation state:

```python
# Add user message
await context.add_message({"role": "user", "content": prompt})

# Add assistant response
await context.add_message({"role": "assistant", "content": response.content})

# Add tool result
await context.add_message({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": result.output
})

# Get messages for LLM request (context handles compaction internally)
messages = await context.get_messages_for_request()
```

## Provider Selection

Handle multiple providers:

```python
# Get default or configured provider
provider_name = config.get("default_provider", list(providers.keys())[0])
provider = providers[provider_name]

# Or allow per-request provider selection
provider_name = request_options.get("provider", default_provider_name)
```

## Configuration

Orchestrators receive configuration via Mount Plan:

```yaml
session:
  orchestrator: my-orchestrator
  context: context-simple

# Orchestrator-specific config can be passed via providers/tools config
```

See [MOUNT_PLAN_SPECIFICATION.md](../specs/MOUNT_PLAN_SPECIFICATION.md) for full schema.

## Observability

Orchestrators **MUST** register the custom events they emit via the `observability.events` contribution channel:

```python
coordinator.register_contributor(
    "observability.events",
    "my-orchestrator",
    lambda: [
        "my-orchestrator:loop_started",
        "my-orchestrator:loop_iteration",
        "my-orchestrator:loop_completed"
    ]
)
```

> **Note**: The standard `execution:start`, `execution:end`, and `orchestrator:complete` events are registered by the kernel and do not need to be re-registered.

See [CONTRIBUTION_CHANNELS.md](../specs/CONTRIBUTION_CHANNELS.md) for the pattern.

## Canonical Example

**Reference implementation**: [amplifier-module-loop-basic](https://github.com/microsoft/amplifier-module-loop-basic)

Study this module for:
- Complete execute() implementation
- Event emission patterns
- Hook result handling
- Context management

Additional examples:
- [amplifier-module-loop-streaming](https://github.com/microsoft/amplifier-module-loop-streaming) - Real-time streaming
- [amplifier-module-loop-events](https://github.com/microsoft/amplifier-module-loop-events) - Event-driven patterns

## Validation Checklist

### Required

- [ ] Implements `execute(prompt, context, providers, tools, hooks, coordinator=None) -> str`
- [ ] `mount()` function with entry point in pyproject.toml
- [ ] **Emits `execution:start` with `{prompt}` at the very beginning of `execute()`**
- [ ] **Emits `execution:end` with `{response, status}` on ALL exit paths (success, error, cancellation)**
- [ ] Emits standard events (provider:request/response, tool:pre/post)
- [ ] **Emits `orchestrator:complete` at the end of execute()**
- [ ] Handles HookResult actions appropriately
- [ ] Manages context (add messages, check compaction)
- [ ] Registers custom observability events via `coordinator.register_contributor("observability.events", ...)`

### Recommended

- [ ] Supports multiple providers
- [ ] Implements max iterations limit (prevent infinite loops)
- [ ] Handles provider errors gracefully
- [ ] Supports streaming via async generators

## Testing

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import (
    MockCoordinator,
    MockTool,
    MockContextManager,
    ScriptedOrchestrator,
    EventRecorder
)

@pytest.mark.asyncio
async def test_orchestrator_basic():
    orchestrator = MyOrchestrator(config={})
    context = MockContextManager()
    providers = {"test": MockProvider()}
    tools = {"test_tool": MockTool()}
    hooks = HookRegistry()

    result = await orchestrator.execute(
        prompt="Test prompt",
        context=context,
        providers=providers,
        tools=tools,
        hooks=hooks
    )

    assert isinstance(result, str)
    assert len(context.messages) > 0
```

### ScriptedOrchestrator for Testing

```python
from amplifier_core.testing import ScriptedOrchestrator

# For testing components that use orchestrators
orchestrator = ScriptedOrchestrator(responses=["Response 1", "Response 2"])

result = await orchestrator.execute(...)
assert result == "Response 1"
```

## Quick Validation Command

```bash
# Structural validation
amplifier module validate ./my-orchestrator --type orchestrator
```

## See Also

- [README.md](index.md) - All contracts
- [CONTEXT_CONTRACT.md](CONTEXT_CONTRACT.md) - Memory management
