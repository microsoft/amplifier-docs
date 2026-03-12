---
title: Sessions
description: Session management, persistence, and resumption
---

# Sessions

Sessions track your conversations with Amplifier, enabling multi-turn interactions and the ability to resume previous work.

## What is a Session?

A session represents a single conversation with Amplifier, including:

- Conversation history (your prompts and AI responses)
- Tool execution results
- Session metadata (timestamp, profile, provider)
- Event log for debugging

## Session Basics

### Starting a Session

Every Amplifier command creates a session:

```bash
# Single command creates a session
amplifier run "Explain this code"

# Interactive mode is one session
amplifier
```

### Listing Sessions

```bash
amplifier session list
```

Output:
```
ID        Created              Profile  Messages  Last Prompt
abc123    2024-01-15 10:30    dev      5         "Add error handling"
def456    2024-01-15 09:15    base     3         "Explain the auth flow"
ghi789    2024-01-14 16:45    dev      12        "Refactor the API"
```

### Viewing Session Details

```bash
amplifier session show abc123
```

## Resuming Sessions

### Resume Most Recent

```bash
# Resume and continue conversation
amplifier continue "Now add tests for that function"

# Resume interactively
amplifier continue
```

### Resume Specific Session

```bash
# By session ID
amplifier session resume abc123

# With a new prompt
amplifier session resume abc123 "Continue from here"

# Using --resume flag
amplifier run --resume abc123 "Continue the refactoring"
```

## Session Storage

Sessions are stored at:

```
~/.amplifier/projects/<project-slug>/sessions/<session-id>/
├── transcript.jsonl     # Conversation history
├── events.jsonl         # Complete event log
└── metadata.json        # Session metadata
```

### Project Slug

The project slug is derived from your working directory:

```
/home/user/projects/my-app → -home-user-projects-my-app
```

This creates a unique storage location per project, enabling:
- Multiple projects with independent session histories
- Easy cleanup by deleting project directories
- Portable session archives

## Session Lifecycle

Sessions have distinct lifecycle states:

| State | Description |
|-------|-------------|
| `created` | Session initialized but not yet executed |
| `running` | Currently executing a prompt |
| `completed` | Execution finished successfully |
| `failed` | Execution encountered an error |
| `cancelled` | User cancelled execution |

States are tracked in `SessionStatus` and reflected in the events log.

## Advanced Topics

### Session Forking (Child Sessions)

Sessions can spawn child sessions for agent delegation:

```python
# Parent session creates child with its own config
child_session = AmplifierSession(
    config=merged_config,
    parent_id=parent_session.session_id,  # Links to parent
    approval_system=parent_approval,
    display_system=parent_display
)
```

**Key features**:
- `parent_id` tracks the lineage
- Child sessions inherit UX systems (approval, display)
- Kernel emits `session:fork` event with parent_id
- Enables hierarchical agent delegation patterns

### Sub-Session Resumption

Child sessions can be resumed for multi-turn interactions:

```python
# Resume existing sub-session
result = await resume_sub_session(
    sub_session_id="abc123-def456_agent-name",
    instruction="Continue the previous task"
)
```

**Persistence**:
- Full transcript saved with metadata
- Configuration preserved for resume
- Trace ID links all sessions in a conversation tree

### Session Metadata

Sessions track rich metadata for observability:

```json
{
  "session_id": "abc123-def456_agent-name",
  "parent_id": "abc123",
  "trace_id": "abc123",
  "agent_name": "code-reviewer",
  "child_span": "def456",
  "created": "2024-01-15T10:30:00Z",
  "turn_count": 3,
  "config": { ... },
  "working_dir": "/home/user/project"
}
```

**Trace Context (W3C pattern)**:
- `trace_id`: Root session ID (traces entire conversation tree)
- `child_span`: Unique span for each child session
- Enables distributed tracing across agent hierarchies

## Session Events

The kernel emits lifecycle events for observability:

| Event | When | Data |
|-------|------|------|
| `session:start` | New session begins | session_id, metadata |
| `session:resume` | Session resumed | session_id, parent_id, turn_count |
| `session:fork` | Child session created | session_id, parent_id |
| `session:end` | Session cleanup | session_id, status |

These events flow through the hook system for logging, metrics, and custom handlers.

## See Also

- [Session Forking Specification](../developer/specs/session-fork.md) - Detailed fork/resume API
- [Hooks](../developer/contracts/hook.md) - Session lifecycle hooks
- [Context Managers](../developer/contracts/context.md) - Memory persistence
