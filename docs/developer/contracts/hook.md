---
title: Hook Contract
description: Observability and control contract
---

# Hook Contract

Hooks observe, validate, and control agent lifecycle events.

## Purpose

Hooks enable:

- **Observation** - Logging, metrics, audit trails
- **Validation** - Security checks, input validation
- **Feedback injection** - Automated correction loops
- **Approval gates** - Dynamic permission requests
- **Output control** - Clean user experience

## Protocol Definition

**Source**: `amplifier_core/interfaces.py`

```python
@runtime_checkable
class HookHandler(Protocol):
    async def __call__(self, event: str, data: dict[str, Any]) -> HookResult:
        """
        Handle a lifecycle event.

        Args:
            event: Event name (e.g., "tool:pre", "execution:start")
            data: Event-specific data

        Returns:
            HookResult indicating action to take
        """
        ...
```

## HookResult Actions

**Source**: `amplifier_core/models.py`

| Action | Behavior | Use Case |
|--------|----------|----------|
| `continue` | Proceed normally | Default, observation only |
| `deny` | Block operation | Validation failure, security |
| `modify` | Transform data | Preprocessing, enrichment |
| `inject_context` | Add to agent's context | Feedback loops, corrections |
| `ask_user` | Request approval | High-risk operations |

```python
from amplifier_core.models import HookResult

# Simple observation
HookResult(action="continue")

# Block with reason
HookResult(action="deny", reason="Access denied")

# Inject feedback
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

## Entry Point Pattern

### mount() Function

```python
async def mount(coordinator: ModuleCoordinator, config: dict) -> Callable | None:
    """
    Initialize and register hook handlers.

    Returns:
        Cleanup callable to unregister handlers
    """
    handlers = []

    # Register handlers for specific events
    handlers.append(
        coordinator.hooks.register("tool:pre", my_validation_hook, priority=10)
    )
    handlers.append(
        coordinator.hooks.register("tool:post", my_feedback_hook, priority=20)
    )

    # Return cleanup function
    def cleanup():
        for unregister in handlers:
            unregister()

    return cleanup
```

### pyproject.toml

```toml
[project.entry-points."amplifier.modules"]
my-hook = "my_hook:mount"
```

## Event Registration

Register handlers during mount():

```python
from amplifier_core.hooks import HookRegistry

# Get registry from coordinator
registry: HookRegistry = coordinator.hooks

# Register with priority (lower = earlier)
unregister = registry.register(
    event="tool:post",
    handler=my_handler,
    priority=10,
    name="my_handler"
)

# Later: unregister()
```

## Common Events

| Event | Trigger | Data Includes |
|-------|---------|---------------|
| `execution:start` | Orchestrator execution begins | prompt |
| `execution:end` | Orchestrator execution completes | response |
| `prompt:submit` | User input | prompt text |
| `tool:pre` | Before tool execution | tool_name, tool_input |
| `tool:post` | After tool execution | tool_name, tool_result |
| `tool:error` | Tool failed | tool_name, error |
| `provider:request` | LLM call starting | provider, messages |
| `provider:response` | LLM call complete | provider, response, usage |

## Configuration

Hooks receive configuration via Mount Plan:

```yaml
hooks:
  - module: my-hook
    source: git+https://github.com/org/my-hook@main
    config:
      enabled_events:
        - "tool:pre"
        - "tool:post"
      log_level: "info"
```

## Debug Events

Hooks can emit debug events for observability:

```python
async def my_handler(event: str, data: dict) -> HookResult:
    # Emit debug event (useful for development/troubleshooting)
    await data.get("hooks").emit("my-hook:debug", {
        "event": event,
        "timestamp": time.time(),
        "details": "Processing..."
    })
    return HookResult(action="continue")
```

## Observability

Register custom events your hook emits:

```python
coordinator.register_contributor(
    "observability.events",
    "my-hook",
    lambda: ["my-hook:validation_failed", "my-hook:approved"]
)
```

## Example: Validation Hook

```python
from amplifier_core.models import HookResult

