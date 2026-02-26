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
# Interactive selection
amplifier resume

# Resume specific session (partial ID)
amplifier resume abc123
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
| `--all-projects` | Show sessions from all projects |
| `--project PATH` | Show sessions for specific project path |
| `--tree, -t SESSION_ID` | Show lineage tree for a session |

**Examples:**

```bash
# List recent sessions
amplifier session list

# Show lineage tree
amplifier session list --tree abc123
```

### `session show`

Show detailed session information.

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

### `session delete`

Delete a session.

```bash
amplifier session delete SESSION_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--force, -f` | Skip confirmation |

### `session fork`

Fork a session at a specific turn.

```bash
amplifier session fork SESSION_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--at-turn, -t TURN` | Turn number to fork at (default: latest) |
| `--name, -n NAME` | Custom name/ID for forked session |
| `--resume, -r` | Resume forked session immediately |
| `--no-events` | Skip copying events.jsonl |

**Examples:**

```bash
# Interactive turn selection
amplifier session fork abc123

# Fork at specific turn
amplifier session fork abc123 --at-turn 3

# Fork with custom name
amplifier session fork abc123 --at-turn 3 --name "jwt-approach"

# Fork and resume
amplifier session fork abc123 --at-turn 3 --resume
```

### `session cleanup`

Delete sessions older than N days.

```bash
amplifier session cleanup [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--days, -d DAYS` | Delete sessions older than N days (default: 30) |
| `--force, -f` | Skip confirmation |

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
amplifier bundle use BUNDLE_NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Configure locally (just you) |
| `--project` | Configure for project (team) |
| `--global` | Configure globally (all projects) |

### `bundle clear`

Clear the active bundle selection.

