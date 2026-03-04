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

This enables project-scoped session management - each project has its own session history.

## Session Lifecycle

1. **Creation** - Session initialized with configuration
2. **Execution** - Messages exchanged, tools executed
3. **Persistence** - Transcript and events written to disk
4. **Resumption** - Previous state restored from storage

### Sub-Sessions

When you delegate to agents, sub-sessions are created:

- **Parent session** - Your main conversation
- **Sub-session** - Agent's isolated workspace
- **State inheritance** - Configuration flows from parent to child
- **Result return** - Agent results merged back to parent

Sub-sessions support:
- **Configuration overlay** - Agents add specialized tools and instructions
- **Tool filtering** - Control which tools agents inherit
- **Independent transcripts** - Each sub-session has its own history
- **Automatic persistence** - Sub-session state saved for resumption

## Session Metadata

Each session stores metadata for tracking and resumption:

```json
{
  "session_id": "abc123",
  "parent_id": null,
  "created": "2024-01-15T10:30:00Z",
  "project_slug": "-home-user-projects-my-app",
  "bundle": "dev",
  "provider": "anthropic",
  "model": "claude-opus-4",
  "config": { ... }
}
```

Sub-sessions include additional metadata:

```json
{
  "session_id": "abc123-sub-001",
  "parent_id": "abc123",
  "agent_name": "zen-architect",
  "created": "2024-01-15T10:35:00Z",
  "config": { ... },
  "agent_overlay": { ... }
}
```

## Multi-Turn Conversations

Sessions maintain conversation context across multiple turns:

```bash
amplifier
amplifier> Create a user authentication module
# ... AI responds ...

amplifier> Now add password reset functionality
# ... AI has context from previous turn ...

amplifier> Write tests for the reset flow
# ... AI remembers the authentication module and reset functionality ...
```

Context includes:
- All previous messages
- Tool execution results
- Agent delegation outcomes
- Session configuration

## Best Practices

### Session Management

**Keep sessions focused:**
```bash
# ✅ Good: Focused session
amplifier run "Implement user authentication"

# ❌ Less effective: Kitchen sink session
amplifier run "Build the entire app"
```

**Resume for continuity:**
```bash
# Continue previous work
amplifier continue "Add tests for the auth module"
```

**Clean up old sessions:**
```bash
# Remove sessions older than 30 days
amplifier session cleanup --days 30
```

### Working Across Projects

Sessions are project-scoped:

```bash
cd ~/projects/api-server
amplifier run "Explain the API structure"

cd ~/projects/web-client  
amplifier run "Explain the client code"  # Different session history
```

### Session Naming

Session IDs are auto-generated. To identify sessions later:

```bash
# Use descriptive prompts
amplifier run "Implement authentication module"  # Clear purpose

# Check session list for context
amplifier session list
```

## Troubleshooting

### Session Not Found

```bash
# List all sessions
amplifier session list --all

# Check if you're in the right project directory
pwd  # Sessions are project-scoped
```

### Session Won't Resume

**Symptoms:**
- "Session not found" errors
- Corrupted transcript or events

**Solutions:**
```bash
# Verify session exists
amplifier session show abc123

# Check session files
ls ~/.amplifier/projects/<project-slug>/sessions/abc123/

# If corrupted, start fresh
amplifier run "Continue the work from session abc123"
```

### Session Performance

**Large sessions slow down:**

Sessions accumulate context over time. If resumption becomes slow:

```bash
# Start a fresh session
amplifier run "Continue work on authentication"

# Reference specific outcomes from previous session if needed
amplifier run "Using the auth design from abc123, implement the login flow"
```

### Sub-Session Issues

**Agent delegation failures:**

```bash
# Check available agents
amplifier agents list

# Verify agent configuration
amplifier agents show zen-architect

# Check session events for error details
amplifier session show abc123
```

## Advanced: Session Configuration

### Tool Inheritance

Control which tools sub-sessions inherit:

```yaml
# In bundle configuration
spawn:
  exclude_tools: [tool-task]  # Agents can't delegate further
```

This prevents infinite delegation loops while allowing agents full access to other tools.

### Hook Inheritance

Similarly, control hook inheritance:

```yaml
# In bundle configuration
spawn:
  exclude_hooks: [hook-custom-logging]  # Agents don't inherit custom hooks
```

### Bundle Context Preservation

Sub-sessions preserve bundle context from parent:
- Module resolution paths
- Mention mappings (`@namespace:path`)
- Tool source locations

This ensures agents can access the same resources as the parent session.

## Session Export

Export session transcripts for analysis or sharing:

```bash
# Export as JSON
amplifier session export abc123 --format json --output session.json

# Export as Markdown
amplifier session export abc123 --format markdown --output session.md
```

Exports include:
- Full conversation history
- Tool execution results
- Session metadata
- Agent delegation outcomes

## Session Cleanup

Regular cleanup prevents disk usage growth:

```bash
# Preview what will be deleted
amplifier session cleanup --days 30 --dry-run

# Delete old sessions
amplifier session cleanup --days 30

# Delete specific session
amplifier session delete abc123
```

**Note:** Active sessions (recently resumed) are protected from cleanup.

## Tips

### Effective Session Usage

**Use sessions for:**
- Multi-turn conversations requiring context
- Complex tasks spanning multiple steps
- Iterative refinement and review cycles

**Start fresh sessions for:**
- Unrelated tasks
- When context becomes too large
- After major changes in direction

### Session History

```bash
# View recent conversation
amplifier continue --no-history  # Resume without showing history

# Show full history
amplifier continue --full-history  # Show all messages

# Replay conversation
amplifier continue --replay  # Simulate typing
```

### Project Isolation

Sessions are automatically isolated by project:
- Each project directory has its own session history
- No cross-project context pollution
- Easy to switch between projects

This enables clean context boundaries when working on multiple projects.
