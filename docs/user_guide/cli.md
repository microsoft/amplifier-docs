---
title: CLI Reference
description: Complete reference for Amplifier CLI commands
---

# CLI Reference

Complete reference for all Amplifier command-line commands.

## Global Options

```bash
amplifier [OPTIONS] COMMAND [ARGS]
```

| Option | Description |
|--------|-------------|
| `--version` | Show version and exit |
| `--help` | Show help and exit |
| `--install-completion` | Install shell completion for the specified shell (bash, zsh, or fish) |

## Core Commands

### `run`

Execute a prompt or start an interactive session.

```bash
amplifier run [OPTIONS] PROMPT
```

| Option | Description |
|--------|-------------|
| `--bundle, -B` | Bundle to use for this session |
| `--provider, -p` | LLM provider (anthropic, openai, etc.) |
| `--model, -m` | Specific model to use |
| `--max-tokens` | Maximum output tokens |
| `--mode` | Execution mode: `chat`, `single` (default: single) |
| `--output-format` | Output format: `text`, `json`, `json-trace` (default: text) |
| `--resume` | Resume specific session with new prompt |
| `--verbose, -v` | Verbose output |

**Examples:**

```bash
# Basic usage
amplifier run "Explain this code"

# With options
amplifier run --bundle dev --model claude-opus-4-6 "Complex task"

# JSON output for scripting
amplifier run --output-format json "What is 2+2?"

# Resume a session
amplifier run --resume abc123 "Continue from where we left off"
```

### `continue`

Resume the most recent session.

```bash
amplifier continue [PROMPT]
```

| Option | Description |
|--------|-------------|
| `--force-bundle, -B` | Force a different bundle for this session (experimental) |
| `--no-history` | Skip displaying conversation history |
| `--full-history` | Show all messages (default: last 10) |
| `--replay` | Replay conversation with timing simulation |
| `--replay-speed, -s` | Replay speed multiplier (default: 2.0) |
| `--show-thinking` | Show thinking blocks in history |

**Examples:**

```bash
# Continue with a new prompt
amplifier continue "And what about tomorrow?"

# Continue via stdin (Unix pipes)
echo "New instruction" | amplifier continue

# Replay conversation with timing
amplifier continue --replay
```

### `resume`

Interactively select and resume a session.

```bash
amplifier resume
```

Displays a list of recent sessions with interactive selection.

## Session Management

### `session list`

List recent sessions.

```bash
amplifier session list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--limit, -n` | Number of sessions to show (default: 20) |
| `--all` | Show all sessions (no limit) |
| `--output` | Output format: `table`, `json` (default: table) |

### `session show`

Show session details.

```bash
amplifier session show <session-id>
```

### `session resume`

Resume a specific session.

```bash
amplifier session resume <session-id>
```

### `session fork`

Fork a session at a specific turn.

```bash
amplifier session fork <session-id> <turn> [name]
```

### `session delete`

Delete a session.

```bash
amplifier session delete <session-id>
```

### `session cleanup`

Clean up old sessions.

```bash
amplifier session cleanup [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--days` | Delete sessions older than N days (default: 30) |
| `--dry-run` | Show what would be deleted without deleting |

## Bundle Management

### `bundle list`

List available bundles.

```bash
amplifier bundle list
```

### `bundle show`

Show bundle details.

```bash
amplifier bundle show <name>
```

### `bundle use`

Set active bundle.

