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

# Interactive mode
amplifier

# Resume last session
amplifier continue

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

# Providers
amplifier provider list
amplifier provider use anthropic
amplifier provider current

# Modules
amplifier module list
amplifier module add tool-web
amplifier module show tool-web
```

### Getting Help

```bash
# Command help
amplifier --help
amplifier run --help

# List agents
amplifier agents list

# Show agent details
amplifier agents show explorer
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

Amplifier uses a three-level configuration system:

1. **Global** (`~/.amplifier/`) - System-wide defaults
2. **Project** (`.amplifier/`) - Project-specific settings
3. **Session** - Runtime overrides

Later levels override earlier ones.

### Setting Scope

Most commands support scope flags:

```bash
# Global scope (default)
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

# Override config location
export AMPLIFIER_CONFIG_DIR="~/.config/amplifier"
```

## Tips and Tricks

### Shell Completion

```bash
amplifier --install-completion
source ~/.bashrc  # or ~/.zshrc
```

### Multi-line Input

In interactive mode:
- Press `Ctrl-J` to insert newline
- Press `Enter` to send message

### Slash Commands

In interactive mode:

```
/help        - Show available commands
/mode        - Set or toggle modes
/status      - Show session status
/config      - Show configuration
/tools       - List available tools
/agents      - List available agents
/save        - Save transcript
/clear       - Clear context
/rename      - Rename session
/fork        - Fork session at turn N
```

### Unix Piping

```bash
# Pipe input to amplifier
cat file.txt | amplifier run

# Continue session via pipe
echo "new prompt" | amplifier continue
```

### JSON Output

```bash
# Get JSON response for scripting
amplifier run --output-format json "What is 2+2?"

# With execution trace
amplifier run --output-format json-trace "Your prompt"
```

## Next Steps

- [CLI Reference](cli.md) - Complete command documentation
- [Bundles](bundles.md) - Composable configuration
- [Agents](agents.md) - Specialized sub-agents
- [Sessions](sessions.md) - Session management
- [Configuration](configuration.md) - Advanced configuration
