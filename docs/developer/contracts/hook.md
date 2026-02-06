---
title: Hook Contract
description: Observability and control contract
---

# Hook Contract

Hooks observe, validate, and control operations in Amplifier.

## Purpose

Hooks participate in the agent's cognitive loop by:

- Observing events (logging, metrics)
- Blocking operations (security, validation)
- Modifying data (transformation)
- Injecting context (feedback loops)
- Requesting approval (user confirmation)

## Protocol

```python
from typing import Protocol, runtime_checkable
from amplifier_core.models import HookResult

@runtime_checkable
class HookHandler(Protocol):
    async def __call__(
        self,
        event: str,
        data: dict
    ) -> HookResult:
        """Handle an event."""
        ...
```

## HookResult

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class HookResult:
    action: Literal["continue", "deny", "modify", "inject_context", "ask_user"]

    # For "deny" and "modify"
    reason: str | None = None
    data: dict | None = None

    # For "inject_context"
    context_injection: str | None = None
    context_injection_role: str = "system"  # "system", "user", "assistant"
    ephemeral: bool = False  # Not stored in history

    # For "ask_user"
    approval_prompt: str | None = None
    approval_options: list[str] | None = None
    approval_timeout: float = 60.0
    approval_default: str = "deny"  # "allow", "deny"

    # Output control
    suppress_output: bool = False
    user_message: str | None = None
    user_message_level: str = "info"  # "info", "warning", "error"
```

## Mount Function

Hooks register handlers rather than mounting:

```python
async def mount(coordinator, config=None):
    config = config or {}
    handler = MyHook(config)

    # Register for events with priority (lower = earlier)
    coordinator.hooks.register("tool:pre", handler.on_tool_pre, priority=10)
    coordinator.hooks.register("tool:post", handler.on_tool_post, priority=10)

    def cleanup():
        # Unregister handlers if needed
        pass

    return cleanup
```

## Actions

### continue

Proceed with no changes:

```python
return HookResult(action="continue")
```

### deny

Block the operation:

```python
return HookResult(
    action="deny",
    reason="Operation not allowed"
)
```

### modify

Transform event data:

```python
return HookResult(
    action="modify",
    data={**data, "modified_field": "new_value"}
)
```

### inject_context

Add to conversation:

```python
return HookResult(
    action="inject_context",
    context_injection="Linter found 3 errors:\n- Line 10: undefined variable\n- Line 25: type mismatch\n- Line 42: unused import",
    context_injection_role="system",
    ephemeral=True,  # Don't persist in history
    user_message="Found linting issues"
)
```

### ask_user

Request approval:

```python
return HookResult(
    action="ask_user",
    approval_prompt="Allow write to /etc/config?",
    approval_options=["Allow", "Deny"],
    approval_default="deny",
    approval_timeout=60.0
)
```

## Events

Hooks can register for these canonical events:

| Event | When | Data |
|-------|------|------|
| `session:start` | Session initialized | session_id, mount_plan |
| `session:end` | Session cleanup | session_id, duration |
| `prompt:submit` | User prompt received | prompt, session_id |
| `prompt:complete` | Response generated | response, duration |
| `provider:request` | Before LLM call | messages, model |
| `provider:response` | After LLM response | response, usage |
| `provider:error` | LLM call failed | error, model |
| `tool:pre` | Before tool execution | tool_name, input |
| `tool:post` | After tool execution | tool_name, result |
| `tool:error` | Tool execution failed | tool_name, error |
| `context:pre_compact` | Before compaction | message_count, tokens |
| `context:post_compact` | After compaction | message_count, tokens |
| `orchestrator:complete` | Main loop finished | iterations, tokens |

### Debug Events

Debug-level events for detailed logging:

| Event | When | Data |
|-------|------|------|
| `llm:request:debug` | Debug logging | Request summary |
| `llm:response:debug` | Debug logging | Response summary |

## Example Implementations

### Safety Hook

```python
from amplifier_core.models import HookResult

