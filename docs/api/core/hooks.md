---
title: Hooks API
description: HookRegistry and HookResult reference
---

# Hooks API

Hooks provide observability, control, and context injection capabilities.

**Source**: [amplifier_core/hooks.py](https://github.com/microsoft/amplifier-core/blob/main/amplifier_core/hooks.py)

## HookRegistry

Manages hook registration and event emission.

### Methods

#### `register(event, handler, priority=0, name=None)`

Register a handler for an event.

```python
async def my_handler(event: str, data: dict) -> HookResult:
    return HookResult(action="continue")

coordinator.hooks.register("tool:pre", my_handler)
```

**Parameters**:
- `event` (str): Event name to hook into
- `handler` (Callable): Async function that handles the event
- `priority` (int): Execution priority (lower = earlier, default: 0)
- `name` (str | None): Optional handler name for debugging

**Returns**: Unregister function

#### `emit(event, data) -> HookResult`

Emit an event to all registered handlers.

```python
result = await coordinator.hooks.emit("tool:pre", {"name": "bash"})
```

Handlers execute sequentially by priority with:
- Short-circuit on `deny` action
- Data modification chaining on `modify` action
- Multiple `inject_context` results merged into single injection
- Continue on `continue` action

#### `emit_and_collect(event, data, timeout=1.0) -> list[Any]`

Emit event and collect data from all handler responses. Unlike `emit()` which processes action semantics (deny short-circuits, modify chains data), this method collects `result.data` from all handlers for aggregation.

Use for decision events where multiple hooks propose candidates (e.g., tool resolution, agent selection).

```python
responses = await coordinator.hooks.emit_and_collect("decision:tool_resolution", {"tools": [...]})
```

#### `set_default_fields(**defaults)`

Set default fields that will be merged with events emitted via `emit()`.

```python
coordinator.hooks.set_default_fields(session_id=session.session_id, parent_id=session.parent_id)
```

Note: These defaults only apply to `emit()`, not `emit_and_collect()`.

## HookResult

Returned by hook handlers to control execution flow.

**Source**: [amplifier_core/models.py](https://github.com/microsoft/amplifier-core/blob/main/amplifier_core/models.py)

### Actions

| Action | Description |
|--------|-------------|
| `continue` | Continue execution (default) |
| `deny` | Block the operation |
| `modify` | Modify the event data |
| `inject_context` | Inject message into agent context |
| `ask_user` | Request user approval |

### Action Precedence

When multiple handlers return different actions, they are resolved by precedence (highest to lowest):

1. **`deny`** — Blocking, short-circuits immediately
2. **`ask_user`** — Blocking, requires user approval
3. **`inject_context`** — Non-blocking, multiple results merged
4. **`modify`** — Non-blocking, chains data through handlers
5. **`continue`** — Non-blocking, default pass-through

**Key principle**: Blocking actions (`deny`, `ask_user`) always take precedence over non-blocking actions.

### Fields

```python
class HookResult(BaseModel):
    action: str = "continue"

    # For deny/modify
    reason: str = None
    data: dict = None

    # For inject_context
    context_injection: str = None
    context_injection_role: str = "system"
    ephemeral: bool = False

    # For ask_user
    approval_prompt: str = None
    approval_options: list[str] = None
    approval_timeout: float = 300.0
    approval_default: str = "deny"

    # Output control
    suppress_output: bool = False
    user_message: str = None
    user_message_level: str = "info"

    # Injection placement control
    append_to_last_tool_result: bool = False
```

### Field Details

**Context Injection**:
- `context_injection`: Text to inject into agent's conversation (default limit: 10 KB per injection, configurable via `session.injection_size_limit`)
- `context_injection_role`: Role for injected message (`"system"`, `"user"`, or `"assistant"`, default: `"system"`)
- `ephemeral`: If `True`, injection is temporary (only for current LLM call, not stored in conversation history)

**Approval Gates**:
- `approval_prompt`: Question to ask user
- `approval_options`: User choice options (default: `["Allow", "Deny"]`)
- `approval_timeout`: Seconds to wait for user response (default: 300.0)
- `approval_default`: Default decision on timeout (`"allow"` or `"deny"`, default: `"deny"`)

**Output Control**:
- `suppress_output`: Hide hook's stdout/stderr from user transcript
- `user_message`: Message to display to user (separate from `context_injection`)
- `user_message_level`: Severity level (`"info"`, `"warning"`, or `"error"`, default: `"info"`)

### Examples

**Continue (observe only)**:
```python
return HookResult(action="continue")
```

**Deny operation**:
```python
return HookResult(
    action="deny",
    reason="Production files require approval"
)
```

**Inject context (automated feedback)**:
```python
return HookResult(
    action="inject_context",
    context_injection="Linter found 3 issues:\n- ...",
    user_message="Found linting issues",
    user_message_level="warning"
)
```

**Request approval**:
```python
return HookResult(
    action="ask_user",
    approval_prompt="Allow write to production file?",
    approval_options=["Allow once", "Allow always", "Deny"]
)
```

## Best Practices

### Security
- Respect the configured `session.injection_size_limit` (default: 10 KB, `None` for unlimited)
- Use `approval_default="deny"` for security-sensitive operations
- All context injections are automatically logged with provenance

### Performance
- Keep pre-tool hooks fast to avoid blocking
- Use `asyncio` for external calls (linters, APIs)
- Consider token usage when injecting feedback (configurable via `session.injection_budget_per_turn`, default: 10,000 tokens/turn)

### User Experience
- Make `approval_prompt` and `user_message` self-explanatory
- Use appropriate `user_message_level` (info/warning/error)
- Use `suppress_output=True` for verbose processing
- Context injection enables immediate correction (no waiting for next turn)

## Related Documentation

- **[Events](../../architecture/events.md)** - Complete list of canonical events
- **[HOOKS_API.md](https://github.com/microsoft/amplifier-core/blob/main/docs/HOOKS_API.md)** - Comprehensive hooks API reference with patterns
