---
title: Event System
description: Canonical events and observability in Amplifier
---

# Event System

Amplifier uses an event-driven architecture for observability. The kernel emits canonical events that hooks can observe, modify, or act upon.

## Design Principles

1. **If it's important, emit an event**
2. **If it's not observable, it didn't happen**
3. **Single source of truth**: One JSONL log
4. **Hooks observe without blocking** (by default)

## Canonical Events

### Session Lifecycle

| Event | When | Data |
|-------|------|------|
| `session:start` | Session initialized | session_id, mount_plan |
| `session:start:debug` | Session start (debug level) | debug details |
| `session:start:raw` | Session start (raw data) | raw initialization data |
| `session:end` | Session cleanup | session_id, duration |
| `session:fork` | Sub-session created | parent_id, child_id |
| `session:fork:debug` | Session fork (debug level) | debug details |
| `session:fork:raw` | Session fork (raw data) | raw fork data |
| `session:resume` | Session resumed | session_id |
| `session:resume:debug` | Session resume (debug level) | debug details |
| `session:resume:raw` | Session resume (raw data) | raw resume data |

### Prompt Lifecycle

| Event | When | Data |
|-------|------|------|
| `prompt:submit` | User prompt received | prompt, session_id |
| `prompt:complete` | Response generated | response, duration |

### Planning Events

| Event | When | Data |
|-------|------|------|
| `plan:start` | Planning phase started | session_id |
| `plan:end` | Planning phase completed | session_id, plan |

### Provider Events

| Event | When | Data |
|-------|------|------|
| `provider:request` | Before LLM call | messages, model |
| `provider:response` | After LLM response | response, usage |
| `provider:error` | LLM call failed | error, model |
| `provider:retry` | Retry attempt initiated | attempt, delay, retry_after |
| `provider:throttle` | Pre-emptive throttling | dimension, remaining, limit, delay |
| `provider:tool_sequence_repaired` | Tool sequence auto-repaired | repair_count, repairs |
| `llm:request` | LLM request (alias) | messages, model |
| `llm:request:debug` | LLM request (debug level) | full request with truncated values |
| `llm:request:raw` | LLM request (raw data) | complete untruncated request params |
| `llm:response` | LLM response (alias) | response, usage |
| `llm:response:debug` | LLM response (debug level) | full response with truncated values |
| `llm:response:raw` | LLM response (raw data) | complete untruncated response |

### Content Block Events

| Event | When | Data |
|-------|------|------|
| `content_block:start` | Content block streaming started | block_index, block_type |
| `content_block:delta` | Content block chunk received | block_index, delta |
| `content_block:end` | Content block streaming complete | block_index, block |
| `thinking:delta` | Thinking content chunk | delta |
| `thinking:final` | Thinking content complete | thinking_block |

### Tool Events

| Event | When | Data |
|-------|------|------|
| `tool:pre` | Before tool execution | tool_name, input |
| `tool:post` | After tool execution | tool_name, result |
| `tool:error` | Tool execution failed | tool_name, error |

### Context Events

| Event | When | Data |
|-------|------|------|
| `context:pre_compact` | Before compaction | message_count, tokens |
| `context:post_compact` | After compaction | message_count, tokens |
| `context:compaction` | Compaction occurred | removed_count, strategy |
| `context:include` | Context injected | source, content |

### Orchestrator Events

| Event | When | Data |
|-------|------|------|
| `orchestrator:complete` | Orchestrator execution complete | session_id |
| `execution:start` | Orchestrator execution begins | session_id |
| `execution:end` | Orchestrator execution completes | session_id, duration |

### User Notification Events

| Event | When | Data |
|-------|------|------|
| `user:notification` | User notification triggered | message, type |

### Artifact Events

| Event | When | Data |
|-------|------|------|
| `artifact:write` | Artifact written | path, type |
| `artifact:read` | Artifact read | path, type |

### Approval Events

| Event | When | Data |
|-------|------|------|
| `approval:required` | Approval requested | operation, prompt |
| `approval:granted` | User approved | operation |
| `approval:denied` | User denied | operation, reason |
| `policy:violation` | Policy violation detected | policy, violation |

### Cancellation Events

| Event | When | Data |
|-------|------|------|
| `cancel:requested` | Cancellation initiated | mode (graceful/immediate) |
| `cancel:completed` | Cancellation finalized | session_id |

## Hook Integration

Hooks subscribe to events and respond:

```python
async def on_tool_execution(event_name: str, data: dict):
    if event_name == "tool:pre":
        print(f"Starting: {data['tool_name']}")

# Register hook
coordinator.hooks.register("tool:pre", on_tool_execution)
```

**Priority**: Higher priority hooks run first (default: 100)

**Blocking vs Non-Blocking**: Hooks are non-blocking by default but can modify event data.

## Event Data

Each event includes:

- **Common fields**: `timestamp`, `session_id`
- **Event-specific fields**: Varies by event type

Example `tool:post` data:

```python
{
    "tool_name": "read_file",
    "input": {"file_path": "README.md"},
    "output": "...",
    "duration_ms": 42,
    "timestamp": "2025-01-15T10:30:00Z",
    "session_id": "abc-123"
}
```

## Contribution Channels

Contribution channels provide pull-based aggregation for module capabilities and metadata. See the [Contribution Channels specification](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/CONTRIBUTION_CHANNELS.md) for details.

**Common channels**:

- `observability.events` - Modules declare lifecycle events
- `capabilities.catalog` - Aggregate callable capabilities
- `session.metadata` - Runtime metadata snapshots

**Usage**:

```python
# Module registration
coordinator.register_contributor(
    "observability.events",
    "tool-filesystem",
    lambda: ["filesystem:read", "filesystem:write"]
)

# Consumer collection
events = await coordinator.collect_contributions("observability.events")
```

See [CONTRIBUTION_CHANNELS.md](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/CONTRIBUTION_CHANNELS.md) for the complete specification.
