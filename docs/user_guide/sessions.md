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

## Session Metadata

Session metadata includes:

- **session_id**: Unique identifier
- **created**: Creation timestamp
- **turn_count**: Number of user turns
- **working_dir**: Working directory for the session

## Session Lifecycle

### Creation

Sessions are created when you start a new conversation or resume an existing one.

### Persistence

Sessions are automatically saved after each turn, storing:
- Updated transcript
- Current metadata
- Session state

### Resumption

Sessions can be resumed by session ID to continue prior conversations.

### Session Events

The kernel emits lifecycle events during session execution:

| Event | Emitted When |
|-------|-------------|
| `session:start` | New session begins executing |
| `session:resume` | Existing session is resumed |
| `session:fork` | Child (sub) session is created |
| `session:end` | Session cleanup completes |
| `cancel:completed` | Session execution is cancelled |

## Sub-Sessions (Agent Delegation)

When agents delegate to other agents, child sessions (sub-sessions) are created:

### Sub-Session Structure

Sub-session IDs follow the format:

```
{parent_id}-{child_span}_{agent_name}
```

### Tool and Hook Inheritance

Control which tools and hooks are inherited by sub-sessions:

```python
# Exclude specific tools from inheritance
tool_inheritance={"exclude_tools": ["tool-task"]}

# Inherit ONLY specific tools (allowlist)
tool_inheritance={"inherit_tools": ["tool-filesystem"]}

# Exclude specific hooks from inheritance
hook_inheritance={"exclude_hooks": ["hooks-logging"]}

# Inherit ONLY specific hooks (allowlist)
hook_inheritance={"inherit_hooks": ["hooks-approval"]}
```

Agent-explicit tools and hooks are always preserved regardless of the filtering policy.
Formula: `final = (inherited - excluded) + explicit`

### Subprocess Spawn Mode

Sub-sessions can run in a subprocess instead of in-process, providing isolation:

```yaml
# In agent bundle config
spawn_mode: subprocess
```

Or pass `use_subprocess: true` in the delegation call. Subprocess mode automatically propagates bundle context (module paths, mention mappings) to the child process.

### Session Metadata

Pass arbitrary metadata into child sessions for observability. Metadata is surfaced on `session:start` and `session:fork` events:

```python
response = await task_tool.execute({
    "agent": "architect",
    "instruction": "Design the API",
    "session_metadata": {"workflow": "planning", "task_id": "t-123"}
})
```

### Multi-Turn Sub-Sessions

Sub-sessions support multi-turn conversations:

```python
# Turn 1: Initial delegation
response = await task_tool.execute({
    "agent": "architect",
    "instruction": "Design the API"
})
session_id = response["session_id"]

# Turn 2: Follow-up
response = await task_tool.execute({
    "session_id": session_id,  # Resume existing sub-session
    "instruction": "Add versioning support"
})
```

### Sub-Session Metadata

Sub-sessions include:

- **session_id**: Unique identifier for this sub-session
- **parent_id**: Parent session ID
- **trace_id**: Root session ID (W3C Trace Context pattern)
- **agent_name**: Agent that ran this session
- **child_span**: 16-char hex span ID for short_id resolution
- **created**: Creation timestamp (ISO 8601, UTC)
- **config**: Merged configuration (parent + agent overlay)
- **agent_overlay**: Original agent configuration
- **turn_count**: Number of conversation turns
- **bundle_context**: Bundle module resolution paths and mention mappings
- **self_delegation_depth**: Recursion depth for self-delegation limit tracking
- **working_dir**: Working directory at session creation time

## Session Context

Sessions maintain context through:

- **Conversation history**: All user/assistant messages
- **Tool results**: Outputs from tool executions
- **System messages**: Agent instructions and guidance

## Best Practices

### Naming Sessions

- Use descriptive names for important work sessions
- Names help when searching/resuming later

### Session Cleanup

- Regularly clean up old sessions to save disk space
- Keep important sessions by giving them descriptive names

### Forking Sessions

- Fork before experimental changes
- Fork to explore alternative approaches
- Keep original session as reference

### Sub-Session Management

- Sub-sessions are automatically persisted
- Use session_id from responses to continue conversations
- Sub-sessions inherit parent configuration with agent overlays

## Related

- [CLI Reference](./cli.md) - Complete command reference
- [Session Storage Specification](../developer/sessions/storage.md) - Technical details
