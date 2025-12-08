---
title: Getting Started
description: Get up and running with Amplifier in under 5 minutes
---

# Getting Started

Get your first AI session running in under 5 minutes.

## Install & Configure

```bash
# Install with uv (recommended)
uv tool install git+https://github.com/microsoft/amplifier

# Run setup wizard
amplifier init
```

That's it! The setup wizard will configure your LLM provider (Anthropic, OpenAI, etc.).

!!! tip "Stay Updated"
    Amplifier is in active development. Run `amplifier update` daily to get the latest features and fixes.

??? info "Alternative installation options"
    See [Installation Options](installation.md) for pipx, development installs, and troubleshooting.

## Start Amplifier

```bash
amplifier
```

This opens an interactive session where you can chat with the AI:

```
amplifier> What is the capital of France?
[AI responds...]

amplifier> Can you write a Python function to sort a list?
[AI responds with code...]

amplifier> /help
[Shows available commands...]

amplifier> /quit
```

### Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/tools` | List available tools |
| `/agents` | List available agents |
| `/status` | Show session information |
| `/clear` | Clear conversation history |
| `/quit` or `/exit` | Exit |

## Working with Code

Amplifier excels at code-related tasks. Start it in a project directory:

```bash
cd your-project
amplifier
```

```
amplifier> Explain the structure of this project
[AI analyzes your codebase...]

amplifier> Review main.py for potential issues
[AI reviews the file...]

amplifier> Write a unit test for the User class
[AI generates tests...]
```

## Using Tools

With the `dev` profile, Amplifier has access to powerful tools:

```bash
amplifier --profile dev
```

```
amplifier> List all Python files in this directory
[AI uses filesystem tool to list files...]

amplifier> Search for TODO comments in the codebase
[AI uses search tool...]
```

The AI can now read/write files, execute shell commands, search the codebase, and browse the web.

## Session Management

Continue your most recent conversation:

```bash
amplifier continue
```

```
amplifier> Now add error handling to that function
[AI continues where you left off...]
```

## Using Profiles

Profiles are pre-configured capability sets:

```bash
# List available profiles
amplifier profile list

# Set default profile
amplifier profile use dev

# Or use a profile for one session
amplifier --profile dev
```

| Profile | Description |
|---------|-------------|
| `foundation` | Minimal - just LLM access |
| `base` | Basic tools (filesystem, bash) |
| `dev` | Full development (tools + agents + search) |

## Using Agents

Agents are specialized assistants for specific tasks:

```
amplifier> @explorer What is the architecture of this project?
[Explorer agent analyzes codebase...]

amplifier> @bug-hunter Find issues in auth.py
[Bug hunter agent reviews code...]
```

| Agent | Purpose |
|-------|---------|
| `explorer` | Breadth-first codebase exploration |
| `bug-hunter` | Systematic debugging |
| `zen-architect` | System design with simplicity focus |

## Next Steps

- [CLI Reference](../user_guide/cli.md) - All available commands
- [Profiles](../user_guide/profiles.md) - Configure capability sets
- [Agents](../user_guide/agents.md) - Specialized sub-agents
- [Sessions](../user_guide/sessions.md) - Session management
- [Architecture](../architecture/overview.md) - How it all works
