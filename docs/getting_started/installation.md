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

### Ollama (Local)

```bash
# No API key needed
amplifier provider use ollama
```

## Verifying Installation

```bash
# Check version
amplifier --version

# Test with a simple prompt
amplifier run "Hello! Can you help me with Python?"
```

## Upgrading

```bash
# Check for updates
amplifier update --check-only

# Update Amplifier and modules
amplifier update
```

## Troubleshooting

### Command Not Found

If `amplifier` command is not found after installation:

```bash
# Verify UV installation
uv --version

# Reinstall
uv tool install --force git+https://github.com/microsoft/amplifier
```

### Python Version

Amplifier requires Python 3.11+. Check your version:

```bash
python --version
# or
python3 --version
```

### API Key Issues

Verify your API keys are set:

```bash
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
```

Test provider connectivity:

```bash
amplifier provider test <provider-name>
```

## Next Steps

- [Getting Started Guide](index.md) - Quick introduction
- [CLI Reference](../user_guide/cli.md) - Complete command reference
- [Configuration](../user_guide/configuration.md) - Advanced configuration options
