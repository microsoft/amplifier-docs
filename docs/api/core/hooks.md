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

#### `emit(event, data) -> HookResult`

Emit an event to all registered handlers.

```python
result = await coordinator.hooks.emit("tool:pre", {"name": "bash"})
```

#### `emit_and_collect(event, data, timeout=1.0) -> list[Any]`

Emit event and collect data from all handler responses. Unlike `emit()` which processes action semantics (deny short-circuits, modify chains data), this method collects `result.data` from all handlers for aggregation.

Use for decision events where multiple hooks propose candidates (e.g., tool resolution, agent selection).

```python
responses = await coordinator.hooks.emit_and_collect("decision:tool_resolution", {"tools": [...]})
```

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

### Examples

**Continue (observe only)**:
```python
return HookResult(action="continue")
```

**Deny operation**:
```python
return HookResult(action="deny", reason="Blocked by policy")
```

**Inject context to agent**:
```python
return HookResult(
    action="inject_context",
    context_injection="Linter found 3 errors",
    user_message="Found linting issues"
)
```

**Request approval**:
```python
return HookResult(
    action="ask_user",
    approval_prompt="Allow write to production/config.py?",
    approval_default="deny"
)
```

See [Hook Contract](../../developer/contracts/hook.md) for implementation details.
