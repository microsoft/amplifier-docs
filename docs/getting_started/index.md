---
title: Getting Started
description: Quick introduction to Amplifier
---

# Getting Started

Welcome to Amplifier! This guide will get you up and running quickly.

## What is Amplifier?

Amplifier is a modular AI assistant platform that makes AI dramatically more effective by providing:

- **Domain knowledge and context** from your work
- **Understanding of your patterns** and preferences
- **Ability to work on multiple things** simultaneously
- **Integration with your development workflow**

Think of Amplifier like a Linux kernel for AI assistants: a small, stable core with a rich ecosystem of modules.

## Quick Start

### 1. Install

```bash
# Using pipx (recommended)
pipx install amplifier-app-cli

# Or using pip
pip install amplifier-app-cli
```

### 2. Configure

Set up your API credentials:

```bash
# Anthropic (recommended)
export ANTHROPIC_API_KEY=your-key-here

# Or OpenAI
export OPENAI_API_KEY=your-key-here

# Or Azure OpenAI
export AZURE_OPENAI_API_KEY=your-key
export AZURE_OPENAI_ENDPOINT=your-endpoint

# Or Ollama (local, no API key needed)
# Just ensure Ollama is running: ollama serve
```

### 3. Run

```bash
# Start a session
amplifier run "What files are in this directory?"

# Or start interactive REPL
amplifier repl
```

## Provider Support

Amplifier supports multiple LLM providers:

| Provider | Models | Setup |
|----------|--------|-------|
| **Anthropic** | claude-sonnet-4-5, claude-haiku-20250110 | `ANTHROPIC_API_KEY` |
| **OpenAI** | gpt-4o, gpt-4o, gpt-4o-mini | `OPENAI_API_KEY` |
| **Azure OpenAI** | Deployment-based | `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT` |
| **Ollama** | Local models | Install Ollama, run `ollama serve` |

!!! note "Provider Priority"
    If multiple providers are configured, Amplifier uses the first available one. You can specify provider preferences in your bundle configuration.

## Core Concepts

### Sessions

A **session** is a single conversation with the AI. Sessions maintain context (conversation history) and can be resumed later.

```bash
# New session
amplifier run "Hello!"

# Resume previous session
amplifier run --resume
```

### Bundles

**Bundles** are configuration files that define what modules to load. They're markdown files with YAML frontmatter:

```markdown
---
bundle:
  name: my-app
  version: 1.0.0

providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
---

You are a helpful assistant.
```

### Tools

**Tools** are capabilities that agents can use: reading files, executing commands, searching the web, etc.

```bash
# Tools are automatically available
amplifier run "Read the README.md file"
amplifier run "Run the tests"
```

### Agents

**Agents** are specialized assistants configured for specific tasks. Agents can delegate to other agents.

```bash
# Use a specific agent
amplifier run --agent explorer "Map the codebase structure"
```

## Context Window and Token Management

Amplifier automatically manages context windows:

- **Dynamic budgeting**: Context managers query provider info to calculate available tokens
- **Automatic compaction**: When approaching limits, older messages are compacted
- **Token awareness**: Tools can report estimated token usage

The formula: `available = context_window - max_output_tokens - safety_margin`

## Validation

Amplifier validates configuration at multiple levels:

- **Bundle validation**: Ensures configuration is well-formed
- **Mount plan validation**: Verifies required modules exist
- **Runtime validation**: Hooks can validate operations before execution

```bash
# Validate a bundle
amplifier validate ./my-bundle.md
```

## What's Next?

<div class="grid">

<div class="card">
<h3><a href="installation/">Installation</a></h3>
<p>Detailed installation instructions and requirements.</p>
</div>

<div class="card">
<h3><a href="configuration/">Configuration</a></h3>
<p>Learn about configuration files and options.</p>
</div>

<div class="card">
<h3><a href="first_session/">First Session</a></h3>
<p>Walk through your first Amplifier session.</p>
</div>

<div class="card">
<h3><a href="../user_guide/">User Guide</a></h3>
<p>Complete guide to using Amplifier CLI.</p>
</div>

</div>

## Architecture Overview

```
┌─────────────────────────────────────────┐
│  amplifier-app-cli (Application)        │
│  • Configuration, Bundles, Profiles     │
│  • User interaction (CLI/REPL)          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  amplifier-core (Kernel)                │
│  • Session lifecycle                    │
│  • Module loading                       │
│  • Event emission                       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Modules (Userspace)                    │
│  • Providers (Anthropic, OpenAI, etc.)  │
│  • Tools (filesystem, bash, web, etc.)  │
│  • Hooks (logging, approval, etc.)      │
└─────────────────────────────────────────┘
```

For detailed architecture documentation, see the [Architecture](../architecture/) section.
