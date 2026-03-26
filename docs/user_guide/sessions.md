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
├── metadata.json        # Session metadata
└── config.md            # Configuration snapshot
```

### Project Slug

The project slug is derived from your working directory:

```
/home/user/projects/my-app → -home-user-projects-my-app
```

This ensures sessions are organized by project.

## Session Metadata

Session metadata includes:

- **session_id**: Unique identifier
- **created**: Creation timestamp
- **bundle**: Bundle used for the session
- **model**: Provider and model used
- **turn_count**: Number of user turns
- **working_dir**: Working directory for the session
- **name**: Optional human-friendly name
- **description**: Optional session description

## Session Lifecycle

### Creation

Sessions are created when you:
- Run `amplifier run "prompt"`
- Start interactive mode with `amplifier`
- Resume with `amplifier continue`

### Persistence

Sessions are automatically saved after each turn, storing:
- Updated transcript
- Current metadata
- Session state

### Resumption

Sessions can be resumed:
- Automatically with `amplifier continue` (most recent)
- By ID with `amplifier session resume <id>`
- Interactively with `amplifier resume` (search/select)

## Session Management Commands

### List Sessions

```bash
# Show recent sessions
amplifier session list

# Show all sessions
amplifier session list --all

# Show limited number
amplifier session list --limit 5
```

### Show Session Details

```bash
amplifier session show abc123
```

Shows:
- Session ID and creation time
- Bundle and model configuration
- Message count
- Last prompt
- Session name (if set)

### Fork Sessions

Fork a session at a specific turn to explore alternative paths:

```bash
# Show turns and fork interactively
amplifier session fork abc123

# Fork at specific turn
amplifier session fork abc123 5

# Fork with custom name
amplifier session fork abc123 5 my-experiment
```

### Delete Sessions

```bash
# Delete specific session
amplifier session delete abc123

# Confirm deletion
amplifier session delete abc123 --confirm
```

### Clean Up Old Sessions

```bash
# Delete sessions older than 30 days
amplifier session cleanup

# Delete sessions older than N days
amplifier session cleanup --days 7

# Preview without deleting
amplifier session cleanup --dry-run
```

## Session Naming

Sessions can be named for easier identification:

- Names can be set manually with `/rename` command in interactive mode
- Some configurations auto-generate names based on conversation content
- Names are stored in session metadata

## Sub-Sessions (Agent Delegation)

When agents delegate to other agents, child sessions (sub-sessions) are created:

### Sub-Session Structure

```
parent-session-id/
├── transcript.jsonl
├── metadata.json
└── config.md

{parent_id}-{child_span}_{agent_name}/  # Sub-session ID format
├── transcript.jsonl
├── metadata.json
└── config.md
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
- **Ephemeral context**: Temporary context for single iterations

## Best Practices

### Naming Sessions

- Use descriptive names for important work sessions
- Names help when searching/resuming later
- Keep names concise (50 chars max)

### Session Cleanup

- Regularly clean up old sessions to save disk space
- Use `--dry-run` to preview cleanup
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

