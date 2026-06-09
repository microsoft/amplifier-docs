---
title: AmplifierSession API
description: Core session class for Amplifier agent execution
---

# AmplifierSession

> **Source**: [`python/amplifier_core/session.py`](https://github.com/microsoft/amplifier-core/blob/main/python/amplifier_core/session.py)

The main entry point for running Amplifier agent sessions. Ties together the orchestrator, context manager, providers, tools, and hooks into a unified execution environment.

## Class Signature

```python
class AmplifierSession:
    def __init__(
        self,
        config: dict[str, Any],
        loader: ModuleLoader | None = None,
        session_id: str | None = None,
        parent_id: str | None = None,
        approval_system: ApprovalSystem | None = None,
        display_system: DisplaySystem | None = None,
        is_resumed: bool = False,
    ) -> None
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config` | `dict[str, Any]` | required | Mount plan with `session.orchestrator` and `session.context` required |
| `loader` | `ModuleLoader \| None` | `None` | Module loader; creates default if not provided |
| `session_id` | `str \| None` | `None` | Session ID; generates UUID if not provided |
| `parent_id` | `str \| None` | `None` | Parent session ID for child sessions; `None` for top-level |
| `approval_system` | `ApprovalSystem \| None` | `None` | App-layer approval policy implementation |
| `display_system` | `DisplaySystem \| None` | `None` | App-layer display/streaming implementation |
| `is_resumed` | `bool` | `False` | `True` if resuming existing session; controls `session:start` vs `session:resume` events |

### Raises

- `ValueError` — If `config` is missing `session.orchestrator` or `session.context`

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `session_id` | `str` | Unique session identifier (UUID) |
| `parent_id` | `str \| None` | Parent session ID; `None` for root sessions |
| `config` | `dict` | The mount plan configuration |
| `status` | `SessionStatus` | Current session status tracker |
| `coordinator` | `ModuleCoordinator` | Module registry and hook dispatcher |
| `loader` | `ModuleLoader` | Module loading and initialization engine |

## Methods

### `initialize()`

```python
async def initialize(self) -> None
```

Load and mount all modules from the config. Must be called before `execute()` when not using the context manager.

Loads orchestrator, context manager, providers, tools, and hooks.

### `execute()`

```python
async def execute(self, prompt: str) -> str
```

Submit a prompt to the orchestrator and return the response.

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | `str` | User message or instruction |

**Returns**: `str` — Assistant response text

### `cleanup()`

```python
async def cleanup(self) -> None
```

Release session resources. Called automatically by context manager exit.

### Context Manager

```python
async with AmplifierSession(config) as session:
    response = await session.execute("Hello!")
```

`__aenter__` calls `initialize()`. `__aexit__` calls `cleanup()`.

## Usage Examples

### Basic Usage

```python
import asyncio
from amplifier_core import AmplifierSession

async def main():
    config = {
        "session": {
            "orchestrator": {"module": "loop-streaming"},
            "context": {"module": "context-simple"},
        },
        "providers": [{"module": "provider-anthropic", "config": {...}}],
    }

    async with AmplifierSession(config) as session:
        response = await session.execute("Hello!")
        print(response)

asyncio.run(main())
```

### Child Session

```python
async with AmplifierSession(
    config,
    session_id="child-abc",
    parent_id=parent_session.session_id,
) as session:
    response = await session.execute("Analyze this code...")
```

When `parent_id` is set, the kernel emits `session:fork` during initialization and includes `parent_id` in all events for lineage tracking.

### Resumed Session

```python
async with AmplifierSession(
    config,
    session_id=existing_session_id,
    is_resumed=True,
) as session:
    # Emits session:resume instead of session:start
    response = await session.execute("Continue from where we left off...")
```

### Manual Lifecycle

```python
session = AmplifierSession(config)
await session.initialize()
try:
    response = await session.execute("Hello!")
    print(response)
finally:
    await session.cleanup()
```

## Session Lifecycle Events

| Phase | Events Emitted |
|-------|---------------|
| First execute() | `session:start` (or `session:resume`) |
| Execute | orchestrator loop (orchestrator emits `prompt:submit` / `prompt:complete`) |
| Cleanup | `session:end` |
| Fork | `session:fork` during init of child session |

## Session Status

`session.status` is a `SessionStatus` object that tracks:

- `session_id`: The session's ID
- Current execution state (`running`, `completed`, `cancelled`, or `failed`)

## Mount Plan Requirements

The `config` dict must follow the mount plan specification:

```python
config = {
    "session": {
        "orchestrator": {"module": "loop-streaming"},  # Required
        "context": {"module": "context-simple"},       # Required
    },
    "providers": [...],   # At least one required for LLM calls
    "tools": [...],       # Optional
    "hooks": [...],       # Optional
    "agents": [...],      # Optional
}
```

## Integration with Foundation

In practice, sessions are created via `PreparedBundle.create_session()` which handles module resolution and capability registration:

```python
from amplifier_foundation import load_bundle

bundle = await load_bundle("/path/to/bundle.md")
prepared = await bundle.prepare()

async with prepared.create_session() as session:
    response = await session.execute("Hello!")
```

`create_session()` additionally:
- Registers `session.working_dir` capability
- Registers `bundle_package_paths` capability
- Injects the module resolver for `@mention` resolution
