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

This ensures each project has its own session history.

## Session Metadata

Metadata includes:

- `session_id` - Unique session identifier
- `created` - ISO timestamp of creation
- `bundle` - Bundle used for this session
- `model` - Model/provider information
- `turn_count` - Number of user messages
- `working_dir` - Working directory when session was created
- `name` - Optional human-readable name
- `description` - Optional session description

## Session Operations

### Delete a Session

```bash
amplifier session delete abc123
```

### Fork a Session

Create a new session from a specific turn in an existing session:

```bash
# Show turns to fork from
amplifier session fork abc123

# Fork at turn 3
amplifier session fork abc123 --turn 3

# Fork with custom name
amplifier session fork abc123 --turn 3 --name my-fix
```

Forking creates a new session with conversation history up to the specified turn, allowing you to explore alternative paths.

### Rename a Session

In interactive mode:

```bash
amplifier> /rename My Feature Work
```

## Session Replay

Review past conversations with timing simulation:

```bash
# Replay with default speed (2x)
amplifier continue --replay

# Replay at custom speed
amplifier continue --replay --replay-speed 1.0
```

## History Display

When resuming a session, Amplifier shows recent conversation history:

```bash
# Show last 10 messages (default)
amplifier continue

# Show all messages
amplifier continue --full-history

# Skip history display
amplifier continue --no-history

# Show thinking blocks
amplifier continue --show-thinking
```

## Session Lineage

Sessions track parent-child relationships for agent delegation:

- **Parent Session** - The main session you're working in
- **Child Session** - Sub-session created by agent delegation
- **Session Fork** - New session branched from existing session

Child sessions include `parent_id` in metadata for lineage tracking.

## Session Events

Sessions emit events for observability:

- `session:start` - New session created
- `session:resume` - Existing session resumed
- `session:fork` - Child session forked from parent
- `session:end` - Session completed
- `prompt:complete` - Prompt execution finished

Events are logged to `events.jsonl` for debugging and analysis.

## Working Directory

Sessions track the working directory where they were created:

- Stored in `metadata.json` as `working_dir`
- Used for resolving relative file paths
- Critical for multi-project workflows

## Session Persistence

Sessions are automatically saved:

- **After each turn** in interactive mode
- **After execution** in single-shot mode
- **During tool execution** for crash recovery
- **On session fork** to preserve state

This enables:
- Resume from any point
- Crash recovery
- Multi-turn agent conversations
- Session analysis and debugging

## Best Practices

### Session Naming

Give sessions meaningful names for easier navigation:

```bash
amplifier> /rename Implement OAuth Support
```

### Session Organization

- Use bundles to organize sessions by type
- Delete old sessions periodically
- Fork sessions to explore alternatives
- Use descriptive names for important sessions

### Session Limits

- Consider deleting sessions older than 30 days
- Large sessions (100+ turns) may be slow to load
- Fork long sessions to start fresh while preserving history

## Related Documentation

- **[CLI Reference](cli.md)** - Session management commands
- **[Agents](agents.md)** - Agent sub-sessions
- **[Session Analysis](https://github.com/microsoft/amplifier-foundation/blob/main/docs/SESSION_ANALYSIS.md)** - Analyzing and debugging sessions
