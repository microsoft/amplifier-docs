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

**Why slugs?** They create unique, filesystem-safe identifiers for each project directory.

## Session Lifecycle

### Session States

Sessions progress through these states:

- **Created** - New session initialized
- **Running** - Actively executing prompts
- **Completed** - Finished successfully
- **Failed** - Encountered an error
- **Cancelled** - User interrupted (Ctrl+C)

### Session Metadata

Each session stores:

```json
{
  "session_id": "abc123",
  "created": "2024-01-15T10:30:00Z",
  "profile": "dev",
  "bundle": "foundation",
  "provider": "anthropic",
  "model": "claude-opus-4",
  "message_count": 5,
  "last_prompt": "Add error handling"
}
```

## Parent-Child Sessions

When agents delegate to sub-agents, a **parent-child relationship** is created:

```
Parent Session (abc123)
├── Child Session 1 (abc123-def456_zen-architect)
│   └── Grandchild (abc123-def456-ghi789_bug-hunter)
└── Child Session 2 (abc123-jkl012_modular-builder)
```

### Session ID Format

Child sessions use a hierarchical format:

```
<parent-id>-<child-span>_<agent-name>
```

Example: `abc123-a1b2c3d4_zen-architect`

- `abc123` - Parent session ID
- `a1b2c3d4` - Child span ID (16 hex chars)
- `zen-architect` - Agent name

### Lineage Tracking

The kernel tracks session lineage:

- `session_id` - Current session's unique ID
- `parent_id` - Parent session ID (None for root sessions)
- `trace_id` - Root session ID (propagates through all children)

**Events include lineage**: All events emitted by sessions include `session_id` and `parent_id` fields for tracing the full execution tree.

## Session Events

The kernel emits lifecycle events:

### Session Start/Resume

```python
# New session
SESSION_START = "session:start"
SESSION_START_DEBUG = "session:start:debug"
SESSION_START_RAW = "session:start:raw"

# Resumed session
SESSION_RESUME = "session:resume"
SESSION_RESUME_DEBUG = "session:resume:debug"
SESSION_RESUME_RAW = "session:resume:raw"
```

**Event data**:
```python
{
    "session_id": "abc123",
    "parent_id": None,  # or parent session ID
    "mount_plan": {...}  # Debug/raw modes only
}
```

### Session Fork

When a child session is created:

```python
SESSION_FORK = "session:fork"
SESSION_FORK_DEBUG = "session:fork:debug"
SESSION_FORK_RAW = "session:fork:raw"
```

**Event data**:
```python
{
    "parent": "abc123",
    "session_id": "abc123-def456_agent",
    "mount_plan": {...}  # Debug/raw modes only
}
```

### Session Cancellation

When a session is cancelled (Ctrl+C):

```python
CANCEL_COMPLETED = "cancel:completed"
```

**Event data**:
```python
{
    "was_immediate": False,  # Whether cancellation was immediate
    "error": "..."  # Optional error message if exception occurred
}
```

## Debug Mode

Enable debug mode for detailed session inspection:

```yaml
# In mount plan
session:
  debug: true        # Enable debug events
  raw_debug: true    # Include full mount plan in events
```

**Debug events** include:
- Full mount plan configuration
- Redacted secrets (API keys, tokens)
- Session initialization details

## Multi-Turn Sub-Session Resumption

Sub-sessions support multi-turn conversations. When a sub-session completes, its state is automatically persisted, enabling resumption across multiple turns.

### State Persistence

The system automatically saves sub-session state:

```python
# Saved to ~/.amplifier/projects/{project}/sessions/{session-id}/
{
    "session_id": "parent-123-child-456_agent",
    "parent_id": "parent-123",
    "trace_id": "parent-123",  # Root session ID
    "agent_name": "zen-architect",
    "child_span": "child-456",
    "created": "2024-01-15T10:30:00Z",
    "config": {...},  # Full merged mount plan
    "agent_overlay": {...},  # Original agent config
    "turn_count": 1
}
```

### Resuming Sub-Sessions

Resume a previous sub-session by providing its `session_id`:

```python
# Via task tool
result = await task_tool.execute({
    "session_id": "parent-123-child-456_agent",  # From previous spawn
    "instruction": "Add OAuth 2.0 support"
})
```

**Resume process**:
1. Load transcript and metadata from storage
2. Recreate AmplifierSession with stored configuration
3. Restore transcript to context
4. Execute new instruction with full conversation history
5. Save updated state

### Multi-Turn Example

```python
# Turn 1: Initial delegation
response1 = await task_tool.execute({
    "agent": "zen-architect",
    "instruction": "Design a caching system"
})
session_id = response1["session_id"]

# Turn 2: Resume with refinement
response2 = await task_tool.execute({
    "session_id": session_id,
    "instruction": "Add TTL support to the cache"
})

# Turn 3: Continue iteration
response3 = await task_tool.execute({
    "session_id": session_id,
    "instruction": "Add eviction policies"
})
```

## Session Configuration

Sessions are configured via the **mount plan**:

```yaml
session:
  orchestrator:
    module: loop-streaming
    config:
      min_delay_between_calls_ms: 500  # Rate limiting
  context:
    module: context-simple
    config:
      max_tokens: 100000

providers:
  - module: provider-anthropic
    config:
      api_key: "${ANTHROPIC_API_KEY}"

tools:
  - module: tool-filesystem
  - module: tool-bash

hooks:
  - module: hooks-logging
```

## Best Practices

### Session Naming

Use descriptive prompts so sessions are easy to identify:

```bash
# Good
amplifier run "Add OAuth 2.0 authentication to user service"

# Less helpful
amplifier run "fix auth"
```

### Session Cleanup

Sessions persist indefinitely. Clean up old sessions:

```bash
# Delete specific session
amplifier session delete abc123

# Delete all sessions older than 30 days
amplifier session cleanup --older-than 30d
```

### Working Directory

Sessions are scoped to the project directory. Change directories for different projects:

```bash
cd ~/projects/project-a
amplifier run "task"  # Session saved to project-a/

cd ~/projects/project-b
amplifier run "task"  # Session saved to project-b/
```

## Troubleshooting

### Session Not Found

If a session can't be found:

```bash
# Verify session exists
amplifier session list

# Check project directory
pwd  # Sessions are scoped to current directory
```

### Corrupted Session

If a session is corrupted:

```bash
# Delete corrupted session
amplifier session delete abc123

# Or use session-analyst agent to repair
amplifier run --agent foundation:session-analyst "Repair session abc123"
```

### Resume Failed

If resuming fails:

```bash
# Check session details
amplifier session show abc123

# Verify events.jsonl isn't too large
ls -lh ~/.amplifier/projects/*/sessions/abc123/events.jsonl
```

## Related Documentation

- [Profiles](profiles.md) - Configure different environments
- [Bundles](bundles.md) - Pre-configured capability sets
- [Agent Delegation](../developer_guides/applications/cli_case_study.md) - Sub-session spawning
