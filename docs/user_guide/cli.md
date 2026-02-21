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
# Resume with a new message
amplifier continue "Now add error handling"

# Just resume interactively
amplifier continue

# Resume with full history
amplifier continue --full-history

# Replay conversation before resuming
amplifier continue --replay --replay-speed 3.0
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

If `SESSION_ID` is provided (can be partial), resumes that session directly. Otherwise, shows recent sessions with numbered selection.

**Examples:**

```bash
# Interactive session picker
amplifier resume

# Resume by partial ID
amplifier resume abc123
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
| `/clear` | Clear conversation context |
| `/config` | Show current configuration |
| `/save` | Save conversation transcript |
| `/mode` | Set or toggle a mode (e.g., /mode plan) |
| `/modes` | List available modes |
| `/rename` | Rename current session |
| `/fork` | Fork session at turn N: /fork [turn] |
| `/allowed-dirs` | Manage allowed write directories |
| `/denied-dirs` | Manage denied write directories |

Type `exit` or `quit` (or press Ctrl-D) to exit interactive mode.

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
| `--limit, -n` | Number of sessions to show (default: 20) |
| `--all-projects` | Show sessions from all projects |
| `--project` | Show sessions for specific project path |
| `--tree, -t` | Show lineage tree for a session |

### `session show`

Show session details.

```bash
amplifier session show SESSION_ID
```

| Option | Description |
|--------|-------------|
| `--detailed, -d` | Show detailed transcript metadata |

### `session resume`

Resume a specific session.

```bash
amplifier session resume SESSION_ID
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

Fork a session from a specific turn.

```bash
amplifier session fork SESSION_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--at-turn, -t` | Turn number to fork at (default: interactive selection) |
| `--name, -n` | Custom name/ID for forked session |
| `--resume, -r` | Resume forked session immediately |
| `--no-events` | Skip copying events.jsonl |

**Examples:**

```bash
# Interactive turn selection
amplifier session fork abc123

# Fork at specific turn
amplifier session fork abc123 --at-turn 3

# Fork with custom name and resume immediately
amplifier session fork abc123 --at-turn 3 --name "jwt-approach" --resume
```

### `session delete`

Delete a session.

