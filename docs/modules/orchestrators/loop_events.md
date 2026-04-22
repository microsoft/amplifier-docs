---
title: loop-events
description: Event-driven orchestrator with scheduler integration
---

# loop-events Orchestrator

Event-driven agent loop orchestrator that trusts LLM decisions with optional scheduler veto/modification.

## Overview

The `loop-events` orchestrator provides an event-driven execution model where:

- LLM makes tool/agent decisions
- Schedulers can observe and optionally veto/modify decisions
- Falls back gracefully if no schedulers respond
- Maintains all standard orchestrator functionality

This enables multi-agent systems with coordinated decision-making.

## Configuration

```yaml
session:
  orchestrator: loop-events

orchestrators:
  - module: loop-events
    source: git+https://github.com/microsoft/amplifier-module-loop-events@main
    config:
      max_iterations: -1              # Maximum iterations (-1 = unlimited)
      default_provider: "anthropic"   # Default provider name (optional)
      extended_thinking: false        # Enable extended thinking mode (default: false)
      reasoning_effort: null          # Reasoning effort level passed to the provider (optional)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_iterations` | integer | `-1` | Maximum loop iterations (`-1` = unlimited) |
| `default_provider` | string | `null` | Default provider name (uses first available if not set) |
| `extended_thinking` | boolean | `false` | Enable extended thinking mode for supported models |
| `reasoning_effort` | string | `null` | Reasoning effort level passed to the provider (provider-specific) |

## Behavior

### Event-Driven Loop

```
1. Receive user prompt
2. Emit prompt:submit event (allows context injection)
3. Loop:
   a. Get messages from context
   b. Call provider.complete()
   c. Parse tool calls
   d. For each tool call:
      - Emit tool:selecting event
      - Schedulers can veto or modify
      - Execute selected tool
      - Emit tool:selected event
   e. Add results to context
   f. Repeat from step 3
4. Emit prompt:complete event
5. Return final response
```

### Scheduler Integration

Schedulers participate via `tool:selecting` hook:

```python
async def scheduler_hook(event: str, data: dict) -> HookResult:
    if data["tool_name"] == "expensive_operation":
        # Veto expensive tool
        return HookResult(action="deny", reason="Cost limit exceeded")
    
    if data["tool_name"] == "slow_tool":
        # Modify to faster alternative
        return HookResult(
            action="modify",
            data={"tool": "fast_tool", "arguments": {...}}
        )
    
    # Allow tool
    return HookResult(action="continue")
```

Multiple schedulers can respond. The orchestrator reduces responses:
- Any `deny` → tool vetoed
- Multiple `modify` → highest priority wins
- All `continue` → original tool proceeds

### Tool Selection Flow

```
LLM selects tool → Emit tool:selecting
                     ↓
               Schedulers respond
                     ↓
         ┌────────────┴────────────┐
         │                         │
    All continue              Deny/Modify
         │                         │
    Original tool            Use scheduler decision
         │                         │
         └────────────┬────────────┘
                      ↓
              Execute selected tool
                      ↓
          Emit tool:selected (source: llm/scheduler)
```

## Events

### Standard Events

Emits all standard orchestrator events:
- `execution:start`, `execution:end`
- `provider:request`, `provider:response`, `provider:error`
- `tool:pre`, `tool:post`, `tool:error`
- `prompt:submit`, `prompt:complete`
- `orchestrator:complete`

### Event-Specific Events

- `tool:selecting` - Before tool execution (scheduler intercept point)
  ```python
  {
      "tool_name": "bash",
      "tool_input": {...},
      "available_tools": ["bash", "filesystem", ...]
  }
  ```

- `tool:selected` - After scheduler decision
  ```python
  {
      "tool": "bash",
      "source": "llm",  # or "scheduler"
      "original_tool": None  # or original if modified
  }
  ```

## Ephemeral Context Injection

Hooks can inject ephemeral context that appears in the next LLM request without being stored:

### From `prompt:submit`

```python
async def my_hook(event: str, data: dict) -> HookResult:
    return HookResult(
        action="inject_context",
        ephemeral=True,  # Not stored in context
        context_injection="Additional context for this turn only",
        context_injection_role="system"  # or "user"
    )
```

