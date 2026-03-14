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
| `session:end` | Session cleanup complete |
| `session:fork` | Child session created |
| `session:resume` | Session resumed |

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
| `provider:resolve` | Provider resolution |
| `llm:request` | LLM request |
| `llm:response` | LLM response |

### Content Block Events

| Event | Description |
|-------|-------------|
| `content_block:start` | Content block started |
| `content_block:delta` | Content block delta received |
| `content_block:end` | Content block completed |

### Thinking Events

| Event | Description |
|-------|-------------|
| `thinking:delta` | Thinking content delta |
| `thinking:final` | Thinking content finalized |

### Tool Events

| Event | Description |
|-------|-------------|
| `tool:pre` | Before tool invocation |
| `tool:post` | After tool invocation |
| `tool:error` | Tool invocation error |

### Context Events

| Event | Description |
|-------|-------------|
| `context:pre_compact` | Before context compaction |
| `context:post_compact` | After context compaction |
| `context:compaction` | Context compaction occurred |
| `context:include` | Context include event |

### Orchestrator Events

| Event | Description |
|-------|-------------|
| `orchestrator:complete` | Orchestrator execution complete |
| `execution:start` | Execution started |
| `execution:end` | Execution ended |

### User Notification Events

| Event | Description |
|-------|-------------|
| `user:notification` | User notification |

### Artifact Events

| Event | Description |
|-------|-------------|
| `artifact:write` | Artifact written |
| `artifact:read` | Artifact read |

### Policy Events

| Event | Description |
|-------|-------------|
| `policy:violation` | Policy violation detected |
| `approval:required` | Approval required |
| `approval:granted` | Approval granted |
| `approval:denied` | Approval denied |

### Cancellation Events

| Event | Description |
|-------|-------------|
| `cancel:requested` | Cancellation requested |
| `cancel:completed` | Cancellation completed |

## Using Events

### Register a Hook

```python
from amplifier_core.events import TOOL_PRE, TOOL_POST

async def log_tool_calls(event: str, data: dict):
    print(f"{event}: {data}")
    return HookResult()

# Register for specific events
coordinator.hooks.register(TOOL_PRE, log_tool_calls)
coordinator.hooks.register(TOOL_POST, log_tool_calls)
```

### Listen to All Events

```python
from amplifier_core.events import ALL_EVENTS

async def monitor_all(event: str, data: dict):
    print(f"Event: {event}")
    return HookResult()

coordinator.hooks.register(ALL_EVENTS, monitor_all)
```

## Event Data

Each event carries a `data` dict with event-specific fields. See the hook contract documentation for details on event data structures.
