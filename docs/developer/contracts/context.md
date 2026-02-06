---
title: Context Contract
description: Memory management contract
---

# Context Contract

Context managers handle conversation memory, token management, and state persistence.

## Purpose

Context managers:

- Store conversation history
- Manage token limits dynamically
- Implement compaction strategies (ephemeral, non-destructive)
- Support persistence for session resumption
- Provide observability through events

## Protocol

```python
from typing import Protocol, runtime_checkable, Any

@runtime_checkable
class ContextManager(Protocol):
    async def add_message(self, message: dict) -> None:
        """Add a message to context."""
        ...

    async def get_messages_for_request(
        self, token_budget: int | None = None, provider: Any | None = None
    ) -> list[dict]:
        """
        Get messages for LLM request.
        
        Performs ephemeral compaction if needed - does NOT modify stored history.
        Provider info used to calculate dynamic token budget.
        """
        ...

    async def get_messages(self) -> list[dict]:
        """Get all messages (full history, no compaction)."""
        ...

    async def set_messages(self, messages: list[dict]) -> None:
        """Replace all messages (used for session restore)."""
        ...

    async def clear(self) -> None:
        """Clear all messages."""
        ...
```

## Mount Function

```python
async def mount(coordinator, config=None):
    config = config or {}
    context = MyContext(config)
    await coordinator.mount("session", context, name="context")
    return context  # Return for graceful cleanup
```

## Configuration

Common configuration options:

| Option | Type | Description |
|--------|------|-------------|
| `max_tokens` | int | Default maximum context tokens |
| `compaction_strategy` | string | How to compact ("truncate", "summarize") |
| `preserve_system` | bool | Keep system messages on compact |
| `persistence` | dict | Persistence configuration |

### Critical vs Ephemeral Messages

Some context manager implementations support message criticality:

| Type | Behavior |
|------|----------|
| `critical` | Never compacted - preserved through all compaction |
| `ephemeral` | Not persisted to storage - lost on session resume |

## Events

Context managers should emit these observability events:

| Event | When | Data |
|-------|------|------|
| `context:pre_compact` | Before compaction | message_count, tokens |
| `context:post_compact` | After compaction | message_count, tokens |
| `context:include` | Context injected | source, content |

## Message Format

Messages follow this structure:

```python
{
    "role": "user" | "assistant" | "system" | "tool",
    "content": str | list,  # Text or content blocks
    "tool_call_id": str | None,  # For tool results
    "name": str | None,  # Tool name for tool messages
}
```

## Dynamic Token Budget

Context managers should calculate token budgets dynamically from provider info:

```python
async def get_messages_for_request(self, token_budget=None, provider=None):
    # Calculate budget from provider if available
    if provider and not token_budget:
        info = provider.get_info()
        defaults = info.defaults or {}
        context_window = defaults.get("context_window", 100000)
        max_output = defaults.get("max_output_tokens", 4096)
        safety_margin = 1000
        token_budget = context_window - max_output - safety_margin
    
    # Ephemeral compaction - return view without modifying stored history
    return self._compact_to_budget(token_budget)
```

## Example Implementation

