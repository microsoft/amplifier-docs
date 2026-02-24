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
amplifier continue "What about error handling?"

# Show full history before continuing
amplifier continue --full-history

# Replay the conversation
amplifier continue --replay --replay-speed 3.0
```

## Session Management

### `session list`

List all sessions.

```bash
amplifier session list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--all, -a` | Show all sessions (default: last 20) |
| `--limit, -n` | Number of sessions to show |
| `--bundle, -b` | Filter by bundle |
| `--project, -p` | Filter by project directory |

### `session show`

Show detailed session information.

```bash
amplifier session show SESSION_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--no-history` | Skip conversation history |
| `--full-history` | Show all messages (default: last 10) |
| `--show-thinking` | Show thinking blocks |
| `--show-events` | Show session events |

### `session resume`

Resume a specific session.

```bash
amplifier session resume SESSION_ID [PROMPT]
```

### `session delete`

Delete one or more sessions.

```bash
amplifier session delete SESSION_ID [SESSION_ID...] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--all` | Delete all sessions |
| `--older-than DAYS` | Delete sessions older than N days |
| `--bundle BUNDLE` | Delete sessions from specific bundle |

### `session history`

Show conversation history for a session.

```bash
amplifier session history SESSION_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--full` | Show all messages (default: last 10) |
| `--show-thinking` | Show thinking blocks |
| `--format FORMAT` | Output format: text, json (default: text) |

### `session search`

Search sessions by content or metadata.

```bash
amplifier session search QUERY [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--bundle, -b` | Filter by bundle |
| `--project, -p` | Filter by project directory |
| `--limit, -n` | Number of results (default: 10) |

## Agent Management

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

## Bundle Management

### `bundle list`

List installed bundles.

```bash
amplifier bundle list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--all, -a` | Show all bundles including inactive |

### `bundle show`

Show bundle details.

```bash
amplifier bundle show BUNDLE_NAME
```

### `bundle install`

Install a bundle.

```bash
amplifier bundle install SOURCE [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--name, -n` | Custom name for the bundle |
| `--force, -f` | Force reinstall if already exists |

**Examples:**

```bash
# Install from git
amplifier bundle install git+https://github.com/org/bundle@main

# Install with custom name
amplifier bundle install ./local-bundle --name my-bundle
```

### `bundle update`

Update bundle(s) to latest version.

```bash
amplifier bundle update [BUNDLE_NAME] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--all, -a` | Update all bundles |
| `--check-only, -c` | Check for updates without installing |

### `bundle remove`

Remove a bundle.

```bash
amplifier bundle remove BUNDLE_NAME
```

### `bundle default`

Set or show the default bundle.

```bash
amplifier bundle default [BUNDLE_NAME]
```

### `bundle clone`

Clone a bundle to local directory for customization.

```bash
amplifier bundle clone BUNDLE_NAME [DESTINATION]
```

## Provider Management

### `provider list`

List configured providers.

```bash
amplifier provider list
```

### `provider show`

Show provider details.

```bash
amplifier provider show PROVIDER_NAME
```

### `provider use`

Set the active provider.

```bash
amplifier provider use PROVIDER_NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--model, -m` | Set default model |
| `--api-key, -k` | Set API key |

**Examples:**

```bash
# Switch to Anthropic
amplifier provider use anthropic

# Switch with model selection
amplifier provider use openai --model gpt-5.1

# Set API key
amplifier provider use anthropic --api-key sk-ant-...
```

### `provider install`

Install a provider module.

```bash
amplifier provider install PROVIDER_NAME
```

## Module Management

### `module list`

List installed modules.

```bash
amplifier module list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--type, -t` | Filter by type (provider, tool, hook) |

### `module show`

Show module details.

```bash
amplifier module show MODULE_NAME
```

### `module install`

Install a module.

```bash
amplifier module install SOURCE [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--name, -n` | Custom name for the module |
| `--force, -f` | Force reinstall if already exists |

### `module update`

Update module(s) to latest version.

```bash
amplifier module update [MODULE_NAME] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--all, -a` | Update all modules |

### `module remove`

Remove a module.

```bash
amplifier module remove MODULE_NAME
```

## Source Management

### `source list`

List configured sources.

```bash
amplifier source list
```

### `source add`

Add a source repository.

```bash
amplifier source add NAME URL [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--priority, -p` | Source priority (higher = checked first) |

### `source remove`

Remove a source.

```bash
amplifier source remove NAME
```

### `source update`

Update source(s) to fetch latest metadata.

```bash
amplifier source update [NAME] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--all, -a` | Update all sources |

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

## Configuration Management

### `init`

Initialize Amplifier configuration.

```bash
amplifier init [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--provider, -p` | Provider to configure (anthropic, openai, azure-openai, ollama) |
| `--api-key, -k` | API key for the provider |
| `--force, -f` | Force reconfiguration |

**Examples:**

```bash
# Interactive initialization
amplifier init

# Non-interactive with provider
amplifier init --provider anthropic --api-key sk-ant-...

# Reinitialize
amplifier init --force
```

### `reset`

Reset Amplifier configuration and data.

```bash
amplifier reset [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--sessions` | Delete all sessions |
| `--config` | Reset configuration to defaults |
| `--modules` | Remove all installed modules |
| `--all` | Reset everything |
| `--force, -f` | Skip confirmation |

### `notify`

Manage notification settings.

```bash
amplifier notify [COMMAND]
```

Subcommands:
- `enable` - Enable notifications
- `disable` - Disable notifications
- `status` - Show notification status

## File Access Control

### `allowed-dirs`

Manage directories allowed for file operations.

```bash
amplifier allowed-dirs [COMMAND]
```

Subcommands:
- `list` - List allowed directories
- `add PATH` - Add directory to allowed list
- `remove PATH` - Remove directory from allowed list

### `denied-dirs`

Manage directories denied for file operations.

```bash
amplifier denied-dirs [COMMAND]
```

Subcommands:
- `list` - List denied directories
- `add PATH` - Add directory to denied list
- `remove PATH` - Remove directory from denied list

## Maintenance

### `version`

Show version information.

```bash
amplifier version [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--check` | Check for updates |

### `update`

Update Amplifier to the latest version.

```bash
amplifier update [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--check-only, -c` | Check for updates without installing |
| `--force, -f` | Force update even if already up to date |

## Interactive Mode

When run without arguments, Amplifier starts in interactive mode:

```bash
amplifier
```

### Special Commands in Interactive Mode

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/config` | Show current configuration |
| `/tools` | List available tools |
| `/agents` | List available agents |
| `/history` | Show conversation history |
| `/fork` | Fork current session |
| `/exit` | Exit interactive mode |
| `@agent` | Invoke a specific agent |

**Examples:**

```
amplifier> @explorer What is the architecture of this project?
amplifier> /tools
amplifier> /config
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `OLLAMA_HOST` | Ollama server URL |
| `AMPLIFIER_CONFIG_DIR` | Override config directory (default: ~/.amplifier) |
| `AMPLIFIER_CACHE_DIR` | Override cache directory |
| `AMPLIFIER_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Shell Completion

Install shell completion for better CLI experience:

```bash
# Install for your shell
amplifier --install-completion

# Or specify shell explicitly
amplifier --install-completion bash
amplifier --install-completion zsh
amplifier --install-completion fish
```

After installation, restart your shell or source the config file.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Network error |
| 4 | API error |
| 130 | Interrupted (Ctrl+C) |

## Next Steps

- [Agents](agents.md) - Learn about specialized agents
- [Configuration](configuration.md) - Advanced configuration options
- [Bundles](../developer_guides/foundation/amplifier_foundation/bundle_system.md) - Create custom bundles
