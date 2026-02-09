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
export AZURE_OPENAI_DEPLOYMENT="your-deployment-name"

# Or use Azure CLI authentication instead of API key
export AZURE_USE_DEFAULT_CREDENTIAL="true"

amplifier provider use azure
```

### Google Gemini

```bash
export GOOGLE_API_KEY="your-key"
amplifier provider use google
```

### Ollama (Local)

No API key needed - runs locally:

```bash
# Install Ollama first: https://ollama.ai
ollama pull llama3.2

amplifier provider use ollama
```

For remote Ollama servers:

```bash
export OLLAMA_HOST="http://your-server:11434"
amplifier provider use ollama
```

## Context Window Limits

Different models have different context limits:

| Model | Context Window | Max Output |
|-------|----------------|------------|
| Claude Sonnet 4.5 | 200K tokens | 8K tokens |
| Claude Opus | 200K tokens | 4K tokens |
| GPT-4o | 128K tokens | 4K tokens |
| GPT-4o-mini | 128K tokens | 16K tokens |
| Gemini 2.5 Pro | 1M tokens | 8K tokens |
| Ollama (varies) | Model dependent | Model dependent |

Amplifier automatically manages context, compacting when needed.

## Updating

```bash
# Check for updates
amplifier update --check-only

# Update Amplifier and all modules
amplifier update

# Force update (skip version detection)
amplifier update --force
```

## Verifying Installation

```bash
# Check version
amplifier --version

# Check current configuration
amplifier provider current
amplifier bundle current

# Test with a simple prompt
amplifier run "Hello, world!"
```

## Troubleshooting

### "Command not found"

Ensure UV tools are in your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### API Key Issues

```bash
# Verify key is set
echo $ANTHROPIC_API_KEY

# Re-run init to reconfigure
amplifier init
```

### Module Loading Errors

```bash
# Refresh modules
amplifier module refresh

# Check module status
amplifier module list
```

### Permission Issues

```bash
# Check file permissions
ls -la ~/.amplifier/

# Reset configuration
rm -rf ~/.amplifier/config.yaml
amplifier init
```

## Development Setup

For contributing to Amplifier:

```bash
# Clone repository
git clone https://github.com/microsoft/amplifier.git
cd amplifier

# Install in development mode
uv pip install -e .

# Run tests
uv run pytest
```

## Next Steps

- **[Getting Started](index.md)** - Basic usage guide
- **[CLI User Guide](../user_guide/)** - Complete command reference
- **[Configuration](../user_guide/configuration.md)** - Advanced configuration

## References

- **→ [CLI README](https://github.com/microsoft/amplifier/blob/main/README.md)** - Full CLI documentation
