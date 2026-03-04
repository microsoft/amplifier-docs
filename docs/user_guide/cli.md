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

# Continue interactively
amplifier continue

# Continue with full history displayed
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
| `--limit, -n` | Max sessions to show (default: 20) |
| `--all` | Show all sessions (no limit) |
| `--json` | Output as JSON |

### `session show`

Show detailed information about a session.

```bash
amplifier session show SESSION_ID
```

### `session resume`

Resume a specific session.

```bash
amplifier session resume SESSION_ID [PROMPT]
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

### `session export`

Export a session transcript.

```bash
amplifier session export SESSION_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--format` | Export format: `json`, `markdown` (default: json) |
| `--output, -o` | Output file path |

## Configuration

### `init`

Initialize Amplifier in the current directory or globally.

```bash
amplifier init [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--global` | Initialize globally (~/.amplifier) instead of current directory |

### `bundle`

Manage bundles.

```bash
amplifier bundle SUBCOMMAND [OPTIONS]
```

**Subcommands:**

- `list` - List registered bundles
- `show BUNDLE` - Show bundle details
- `use BUNDLE` - Set active bundle for this project
- `add URI` - Register a new bundle
- `remove BUNDLE` - Unregister a bundle
- `update BUNDLE` - Update bundle to latest version

**Examples:**

```bash
# List bundles
amplifier bundle list

# Show bundle details
amplifier bundle show foundation

# Set active bundle
amplifier bundle use dev

# Add a new bundle
amplifier bundle add git+https://github.com/org/my-bundle@main
```

### `provider`

Manage LLM providers.

```bash
amplifier provider SUBCOMMAND [OPTIONS]
```

**Subcommands:**

- `list` - List available providers
- `show PROVIDER` - Show provider details
- `use PROVIDER` - Set active provider for this project
- `add URI` - Register a new provider module

**Examples:**

```bash
# List providers
amplifier provider list

# Show provider details
amplifier provider show anthropic

# Set active provider
amplifier provider use openai
```

### `config`

Manage configuration settings.

```bash
amplifier config SUBCOMMAND KEY [VALUE]
```

**Subcommands:**

- `get KEY` - Get a configuration value
- `set KEY VALUE` - Set a configuration value
- `unset KEY` - Remove a configuration value
- `list` - List all configuration values

**Examples:**

```bash
# Get a value
amplifier config get bundle.active

# Set a value
amplifier config set bundle.active dev

# List all config
amplifier config list
```

## Module Management

### `module`

Manage modules (tools, hooks, etc.).

```bash
amplifier module SUBCOMMAND [OPTIONS]
```

**Subcommands:**

- `list` - List installed modules
- `show MODULE` - Show module details
- `add URI` - Install a module
- `remove MODULE` - Uninstall a module
- `update MODULE` - Update module to latest version

### `tool`

Manage tools specifically.

```bash
amplifier tool SUBCOMMAND [OPTIONS]
```

**Subcommands:**

- `list` - List available tools
- `show TOOL` - Show tool details

### `source`

Manage module sources.

```bash
amplifier source SUBCOMMAND [OPTIONS]
```

**Subcommands:**

- `list` - List registered sources
- `add URI` - Add a source
- `remove URI` - Remove a source

## Agent Management

### `agent`

Manage agents.

```bash
amplifier agent SUBCOMMAND [OPTIONS]
```

**Subcommands:**

- `list` - List available agents
- `show AGENT` - Show agent details

## Mode Management

### `mode`

Manage runtime modes.

```bash
amplifier mode SUBCOMMAND [OPTIONS]
```

**Subcommands:**

- `list` - List available modes
- `current` - Show active mode
- `set MODE` - Activate a mode
- `clear` - Deactivate current mode

**Examples:**

```bash
# List modes
amplifier mode list

# Activate a mode
amplifier mode set brainstorm-mode

# Clear active mode
amplifier mode clear
```

## Interactive Mode Commands

When running in interactive mode (`amplifier` or `amplifier run --mode chat`), these special commands are available:

| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/exit`, `/quit` | Exit interactive mode |
| `/clear` | Clear the screen |
| `/history` | Show conversation history |
| `/session` | Show current session info |
| `/bundle` | Show current bundle |
| `/provider` | Show current provider |
| `/model` | Show current model |
| `/agents` | List available agents |
| `/allowed-dirs` | Manage allowed write directories |
| `/denied-dirs` | Manage denied write directories |
| `@AGENT prompt` | Invoke a named agent |

**Examples:**

```bash
amplifier
amplifier> @explorer What is the architecture of this project?
amplifier> /history
amplifier> /exit
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `AMPLIFIER_HOME` | Base directory for Amplifier data (default: ~/.amplifier) |
| `AMPLIFIER_AGENT_<NAME>` | Override agent file path for testing (e.g., AMPLIFIER_AGENT_ZEN_ARCHITECT) |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `GOOGLE_API_KEY` | Google AI API key |

## Shell Completion

Install shell completion for your shell:

```bash
# Auto-detect and install
amplifier --install-completion

# The installer will detect your shell and add completion to your config file
```

Supported shells: bash, zsh, fish

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid configuration |
| 3 | API error |
| 4 | Session error |

## Tips

### Using JSON Output for Scripting

```bash
# Parse JSON output with jq
amplifier run --output-format json "What is 2+2?" | jq -r '.response'

# Get session list as JSON
amplifier session list --json | jq '.[] | select(.messages > 5)'
```

### Resuming Work Across Projects

Sessions are project-scoped (by working directory). To resume a session from another project:

```bash
cd /path/to/project
amplifier continue  # Resumes most recent session in THIS project
```

### Quick Provider Switching

```bash
# One-shot with specific provider
amplifier run --provider anthropic --model claude-opus-4-6 "prompt"

# Set default for project
amplifier provider use openai
```

### Agent Invocation

```bash
# In interactive mode
amplifier
amplifier> @explorer What files handle authentication?

# Or via run command (requires task tool in bundle)
amplifier run "@explorer What files handle authentication?"
```
