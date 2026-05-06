---
title: Session API
description: AmplifierSession class reference
---

# Session API

The `AmplifierSession` class is the main interface for interacting with Amplifier.

**Source**: [amplifier_core/session.py](https://github.com/microsoft/amplifier-core/blob/main/amplifier_core/session.py)

## AmplifierSession

```python
from amplifier_core import AmplifierSession

async with AmplifierSession(config=mount_plan) as session:
    response = await session.execute("Hello, world!")
```

### Constructor

```python
AmplifierSession(
    config: dict[str, Any],                    # Mount plan configuration
    loader: ModuleLoader | None = None,        # Optional module loader
    session_id: str | None = None,             # Optional session ID (auto-generated if not provided)
    parent_id: str | None = None,              # Parent session ID for child sessions
    approval_system: ApprovalSystem | None = None,  # Optional approval system
    display_system: DisplaySystem | None = None,    # Optional display system
    is_resumed: bool = False                   # Whether resuming existing session (controls event type)
)
```

When `parent_id` is set, the session is a child session. The kernel emits a `session:fork` event during initialization and includes `parent_id` in all events for lineage tracking.

The `is_resumed` parameter controls whether the session emits `session:start` (new session) or `session:resume` (resumed session) events.

### Methods

#### `initialize()`

Initialize the session, loading all modules specified in the mount plan. Delegates to `_session_init.initialize_session()` — the single implementation shared by both `AmplifierSession` and `RustSession`.

```python
await session.initialize()
```

#### `execute(prompt: str) -> str`

Execute a prompt and return the response.

```python
response = await session.execute("Explain this code")
```

#### `cleanup()`

Clean up session resources.

```python
await session.cleanup()
```

### Context Manager

`AmplifierSession` supports async context manager for automatic initialization and cleanup:

```python
async with AmplifierSession(config=config) as session:
    # Session is initialized
    response = await session.execute(prompt)
# Session is cleaned up
```

## Example

```python
import asyncio
from amplifier_core import AmplifierSession

config = {
    "session": {
        "orchestrator": "loop-basic",
        "context": "context-simple"
    },
    "providers": [{
        "module": "provider-anthropic",
        "source": "git+https://github.com/microsoft/amplifier-module-provider-anthropic@main",
        "config": {"model": "claude-sonnet-4-5"}
    }],
    "tools": []
}

async def main():
    async with AmplifierSession(config=config) as session:
        response = await session.execute("What is 2 + 2?")
        print(response)

asyncio.run(main())
```
