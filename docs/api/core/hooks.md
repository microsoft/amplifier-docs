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
coordinator.hooks.set_default_fields(session_id=session.session_id, path=path)
```

Defaults are automatically merged into event data for all subsequent `emit()` calls.

## HookResult

Return value from hook handlers indicating what action to take.

### Fields

**`action`** (required)
- Type: `Literal["continue", "deny", "modify", "inject_context", "ask_user"]`
- Description: Action to take after hook execution

**`data`** (optional)
- Type: `dict[str, Any] | None`
- Description: Modified event data (for `action="modify"`)

**`reason`** (optional)
- Type: `str | None`
- Description: Explanation for deny/modification

**`context_injection`** (optional)
- Type: `str | None`
- Description: Text to inject into agent's context (for `action="inject_context"`)

**`context_injection_role`** (optional)
- Type: `Literal["system", "user", "assistant"]`
- Default: `"system"`
- Description: Role for injected message

**`ephemeral`** (optional)
- Type: `bool`
- Default: `False`
- Description: If `True`, injection is temporary (only for current LLM call)

**`approval_prompt`** (optional)
- Type: `str | None`
- Description: Question to ask user (for `action="ask_user"`)

**`approval_options`** (optional)
- Type: `list[str] | None`
- Default: `["Allow", "Deny"]`
- Description: User choice options

**`approval_timeout`** (optional)
- Type: `float`
- Default: `300.0`
- Description: Seconds to wait for user response

**`approval_default`** (optional)
- Type: `Literal["allow", "deny"]`
- Default: `"deny"`
- Description: Default decision on timeout

**`suppress_output`** (optional)
- Type: `bool`
- Default: `False`
- Description: Hide hook's stdout/stderr from user

**`user_message`** (optional)
- Type: `str | None`
- Description: Message to display to user

**`user_message_level`** (optional)
- Type: `Literal["info", "warning", "error"]`
- Default: `"info"`
- Description: Severity level for user message

**`append_to_last_tool_result`** (optional)
- Type: `bool`
- Default: `False`
- Description: Append ephemeral injection to last tool result instead of creating new message

### Examples

```python
from amplifier_core.models import HookResult

# Simple observation
HookResult(action="continue")

# Block operation
HookResult(action="deny", reason="Access denied")

# Inject context
HookResult(
    action="inject_context",
    context_injection="Found 3 linting errors...",
    user_message="Linting issues detected"
)

# Request approval
HookResult(
    action="ask_user",
    approval_prompt="Allow write to production file?",
    approval_default="deny"
)
```

## Common Patterns

### Context Injection (Automated Feedback)

```python
async def validation_hook(event: str, data: dict) -> HookResult:
    validation_errors = validate(data["tool_result"])
    
    if validation_errors:
        return HookResult(
            action="inject_context",
            context_injection=f"Validation errors:\n{format_errors(validation_errors)}",
            user_message="Validation found issues",
            suppress_output=True
        )
    
    return HookResult(action="continue")
```

### Approval Gates

```python
async def production_protection_hook(event: str, data: dict) -> HookResult:
    file_path = data["tool_input"]["file_path"]
    
    if "/production/" in file_path:
        return HookResult(
            action="ask_user",
            approval_prompt=f"Allow write to production file: {file_path}?",
            approval_options=["Allow once", "Allow always", "Deny"],
            approval_default="deny"
        )
    
    return HookResult(action="continue")
```

## See Also

- [Hook Contract](../../developer/contracts/hook.md) - Full contract specification
- [Hooks Guide](../guides/hooks.md) - Tutorial introduction
