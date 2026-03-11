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

Sessions are isolated per project, so you can work on multiple projects without confusion.

## Session Events

Sessions emit lifecycle events for observability:

| Event | When | Payload |
|-------|------|---------|
| `session:start` | New session begins | session_id, metadata |
| `session:resume` | Session resumed | session_id, metadata |
| `session:fork` | Child session created | parent, session_id, metadata |
| `session:end` | Session completes | session_id, status |

**Status values**: `running`, `completed`, `failed`, `cancelled`

## Advanced Usage

### Custom Session Creation

For programmatic use:

```python
from amplifier_core import AmplifierSession

session = AmplifierSession(
    config={
        "session": {
            "orchestrator": {"module": "loop-streaming"},
            "context": {"module": "context-simple"}
        },
        "providers": [...],
        "tools": [...]
    },
    session_id="custom-id",  # Optional, generates UUID if not provided
    parent_id=None,          # Optional, for child sessions
    is_resumed=False         # Controls session:start vs session:resume event
)

await session.initialize()
result = await session.execute("Your prompt here")
await session.cleanup()
```

### Multi-Turn Conversations

Sessions maintain context across turns automatically:

```bash
amplifier run "Explain this function"
# Session abc123 created

amplifier run --resume abc123 "Now add error handling"
# Continues previous conversation

amplifier run --resume abc123 "Add tests for it"
# Builds on entire conversation history
```

### Session Configuration

Sessions require:
- **Orchestrator**: Execution strategy (e.g., `loop-streaming`, `loop-basic`)
- **Context Manager**: Conversation memory (e.g., `context-simple`)
- **Providers**: At least one LLM provider

Optional components:
- **Tools**: Additional capabilities
- **Hooks**: Lifecycle observers

### Cleanup

Sessions clean up automatically, but you can force cleanup:

```python
await session.cleanup()
```

This:
- Emits `session:end` event
- Runs registered cleanup functions
- Releases resources

## Troubleshooting

### Session Not Found

```bash
amplifier session resume abc123
# Error: Session 'abc123' not found
```

**Solution**: List sessions to find the correct ID:
```bash
amplifier session list
```

### Corrupted Session

If a session won't resume:

1. **Check events log**: `cat ~/.amplifier/projects/<slug>/sessions/<id>/events.jsonl`
2. **Validate transcript**: Ensure `transcript.jsonl` is valid JSONL
3. **Start fresh**: Create a new session if recovery fails

### Missing Context

If resumed session lacks context:

- **Context compaction**: Long sessions may have truncated early messages
- **Solution**: Reference specific files/code in your prompt

### Performance Issues

Large sessions (100+ turns) may slow down:

- **Context manager overhead**: Processing entire history
- **Solution**: Start a new session or use session compaction features

## Best Practices

### Session Naming

While session IDs are auto-generated, you can track them by:
- Using `--resume` with the last session ID
- Creating project-specific workflows with consistent prompts

### Session Hygiene

- **One topic per session**: Start new sessions for unrelated tasks
- **Regular cleanup**: Old sessions consume disk space
- **Archive important sessions**: Copy session directories for future reference

### Debugging Sessions

Enable debug logging to see session lifecycle:

```bash
export AMPLIFIER_LOG_LEVEL=DEBUG
amplifier run "Your prompt"
```

Check the `events.jsonl` file for complete event history.

## Next Steps

- [Provider Setup](../getting_started/providers.md) - Configure LLM providers
- [Tools](../tools/index.md) - Add capabilities to your sessions
- [Profiles](../profiles/index.md) - Create reusable session configurations
