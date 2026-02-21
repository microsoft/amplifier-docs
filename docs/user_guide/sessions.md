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

This means sessions are project-specific.

## Session Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│  1. Session Created                                          │
│     - Unique ID generated                                    │
│     - Profile and provider configured                        │
│     - Storage initialized                                    │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Session Active                                           │
│     - Messages exchanged                                     │
│     - Tools executed                                         │
│     - Events logged                                          │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Session Ended                                            │
│     - Final state persisted                                  │
│     - Available for resumption                               │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Session Resumed (optional)                               │
│     - History loaded                                         │
│     - Context restored                                       │
│     - Continues from last state                              │
└─────────────────────────────────────────────────────────────┘
```

## Managing Sessions

### Delete a Session

```bash
amplifier session delete abc123
```

### Cleanup Old Sessions

```bash
# Delete sessions older than 30 days (default)
amplifier session cleanup

# Delete sessions older than 7 days
amplifier session cleanup --days 7
```

## Session Context

### What's Preserved

When you resume a session:

- Conversation history
- Session ID
- Project context

### What's Reloaded

- Profile configuration (current, not original)
- Provider configuration
- Module state

### What's NOT Preserved

- Tool execution state (files may have changed)
- In-memory context beyond token limit

## Multi-Turn Workflows

Sessions enable sophisticated multi-turn workflows:

```bash
# Start analysis
amplifier run "Analyze the user authentication module"

# Continue with follow-up
amplifier continue "What security issues did you find?"

# Act on findings
amplifier continue "Fix the SQL injection vulnerability you identified"

# Verify fix
amplifier continue "Now write tests for the fix"
```

## Conversational Single-Shot Workflows

You can build context across multiple single-shot commands, combining focused execution with conversational continuity:

```bash
# Analyze in one shot
amplifier run "Review the database schema for performance issues"

# Build on the analysis with follow-ups
amplifier continue "Which tables need indexing?"
amplifier continue "Generate the migration for those indexes"
amplifier continue "Write tests to verify query performance improved"
```

Each `continue` picks up the full conversation history, so the assistant remembers all previous analysis and decisions. This is particularly useful for:

- **Scripted workflows**: Chain commands in shell scripts
- **Incremental refinement**: Build up complex solutions step by step
- **Context preservation**: Maintain analysis across separate commands without interactive mode

## Session IDs

Session IDs follow the format:

```
{timestamp}-{random}
```

For sub-sessions (agent delegation):

```
{parent-span}-{child-span}_{agent-name}
```

Example: `a1b2c3-d4e5f6_explorer`

## Debugging Sessions

### View Event Log

```bash
# Find session log
ls ~/.amplifier/projects/*/sessions/abc123/

# View events
cat ~/.amplifier/projects/*/sessions/abc123/events.jsonl | head
```

### Event Types

| Event | Description |
|-------|-------------|
| `session:start` | Session initialized |
| `prompt:submit` | User prompt received |
| `provider:request` | LLM API call made |
| `provider:response` | LLM response received |
| `tool:pre` | Tool execution starting |
| `tool:post` | Tool execution completed |
| `session:end` | Session ended |

## Best Practices

1. **Use `continue` for related work**: Keep context when working on the same task
2. **New session for new tasks**: Start fresh for unrelated work
3. **Clean up regularly**: Run `session cleanup` periodically
4. **Name your sessions**: Use meaningful initial prompts for easy identification

## Troubleshooting

### "Session not found"

```bash
# List available sessions
amplifier session list --all

# Check session exists
ls ~/.amplifier/projects/*/sessions/
```

### "Context too long" on resume

The conversation history may exceed the model's context limit. Solutions:

1. Start a new session
2. Use a model with larger context
3. Manually summarize and start fresh

### Session resume behaves differently

Remember that:

- Profile may have changed
- Files may have changed since original session
- Tools execute against current state

## See Also

- [CLI Reference](cli.md) - Session commands
- [Architecture: Events](../architecture/events.md) - Event system details