```bash
amplifier bundle use <name> [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Set for current directory only |
| `--project` | Set for current project |
| `--global` | Set globally (default) |

### `bundle current`

Show active bundle.

```bash
amplifier bundle current
```

### `bundle add`

Register a bundle.

```bash
amplifier bundle add <git-url> [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--name` | Alias for the bundle (auto-derived if not provided) |

### `bundle remove`

Unregister a bundle.

```bash
amplifier bundle remove <name>
```

### `bundle clear`

Reset to default bundle (foundation).

```bash
amplifier bundle clear
```

### `bundle update`

Update bundles to latest versions.

```bash
amplifier bundle update
```

## Provider Management

### `provider list`

List available providers.

```bash
amplifier provider list
```

### `provider use`

Set active provider.

```bash
amplifier provider use <name> [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Set for current directory only |
| `--project` | Set for current project |
| `--global` | Set globally (default) |

### `provider current`

Show active provider.

```bash
amplifier provider current
```

### `provider models`

List available models for a provider.

```bash
amplifier provider models <provider-name>
```

### `provider reset`

Reset provider configuration.

```bash
amplifier provider reset [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope` | Configuration scope: `local`, `project`, `global` |

## Module Management

### `module list`

List installed modules.

```bash
amplifier module list
```

### `module show`

Show module details.

```bash
amplifier module show <name>
```

### `module add`

Add a module.

```bash
amplifier module add <name> [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Add for current directory only |
| `--project` | Add for current project |
| `--global` | Add globally (default) |

### `module remove`

Remove a module.

```bash
amplifier module remove <name> [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope` | Configuration scope: `local`, `project`, `global` |

### `module current`

Show active modules.

```bash
amplifier module current
```

### `module refresh`

Refresh module sources.

```bash
amplifier module refresh [name] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--mutable-only` | Only refresh mutable sources (branches, not tags) |

### `module check-updates`

Check for module updates.

```bash
amplifier module check-updates
```

### `module validate`

Validate a module.

```bash
amplifier module validate <name>
```

### `module override`

Override module source.

```bash
amplifier module override <name> <source>
```

## Source Management

### `source add`

Add a source override.

```bash
amplifier source add <id> <uri> [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Add for current directory only |
| `--project` | Add for current project |
| `--global` | Add globally (default) |

### `source remove`

Remove a source override.

```bash
amplifier source remove <id> [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope` | Configuration scope: `local`, `project`, `global` |

### `source list`

List source overrides.

```bash
amplifier source list
```

### `source show`

Show source details.

```bash
amplifier source show <id>
```

## Agent Management

### `agents list`

List available agents.

```bash
amplifier agents list
```

### `agents show`

Show agent configuration.

```bash
amplifier agents show <name>
```

### `agents dirs`

Show agent search directories.

```bash
amplifier agents dirs
```

## Directory Access Control

### `allowed-dirs list`

List allowed write directories.

```bash
amplifier allowed-dirs list
```

### `allowed-dirs add`

Add an allowed write directory.

```bash
amplifier allowed-dirs add <path>
```

### `allowed-dirs remove`

Remove an allowed write directory.

```bash
amplifier allowed-dirs remove <path>
```

### `denied-dirs list`

List denied write directories.

```bash
amplifier denied-dirs list
```

### `denied-dirs add`

Add a denied write directory.

```bash
amplifier denied-dirs add <path>
```

### `denied-dirs remove`

Remove a denied write directory.

```bash
amplifier denied-dirs remove <path>
```

## Tool Management

### `tool list`

List tools available in the active bundle.

```bash
amplifier tool list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--modules` | Show module names (fast, no mount) |
| `--bundle` | Specify bundle to query |
| `--output` | Output format: `table`, `json` (default: table) |

### `tool info`

Show details about a specific tool.

```bash
amplifier tool info <tool-name> [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--bundle` | Specify bundle |
| `--module` | Show module info (fast) |

### `tool invoke`

Invoke a tool directly with arguments.

```bash
amplifier tool invoke <tool-name> <arg1>=<value1> [arg2=value2...]
```

**Examples:**

```bash
amplifier tool invoke read_file file_path=/tmp/test.txt
amplifier tool invoke bash command="ls -la"
amplifier tool invoke web_fetch url="https://example.com"
```

## Notification Configuration

### `notify status`

Show current notification settings.

```bash
amplifier notify status
```

### `notify desktop`

Configure desktop/terminal notifications.

```bash
amplifier notify desktop --enable [OPTIONS]
amplifier notify desktop --disable [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope` | Configuration scope: `local`, `project`, `global` |

### `notify ntfy`

Configure ntfy.sh push notifications.

```bash
amplifier notify ntfy --enable --topic <topic> [OPTIONS]
amplifier notify ntfy --disable [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope` | Configuration scope: `local`, `project`, `global` |

### `notify reset`

Clear notification settings.

```bash
amplifier notify reset --all [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope` | Configuration scope: `local`, `project`, `global` |

## Utility Commands

### `init`

First-time setup wizard.

```bash
amplifier init
```

Guides you through:
- API key configuration
- Provider selection
- Default model settings

### `update`

Update Amplifier and modules.

```bash
amplifier update [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--check-only` | Check for updates without installing |
| `--force` | Force update all sources (skip update detection) |
| `-y, --yes` | Skip confirmation prompts |
| `--verbose` | Show detailed multi-line output per source |

### `version`

Show version information.

```bash
amplifier version
```

### `reset`

Reset Amplifier configuration.

```bash
amplifier reset
```

## Interactive Mode

When running without a command (`amplifier`), the CLI enters interactive mode with these features:

### Slash Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/mode <name>` | Set or toggle a mode |
| `/modes` | List available modes |
| `/config` | Show current configuration |
| `/tools` | List available tools |
| `/agents` | List available agents |
| `/status` | Show session status |
| `/save [filename]` | Save conversation transcript |
| `/clear` | Clear conversation context |
| `/allowed-dirs <action>` | Manage allowed write directories |
| `/denied-dirs <action>` | Manage denied write directories |
| `/rename <name>` | Rename current session |
| `/fork [turn] [name]` | Fork session at specific turn |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl-J` | Insert newline (multi-line input) |
| `Enter` | Submit prompt |
| `Ctrl-D` | Exit interactive mode |
| `Ctrl-C` | Cancel current operation (during execution) |
| `Ctrl-R` | Search history |

### Mode System

Modes are runtime behavioral modifiers that change how the agent responds:

```bash
# Activate a mode
/mode architect

# Deactivate current mode
/mode off

# List available modes
/modes

# Mode with immediate prompt
/mode architect Design a caching system
```

## Configuration Scopes

Amplifier uses a three-level configuration system:

| Scope | Location | Priority | Use Case |
|-------|----------|----------|----------|
| **Local** | `./.amplifier/` | Highest | Directory-specific overrides |
| **Project** | Project root `.amplifier/` | Medium | Project-wide settings |
| **Global** | `~/.amplifier/` | Lowest | User defaults |

Settings cascade with local > project > global precedence.

## Session Storage

Sessions are stored in:

```
~/.amplifier/projects/<project-slug>/sessions/<session-id>/
├── transcript.jsonl    # Conversation history
├── metadata.json       # Session metadata
└── events.jsonl        # Event log
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `GOOGLE_API_KEY` | Google API key |
| `OLLAMA_HOST` | Ollama server URL |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 130 | Interrupted by user (Ctrl+C) |

## Tips

**Unix Piping:**

```bash
# Send file content as prompt
cat README.md | amplifier run "Summarize this"

# Chain with other commands
git diff | amplifier continue
```

**Conversational Single-Shot Workflows:**

```bash
# Question 1: Start conversation
$ amplifier run "What's the weather in Seattle?"
Session ID: a1b2c3d4
[Response]

# Question 2: Follow-up with context
$ amplifier continue "And what about tomorrow?"
✓ Resuming most recent session: a1b2c3d4
[Response with context from previous question]
```

**Background Processing:**

```bash
# Long-running command with timeout increase
amplifier run --max-tokens 8000 "Analyze this large codebase"
```

## See Also

- [Installation Guide](../getting_started/installation.md) - Setup instructions
- [Provider Configuration](../modules/providers/index.md) - Provider-specific settings
- [Bundle Guide](../developer_guides/foundation/amplifier_foundation/bundle_guide.md) - Creating bundles
