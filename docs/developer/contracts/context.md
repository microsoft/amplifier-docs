---
title: Context Contract
description: Memory management contract
---

# Context Contract

Context managers handle conversation memory and message storage.

## Purpose

Context managers control **what the agent remembers**:

- **Message storage** - Store conversation history
- **Request preparation** - Return messages that fit within token limits
- **Persistence** - Optionally persist across sessions
- **Memory strategies** - Implement various memory patterns

**Key principle**: The context manager owns **policy** for memory. The orchestrator asks for messages; the context manager decides **how** to fit them within limits. Swap context managers to change memory behavior without modifying orchestrators.

**Mechanism vs Policy**: Orchestrators provide the mechanism (request messages, make LLM calls). Context managers provide the policy (what to return, when to compact, how to fit within limits).

## Protocol Definition

**Source**: `amplifier_core/interfaces.py`

```python
@runtime_checkable
class ContextManager(Protocol):
    async def add_message(self, message: dict[str, Any]) -> None:
        """Add a message to the context."""
        ...

    async def get_messages_for_request(
        self,
        token_budget: int | None = None,
        provider: Any | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get messages ready for an LLM request.

        The context manager handles any compaction needed internally.
        Returns messages that fit within the token budget.

        Args:
            token_budget: Optional explicit token limit (deprecated, prefer provider).
            provider: Optional provider instance for dynamic budget calculation.
                If provided, budget = context_window - max_output_tokens - safety_margin.

        Returns:
            Messages ready for LLM request, compacted if necessary.
        """
        ...

    async def get_messages(self) -> list[dict[str, Any]]:
        """Get all messages (raw, uncompacted) for transcripts/debugging."""
        ...

    async def set_messages(self, messages: list[dict[str, Any]]) -> None:
        """Set messages directly (for session resume)."""
        ...

    async def clear(self) -> None:
        """Clear all messages."""
        ...
```

## Message Format

Messages follow a standard structure:

```python
# User message
{
    "role": "user",
    "content": "User's input text"
}

# Assistant message
{
    "role": "assistant",
    "content": "Assistant's response"
}

# Assistant message with tool calls
{
    "role": "assistant",
    "content": None,
    "tool_calls": [
        {
            "id": "call_123",
            "type": "function",
            "function": {"name": "read_file", "arguments": "{...}"}
        }
    ]
}

# System message
{
    "role": "system",
    "content": "System instructions"
}

# Tool result
{
    "role": "tool",
    "tool_call_id": "call_123",
    "content": "Tool output"
}
```

## Entry Point Pattern

### mount() Function

```python
async def mount(coordinator: ModuleCoordinator, config: dict) -> ContextManager | Callable | None:
    """
    Initialize and return context manager instance.

    Returns:
        - ContextManager instance
        - Cleanup callable
        - None for graceful degradation
    """
    context = MyContextManager(
        max_tokens=config.get("max_tokens", 100000),
        compaction_threshold=config.get("compaction_threshold", 0.8)
    )
    await coordinator.mount("session", context, name="context")
    return context
```

### pyproject.toml

```toml
[project.entry-points."amplifier.modules"]
my-context = "my_context:mount"
```

## Non-Destructive Compaction

**Critical Design Principle**: Compaction MUST be **ephemeral** - it returns a compacted VIEW without modifying the stored history.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NON-DESTRUCTIVE COMPACTION                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                 │
│  messages[]                    get_messages_for_request()       │
│  ┌──────────┐                  ┌──────────┐                     │
│  │ msg 1    │                  │ msg 1    │  (compacted view)   │
│  │ msg 2    │   ──────────▶    │ [summ]   │                     │
│  │ msg 3    │   ephemeral      │ msg N    │                     │
│  │ ...      │   compaction     └──────────┘                     │
│  │ msg N    │                                                   │
│  └──────────┘                  get_messages()                   │
│       │                        ┌──────────┐                     │
│       │                        │ msg 1    │  (FULL history)     │
│       └──────────────────────▶ │ msg 2    │                     │
│         unchanged              │ msg 3    │                     │
│                                │ ...      │                     │
│                                │ msg N    │                     │
│                                └──────────┘                     │
│                                                                 │
│  Key: Internal state is NEVER modified by compaction.           │
│       Compaction produces temporary views for LLM requests.     │
│       Full history is always available via get_messages().      │
│                                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

**Why Non-Destructive?**:
- **Transcript integrity**: Full conversation history is preserved for replay/debugging
- **Session resume**: Can resume from any point with complete context
- **Reproducibility**: Same inputs produce same outputs
- **Observability**: Hook systems can observe the full conversation

