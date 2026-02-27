---
title: Installation
description: Installing Amplifier CLI
---

# Installation

This guide covers installing the Amplifier CLI.

## Requirements

- **Python 3.11+**
- **[UV](https://github.com/astral-sh/uv)** - Fast Python package manager (recommended)

### Install UV

```bash
# macOS/Linux/WSL
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Quick Install

### Try Without Installing

```bash
uvx --from git+https://github.com/microsoft/amplifier amplifier
```

This downloads and runs Amplifier in an isolated environment without permanent installation.

### Install Globally

```bash
uv tool install git+https://github.com/microsoft/amplifier
```

This installs the `amplifier` command globally.

## First-Time Setup

After installation, run:

```bash
amplifier init
```

The setup wizard will:

1. **Detect API keys** - Checks for `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `AZURE_OPENAI_API_KEY`, `GOOGLE_API_KEY`
2. **Configure provider** - Sets your preferred LLM provider
3. **Set defaults** - Configures default model and settings

**Tip**: Set environment variables before running `init` for faster setup:

```bash
export ANTHROPIC_API_KEY="your-key"
amplifier init
```

## Shell Completion

Enable tab completion for faster CLI usage:

```bash
amplifier --install-completion
```

This automatically:
- Detects your shell (bash, zsh, fish)
- Adds completion to your shell config
- Safe to run multiple times

After installation:
```bash
source ~/.bashrc  # or ~/.zshrc for zsh
```

## Provider Configuration

### Anthropic (Recommended)

```bash
export ANTHROPIC_API_KEY="your-key"
amplifier provider use anthropic
```

### OpenAI

```bash
export OPENAI_API_KEY="your-key"
amplifier provider use openai
```

### Azure OpenAI

```bash
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
amplifier provider use azure-openai
```

### Google Gemini

```bash
export GOOGLE_API_KEY="your-key"
amplifier provider use google
```

### Ollama (Local, No API Key)

```bash
# Install Ollama first: https://ollama.ai
ollama pull llama3.2:3b
amplifier provider use ollama
```

## Supported Providers

- **Anthropic Claude** - Recommended, most tested (Sonnet, Opus models)
- **OpenAI** - Good alternative (GPT-4o, GPT-4o-mini, o1 models)
- **Azure OpenAI** - Enterprise users with Azure subscriptions
- **Google Gemini** - Google's AI models with large context windows (Gemini 2.5 Flash, Pro)
- **Ollama** - Local, free, no API key needed

## Update Amplifier

```bash
# Check for updates and install
amplifier update

# Check only (don't install)
amplifier update --check-only

# Skip confirmation prompts
amplifier update -y
```

## Next Steps

- [CLI Reference](../user_guide/cli.md) - Complete command documentation
- [Provider Configuration](../modules/providers/index.md) - Detailed provider setup
- [Getting Started Tutorial](../tutorials/getting_started.md) - First steps with Amplifier