async def mount(coordinator, config=None):
    config = config or {}
    blocked_paths = config.get("blocked_paths", ["/etc", "/root"])

    async def validate_file_access(event: str, data: dict) -> HookResult:
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        # Check file operations
        if tool_name in ["read_file", "write_file", "edit_file"]:
            file_path = tool_input.get("file_path", "")
            for blocked in blocked_paths:
                if file_path.startswith(blocked):
                    return HookResult(
                        action="deny",
                        reason=f"Access to {blocked} is not allowed"
                    )

        return HookResult(action="continue")

    # Register for tool:pre events
    coordinator.hooks.register("tool:pre", validate_file_access, priority=5)

    return None
```

## Example: Approval Hook

```python
async def mount(coordinator, config=None):
    config = config or {}
    approval_patterns = config.get("require_approval", ["*.py", "*.js"])

    async def request_approval(event: str, data: dict) -> HookResult:
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        if tool_name == "write_file":
            file_path = tool_input.get("file_path", "")
            for pattern in approval_patterns:
                if fnmatch.fnmatch(file_path, pattern):
                    return HookResult(
                        action="ask_user",
                        approval_prompt=f"Allow writing to {file_path}?",
                        approval_default="deny"
                    )

        return HookResult(action="continue")

    coordinator.hooks.register("tool:pre", request_approval, priority=10)
    return None
```

## Graceful Degradation

Hooks should handle errors gracefully without crashing the kernel:

```python
async def safe_handler(event: str, data: dict) -> HookResult:
    try:
        # Your hook logic
        result = await process_event(event, data)
        return result
    except Exception as e:
        # Log error but don't crash
        logger.error(f"Hook error: {e}")
        # Continue execution - don't block on hook failures
        return HookResult(action="continue")
```

## Testing

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import TestCoordinator, EventRecorder
from amplifier_core.models import HookResult

@pytest.mark.asyncio
async def test_hook_handler():
    # Test handler directly
    result = await my_validation_hook("tool:pre", {
        "tool_name": "write_file",
        "tool_input": {"file_path": "/etc/passwd"}
    })

    assert result.action == "deny"
    assert "denied" in result.reason.lower()

@pytest.mark.asyncio
async def test_hook_registration():
    coordinator = TestCoordinator()
    cleanup = await mount(coordinator, {})

    # Verify handlers registered
    assert len(coordinator.hooks.handlers["tool:pre"]) > 0

    if cleanup:
        cleanup()
```

### EventRecorder for Testing

```python
from amplifier_core.testing import EventRecorder

recorder = EventRecorder()

# Use in tests
await recorder.record("tool:pre", {"tool_name": "write_file"})

# Assert
events = recorder.get_events()
assert len(events) == 1
assert events[0][0] == "tool:pre"
```

## Validation Checklist

### Required

- [ ] Handler implements `async def __call__(event, data) -> HookResult`
- [ ] `mount()` function with entry point in pyproject.toml
- [ ] Returns valid `HookResult` for all code paths
- [ ] Handles exceptions gracefully (don't crash kernel)

### Recommended

- [ ] Register cleanup function to unregister handlers
- [ ] Use appropriate priority (10-90, lower = earlier)
- [ ] Log handler registration for debugging
- [ ] Support configuration for enabled events
- [ ] Register custom events via contribution channels

## Quick Validation Command

```bash
amplifier module validate ./my-hook --type hook
```

## Canonical Examples

Study these reference implementations:

- **[amplifier-module-hooks-logging](https://github.com/microsoft/amplifier-module-hooks-logging)** - Logging and observability
- **[amplifier-module-hooks-approval](https://github.com/microsoft/amplifier-module-hooks-approval)** - Approval gates
- **[amplifier-module-hooks-redaction](https://github.com/microsoft/amplifier-module-hooks-redaction)** - Security redaction

## Related Contracts

- **[HOOKS_API.md](https://github.com/microsoft/amplifier-core/blob/main/docs/HOOKS_API.md)** - Detailed API documentation
- **[Orchestrator Contract](orchestrator.md)** - Orchestrators emit events
- **[Tool Contract](tool.md)** - Tools trigger tool:* events

## References

- **→ [HOOK_CONTRACT.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/HOOK_CONTRACT.md)** - Authoritative contract specification
