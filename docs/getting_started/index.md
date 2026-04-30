---
title: Getting Started
description: Quick introduction to Amplifier
---

# Getting Started

Welcome to Amplifier! This guide will help you get up and running quickly.

## What is Amplifier?

Amplifier is an **AI-powered modular development platform** with a command-line interface built on amplifier-core:

- **Bundle system** - Composable configuration packages (via amplifier-foundation)
- **Settings management** - Three-scope configuration (local/project/global via amplifier-config)
- **Module resolution** - Module source resolution for tools, providers, hooks
- **Session storage** - Project-scoped session persistence with multi-turn sub-session resumption
- **Agent delegation** - Spawn and resume sub-sessions for iterative collaboration with specialized agents
- **Interactive mode** - REPL with slash commands
- **Key management** - Secure API key storage

## Quick Start

### Install

```bash
# Try without installing
uvx --from git+https://github.com/microsoft/amplifier amplifier

# Or install globally
uv tool install git+https://github.com/microsoft/amplifier
```

### First Run

```bash
# First-time setup — opens a combined dashboard to add providers,
# select a routing matrix, and verify configuration (auto-runs if no config)
amplifier init

# Start a conversation
amplifier
```

**Tip**: Set environment variables before running `init` for faster setup — the dashboard detects env vars and shows them as defaults.

### Provider Support

| Provider | Models | Notes |
|----------|--------|-------|
| **Anthropic** | Sonnet, Opus | Recommended, most tested |
| **OpenAI** | GPT-4o, GPT-4o-mini, o1 | Good alternative |
| **Azure OpenAI** | — | Enterprise users with Azure subscriptions |
| **Google Gemini** | Gemini 2.5 Flash, Pro | Large context windows |
| **Ollama** | Local models | Free, no API key needed |

Set your API key before running:

```bash
export ANTHROPIC_API_KEY="your-key"
# or
export OPENAI_API_KEY="your-key"
# or
export GOOGLE_API_KEY="your-key"
```

## Basic Usage

### Single Command

```bash
# Execute a single prompt
amplifier run "Create a Python function to calculate fibonacci numbers"

# Use specific provider/model
amplifier run -p anthropic -m claude-sonnet-4-5 "Complex task"

# Single command via stdin (useful for scripts/pipelines)
echo "Summarize this spec" | amplifier run
```

### Interactive Mode

```bash
# Start interactive session
amplifier

# Or resume last session
amplifier continue
```

### Session Management

```bash
# List recent sessions
amplifier session list

# Resume specific session
amplifier session resume <session-id>

# Continue most recent session
amplifier continue
```

## Key Commands

```bash
# Configuration
amplifier init                           # First-time setup
amplifier bundle list                    # List available bundles
amplifier provider list                  # List providers
amplifier module list                    # List modules

# Running tasks
amplifier run "your prompt"              # Single command
amplifier                                # Interactive mode
amplifier continue                       # Resume last session

# Session management
amplifier session list                   # List sessions
amplifier session resume <id>            # Resume session

# Tools
amplifier tool list                      # List available tools
amplifier tool invoke <tool> <args>      # Invoke tool directly

# Updates
amplifier update                         # Update Amplifier and modules
```

## Next Steps

- [Installation Guide](installation.md) - Detailed installation instructions
- [CLI Reference](../user_guide/cli.md) - Complete command reference
- [Bundles Guide](../user_guide/bundles.md) - Composable configuration
- [Agents Guide](../user_guide/agents.md) - Specialized sub-agents

## Getting Help

```bash
# CLI help
amplifier --help
amplifier <command> --help

# Shell completion
amplifier --install-completion

# Documentation
https://github.com/microsoft/amplifier
```

## Example Workflow

```bash
# 1. Initial setup
amplifier init

# 2. Start a task
amplifier run "Analyze the authentication flow in src/auth.py"

# 3. Continue the conversation
amplifier continue "Now add error handling"

# 4. Review session
amplifier session list
```