```bash
amplifier session delete SESSION_ID
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

## Bundle Commands

### `bundle list`

List available bundles.

```bash
amplifier bundle list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--all, -a` | Show all bundles including dependencies and nested bundles |

### `bundle use`

Set the active bundle.

```bash
amplifier bundle use BUNDLE_NAME [--local|--project|--global]
```

### `bundle show`

Show bundle details.

```bash
amplifier bundle show BUNDLE_NAME
```

| Option | Description |
|--------|-------------|
| `--detailed, -d` | Show detailed configuration |

### `bundle current`

Show the current active bundle.

```bash
amplifier bundle current
```

### `bundle add`

Register a bundle from a URI.

```bash
amplifier bundle add URI [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--name, -n` | Custom name for the bundle (default: from bundle metadata) |
| `--app` | Add as app bundle (automatically composed with all sessions) |

**Examples:**

```bash
# Auto-derives name from bundle metadata
amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-recipes@main

# Use custom alias
amplifier bundle add git+https://github.com/org/repo@main --name my-recipes

# Local bundle
amplifier bundle add file:///path/to/bundle

# Add as app bundle (always active)
amplifier bundle add git+https://github.com/org/team-bundle@main --app
```

### `bundle remove`

Unregister a bundle.

```bash
amplifier bundle remove BUNDLE_NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--app` | Remove an app bundle by name or URI |

### `bundle clear`

Reset to default (foundation) bundle.

```bash
amplifier bundle clear [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Clear local settings |
| `--project` | Clear project settings |
| `--global` | Clear global settings |
| `--all` | Clear settings from all scopes |

### `bundle update`

Check for and apply updates to bundle sources.

```bash
amplifier bundle update [BUNDLE_NAME] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--all` | Check/update all discovered bundles |
| `--check` | Only check for updates, don't apply |
| `--yes, -y` | Auto-confirm update without prompting |
| `--source` | Update only a specific source URI |

**Examples:**

```bash
# Check and update active bundle
amplifier bundle update

# Only check, don't update
amplifier bundle update --check

# Check specific bundle
amplifier bundle update foundation

# Update all bundles without prompting
amplifier bundle update --all -y
```

## Provider Commands

### `provider list`

List available providers.

```bash
amplifier provider list
```

### `provider use`

Configure a provider.

```bash
amplifier provider use PROVIDER_NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--model` | Model name (Anthropic/OpenAI/Ollama) |
| `--deployment` | Deployment name (Azure OpenAI) |
| `--endpoint` | Azure endpoint URL |
| `--use-azure-cli` | Use Azure CLI auth (Azure OpenAI) |
| `--local` | Configure locally (just you) |
| `--project` | Configure for project (team) |
| `--global` | Configure globally (all projects) |
| `--yes, -y` | Non-interactive mode: use CLI values and env vars, skip prompts |

**Examples:**

```bash
amplifier provider use anthropic --model claude-opus-4-6 --local
amplifier provider use openai --model gpt-5.1 --project
amplifier provider use azure-openai --endpoint https://... --deployment gpt-5.1-codex --use-azure-cli
amplifier provider use ollama --model llama3
```

### `provider current`

Show the current provider.

```bash
amplifier provider current
```

### `provider reset`

Reset to default provider.

```bash
amplifier provider reset [--local|--project|--global]
```

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

# Silent install (CI/CD)
amplifier provider install -q
```

### `provider models`

List available models for a provider.

```bash
amplifier provider models [PROVIDER_ID]
```

If `PROVIDER_ID` is omitted, uses the currently active provider.

**Examples:**

```bash
amplifier provider models anthropic
amplifier provider models openai
amplifier provider models  # uses current provider
```

## Module Commands

### `module list`

List installed modules.

```bash
amplifier module list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--type, -t` | Filter by type (all, orchestrator, provider, tool, agent, context, hook) |

### `module add`

Add a module.

```bash
amplifier module add MODULE_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--source, -s` | Source URI (git+https://... or file path) |
| `--local` | Add locally (just you) |
| `--project` | Add for project (team) |
| `--global` | Add globally (all projects) |

### `module remove`

Remove a module.

```bash
amplifier module remove MODULE_ID [--local|--project|--global]
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

### `module update`

Update module cache.

```bash
amplifier module update [MODULE_ID] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--check-only` | Check for updates without installing |
| `--mutable-only` | Only update mutable refs (branches, not tags/SHAs) |

### `module validate`

Validate a module against its contract.

```bash
amplifier module validate MODULE_PATH [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--type, -t` | Module type: provider, tool, hook, orchestrator, context (auto-detected from name) |
| `--output, -o` | Output format: `human`, `json` |
| `--verbose, -v` | Show additional details and actionable tips for failed checks |
| `--behavioral, -b` | Run behavioral tests in addition to structural validation |

### `module override set`

Set a module source or config override.

```bash
amplifier module override set MODULE_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--source, -s` | Source path or URI for the module |
| `--config, -c` | Config key=value pair (can be repeated) |
| `--scope` | Where to save: local, project, global (default: project) |

**Examples:**

```bash
# Override source to local path
amplifier module override set tool-task --source /path/to/local/module

# Override config values
amplifier module override set tool-task -c inherit_context=recent -c timeout=30
```

### `module override remove`

Remove a module override.

```bash
amplifier module override remove MODULE_ID [--scope SCOPE]
```

### `module override list`

List all module overrides.

```bash
amplifier module override list [--scope SCOPE]
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
amplifier source add IDENTIFIER SOURCE_URI [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--local` | Store in local settings |
| `--project` | Store in project settings |
| `--global` | Store in user settings |
| `--module` | Force treating as module (skip auto-detect) |
| `--bundle` | Force treating as bundle (skip auto-detect) |

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
| `--module` | Force treating as module (skip auto-detect) |
| `--bundle` | Force treating as bundle (skip auto-detect) |

### `source show`

Show source override details.

```bash
amplifier source show MODULE_ID
```

## Tool Commands

### `tool list`

List available tools.

```bash
amplifier tool list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--modules, -m` | Show module names instead of mounted tools |
| `--bundle, -b` | Bundle to use (default: active bundle) |
| `--output, -o` | Output format: `table`, `json` |

### `tool info`

Show tool details.

```bash
amplifier tool info TOOL_NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--bundle, -b` | Bundle to use (default: active bundle) |
| `--output, -o` | Output format: `text`, `json` |
| `--module, -m` | Look up by module name instead of mounted tool name |

### `tool invoke`

Directly invoke a tool (for testing).

```bash
amplifier tool invoke TOOL_NAME KEY=VALUE... [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--bundle, -b` | Bundle to use (default: active bundle) |
| `--output, -o` | Output format: `text`, `json` |

## Agent Commands

### `agents list`

List available agents.

```bash
amplifier agents list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--bundle, -b` | Bundle to list agents from |

### `agents show`

Show agent details.

```bash
amplifier agents show AGENT_NAME
```

### `agents dirs`

Show agent search directories.

```bash
amplifier agents dirs
```

## Notify Commands

### `notify status`

Show current notification settings.

```bash
amplifier notify status
```

### `notify desktop`

Configure desktop/terminal notifications.

```bash
amplifier notify desktop [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--enable/--disable` | Enable or disable desktop notifications |
| `--show-device/--no-show-device` | Show device/hostname in notification |
| `--show-project/--no-show-project` | Show project name in notification |
| `--show-preview/--no-show-preview` | Show message preview in notification |
| `--preview-length` | Max characters for preview (default: 100) |
| `--local` | Apply to local scope |
| `--project` | Apply to project scope |
| `--global` | Apply to global scope (default) |

### `notify ntfy`

Configure ntfy.sh push notifications.

```bash
amplifier notify ntfy [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--enable/--disable` | Enable or disable ntfy push notifications |
| `--server` | ntfy server URL (default: https://ntfy.sh) |
| `--local` | Apply to local scope |
| `--project` | Apply to project scope |
| `--global` | Apply to global scope (default) |

When enabling for the first time, you will be prompted to enter a topic securely.

### `notify reset`

Clear notification settings.

```bash
amplifier notify reset [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--desktop` | Reset only desktop settings |
| `--ntfy` | Reset only ntfy settings |
| `--all` | Reset all notification settings |
| `--local` | Reset at local scope |
| `--project` | Reset at project scope |
| `--global` | Reset at global scope (default) |

## Allowed/Denied Directory Commands

### `allowed-dirs`

Manage directories the AI can write to.

```bash
amplifier allowed-dirs list [--local|--project|--global|--session]
amplifier allowed-dirs add PATH [--local|--project|--global]
amplifier allowed-dirs remove PATH [--local|--project|--global]
```

### `denied-dirs`

Manage directories the AI is blocked from writing to.

```bash
amplifier denied-dirs list [--local|--project|--global|--session]
amplifier denied-dirs add PATH [--local|--project|--global]
amplifier denied-dirs remove PATH [--local|--project|--global]
```

## Other Commands

### `init`

Run first-time setup wizard.

```bash
amplifier init [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--yes, -y` | Non-interactive mode: use env vars and defaults, skip prompts |

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

Show Amplifier version information.

```bash
amplifier version [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--verbose, -v` | Show detailed version information including install type |

### `reset`

Reinstall Amplifier while preserving your data.

```bash
amplifier reset [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--preserve LIST` | Comma-separated categories to preserve (e.g., projects,settings,keys) |
| `--remove LIST` | Comma-separated categories to remove (e.g., cache,registry) |
| `--full` | Remove everything including projects |
| `-y, --yes` | Skip interactive prompt |
| `--dry-run` | Preview what would be removed without making changes |
| `--no-install` | Uninstall only, don't reinstall |

**Categories:** projects, settings, keys, cache, registry, other

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

- [Sessions](sessions.md) - Session management
- [Agents](agents.md) - Agent delegation