class SafetyHook:
    def __init__(self, config):
        self.blocked_commands = config.get("blocked_commands", ["rm -rf /", "sudo rm"])
        self.blocked_paths = config.get("blocked_paths", ["/etc", "/sys"])

    async def on_tool_pre(self, event, data) -> HookResult:
        tool_name = data.get("tool_name")
        input_data = data.get("input", {})

        # Check bash commands
        if tool_name == "bash":
            command = input_data.get("command", "")
            for blocked in self.blocked_commands:
                if blocked in command:
                    return HookResult(
                        action="deny",
                        reason=f"Blocked command pattern: {blocked}"
                    )

        # Check file paths
        if tool_name in ["read_file", "write_file"]:
            path = input_data.get("file_path", "")
            for blocked in self.blocked_paths:
                if path.startswith(blocked):
                    return HookResult(
                        action="deny",
                        reason=f"Access to {blocked} is not allowed"
                    )

        return HookResult(action="continue")
```

### Logging Hook

```python
import json
from pathlib import Path
from datetime import datetime

class LoggingHook:
    def __init__(self, config):
        self.log_path = Path(config.get("output", "~/.amplifier/logs")).expanduser()
        self.level = config.get("level", "info")
        self.log_path.mkdir(parents=True, exist_ok=True)

    async def on_any_event(self, event, data) -> HookResult:
        # Skip debug events unless debug level
        if ":debug" in event and self.level != "debug":
            return HookResult(action="continue")

        log_entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "event": event,
            "data": self._sanitize(data)
        }

        log_file = self.log_path / "events.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        return HookResult(action="continue")

    def _sanitize(self, data):
        """Remove sensitive data from logs."""
        sanitized = dict(data)
        if "api_key" in sanitized:
            sanitized["api_key"] = "[REDACTED]"
        return sanitized
```

### Context Injection Hook

```python
import subprocess

class LinterHook:
    def __init__(self, config):
        self.enabled = config.get("enabled", True)

    async def on_tool_post(self, event, data) -> HookResult:
        if not self.enabled:
            return HookResult(action="continue")

        tool_name = data.get("tool_name")
        if tool_name != "write_file":
            return HookResult(action="continue")

        file_path = data.get("input", {}).get("file_path", "")
        if not file_path.endswith(".py"):
            return HookResult(action="continue")

        # Run linter
        try:
            result = subprocess.run(
                ["ruff", "check", file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return HookResult(
                    action="inject_context",
                    context_injection=f"Linter errors in {file_path}:\n{result.stdout}",
                    context_injection_role="system",
                    user_message="Found linting issues",
                    user_message_level="warning"
                )
        except Exception:
            pass

        return HookResult(action="continue")
```

### Approval Hook

```python
class ApprovalHook:
    def __init__(self, config):
        self.require_approval = config.get("require_approval", ["write_file", "bash"])

    async def on_tool_pre(self, event, data) -> HookResult:
        tool_name = data.get("tool_name")
        
        if tool_name not in self.require_approval:
            return HookResult(action="continue")

        input_data = data.get("input", {})
        
        # Build approval prompt
        if tool_name == "bash":
            prompt = f"Allow execution of: {input_data.get('command', '')[:100]}?"
        elif tool_name == "write_file":
            prompt = f"Allow write to: {input_data.get('file_path', '')}?"
        else:
            prompt = f"Allow {tool_name}?"

        return HookResult(
            action="ask_user",
            approval_prompt=prompt,
            approval_options=["Allow", "Deny"],
            approval_default="deny"
        )
```

## Graceful Degradation

Hooks should handle errors gracefully:

```python
async def on_tool_post(self, event, data) -> HookResult:
    try:
        # Potentially failing operation
        result = self._process(data)
        if result.has_issues:
            return HookResult(
                action="inject_context",
                context_injection=result.message
            )
    except Exception as e:
        # Log but don't block - graceful degradation
        self._log_error(f"Hook error: {e}")
    
    return HookResult(action="continue")
```

## Authoritative Reference

**→ [Hook Contract](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/HOOK_CONTRACT.md)** - Complete specification

**→ [Hooks API](https://github.com/microsoft/amplifier-core/blob/main/docs/HOOKS_API.md)** - Full API reference