## Tool Pair Preservation

**Critical**: During compaction, tool_use and tool_result messages must be kept together. Separating them causes LLM API errors.

```python
async def _compact_internal(self) -> list[dict]:
    """Internal compaction - preserves tool pairs."""
    # Build tool_call_id -> tool_use index map
    tool_use_ids = set()
    for msg in self._messages:
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                tool_use_ids.add(tc.get("id"))

    # Strategy: Keep system messages + recent messages
    # But ensure we don't split tool pairs
    system_messages = [m for m in self._messages if m["role"] == "system"]

    # Find safe truncation point (not in middle of tool sequence)
    keep_count = self._keep_recent
    recent_start = max(0, len(self._messages) - keep_count)

    # Adjust start to not split tool sequences
    while recent_start > 0:
        msg = self._messages[recent_start]
        if msg.get("role") == "tool":
            # This is a tool result - need to include the tool_use before it
            recent_start -= 1
        else:
            break

    recent_messages = self._messages[recent_start:]
    return system_messages + recent_messages
```

## Debug Logging

Context managers should emit debug events for observability:

```python
async def add_message(self, message: dict[str, Any]) -> None:
    """Add message with debug logging."""
    self._messages.append(message)
    self._token_count += self._estimate_tokens(message)

    # Emit debug event
    await self._hooks.emit("context:message_added", {
        "role": message.get("role"),
        "token_count": self._token_count,
        "message_count": len(self._messages)
    })
```

## Graceful Degradation

Context managers can return `None` from `mount()` for graceful degradation:

```python
async def mount(coordinator, config=None):
    config = config or {}

    # Check for required configuration
    persistence_path = config.get("persistence_path")
    if not persistence_path:
        # Fall back to in-memory context
        return None

    context = PersistentContext(persistence_path)
    await coordinator.mount("session", context, name="context")
    return context
```

## Observability

Register compaction events:

```python
coordinator.register_contributor(
    "observability.events",
    "my-context",
    lambda: ["context:pre_compact", "context:post_compact", "context:message_added"]
)
```

Standard events to emit:
- `context:pre_compact` - Before compaction (include message_count, token_count)
- `context:post_compact` - After compaction (include new counts)
- `context:message_added` - After adding a message

## Testing

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import MockContextManager

@pytest.mark.asyncio
async def test_context_manager():
    context = MyContextManager(max_tokens=1000)

    # Add messages
    await context.add_message({"role": "user", "content": "Hello"})
    await context.add_message({"role": "assistant", "content": "Hi there!"})

    # Get messages for request (may compact)
    messages = await context.get_messages_for_request()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"

    # Get raw messages (no compaction)
    raw_messages = await context.get_messages()
    assert len(raw_messages) == 2

    # Test clear
    await context.clear()
    assert len(await context.get_messages()) == 0


@pytest.mark.asyncio
async def test_compaction_preserves_tool_pairs():
    """Verify tool_use and tool_result stay together during compaction."""
    context = MyContextManager(max_tokens=100, compaction_threshold=0.5)

    # Add messages including tool sequence
    await context.add_message({"role": "user", "content": "Read file.txt"})
    await context.add_message({
        "role": "assistant",
        "content": None,
        "tool_calls": [{"id": "call_123", "type": "function", "function": {...}}]
    })
    await context.add_message({
        "role": "tool",
        "tool_call_id": "call_123",
        "content": "File contents..."
    })

    # Force compaction by adding more messages
    for i in range(50):
        await context.add_message({"role": "user", "content": f"Message {i}"})

    # Get messages for request (triggers compaction)
    messages = await context.get_messages_for_request()

    # Verify tool pairs are preserved
    tool_use_ids = set()
    tool_result_ids = set()
    for msg in messages:
        if msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                tool_use_ids.add(tc.get("id"))
        if msg.get("role") == "tool":
            tool_result_ids.add(msg.get("tool_call_id"))

    # Every tool result should have matching tool use
    assert tool_result_ids.issubset(tool_use_ids), "Orphaned tool results found!"
```

## Related Contracts

- **[Orchestrator Contract](orchestrator.md)** - Orchestrators call context methods
- **[Hook Contract](hook.md)** - Hooks can observe context events

## References

- **→ [CONTEXT_CONTRACT.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/CONTEXT_CONTRACT.md)** - Authoritative contract specification
- **→ [amplifier-module-context-simple](https://github.com/microsoft/amplifier-module-context-simple)** - Reference implementation
