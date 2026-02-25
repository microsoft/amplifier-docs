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
amplifier continue "Now add tests for that function"

# Resume interactively
amplifier continue

# Review full history
amplifier continue --full-history
```

## Session Management

### `session list`

List all sessions.

```bash
amplifier session list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--limit, -n` | Maximum number of sessions to show (default: 20) |
| `--bundle, -B` | Filter by bundle |
| `--all` | Show all sessions (no limit) |

### `session show`

Show detailed session information.

```bash
amplifier session show SESSION_ID
```

### `session resume`

Resume a specific session.

```bash
amplifier session resume SESSION_ID [PROMPT]
```

| Option | Description |
|--------|-------------|
| `--force-bundle, -B` | Force a different bundle for this session (experimental) |
| `--no-history` | Skip displaying conversation history |
| `--full-history` | Show all messages (default: last 10) |
| `--replay` | Replay conversation with timing simulation |
| `--replay-speed, -s` | Replay speed multiplier (default: 2.0) |
| `--show-thinking` | Show thinking blocks in history |

### `session delete`

Delete a session.

```bash
amplifier session delete SESSION_ID
```

### `session fork`

Fork a session at a specific turn.

```bash
amplifier session fork SESSION_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--turn, -t` | Turn number to fork from (required) |
| `--name, -n` | Name for the forked session |

## Bundle Management

### `bundle list`

List available bundles.

```bash
amplifier bundle list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--all, -a` | Show all bundles including dependencies and nested bundles |

### `bundle show`

Show bundle configuration.

```bash
amplifier bundle show BUNDLE_NAME
```

### `bundle use`

Set the active bundle.

```bash
amplifier bundle use BUNDLE_NAME
```

### `bundle clear`

Clear the active bundle selection.

```bash
amplifier bundle clear
```

### `bundle add`

Add a bundle from a source URI.

```bash
amplifier bundle add SOURCE_URI [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--name, -n` | Bundle name (auto-detected if not provided) |
| `--app` | Register as an app bundle (always composed onto sessions) |

### `bundle remove`

Remove a previously added bundle.

```bash
amplifier bundle remove BUNDLE_NAME
```

### `bundle update`

Update bundles from their sources.

```bash
amplifier bundle update [BUNDLE_NAME]
```

| Option | Description |
|--------|-------------|
| `--all` | Update all bundles |

### `bundle validate`

Validate bundle structure and configuration.

```bash
amplifier bundle validate BUNDLE_PATH
```

## Provider Management

### `provider list`

List configured providers.

```bash
amplifier provider list
```

### `provider use`

Set the active provider.

```bash
amplifier provider use PROVIDER_NAME
```

### `provider clear`

Clear the active provider selection.

```bash
amplifier provider clear
```

## Module Management

### `module list`

List installed modules.

```bash
amplifier module list
```

### `module show`

Show module details.

```bash
amplifier module show MODULE_NAME
```

## Source Management

### `source list`

List configured bundle sources.

```bash
amplifier source list
```

### `source add`

Add a bundle source.

```bash
amplifier source add NAME URI
```

### `source remove`

Remove a bundle source.

```bash
amplifier source remove NAME
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
amplifier agents show AGENT_NAME
```

## Directory Access Control

### `allowed-dirs`

Manage allowed write directories.

```bash
amplifier allowed-dirs COMMAND [OPTIONS]
```

**Commands:**
- `list` - List allowed write directories
- `add PATH` - Add directory to allowed list
- `remove PATH` - Remove directory from allowed list

### `denied-dirs`

Manage denied write directories.

```bash
amplifier denied-dirs COMMAND [OPTIONS]
```

**Commands:**
- `list` - List denied write directories
- `add PATH` - Add directory to denied list
- `remove PATH` - Remove directory from denied list

## Tool Management

### `tool list`

List available tools.

```bash
amplifier tool list
```

### `tool show`

Show tool details.

```bash
amplifier tool show TOOL_NAME
```

## Configuration

### `init`

Initialize Amplifier configuration.

```bash
amplifier init
```

Interactive setup for API keys and providers.

### `reset`

Reset Amplifier configuration.

```bash
amplifier reset
```

Clears all configuration and returns to first-run state.

### `notify`

Configure desktop notifications.

```bash
amplifier notify COMMAND
```

**Commands:**
- `enable` - Enable desktop notifications
- `disable` - Disable desktop notifications
- `test` - Test notification system

## Utilities

### `update`

Check for updates.

```bash
amplifier update
```

### `version`

Show version information.

```bash
amplifier version
```

## Interactive Mode

Running `amplifier` without a command starts interactive mode:

```bash
amplifier
```

**Interactive Commands:**

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/mode <name>` | Set or toggle a mode |
| `/modes` | List available modes |
| `/status` | Show session status |
| `/config` | Show current configuration |
| `/tools` | List available tools |
| `/agents` | List available agents |
| `/allowed-dirs` | Manage allowed write directories |
| `/denied-dirs` | Manage denied write directories |
| `/save [filename]` | Save conversation transcript |
| `/clear` | Clear conversation context |
| `/rename <name>` | Rename current session |
| `/fork [turn]` | Fork session at turn N |

**Key Bindings:**
- `Ctrl-J` - Insert newline (multi-line input)
- `Enter` - Submit prompt
- `Ctrl-D` - Exit
- `Ctrl-C` - Cancel execution (or confirm exit at prompt)

## Environment Variables

### Agent Overrides

Override agent resolution for testing:

```bash
export AMPLIFIER_AGENT_ZEN_ARCHITECT=~/test-zen.md
amplifier run "design system"
```

Format: `AMPLIFIER_AGENT_<NAME>` (uppercase, dashes → underscores)

## Output Formats

### Text Format (Default)

Human-readable markdown output.

### JSON Format

```bash
amplifier run --output-format json "prompt"
```

Returns:
```json
{
  "status": "success",
  "response": "...",
  "session_id": "...",
  "bundle": "...",
  "model": "...",
  "timestamp": "..."
}
```

### JSON-Trace Format

```bash
amplifier run --output-format json-trace "prompt"
```

Includes full execution trace with tool calls and timing.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (validation, runtime, etc.) |

## Shell Completion

Install shell completion:

```bash
amplifier --install-completion
```

Auto-detects your shell (bash, zsh, fish) and configures completion.
