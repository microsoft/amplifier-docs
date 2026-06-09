---
title: Events API
description: Event constants for the Amplifier kernel hook system
---

# Events API

> **Source**: [`python/amplifier_core/events.py`](https://github.com/microsoft/amplifier-core/blob/main/python/amplifier_core/events.py)

All constants are defined in the Rust kernel and re-exported from Python for use in hooks and orchestrators.

## Event Taxonomy

Events follow a `namespace:action` naming convention. Subscribe using `HookRegistry.on()` or emit via `HookRegistry.emit()`.

### Session Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `SESSION_START` | `session:start` | Session initialized and ready |
| `SESSION_END` | `session:end` | Session completed or terminated |
| `SESSION_FORK` | `session:fork` | Sub-session spawned from parent |
| `SESSION_RESUME` | `session:resume` | Existing session resumed |

### Prompt Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `PROMPT_SUBMIT` | `prompt:submit` | User prompt submitted to orchestrator |
| `PROMPT_COMPLETE` | `prompt:complete` | Orchestrator finished processing prompt |

### Planning Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `PLAN_START` | `plan:start` | Planning phase started |
| `PLAN_END` | `plan:end` | Planning phase completed |

### Provider Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `PROVIDER_REQUEST` | `provider:request` | About to call LLM provider |
| `PROVIDER_RESPONSE` | `provider:response` | Provider returned response |
| `PROVIDER_RETRY` | `provider:retry` | Provider call being retried |
| `PROVIDER_ERROR` | `provider:error` | Provider returned error |
| `PROVIDER_THROTTLE` | `provider:throttle` | Provider rate limit hit |
| `PROVIDER_TOOL_SEQUENCE_REPAIRED` | `provider:tool_sequence_repaired` | Tool call sequence repaired |
| `PROVIDER_RESOLVE` | `provider:resolve` | Provider selected for request |

### LLM Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `LLM_REQUEST` | `llm:request` | Raw LLM request (post-provider-resolve) |
| `LLM_RESPONSE` | `llm:response` | Raw LLM response received |

### Content Block Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `CONTENT_BLOCK_START` | `content_block:start` | Content block started streaming |
| `CONTENT_BLOCK_DELTA` | `content_block:delta` | Streaming token delta received |
| `CONTENT_BLOCK_END` | `content_block:end` | Content block finished streaming |

### Thinking Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `THINKING_DELTA` | `thinking:delta` | Extended thinking token delta |
| `THINKING_FINAL` | `thinking:final` | Final consolidated thinking block |

### Tool Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `TOOL_PRE` | `tool:pre` | About to execute tool call |
| `TOOL_POST` | `tool:post` | Tool call completed |
| `TOOL_ERROR` | `tool:error` | Tool call failed |

### Context Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `CONTEXT_PRE_COMPACT` | `context:pre_compact` | About to compact conversation context |
| `CONTEXT_POST_COMPACT` | `context:post_compact` | Context compaction completed |
| `CONTEXT_COMPACTION` | `context:compaction` | Context compaction details |
| `CONTEXT_INCLUDE` | `context:include` | Context file included in conversation |

### Orchestrator Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `ORCHESTRATOR_COMPLETE` | `orchestrator:complete` | Orchestrator loop completed |
| `EXECUTION_START` | `execution:start` | Orchestrator execution began |
| `EXECUTION_END` | `execution:end` | Orchestrator execution finished |

### User Notification Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `USER_NOTIFICATION` | `user:notification` | Notification intended for end user |

### Artifact Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `ARTIFACT_WRITE` | `artifact:write` | Artifact written (file, output, etc.) |
| `ARTIFACT_READ` | `artifact:read` | Artifact read |

### Policy and Approval Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `POLICY_VIOLATION` | `policy:violation` | Policy constraint violated |
| `APPROVAL_REQUIRED` | `approval:required` | Human approval needed before proceeding |
| `APPROVAL_GRANTED` | `approval:granted` | Approval granted, execution continues |
| `APPROVAL_DENIED` | `approval:denied` | Approval denied, execution halted |

### Cancellation Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `CANCEL_REQUESTED` | `cancel:requested` | Cancellation requested |
| `CANCEL_COMPLETED` | `cancel:completed` | Cancellation completed |

### Module Lifecycle Events

| Constant | Event Name | Description |
|----------|------------|-------------|
| `MODULE_ON_SESSION_READY_FAILED` | `module:on_session_ready_failed` | Module's `on_session_ready` callback failed |

### Wildcard

| Constant | Event Name | Description |
|----------|------------|-------------|
| `ALL_EVENTS` | `*` | Subscribe to all events |

## Usage

### Importing Constants

```python
from amplifier_core.events import (
    SESSION_START, SESSION_END,
    TOOL_PRE, TOOL_POST, TOOL_ERROR,
    PROMPT_SUBMIT, PROMPT_COMPLETE,
    EXECUTION_START, EXECUTION_END,
    APPROVAL_REQUIRED, APPROVAL_GRANTED, APPROVAL_DENIED,
)
```

### Subscribing to Events

```python
from amplifier_core import HookRegistry
from amplifier_core.events import TOOL_PRE, TOOL_POST, TOOL_ERROR

async def mount(coordinator, config=None):
    hooks: HookRegistry = coordinator.hooks

    @hooks.on(TOOL_PRE)
    async def before_tool(event_name, data):
        tool_name = data.get("name")
        print(f"Calling tool: {tool_name}")

    @hooks.on(TOOL_POST)
    async def after_tool(event_name, data):
        tool_name = data.get("name")
        print(f"Tool completed: {tool_name}")

    @hooks.on(TOOL_ERROR)
    async def on_tool_error(event_name, data):
        error = data.get("error")
        print(f"Tool failed: {error}")
```

### Subscribing to All Events

```python
from amplifier_core.events import ALL_EVENTS

@hooks.on(ALL_EVENTS)
async def log_everything(event_name, data):
    print(f"Event: {event_name} — {data}")
```

### Emitting Custom Events

```python
from amplifier_core.events import USER_NOTIFICATION

await coordinator.hooks.emit(
    USER_NOTIFICATION,
    {"message": "Task completed", "level": "info"},
)
```

### Registering Observable Events

Modules can declare which events they emit so hooks-logging auto-discovers them:

```python
coordinator.register_contributor(
    "observability.events",
    "my-module",
    lambda: [
        "execution:start",
        "execution:end",
    ],
)
```

## Event Data

Event data is a dict. Common fields by category:

| Category | Common Data Fields |
|----------|--------------------|
| Session | `session_id`, `status` |
| Tool | `name`, `input`, `output`, `error` |
| Provider | `model`, `request`, `response`, `error` |
| Context | `tokens_before`, `tokens_after`, `strategy` |
| Cancellation | `was_immediate`, `error` |
| Approval | `reason`, `tool_name`, `decision` |
