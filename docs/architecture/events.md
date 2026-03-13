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
| `provider:tool_sequence_repaired` | Tool sequence auto-repaired | original_calls, repaired_calls |
| `provider:resolve` | Provider resolved for request | provider_id, model |

### LLM Events

| Event | When | Data |
|-------|------|------|
| `llm:request` | Raw LLM request | messages, model, parameters |
| `llm:response` | Raw LLM response | response, usage |

### Content Block Events

| Event | When | Data |
|-------|------|------|
| `content_block:start` | Content block started | block_type, index |
| `content_block:delta` | Content block delta | block_type, index, delta |
| `content_block:end` | Content block completed | block_type, index, content |

### Thinking Events

| Event | When | Data |
|-------|------|------|
| `thinking:delta` | Thinking content delta | delta |
| `thinking:final` | Thinking content finalized | thinking |

### Tool Invocations

| Event | When | Data |
|-------|------|------|
| `tool:pre` | Before tool execution | tool_name, arguments |
| `tool:post` | After tool execution | tool_name, result, duration |
| `tool:error` | Tool execution failed | tool_name, error |

### Context Management

| Event | When | Data |
|-------|------|------|
| `context:pre_compact` | Before context compaction | current_size, threshold |
| `context:post_compact` | After context compaction | old_size, new_size, method |
| `context:compaction` | Context compaction occurred | details |
| `context:include` | Context file included | file_path, size |

### Orchestrator Lifecycle

| Event | When | Data |
|-------|------|------|
| `orchestrator:complete` | Orchestrator finished | status, turn_count, metadata |
| `execution:start` | Execution started | prompt |
| `execution:end` | Execution ended | response, duration |

### User Notifications

| Event | When | Data |
|-------|------|------|
| `user:notification` | User notification sent | level, message, source |

### Artifacts

| Event | When | Data |
|-------|------|------|
| `artifact:write` | Artifact written | artifact_id, path, size |
| `artifact:read` | Artifact read | artifact_id, path |

### Policy / Approvals

| Event | When | Data |
|-------|------|------|
| `policy:violation` | Policy violation detected | policy, details |
| `approval:required` | Approval required | operation, reason |
| `approval:granted` | Approval granted | operation, approver |
| `approval:denied` | Approval denied | operation, reason |

### Cancellation Lifecycle

| Event | When | Data |
|-------|------|------|
| `cancel:requested` | Cancellation requested | immediate |
| `cancel:completed` | Cancellation completed | was_immediate, error |

## Event Access

All event constants are exported from `amplifier_core.events`:

```python
from amplifier_core.events import (
    SESSION_START,
    SESSION_END,
    TOOL_PRE,
    TOOL_POST,
    # ... all other events
)
```

## Contribution Channels

The kernel uses contribution channels for pull-based aggregation across modules. This allows modules to declare capabilities that consumers aggregate on demand.

### Example: Module Observability

Modules can declare which events they emit:

```python
coordinator.register_contributor(
    "observability.events",
    "module-hooks-streaming-ui",
    lambda: [
        "streaming-ui:content-block-start",
        "streaming-ui:content-block-end",
    ],
)
```

Consumers collect contributions dynamically:

```python
discovered = await coordinator.collect_contributions("observability.events")
for contribution in discovered:
    for event_name in contribution or []:
        register_handler(event_name)
```

### Channel Naming

Use `{domain}.{purpose}` for shared channels:
- `observability.events` — modules declare lifecycle events
- `capabilities.catalog` — aggregate callable capabilities
- `session.metadata` — runtime metadata snapshots

## Hook Integration

Hooks observe events via the hook registry:

```python
async def my_handler(event: str, data: dict) -> HookResult:
    # Observe or react to event
    return HookResult(action="continue")

coordinator.hooks.register("tool:pre", my_handler)
```

Hooks can:
- **Observe**: Log or track events
- **Modify**: Change event data
- **Deny**: Block operations
- **Inject context**: Add content to agent's conversation
- **Request approval**: Ask user for permission

## Related Documentation

- **[Hook Contract](../developer/contracts/hook.md)** - Hook interface specification
- **[CONTRIBUTION_CHANNELS.md](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/CONTRIBUTION_CHANNELS.md)** - Contribution channel specification
