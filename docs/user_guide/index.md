---
title: User Guide - Amplifier CLI
description: Complete guide to using the Amplifier CLI application
---

# User Guide: Amplifier CLI

This guide covers everything you need to know to use **amplifier-app-cli**, the command-line application for Amplifier.

!!! info "About This Guide"
    This guide is for **using the Amplifier CLI** (`amplifier` command). If you're:
    
    - **Building applications on amplifier-core** → See [Application Developer Guide](../developer_guides/applications/)
    - **Creating custom modules** → See [Module Developer Guide](../developer/)
    - **Contributing to the foundation** → See [Foundation Developer Guide](../developer_guides/foundation/)

## Topics

<div class="grid">

<div class="card">
<h3><a href="cli/">CLI Reference</a></h3>
<p>Complete reference for all Amplifier commands and options.</p>
</div>

<div class="card">
<h3><a href="bundles/">Bundles</a></h3>
<p>Composable configuration packages for different use cases.</p>
</div>

<div class="card">
<h3><a href="agents/">Agents</a></h3>
<p>Specialized sub-agents for focused tasks.</p>
</div>

<div class="card">
<h3><a href="sessions/">Sessions</a></h3>
<p>Session management, persistence, and resumption.</p>
</div>

</div>

## Quick Reference

### Most Common Commands

```bash
# Run a single command
amplifier run "Your prompt"

# Single command via stdin (useful for scripts/pipelines)
echo "Summarize this spec" | amplifier run

# Runtime overrides (highest priority, override all config levels)
amplifier run -p anthropic "prompt"              # Use specific provider
amplifier run -m claude-sonnet-4-5 "prompt"      # Use specific model
amplifier run --max-tokens 500 "prompt"          # Limit output tokens
amplifier run -p openai -m gpt-5.2 --max-tokens 1000 "prompt"  # Combine flags

# Interactive mode
amplifier

# Resume last session
amplifier continue
amplifier continue "new prompt"          # Resume most recent (single-shot)

# Use specific bundle
amplifier run --bundle my-bundle "Your prompt"

# List sessions
amplifier session list
```

### Configuration Commands

```bash
# Bundles
amplifier bundle list
amplifier bundle use my-bundle
amplifier bundle current
amplifier bundle show <name>
amplifier bundle add <git-url> [--name alias]
amplifier bundle remove <name>
amplifier bundle clear

# Providers
amplifier provider add <name> [--local|--project|--global]
amplifier provider list
amplifier provider remove <name> [--scope]
amplifier provider edit <name>
amplifier provider test [<name>]
amplifier provider manage

# Routing matrix
amplifier routing list
amplifier routing use <name> [--local|--project|--global]
amplifier routing show [<name>]
amplifier routing manage

# Modules
amplifier module add <name> [--local|--project|--global]
amplifier module remove <name> [--scope]
amplifier module current
amplifier module list
amplifier module show <name>
amplifier module refresh [<name>] [--mutable-only]
amplifier module check-updates

# Source management
amplifier source add <id> <uri> [--local|--project|--global]
amplifier source remove <id> [--scope]
amplifier source list
amplifier source show <id>

# Notification settings (requires notify bundle)
amplifier notify status                              # Show current notification settings
amplifier notify desktop --enable [--scope]          # Enable desktop/terminal notifications
amplifier notify desktop --disable [--scope]         # Disable desktop notifications
amplifier notify ntfy --enable --topic <topic>       # Enable ntfy.sh push notifications
amplifier notify ntfy --disable [--scope]            # Disable push notifications
amplifier notify reset --all [--scope]               # Clear all notification settings
```

### Utility Commands

```bash
amplifier init                                     # First-time setup (combined dashboard)
amplifier update [--check-only] [--force] [-y]    # Update Amplifier and modules
amplifier --install-completion                     # Set up tab completion
amplifier --version                                # Show version
amplifier --help                                   # Show help
```

**Update command options**:
- `--check-only`: Check for updates without installing
- `--force`: Force update all sources (skip update detection)
- `-y, --yes`: Skip confirmation prompts
- `--verbose`: Show detailed multi-line output per source (default: concise one-line format)

### Getting Help

```bash
# Command help
amplifier --help
amplifier run --help
```

## Common Workflows

### Quick Task

```bash
# Single command execution
amplifier run "Analyze this code for security issues"
```

### Multi-Turn Conversation

```bash
# Start interactive session
amplifier

# In session:
> Explain the authentication system
> Now add OAuth support
> Write tests for it
> /help  # Show available commands
```

### Resume Previous Work

```bash
# Resume most recent
amplifier continue

# Resume specific session
amplifier session resume abc123

# Continue with new prompt
amplifier continue "Now add documentation"
```

### Using Different Bundles

```bash
# List available bundles
amplifier bundle list

# Use specific bundle for one command
amplifier run --bundle dev-bundle "Your prompt"

# Set default bundle
amplifier bundle use dev-bundle

# Reset to default (foundation)
amplifier bundle clear
```

## Configuration Hierarchy

Amplifier uses a three-scope configuration system:

1. **Global** - System-wide defaults
2. **Project** - Project-specific settings
3. **Local** - Directory-specific overrides

Later levels override earlier ones.

### Setting Scope

Most commands support scope flags:

```bash
# Global scope
amplifier bundle use my-bundle --global

# Project scope
amplifier bundle use my-bundle --project

# Local scope
amplifier bundle use my-bundle --local
```

## Environment Variables

```bash
# API Keys (detected by init)
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export AZURE_OPENAI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
```

## Tips and Tricks

### Shell Completion

```bash
amplifier --install-completion
source ~/.bashrc  # or ~/.zshrc
```

### Slash Commands

In interactive mode, the REPL supports slash commands. Use `amplifier --help` or the in-session help for available commands.

### Unix Piping

```bash
# Pipe input to amplifier
cat file.txt | amplifier run

# Continue session via pipe
echo "new prompt" | amplifier continue
```

## Next Steps

- [CLI Reference](cli.md) - Complete command documentation
- [Bundles](bundles.md) - Composable configuration
- [Agents](agents.md) - Specialized sub-agents
- [Sessions](sessions.md) - Session management
- [Configuration](configuration.md) - Advanced configuration
