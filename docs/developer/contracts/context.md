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

**Source**: `amplifier_core/interfaces.py` lines 162-209

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

## Mount Function

```python
async def mount(coordinator, config=None):
    config = config or {}
    context = MyContextManager(
        max_tokens=config.get("max_tokens", 100000),
        compaction_threshold=config.get("compaction_threshold", 0.8)
    )
    await coordinator.mount("session", context, name="context")
    return None
```

## Internal Compaction

Compaction is an **internal implementation detail** of the context manager. It happens automatically when `get_messages_for_request()` is called and the context exceeds thresholds.

### Non-Destructive Compaction (REQUIRED)

**Critical Design Principle**: Compaction MUST be **ephemeral** - it returns a compacted VIEW without modifying the stored history.

```
┌─────────────────────────────────────────────────────────────────┐
│                    NON-DESTRUCTIVE COMPACTION                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  messages[]                    get_messages_for_request()       │
│  ┌──────────┐                  ┌──────────┐                     │
│  │ msg 1    │                  │ msg 1    │  (compacted view)   │
│  │ msg 2    │   ──────────►    │ [summ]   │                     │
│  │ msg 3    │   ephemeral      │ msg N    │                     │
│  │ ...      │   compaction     └──────────┘                     │
│  │ msg N    │                                                   │
│  └──────────┘                  get_messages()                   │
│       │                        ┌──────────┐                     │
│       │                        │ msg 1    │  (FULL history)     │
│       └──────────────────────► │ msg 2    │                     │
│         unchanged              │ msg 3    │                     │
│                                │ ...      │                     │
│                                │ msg N    │                     │
│                                └──────────┘                     │
│                                                                 │
│  Key: Internal state is NEVER modified by compaction.           │
│       Compaction produces temporary views for LLM requests.     │
│       Full history is always available via get_messages().      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Why Non-Destructive?**:
- **Transcript integrity**: Full conversation history is preserved for replay/debugging
- **Session resume**: Can resume from any point with complete context
- **Reproducibility**: Same inputs produce same outputs
- **Observability**: Hook systems can observe the full conversation

**Implementation Pattern**:
```python
async def get_messages_for_request(self, token_budget=None, provider=None):
    """Return compacted VIEW without modifying internal state."""
    budget = self._calculate_budget(token_budget, provider)
    
    # Read current messages (don't modify)
    messages = list(self._messages)  # Copy!
    
    # Check if compaction needed
    token_count = self._count_tokens(messages)
    if not self._should_compact(token_count, budget):
        return messages
    
    # Compact EPHEMERALLY - return compacted copy
    return self._compact_messages(messages, budget)  # Returns NEW list

async def get_messages(self):
    """Return FULL history (never compacted)."""
    return list(self._messages)  # Always complete
```

### Tool Pair Preservation

**Critical**: During compaction, tool_use and tool_result messages must be kept together. Separating them causes LLM API errors.

```python
# Build tool_call_id -> tool_use index map
tool_use_ids = set()
for msg in self._messages:
    if msg.get("role") == "assistant" and msg.get("tool_calls"):
        for tc in msg["tool_calls"]:
            tool_use_ids.add(tc.get("id"))

# Identify orphaned tool results
orphan_result_indices = []
for i, msg in enumerate(self._messages):
    if msg.get("role") == "tool":
        if msg.get("tool_call_id") not in tool_use_ids:
            orphan_result_indices.append(i)
```

## Configuration

Context managers receive configuration via Mount Plan:

```yaml
session:
  orchestrator: loop-basic
  context: my-context
```

See [MOUNT_PLAN_SPECIFICATION.md](../specs/MOUNT_PLAN_SPECIFICATION.md) for full schema.

## Observability

Register compaction events:

```python
coordinator.register_contributor(
    "observability.events",
    "my-context",
    lambda: ["context:pre_compact", "context:post_compact"]
)
```

Standard events to emit:
- `context:pre_compact` - Before compaction (include message_count, token_count)
- `context:post_compact` - After compaction (include new counts)

See [CONTRIBUTION_CHANNELS.md](../specs/CONTRIBUTION_CHANNELS.md) for the pattern.

## Canonical Example

**Reference implementation**: [amplifier-module-context-simple](https://github.com/microsoft/amplifier-module-context-simple)

Study this module for:
- Basic ContextManager implementation
- Token counting approach
- Internal compaction with tool pair preservation

Additional examples:
- [amplifier-module-context-persistent](https://github.com/microsoft/amplifier-module-context-persistent) - File-based persistence

## Validation Checklist

### Required

- [ ] Implements all 5 ContextManager protocol methods
- [ ] `mount()` function with entry point in pyproject.toml
- [ ] `get_messages_for_request()` handles compaction internally
- [ ] Compaction preserves tool_use/tool_result pairs
- [ ] Messages returned in conversation order

### Recommended

- [ ] Token counting for accurate compaction triggers
- [ ] Emits context:pre_compact and context:post_compact events
- [ ] Preserves system messages during compaction
- [ ] Thread-safe for concurrent access
- [ ] Configurable thresholds

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
```

## Quick Validation Command

```bash
# Structural validation
amplifier module validate ./my-context --type context
```

## See Also

- [README.md](index.md) - All contracts
- [ORCHESTRATOR_CONTRACT.md](orchestrator.md) - Execution loop strategy
