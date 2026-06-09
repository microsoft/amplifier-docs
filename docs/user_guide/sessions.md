---
title: Sessions
description: How Amplifier sessions work — creation, persistence, and sub-sessions
---

# Sessions

A **session** is the fundamental unit of Amplifier execution. It ties together the orchestrator, context manager, providers, tools, and hooks for a single conversation or agent run.

## Creating a Session

Sessions are created via `PreparedBundle.create_session()`:

```python
from amplifier_foundation import load_bundle

bundle = await load_bundle("/path/to/bundle.md")
prepared = await bundle.prepare()

async with prepared.create_session() as session:
    response = await session.execute("Hello!")
    print(response)
```

### Session ID

Every session has a unique `session_id` (UUID):

```python
async with prepared.create_session() as session:
    print(session.session_id)  # e.g. "a1b2c3d4-..."
```

You can provide a specific session ID:

```python
async with prepared.create_session(session_id="my-session-001") as session:
    response = await session.execute("Hello!")
```

## Persistence and Resuming

Amplifier sessions can persist conversation history across process restarts using the `context-persistent` module.

### Persistent Context Configuration

```yaml
session:
  orchestrator: {module: loop-streaming}
  context:
    module: context-persistent
    config:
      persist_dir: ~/.amplifier/sessions
```

### Resuming a Session

```python
session_id = "existing-session-uuid"

async with prepared.create_session(
    session_id=session_id,
    is_resumed=True,
) as session:
    # Continues from where the previous session left off
    response = await session.execute("Continue where we left off")
```

Setting `is_resumed=True` causes the kernel to emit `session:resume` instead of `session:start`, preserving session lifecycle semantics.

## Sub-Sessions and Agent Delegation

Sub-sessions (child sessions) are a core feature for multi-agent architectures. A parent session can spawn child sessions to delegate work to specialized agents.

### Spawning from Foundation

```python
result = await prepared.spawn(
    child_bundle=agent_bundle,
    instruction="Find the bug in auth.py",
    parent_session=session,
)
print(result["output"])
print(result["session_id"])  # Child session ID for resumption
```

### Parent-Child Tracking

Child sessions include `parent_id` in all events for lineage tracking:

```python
async with prepared.create_session(
    parent_id=parent_session.session_id,
) as child_session:
    # All events include parent_id
    response = await child_session.execute("Analyze this code...")
```

The kernel emits `session:fork` during child session initialization.

## Tool Inheritance

When a parent session spawns a sub-session, the child inherits the parent's tools by default. The tool inheritance policy is configured in the `tool-task` module config.

### Exclude Specific Tools

Prevent certain tools from being inherited:

```yaml
tools:
  - module: tool-task
    config:
      exclude_tools: [tool-task]  # Child agents can't delegate further
```

### Allowlist Mode

Specify exactly which tools the child gets:

```yaml
tools:
  - module: tool-task
    config:
      inherit_tools: [tool-filesystem, tool-bash]  # Only these tools
```

### Explicit Agent Tools

Tools explicitly declared by an agent in its bundle are **always preserved**, even if they would be excluded by the parent's policy:

```
final_tools = (inherited − excluded) ∪ explicit
```

This ensures agents always have the tools they explicitly require.

## Hook Inheritance

Hook inheritance follows the same pattern as tool inheritance:

```yaml
tools:
  - module: tool-task
    config:
      exclude_hooks: [hooks-approval]  # Child sessions skip approval
```

Or allowlist mode:

```yaml
tools:
  - module: tool-task
    config:
      inherit_hooks: [hooks-logging]  # Only logging inherited
```

Hooks explicitly declared by an agent are always preserved regardless of inheritance policy.

## Working Directory

Sessions have a `session.working_dir` capability that tracks the current working directory. This is critical for server/daemon deployments where `Path.cwd()` returns the server's directory, not the user's project.

```python
from amplifier_foundation import get_working_dir, set_working_dir

# In a tool's execute()
working_dir = get_working_dir(coordinator)  # Returns Path
set_working_dir(coordinator, Path("/new/dir"))  # Dynamic updates
```

## Session Lifecycle Events

| Phase | Event |
|-------|-------|
| New session | `session:start` |
| Resumed session | `session:resume` |
| Child session spawned | `session:fork` |
| Prompt submitted | `prompt:submit` |
| Prompt complete | `prompt:complete` |
| Session ended | `session:end` |

## Direct AmplifierSession Usage

For advanced use cases without Foundation, create sessions directly:

```python
from amplifier_core import AmplifierSession

config = {
    "session": {
        "orchestrator": {"module": "loop-streaming"},
        "context": {"module": "context-simple"},
    },
    "providers": [{"module": "provider-anthropic", "config": {...}}],
    "tools": [...],
}

async with AmplifierSession(config) as session:
    response = await session.execute("Hello!")
```

See the [AmplifierSession API](../api/core/session.md) for full constructor documentation.
