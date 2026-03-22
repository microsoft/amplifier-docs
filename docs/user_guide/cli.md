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

List recent sessions for the current project.

```bash
amplifier session list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--limit, -n` | Number of sessions to show (default: 20) |
| `--all-projects` | Show sessions from all projects |
| `--project PATH` | Show sessions for a specific project path |
| `--tree, -t SESSION_ID` | Show lineage tree for a session |

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

Delete sessions older than N days.

```bash
amplifier session cleanup [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--days, -d` | Delete sessions older than N days (default: 30) |
| `--force, -f` | Skip confirmation |

## Configuration

### `init`

Interactive setup -- manage providers and routing.

```bash
amplifier init
```

### `bundle`

Manage bundles.

```bash
amplifier bundle SUBCOMMAND [OPTIONS]
```

**Subcommands:**

- `list` - List registered bundles
- `show BUNDLE` - Show bundle details
- `use BUNDLE` - Set active bundle for this project
- `clear` - Clear active bundle setting
- `current` - Show currently active bundle
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

Manage AI providers.

```bash
amplifier provider SUBCOMMAND [OPTIONS]
```

**Subcommands:**

- `install` - Install provider modules (one or all known providers)
- `add [PROVIDER_TYPE]` - Add and configure a provider (interactive picker if omitted)
- `list` - List configured providers with status
- `remove NAME` - Remove a configured provider
- `edit NAME` - Re-configure an existing provider
- `test [NAME]` - Test provider connectivity
- `models [PROVIDER_ID]` - List available models for a provider
- `manage` - Interactive provider management dashboard

**Examples:**

```bash
# List configured providers
amplifier provider list

# Add a new provider interactively
amplifier provider add

# Add a specific provider type
amplifier provider add anthropic

# Test all configured providers
amplifier provider test
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
- `add MODULE_ID` - Install a module
- `remove MODULE_ID` - Uninstall a module
- `current` - Show currently active modules
- `update [MODULE_ID]` - Update module to latest version
- `validate` - Validate module configuration
- `override` - Module override management (set, remove, list)

### `tool`

Manage tools.

```bash
amplifier tool SUBCOMMAND [OPTIONS]
```

**Subcommands:**

- `list` - List available tools
- `info TOOL` - Show detailed tool information
- `invoke TOOL [ARGS]` - Invoke a tool directly

### `source`

Manage module sources.

```bash
amplifier source SUBCOMMAND [OPTIONS]
```

**Subcommands:**

- `list` - List registered sources
- `show MODULE_ID` - Show source details for a module
- `add URI` - Add a source
- `remove URI` - Remove a source


## Routing Configuration

Configure model routing for semantic roles.

```bash
amplifier routing SUBCOMMAND
```

| Subcommand | Description |
|------------|-------------|
| `list` | List available routing matrices |
| `use MATRIX` | Set active routing matrix |
| `show [MATRIX]` | Display routing matrix configuration |
| `manage` | Interactive routing management dashboard |
| `create` | Create a new routing matrix |

### Examples

```bash
# List available routing matrices
amplifier routing list

# Show current routing configuration
amplifier routing show

# Set active routing matrix
amplifier routing use balanced

# Interactive management
amplifier routing manage
```

## Agent Management

### `agents`

Manage agents.

```bash
amplifier agents SUBCOMMAND [OPTIONS]
```

**Subcommands:**

- `list` - List available agents from bundles
- `show AGENT` - Show detailed agent information
- `dirs` - Show agent search directories

## Interactive Mode Commands

When running in interactive mode (`amplifier` or `amplifier run --mode chat`), these special commands are available:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/status` | Show session status |
| `/config` | Show current configuration |
| `/mode [NAME]` | Set or toggle a mode |
| `/modes` | List available modes |
| `/tools` | List available tools |
| `/agents` | List available agents |
| `/skills` | List available skills |
| `/skill NAME` | Load a skill |
| `/allowed-dirs` | Manage allowed write directories |
| `/denied-dirs` | Manage denied write directories |
| `/save` | Save conversation transcript |
| `/clear` | Clear conversation context |
| `/rename` | Rename current session |
| `/fork [turn]` | Fork session at turn N |
| `exit`, `quit` | Exit interactive mode |

**Examples:**

```bash
amplifier
amplifier> /status
amplifier> /mode brainstorm
amplifier> exit
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
| 1 | Error (configuration, API, session, or general failure) |

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

# Add a provider to your project
amplifier provider add openai
```

### Agent Invocation

```bash
# In interactive mode
amplifier
amplifier> @explorer What files handle authentication?

# Or via run command (requires task tool in bundle)
amplifier run "@explorer What files handle authentication?"
```
