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
amplifier run -p anthropic -m claude-sonnet-4-5 "Your prompt"

# Pipe input
echo "Summarize this" | amplifier run
```

### Interactive Mode

```bash
# Start interactive session
amplifier

# You'll see a prompt like:
# amplifier> Type your message...
```

### Sessions

Amplifier automatically saves conversation state:

```bash
# Continue most recent session
amplifier continue

# Continue with new prompt
amplifier continue "Follow up question"

# List sessions
amplifier session list

# Resume specific session
amplifier session resume <session-id>
```

## Context Window Awareness

Amplifier automatically manages context windows. Providers report their model's context window size, enabling automatic token budget management.

| Model | Context Window | Behavior |
|-------|----------------|----------|
| Claude Sonnet | 200K tokens | Full context available |
| GPT-4o | 128K tokens | Full context available |
| Smaller models | 8K-32K | Auto-compacts when needed |

When conversations exceed limits, Amplifier gracefully compacts older messages while preserving:
- System instructions
- Recent conversation
- Tool call/result pairs

## Bundles

Bundles are composable configuration packages:

```bash
# See current bundle
amplifier bundle current

# List available bundles
amplifier bundle list

# Switch bundles
amplifier bundle use my-custom-bundle
```

The default **foundation** bundle provides:
- Common development tools (filesystem, bash, web)
- Streaming output
- Session persistence

## Common Commands

```bash
# Configuration
amplifier init                    # First-time setup
amplifier provider use anthropic  # Set provider
amplifier bundle use foundation   # Set bundle

# Running
amplifier                         # Interactive mode
amplifier run "prompt"            # Single command
amplifier continue               # Resume last session

# Tools
amplifier tool list              # List available tools
amplifier tool info <tool-name>  # Tool details

# Sessions
amplifier session list           # List sessions
amplifier session show <id>      # Session details

# Utilities
amplifier update                 # Update Amplifier
amplifier --version              # Show version
```

## Next Steps

- **[Installation](installation.md)** - Detailed installation options
- **[CLI User Guide](../user_guide/)** - Complete command reference
- **[Architecture](../architecture/)** - Understand the system design

## References

> **Note**: The Amplifier CLI is a **reference implementation**. You can use it as-is, fork it, or build your own CLI using amplifier-core.

- **→ [CLI README](https://github.com/microsoft/amplifier/blob/main/README.md)** - Full CLI documentation
- **→ [User Onboarding](https://github.com/microsoft/amplifier/blob/main/docs/USER_ONBOARDING.md)** - Complete user guide