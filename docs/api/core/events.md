---
title: Events API
description: Canonical event constants
---

# Events API

Amplifier uses a canonical event system for observability and hook integration.

**Source**: [amplifier_core/events.py](https://github.com/microsoft/amplifier-core/blob/main/amplifier_core/events.py)

## Event Taxonomy

Events follow a `namespace:action` naming convention.

### Session Events

| Event | Description |
|-------|-------------|
| `session:start` | Session initialized |
| `session:start:debug` | Session start with debug details |
| `session:start:raw` | Session start with raw data |
| `session:end` | Session cleanup complete |
| `session:fork` | Child session created |
| `session:fork:debug` | Session fork with debug details |
| `session:fork:raw` | Session fork with raw data |
| `session:resume` | Session resumed |
| `session:resume:debug` | Session resume with debug details |
| `session:resume:raw` | Session resume with raw data |

### Prompt Events

| Event | Description |
|-------|-------------|
| `prompt:submit` | User prompt submitted |
| `prompt:complete` | Prompt processing complete |

### Planning Events

| Event | Description |
|-------|-------------|
| `plan:start` | Planning phase started |
| `plan:end` | Planning phase completed |

### Provider Events

| Event | Description |
|-------|-------------|
| `provider:request` | LLM request initiated |
| `provider:response` | LLM response received |
| `provider:error` | LLM request failed |
| `provider:retry` | Retry attempt before LLM call |
| `provider:throttle` | Pre-emptive throttling triggered |
| `provider:tool_sequence_repaired` | Tool call sequence repaired |
| `llm:request` | LLM request (alias) |
| `llm:request:debug` | LLM request with debug details |
| `llm:request:raw` | LLM request with raw untruncated data |
| `llm:response` | LLM response (alias) |
| `llm:response:debug` | LLM response with debug details |
| `llm:response:raw` | LLM response with raw untruncated data |

### Content Block Events

| Event | Description |
|-------|-------------|
| `content_block:start` | Content block streaming started |
| `content_block:delta` | Content block chunk received |
| `content_block:end` | Content block streaming complete |
| `thinking:delta` | Thinking content chunk |
| `thinking:final` | Thinking content complete |

### Tool Events

| Event | Description |
|-------|-------------|
| `tool:pre` | Before tool execution |
| `tool:post` | After tool execution |
| `tool:error` | Tool execution failed |

### Context Events

| Event | Description |
|-------|-------------|
| `context:pre_compact` | Before context compaction |
| `context:post_compact` | After context compaction |
| `context:compaction` | Context compaction occurred |
| `context:include` | Content included in context |

### Orchestrator Events

| Event | Description |
|-------|-------------|
| `orchestrator:complete` | Orchestrator execution complete |
| `execution:start` | Orchestrator execution begins |
| `execution:end` | Orchestrator execution completes |

### User Events

| Event | Description |
|-------|-------------|
| `user:notification` | User notification triggered |

### Artifact Events

| Event | Description |
|-------|-------------|
| `artifact:write` | Artifact written to storage |
| `artifact:read` | Artifact read from storage |

### Policy & Approval Events

| Event | Description |
|-------|-------------|
| `policy:violation` | Policy violation detected |
| `approval:required` | Approval requested |
| `approval:granted` | User approved |
| `approval:denied` | User denied |

### Cancellation Events

| Event | Description |
|-------|-------------|
| `cancel:requested` | Cancellation initiated (graceful or immediate) |
| `cancel:completed` | Cancellation finalized, session stopping |

## Usage

Hooks subscribe to events:

```python
async def my_hook(event_name, data):
    if event_name == "tool:pre":
        print(f"Tool starting: {data['tool_name']}")

coordinator.hooks.register("tool:pre", my_hook)
```

See [Hook Contract](../../developer/contracts/hook.md) for details.