### From `tool:post`

```python
async def my_hook(event: str, data: dict) -> HookResult:
    return HookResult(
        action="inject_context",
        ephemeral=True,
        context_injection="Tool execution note",
        context_injection_role="system",
        append_to_last_tool_result=True  # Append to last tool result
    )
```

Ephemeral injections:
- ✅ Appear in next LLM request
- ❌ Not stored in persistent context
- ✅ Cleared after use
- ✅ Can append to tool results

## Extended Thinking

When `extended_thinking: true`:

```python
response = await provider.complete(chat_request, extended_thinking=True)
```

Providers supporting extended thinking will include thinking blocks in responses.

## Comparison with Other Orchestrators

| Feature | loop-basic | loop-streaming | loop-events |
|---------|------------|----------------|-------------|
| Tool execution | **Parallel** | Parallel | Sequential |
| Scheduler integration | No | No | **Yes** |
| Event-driven decisions | No | No | **Yes** |
| Ephemeral injection | No | No | **Yes** |
| Best for | Testing | Interactive UIs | **Multi-agent** |

## Use Cases

### 1. Multi-Agent Systems

```yaml
session:
  orchestrator: loop-events

hooks:
  - module: hooks-scheduler-heuristic
  - module: hooks-scheduler-cost-aware
    config:
      cost_weight: 0.6
      latency_weight: 0.4
```

Multiple schedulers coordinate tool/agent selection.

### 2. Cost-Aware Execution

```python
async def cost_scheduler(event: str, data: dict) -> HookResult:
    if estimated_cost(data["tool_name"]) > budget:
        return HookResult(action="deny", reason="Budget exceeded")
    return HookResult(action="continue")
```

Scheduler enforces cost constraints.

### 3. Dynamic Tool Routing

```python
async def router_scheduler(event: str, data: dict) -> HookResult:
    if data["tool_name"] == "web_search":
        # Route to specialized search service
        return HookResult(
            action="modify",
            data={"tool": "advanced_search", "arguments": {...}}
        )
    return HookResult(action="continue")
```

Scheduler routes tools to specialized implementations.

## Best Practices

### 1. Set Iteration Limits

```yaml
config:
  max_iterations: 20  # Prevent infinite loops
```

### 2. Configure Default Provider

```yaml
config:
  default_provider: "anthropic"  # Explicit default
```

### 3. Use Scheduler Priority

When multiple schedulers respond with `modify`:

```python
# Higher priority scheduler wins
HookResult(action="modify", priority=10, data={...})
```

### 4. Graceful Fallback

If no schedulers registered:
- Orchestrator uses LLM decisions
- No scheduler overhead
- Degrades to standard loop

## Implementation Notes

- Tool calls execute sequentially (not parallel)
- LLM decisions trusted by default
- Scheduler responses reduced to single decision
- Ephemeral injections cleared after each iteration
- Context compaction handled automatically

## Error Handling

### Provider Errors

On LLM error:
1. Emit `provider:error` event
2. Return error message to user
3. Exit loop

### Tool Errors

On tool execution error:
1. Emit `tool:error` event
2. Add error as tool result
3. Continue loop (LLM sees error)

### Scheduler Errors

If scheduler hook throws:
1. Log error
2. Ignore failed scheduler
3. Use other scheduler responses
4. Fallback to LLM decision if all fail

## Orphaned Tool Call Prevention

The orchestrator ensures every tool call gets a result:

```python
# Safety net: ALWAYS add tool response
try:
    result = await tool.execute(input)
    await context.add_message({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result
    })
except Exception as e:
    # Even on error, add tool response
    await context.add_message({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": f"Internal error: {str(e)}"
    })
```

This prevents API errors from orphaned tool calls (tool_call without matching result).

## See Also

- [loop-basic](loop_basic.md) - Sequential execution reference implementation
- [loop-streaming](loop_streaming.md) - Streaming responses with parallel tools
- [Scheduler Hooks](../hooks/scheduler.md) - Building scheduler modules
