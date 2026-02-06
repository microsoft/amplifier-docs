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
| `session:end` | Session cleanup | session_id, duration |
| `session:fork` | Sub-session created | parent_id, child_id |
| `session:resume` | Session resumed | session_id |

### Prompt Lifecycle

| Event | When | Data |
|-------|------|------|
| `prompt:submit` | User prompt received | prompt, session_id |
| `prompt:complete` | Response generated | response, duration |

### Provider Events

| Event | When | Data |
|-------|------|------|
| `provider:request` | Before LLM call | messages, model |
| `provider:response` | After LLM response | response, usage |
| `provider:stream` | During streaming | chunk |
| `provider:error` | LLM call failed | error, model |

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
| `context:include` | Context injected | source, content |

### Approval Events

| Event | When | Data |
|-------|------|------|
| `approval:required` | Approval requested | operation, prompt |
| `approval:granted` | User approved | operation |
| `approval:denied` | User denied | operation, reason |

### Orchestrator Events

| Event | When | Data |
|-------|------|------|
| `orchestrator:complete` | Main loop finished | orchestrator, turn_count, status |

## Event Schema

Events are logged as JSONL with this schema:

```json
{
  "ts": "2024-01-15T10:30:00.123Z",
  "lvl": "info",
  "schema": {"name": "amplifier.log", "ver": "1.0.0"},
  "session_id": "abc123",
  "request_id": "def456",
  "span_id": "ghi789",
  "event": "provider:request",
  "component": "orchestrator",
  "module": "provider-anthropic",
  "status": "success",
  "duration_ms": 1234,
  "data": {
    "model": "claude-sonnet-4-5",
    "message_count": 5
  },
  "error": null
}
```

### Schema Fields

| Field | Type | Description |
|-------|------|-------------|
| `ts` | ISO8601 | Timestamp |
| `lvl` | string | Log level (info, warn, error) |
| `schema` | object | Schema name and version |
| `session_id` | string | Session identifier |
| `request_id` | string? | Request identifier |
| `span_id` | string? | Span identifier for tracing |
| `event` | string | Event name |
| `component` | string | Emitting component |
| `module` | string? | Module name |
| `status` | string? | success or error |
| `duration_ms` | number? | Duration in milliseconds |
| `data` | object | Event-specific data |
| `error` | object? | Error details if applicable |

## Hooks and Events

### Observing Events

Hooks register handlers for events:

```python
async def my_handler(event: str, data: dict) -> HookResult:
    if event == "tool:post":
        print(f"Tool {data['tool_name']} completed")
    return HookResult(action="continue")

# Register
coordinator.hooks.register("tool:post", my_handler)
```

### Hook Actions

Handlers return `HookResult` with an action:

| Action | Effect |
|--------|--------|
| `continue` | Proceed normally |
| `deny` | Block the operation |
| `modify` | Modify event data |
| `inject_context` | Add to conversation |
| `ask_user` | Request approval |

### Example: Blocking Dangerous Operations

```python
async def safety_hook(event: str, data: dict) -> HookResult:
    if event == "tool:pre" and data["tool_name"] == "bash":
        command = data["input"].get("command", "")
        if "rm -rf" in command:
            return HookResult(
                action="deny",
                reason="Destructive command blocked"
            )
    return HookResult(action="continue")
```

### Example: Context Injection

```python
async def linter_hook(event: str, data: dict) -> HookResult:
    if event == "tool:post" and data["tool_name"] == "write_file":
        # Run linter on written file
        errors = run_linter(data["file_path"])
        if errors:
            return HookResult(
                action="inject_context",
                context_injection=f"Linter errors:\n{errors}",
                user_message="Found linting issues"
            )
    return HookResult(action="continue")
```

## Streaming via Events

Streaming output is implemented via events, not callbacks:

```python
# Orchestrator emits stream events
async for chunk in provider.stream_complete(request):
    await hooks.emit("provider:stream", {"chunk": chunk})

# Hook handles streaming UI
async def streaming_ui_hook(event: str, data: dict) -> HookResult:
    if event == "provider:stream":
        chunk = data.get("chunk", {})
        if text := chunk.get("text"):
            print(text, end="", flush=True)
    return HookResult(action="continue")
```

## Event Logging

### Default Logging

The `hooks-logging` module logs all events to JSONL:

```yaml
hooks:
  - module: hooks-logging
    config:
      level: info
      output: ~/.amplifier/logs/
```

### Log Levels

| Level | Events Logged |
|-------|---------------|
| `error` | Errors only |
| `warn` | Errors + warnings |
| `info` | Standard events |
| `debug` | + LLM request/response summaries |
| `raw` | + Complete API payloads |

### Finding Logs

```bash
# Session logs
ls ~/.amplifier/projects/<project>/sessions/<session-id>/events.jsonl

# Search logs
grep '"event":"tool:error"' events.jsonl

# Pretty print
cat events.jsonl | jq 'select(.event == "provider:request")'
```

## Custom Events

Modules can emit custom events:

```python
async def mount(coordinator, config):
    # Declare observable events
    coordinator.register_contributor(
        "observability.events",
        "my-module",
        lambda: [
            "my-module:initialized",
            "my-module:processing",
            "my-module:completed"
        ]
    )

    # Emit events
    await coordinator.hooks.emit("my-module:initialized", {
        "version": "1.0.0"
    })
```

Custom events follow the `namespace:action` convention.

## Validation via Events

Hooks can validate operations before they execute:

```python
async def validation_hook(event: str, data: dict) -> HookResult:
    if event == "tool:pre" and data["tool_name"] == "write_file":
        path = data["input"].get("file_path", "")
        
        # Validate path is allowed
        if not is_allowed_path(path):
            return HookResult(
                action="deny",
                reason=f"Write to {path} not allowed"
            )
        
        # Validate content
        content = data["input"].get("content", "")
        if errors := validate_content(content, path):
            return HookResult(
                action="deny",
                reason=f"Validation failed: {errors}"
            )
    
    return HookResult(action="continue")
```

## Graceful Event Handling

Hooks should handle errors gracefully:

```python
async def my_hook(event: str, data: dict) -> HookResult:
    try:
        # Processing that might fail
        result = process_event(data)
    except Exception as e:
        # Log but don't block
        log_error(f"Hook error: {e}")
    
    # Always return continue unless intentionally blocking
    return HookResult(action="continue")
```

## Tracing

### Trace Context

Events include tracing identifiers:

- `session_id`: Identifies the session
- `request_id`: Identifies a single prompt/response cycle
- `span_id`: Identifies a specific operation

### Sub-Session Tracing

When agents spawn sub-sessions, IDs are related:

```
Parent: session_id=abc123
  └── Child: session_id=abc123-def456_explorer
```

## Best Practices

1. **Emit events for important operations**
2. **Include useful data**: Enough to debug, not too much to be noise
3. **Use canonical event names**: Follow the `component:action` pattern
4. **Handle hook results**: Check for `deny` and `inject_context`
5. **Aggregate logs centrally**: For production debugging

## References

- **→ [Hooks API](https://github.com/microsoft/amplifier-core/blob/main/docs/HOOKS_API.md)** - Complete hook API
- **→ [Hooks Events](https://github.com/microsoft/amplifier-core/blob/main/docs/HOOKS_EVENTS.md)** - Event reference
- **→ [Hook Patterns](https://github.com/microsoft/amplifier-core/blob/main/docs/guides/HOOK_PATTERNS.md)** - Common patterns