```bash
amplifier bundle clear [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Clear local configuration |
| `--project` | Clear project configuration |
| `--global` | Clear global configuration |

### `bundle current`

Show currently active bundle.

```bash
amplifier bundle current
```

### `bundle add`

Add a bundle from a source URI.

```bash
amplifier bundle add SOURCE_URI [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--name, -n NAME` | Bundle name (auto-detected if not provided) |
| `--app` | Register as an app bundle (always composed onto sessions) |
| `--local` | Add locally (just you) |
| `--project` | Add for project (team) |
| `--global` | Add globally (all projects) |

### `bundle remove`

Remove a previously added bundle.

```bash
amplifier bundle remove BUNDLE_NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Remove from local configuration |
| `--project` | Remove from project configuration |
| `--global` | Remove from global configuration |

### `bundle update`

Update bundles from their sources.

```bash
amplifier bundle update [BUNDLE_NAME] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--all` | Update all bundles |
| `--force, -f` | Force update even if no changes detected |

## Provider Management

### `provider install`

Install provider modules.

```bash
amplifier provider install [PROVIDER_IDS...] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--all` | Install all known providers |
| `--quiet, -q` | Suppress progress output (for CI/CD) |
| `--force` | Reinstall even if already installed |

**Examples:**

```bash
# Install all providers
amplifier provider install

# Install specific providers
amplifier provider install anthropic openai

# Silent install for CI/CD
amplifier provider install -q
```

### `provider use`

Configure provider.

```bash
amplifier provider use PROVIDER_NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--model MODEL` | Model name (Anthropic/OpenAI/Ollama) |
| `--deployment NAME` | Deployment name (Azure OpenAI) |
| `--endpoint URL` | Azure endpoint URL |
| `--use-azure-cli` | Use Azure CLI auth (Azure OpenAI) |
| `--local` | Configure locally (just you) |
| `--project` | Configure for project (team) |
| `--global` | Configure globally (all projects) |
| `--yes, -y` | Non-interactive mode (use env vars, skip prompts) |

**Examples:**

```bash
amplifier provider use anthropic --model claude-opus-4-6 --local
amplifier provider use openai --model gpt-5.1 --project
amplifier provider use azure-openai --endpoint https://... --deployment gpt-5.1-codex --use-azure-cli
amplifier provider use ollama --model llama3
```

### `provider current`

Show currently active provider.

```bash
amplifier provider current
```

### `provider list`

List available providers.

```bash
amplifier provider list
```

### `provider reset`

Remove provider override.

```bash
amplifier provider reset [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Reset local configuration |
| `--project` | Reset project configuration |
| `--global` | Reset global configuration |

### `provider models`

List available models for a provider.

```bash
amplifier provider models [PROVIDER_ID]
```

If PROVIDER_ID is omitted, uses the currently active provider.

**Examples:**

```bash
amplifier provider models anthropic
amplifier provider models openai
amplifier provider models  # uses current provider
```

## Module Management

### `module list`

List installed modules.

```bash
amplifier module list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--type, -t TYPE` | Module type to list: `all`, `orchestrator`, `provider`, `tool`, `agent`, `context`, `hook` (default: all) |

### `module show`

Show module details.

```bash
amplifier module show MODULE_NAME
```

### `module add`

Add a module override to settings.

```bash
amplifier module add MODULE_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--source, -s URI` | Source URI (git+https://... or file path) |
| `--local` | Add locally (just you) |
| `--project` | Add for project (team) |
| `--global` | Add globally (all projects) |

### `module remove`

Remove a module override.

```bash
amplifier module remove MODULE_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Remove from local configuration |
| `--project` | Remove from project configuration |
| `--global` | Remove from global configuration |

### `module current`

Show current module configuration.

```bash
amplifier module current
```

### `module update`

Update module from its source.

```bash
amplifier module update MODULE_ID
```

### `module validate`

Validate module structure.

```bash
amplifier module validate MODULE_PATH
```

### `module override`

Manage module source overrides.

```bash
amplifier module override COMMAND [OPTIONS]
```

**Commands:**
- `set MODULE_ID SOURCE_URI` - Set source override
- `remove MODULE_ID` - Remove source override
- `list` - List all source overrides

## Source Management

### `source add`

Add a source override for a module or bundle.

```bash
amplifier source add IDENTIFIER SOURCE_URI [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Store in local settings |
| `--project` | Store in project settings |
| `--global` | Store in user settings |
| `--module` | Force treating as module (skip auto-detect) |
| `--bundle` | Force treating as bundle (skip auto-detect) |

**Examples:**

```bash
# Auto-detect type
amplifier source add provider-anthropic ~/dev/provider-anthropic

# Force bundle type
amplifier source add foundation ~/dev/foundation --bundle
```

### `source remove`

Remove a source override.

```bash
amplifier source remove IDENTIFIER [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Remove from local settings |
| `--project` | Remove from project settings |
| `--global` | Remove from user settings |

### `source list`

List configured source overrides.

```bash
amplifier source list
```

### `source current`

Show current source configuration.

```bash
amplifier source current
```

## Agent Management

### `agents list`

List available agents from bundles.

```bash
amplifier agents list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--bundle, -b BUNDLE` | Bundle to list agents from |

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

## Directory Access Control

### `allowed-dirs`

Manage allowed write directories.

```bash
amplifier allowed-dirs COMMAND [OPTIONS]
```

**Commands:**
- `list` - List allowed write directories
- `add PATH` - Add directory to allowed list (session scope)
- `remove PATH` - Remove directory from allowed list (session scope)

| Option | Description |
|--------|-------------|
| `--local` | Configure locally |
| `--project` | Configure for project |
| `--global` | Configure globally |

### `denied-dirs`

Manage denied write directories.

```bash
amplifier denied-dirs COMMAND [OPTIONS]
```

**Commands:**
- `list` - List denied write directories
- `add PATH` - Add directory to denied list (session scope)
- `remove PATH` - Remove directory from denied list (session scope)

| Option | Description |
|--------|-------------|
| `--local` | Configure locally |
| `--project` | Configure for project |
| `--global` | Configure globally |

## Tool Management

### `tool list`

List available tools.

```bash
amplifier tool list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--bundle BUNDLE` | Bundle to list tools from (default: active bundle) |

### `tool show`

Show tool details.

```bash
amplifier tool show TOOL_NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--bundle BUNDLE` | Bundle context (default: active bundle) |

### `tool invoke`

Invoke a tool from CLI.

```bash
amplifier tool invoke TOOL_NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--args JSON` | Tool arguments as JSON |
| `--bundle BUNDLE` | Bundle context (default: active bundle) |

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

Configure notification settings.

```bash
amplifier notify COMMAND
```

**Commands:**
- `status` - Show current notification settings
- `desktop` - Configure desktop (terminal) notifications
- `ntfy` - Configure push notifications (ntfy.sh)
- `reset` - Reset notification configuration

**Examples:**

```bash
# Check status
amplifier notify status

# Enable desktop notifications
amplifier notify desktop --enable

# Configure ntfy.sh notifications
amplifier notify ntfy --enable
```

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

**Mode Shortcuts:**

Dynamic shortcuts from mode definitions (e.g., `/plan` → `/mode plan on`)

**Key Bindings:**
- `Ctrl-J` - Insert newline (multi-line input)
- `Enter` - Submit prompt
- `Ctrl-D` - Exit
- `Ctrl-C` - Cancel execution (or confirm exit at prompt)
- `Ctrl-R` - Search history

## Environment Variables

### Agent Overrides

Override agent resolution for testing:

```bash
export AMPLIFIER_AGENT_ZEN_ARCHITECT=~/test-zen.md
amplifier run "design system"
```

Format: `AMPLIFIER_AGENT_<NAME>` (uppercase, dashes → underscores)

### Provider Configuration

See individual provider documentation for provider-specific environment variables.

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

Includes full execution trace with tool calls, timing, and metadata:

```json
{
  "status": "success",
  "response": "...",
  "session_id": "...",
  "bundle": "...",
  "model": "...",
  "timestamp": "...",
  "execution_trace": [...],
  "metadata": {...}
}
```

## Exit Codes

| Code | Meaning |
|---------|
| 0 | Success |
| 1 | Error (validation, runtime, etc.) |

## Shell Completion

Install shell completion:

```bash
amplifier --install-completion
```

Auto-detects your shell (bash, zsh, fish) and configures completion.
