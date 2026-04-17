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
amplifier continue "Now add tests"

# Interactive continuation
amplifier continue

# With full history
amplifier continue --full-history "Continue from here"
```

### `resume`

Interactively select and resume a session.

```bash
amplifier resume [SESSION_ID]
```

| Option | Description |
|--------|-------------|
| `--limit, -n` | Number of sessions per page (default: 10) |
| `--force-bundle, -B` | Force a different bundle for this session (experimental) |

**Examples:**

```bash
# Interactive session picker
amplifier resume

# Resume by partial session ID
amplifier resume auth
```

## Session Management

### `session list`

List all sessions.

```bash
amplifier session list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--limit, -n` | Number of sessions to show (default: 20) |
| `--all-projects` | Show sessions from all projects |
| `--project` | Filter by project path |
| `--tree, -t` | Show lineage tree for a session |

### `session show`

Show session details.

```bash
amplifier session show SESSION_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--detailed, -d` | Show detailed transcript metadata |

### `session resume`

Resume a specific session.

```bash
amplifier session resume SESSION_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--force-bundle, -B` | Force a different bundle for this session (experimental) |
| `--no-history` | Skip displaying conversation history |
| `--full-history` | Show all messages (default: last 10) |
| `--replay` | Replay conversation with timing simulation |
| `--replay-speed, -s` | Replay speed multiplier (default: 2.0) |
| `--show-thinking` | Show thinking blocks in history |

### `session fork`

Fork a session at a specific turn.

```bash
amplifier session fork SESSION_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--at-turn, -t` | Turn number to fork at (default: latest) |
| `--name, -n` | Custom name/ID for forked session |
| `--resume, -r` | Resume forked session immediately |
| `--no-events` | Skip copying events.jsonl |

### `session delete`

Delete a session.

```bash
amplifier session delete SESSION_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--force, -f` | Skip confirmation |

### `session cleanup`

Clean up old sessions.

```bash
amplifier session cleanup [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--days, -d` | Delete sessions older than N days (default: 30) |
| `--force, -f` | Skip confirmation |

## Bundle Management

### `bundle list`

List available bundles.

```bash
amplifier bundle list
```

### `bundle show`

Show bundle details.

```bash
amplifier bundle show BUNDLE_NAME
```

### `bundle use`

Set active bundle.

```bash
amplifier bundle use BUNDLE_NAME
```

### `bundle current`

Show currently active bundle.

```bash
amplifier bundle current
```

### `bundle add`

Add a bundle from a source.

```bash
amplifier bundle add NAME SOURCE
```

### `bundle remove`

Remove a bundle.

```bash
amplifier bundle remove NAME
```

### `bundle update`

Update bundle sources.

```bash
amplifier bundle update [BUNDLE_NAME]
```

### `bundle clear`

Clear active bundle.

```bash
amplifier bundle clear
```

## Provider Management

### `provider list`

List configured providers.

```bash
amplifier provider list
```

### `provider add`

Add a new provider.

```bash
amplifier provider add PROVIDER [OPTIONS]
```

### `provider remove`

Remove a provider.

```bash
amplifier provider remove PROVIDER
```

### `provider edit`

Edit provider configuration.

```bash
amplifier provider edit PROVIDER
```

### `provider test`

Test provider connection.

```bash
amplifier provider test PROVIDER
```

### `provider models`

List available models for a provider.

```bash
amplifier provider models PROVIDER
```

### `provider manage`

Interactive provider management.

```bash
amplifier provider manage
```

### `provider install`

Install a provider from source.

```bash
amplifier provider install SOURCE
```

## Module Management

### `module list`

List installed modules.

```bash
amplifier module list [TYPE]
```

| Type | Description |
|------|-------------|
| `provider` | LLM providers |
| `tool` | Agent tools |
| `orchestrator` | Execution loops |
| `context` | Memory management |
| `hook` | Lifecycle hooks |

### `module show`

Show module details.

```bash
amplifier module show MODULE_NAME
```

### `module add`

Add a module from source.

```bash
amplifier module add SOURCE
```

### `module remove`

Remove a module.

```bash
amplifier module remove MODULE_NAME
```

### `module current`

Show currently active modules.

```bash
amplifier module current
```

### `module update`

Update modules.

```bash
amplifier module update [MODULE_NAME]
```

### `module validate`

Validate a module.

```bash
amplifier module validate PATH
```

### `module override`

Override module source.

```bash
amplifier module override MODULE SOURCE
```

## Source Management

### `source list`

List module source overrides.

```bash
amplifier source list
```

### `source add`

Add a source override.

```bash
amplifier source add MODULE SOURCE
```

### `source remove`

Remove a source override.

```bash
amplifier source remove MODULE
```

### `source show`

Show override details.

```bash
amplifier source show MODULE
```

## Routing Management

### `routing list`

List available routing matrices.

```bash
amplifier routing list
```

### `routing use`

Set active routing matrix.

```bash
amplifier routing use MATRIX_NAME
```

### `routing show`

Show routing matrix details.

```bash
amplifier routing show MATRIX_NAME
```

### `routing manage`

Interactive routing management.

```bash
amplifier routing manage
```

### `routing create`

Create a new routing matrix.

```bash
amplifier routing create NAME
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

### `agents dirs`

Show agent search directories.

```bash
amplifier agents dirs
```

## Directory Management

### `allowed-dirs list`

List allowed write directories.

```bash
amplifier allowed-dirs list
```

### `allowed-dirs add`

Add allowed write directory.

```bash
amplifier allowed-dirs add PATH
```

### `allowed-dirs remove`

Remove allowed write directory.

```bash
amplifier allowed-dirs remove PATH
```

### `denied-dirs list`

List denied write directories.

```bash
amplifier denied-dirs list
```

### `denied-dirs add`

Add denied write directory.

```bash
amplifier denied-dirs add PATH
```

### `denied-dirs remove`

Remove denied write directory.

```bash
amplifier denied-dirs remove PATH
```

## Tool Management

### `tool list`

List available tools.

```bash
amplifier tool list
```

### `tool info`

Show tool information.

```bash
amplifier tool info TOOL_NAME
```

### `tool invoke`

Invoke a tool directly.

```bash
amplifier tool invoke TOOL_NAME [PARAMS]
```

## Notification Management

### `notify status`

Show notification configuration.

```bash
amplifier notify status
```

### `notify desktop`

Configure desktop notifications.

```bash
amplifier notify desktop [on|off]
```

### `notify ntfy`

Configure ntfy.sh notifications.

```bash
amplifier notify ntfy [OPTIONS]
```

### `notify reset`

Reset notification configuration.

```bash
amplifier notify reset
```

## System Commands

### `init`

Run first-time initialization wizard.

```bash
amplifier init
```

### `update`

Update Amplifier and modules.

```bash
amplifier update [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--check-only` | Check for updates without installing |
| `--yes, -y` | Skip confirmations |
| `--force` | Force update even if already latest |
| `--verbose, -v` | Show detailed output |

### `version`

Show version information.

```bash
amplifier version
```

### `reset`

Reset Amplifier configuration.

```bash
amplifier reset [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--preserve` | Categories to preserve during reset |
| `--remove` | Categories to remove during reset |
| `--full` | Full reset (remove all categories) |
| `-y, --yes` | Skip confirmation prompt |
| `--dry-run` | Preview what would be reset |
| `--no-install` | Skip reinstalling after reset |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `AMPLIFIER_HOME` | Override home directory (default: `~/.amplifier`) |
| `AMPLIFIER_AGENT_<NAME>` | Override agent path for testing (uppercase, dashes become underscores) |

## Shell Completion

Install shell completion for better CLI experience:

```bash
# Auto-detect shell and install
amplifier --install-completion
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error or failure |
