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
| `--install-completion` | Install shell completion |
| `--show-completion` | Show shell completion script |

## Core Commands

### `run`

Execute a single prompt.

```bash
amplifier run [OPTIONS] PROMPT
```

| Option | Description |
|--------|-------------|
| `--bundle` | Bundle to use |
| `--provider, -p` | LLM provider (anthropic, openai, etc.) |
| `--model, -m` | Specific model to use |
| `--max-tokens` | Maximum response tokens |
| `--output-format, -o` | Output format: `text`, `json`, `json-trace` |
| `--resume, -r` | Resume session by ID |
| `--no-tools` | Disable tool use |

**Examples:**

```bash
# Basic usage
amplifier run "Explain this code"

# With options
amplifier run --bundle dev --model claude-opus-4-1 "Complex task"

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

**Examples:**

```bash
# Resume with a new message
amplifier continue "Now add error handling"

# Just resume interactively
amplifier continue
```

### Interactive Mode

Start without a command for interactive chat:

```bash
amplifier
```

#### Interactive Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/tools` | List available tools |
| `/agents` | List available agents |
| `/status` | Show session status |
| `/clear` | Clear conversation history |
| `/think` | Enable planning mode |
| `/quit`, `/exit` | Exit interactive mode |

#### Using Agents

```bash
amplifier> @explorer Analyze this codebase
amplifier> @bug-hunter Find issues in main.py
```

#### Using Mentions

Reference files or context:

```bash
amplifier> Review @src/main.py for issues
amplifier> @project:context/standards.md Apply these standards
```

## Session Commands

### `session list`

List recent sessions.

```bash
amplifier session list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--limit, -n` | Number of sessions to show (default: 10) |
| `--all` | Show all sessions |

### `session show`

Show session details.

```bash
amplifier session show SESSION_ID
```

### `session resume`

Resume a specific session.

```bash
amplifier session resume SESSION_ID [PROMPT]
```

### `session delete`

Delete a session.

```bash
amplifier session delete SESSION_ID
```

### `session cleanup`

Clean up old sessions.

```bash
amplifier session cleanup [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--days, -d` | Delete sessions older than N days (default: 30) |

## Bundle Commands

### `bundle list`

List available bundles.

```bash
amplifier bundle list
```

### `bundle use`

Set the active bundle.

```bash
amplifier bundle use BUNDLE_NAME [--local|--project|--global]
```

### `bundle show`

Show bundle details.

```bash
amplifier bundle show [BUNDLE_NAME]
```

### `bundle current`

Show the current active bundle.

```bash
amplifier bundle current
```

### `bundle add`

Register a bundle from a git URL.

```bash
amplifier bundle add GIT_URL [--name ALIAS]
```

### `bundle remove`

Unregister a bundle.

```bash
amplifier bundle remove BUNDLE_NAME
```

### `bundle clear`

Reset to default (foundation) bundle.

```bash
amplifier bundle clear
```

## Provider Commands

### `provider list`

List available providers.

```bash
amplifier provider list
```

### `provider use`

Set the active provider.

```bash
amplifier provider use PROVIDER_NAME [--local|--project|--global]
```

### `provider current`

Show the current provider.

```bash
amplifier provider current
```

### `provider reset`

Reset to default provider.

```bash
amplifier provider reset [--scope SCOPE]
```

## Module Commands

### `module list`

List configured modules.

```bash
amplifier module list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--type, -t` | Filter by type (provider, tool, hook, etc.) |

### `module add`

Add a module.

```bash
amplifier module add MODULE_NAME [--local|--project|--global]
```

### `module remove`

Remove a module.

```bash
amplifier module remove MODULE_NAME [--scope SCOPE]
```

### `module current`

Show current module configuration.

```bash
amplifier module current
```

### `module show`

Show module details.

```bash
amplifier module show MODULE_NAME
```

### `module check-updates`

Check for module updates.

```bash
amplifier module check-updates
```

### `module refresh`

Refresh module cache.

```bash
amplifier module refresh [MODULE_NAME] [--mutable-only]
```

## Collection Commands

### `collection list`

List installed collections.

```bash
amplifier collection list
```

### `collection add`

Add a collection.

```bash
amplifier collection add COLLECTION_NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--source, -s` | Collection source (git URL) |

### `collection remove`

Remove a collection.

```bash
amplifier collection remove COLLECTION_NAME
```

### `collection show`

Show collection details.

```bash
amplifier collection show COLLECTION_NAME
```

### `collection refresh`

Refresh collection cache.

```bash
amplifier collection refresh
```

## Source Commands

### `source list`

List module source overrides.

```bash
amplifier source list
```

### `source add`

Add a source override (for local development).

```bash
amplifier source add ID URI [--local|--project|--global]
```

### `source remove`

Remove a source override.

```bash
amplifier source remove ID [--scope SCOPE]
```

### `source show`

Show source override details.

```bash
amplifier source show ID
```

## Tool Commands

### `tool list`

List available tools.

```bash
amplifier tool list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--modules` | Show module names (fast) |
| `--bundle BUNDLE` | Specify bundle |
| `--output json` | JSON output |

### `tool info`

Show tool details.

```bash
amplifier tool info TOOL_NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--module MODULE` | Show module info (fast) |

### `tool invoke`

Directly invoke a tool (for testing).

```bash
amplifier tool invoke TOOL_NAME KEY=VALUE...
```

## Agent Commands

### `agents list`

List available agents.

```bash
amplifier agents list
```

### `agents show`

Show agent details.

```bash
amplifier agents show AGENT_NAME
```

## Notify Commands

### `notify status`

Show current notification settings.

```bash
amplifier notify status
```

### `notify desktop`

Enable or disable desktop/terminal notifications.

```bash
amplifier notify desktop --enable [--scope SCOPE]
amplifier notify desktop --disable [--scope SCOPE]
```

### `notify ntfy`

Enable or disable ntfy.sh push notifications.

```bash
amplifier notify ntfy --enable --topic TOPIC [--scope SCOPE]
amplifier notify ntfy --disable [--scope SCOPE]
```

### `notify reset`

Clear all notification settings.

```bash
amplifier notify reset --all [--scope SCOPE]
```

## Other Commands

### `init`

Run first-time setup wizard.

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
| `--force` | Force update all sources (skip update detection) |
| `-y, --yes` | Skip confirmation prompts |
| `--verbose` | Show detailed multi-line output per source |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version |
| `AZURE_USE_DEFAULT_CREDENTIAL` | Use Azure DefaultAzureCredential |

## Configuration Files

| File | Scope | Purpose |
|------|-------|---------|
| `~/.amplifier/settings.yaml` | User | Global user settings |
| `.amplifier/settings.yaml` | Project | Project settings (committed) |
| `.amplifier/settings.local.yaml` | Local | Machine-local settings (gitignored) |

## See Also

- [Profiles](profiles.md) - Profile configuration
- [Sessions](sessions.md) - Session management
- [Agents](agents.md) - Agent delegation