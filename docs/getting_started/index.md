---
title: Getting Started
description: Quick introduction to Amplifier
---

# Getting Started

Welcome to Amplifier! This guide will help you get up and running quickly.

## What is Amplifier?

Amplifier is a **modular AI agent system** that lets you build, customize, and run AI-powered development workflows. It follows a Linux kernel-inspired architecture:

- **Tiny kernel** (`amplifier-core`) - Provides mechanisms only
- **Pluggable modules** - All features live at the edges as replaceable components
- **Composable configuration** - Mix and match capabilities via bundles
- **Load-time validation** - The kernel validates module configurations at load time

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
# Interactive setup (auto-runs on first use)
amplifier init

# Start a conversation
amplifier
```

The `init` wizard will:
1. Detect available API keys from environment variables
2. Help you configure your preferred provider
3. Set up default settings

### Provider Support

| Provider | Models | Notes |
|----------|--------|-------|
| **Anthropic** | Claude Sonnet, Opus, Haiku | Recommended, most tested |
| **OpenAI** | GPT-4o, GPT-4o-mini, o1 | Good alternative |
| **Azure OpenAI** | GPT models via Azure | Enterprise users |
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

```bash
# Ollama (local, no API key needed)
amplifier provider use ollama
```

## Basic Usage

### Single Command

```bash
# Execute a single prompt
amplifier run "Create a Python function to calculate fibonacci numbers"

# Use specific provider/model
amplifier run --provider anthropic --model claude-opus-4 "Complex task"

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

In interactive mode:
- Type naturally, press Enter to send
- Use `Ctrl-J` for multi-line input
- Use `Ctrl-D` to exit
- Use `/help` for slash commands

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