```python
from amplifier_core.models import HookResult

class SimpleContext:
    def __init__(self, config):
        self.max_tokens = config.get("max_tokens", 100000)
        self.messages = []
        self.preserve_system = config.get("preserve_system", True)

    async def add_message(self, message):
        self.messages.append(message)

    async def get_messages_for_request(self, token_budget=None, provider=None):
        """Return messages for LLM, with ephemeral compaction if needed."""
        # Calculate budget
        budget = self._calculate_budget(token_budget, provider)
        
        # Ephemeral compaction - don't modify self.messages
        if self._estimate_tokens() > budget * 0.9:
            return self._compact_messages(budget)
        
        return list(self.messages)

    async def get_messages(self):
        """Return full history (no compaction)."""
        return list(self.messages)

    async def set_messages(self, messages):
        """Replace all messages (for session restore)."""
        self.messages = list(messages)

    async def clear(self):
        self.messages = []

    def _calculate_budget(self, token_budget, provider):
        if token_budget:
            return token_budget
        if provider:
            info = provider.get_info()
            defaults = info.defaults or {}
            context_window = defaults.get("context_window", self.max_tokens)
            max_output = defaults.get("max_output_tokens", 4096)
            return context_window - max_output - 1000
        return self.max_tokens

    def _estimate_tokens(self):
        # Rough estimate: 4 chars per token
        total_chars = sum(len(str(m.get("content", ""))) for m in self.messages)
        return total_chars // 4

    def _compact_messages(self, budget):
        """Return compacted view WITHOUT modifying internal state."""
        if self.preserve_system:
            system_messages = [m for m in self.messages if m["role"] == "system"]
            other_messages = [m for m in self.messages if m["role"] != "system"]
        else:
            system_messages = []
            other_messages = list(self.messages)

        # Keep recent messages that fit within budget
        result = list(other_messages)
        while self._estimate_tokens_for(system_messages + result) > budget * 0.7:
            if result:
                result.pop(0)
            else:
                break

        return system_messages + result

    def _estimate_tokens_for(self, messages):
        return sum(len(str(m.get("content", ""))) for m in messages) // 4
```

## Persistent Context

For session resumption, implement persistence:

```python
import json
from pathlib import Path

class PersistentContext:
    def __init__(self, config):
        self.storage_path = Path(config.get("storage_path"))
        self.messages = self._load()
        self.max_tokens = config.get("max_tokens", 100000)

    async def add_message(self, message):
        self.messages.append(message)
        self._save()

    async def get_messages_for_request(self, token_budget=None, provider=None):
        budget = self._calculate_budget(token_budget, provider)
        if self._estimate_tokens() > budget * 0.9:
            return self._compact_messages(budget)
        return list(self.messages)

    async def get_messages(self):
        return list(self.messages)

    async def set_messages(self, messages):
        self.messages = list(messages)
        self._save()

    def _load(self):
        if self.storage_path.exists():
            return json.loads(self.storage_path.read_text())
        return []

    def _save(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(json.dumps(self.messages))

    def _calculate_budget(self, token_budget, provider):
        if token_budget:
            return token_budget
        if provider:
            info = provider.get_info()
            defaults = info.defaults or {}
            return defaults.get("context_window", self.max_tokens) - defaults.get("max_output_tokens", 4096) - 1000
        return self.max_tokens

    def _estimate_tokens(self):
        return sum(len(str(m.get("content", ""))) for m in self.messages) // 4

    def _compact_messages(self, budget):
        system = [m for m in self.messages if m["role"] == "system"]
        other = [m for m in self.messages if m["role"] != "system"]
        while self._estimate_tokens_for(system + other) > budget * 0.7 and other:
            other.pop(0)
        return system + other

    def _estimate_tokens_for(self, messages):
        return sum(len(str(m.get("content", ""))) for m in messages) // 4
```

## Debug Logging

Context managers can emit debug events for observability:

```python
async def add_message(self, message):
    self.messages.append(message)
    
    # Emit debug event
    if self.hooks:
        await self.hooks.emit("context:message_added:debug", {
            "role": message.get("role"),
            "content_length": len(str(message.get("content", ""))),
            "total_messages": len(self.messages)
        })
```

## Graceful Degradation

Context managers should support graceful degradation:

```python
async def mount(coordinator, config=None):
    config = config or {}
    
    # Try to load persistence backend
    storage_path = config.get("storage_path")
    if storage_path and Path(storage_path).parent.exists():
        context = PersistentContext(config)
    else:
        # Fall back to in-memory context
        context = SimpleContext(config)
    
    await coordinator.mount("session", context, name="context")
    return context
```

## Related Contracts

- **[Orchestrator Contract](orchestrator.md)** - Orchestrators call context managers
- **[Hook Contract](hook.md)** - Hooks can inject context via `inject_context` action

## Authoritative Reference

**→ [Context Contract](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/CONTEXT_CONTRACT.md)** - Complete specification
