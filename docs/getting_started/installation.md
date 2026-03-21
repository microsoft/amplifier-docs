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
amplifier provider add anthropic
```

### OpenAI

```bash
export OPENAI_API_KEY="your-key"
amplifier provider add openai
```

### Azure OpenAI

```bash
export AZURE_OPENAI_API_KEY="your-key"
amplifier provider add azure-openai
```

### Google Gemini

```bash
export GOOGLE_API_KEY="your-key"
amplifier provider add google
```

### Ollama (Local, Free)

```bash
# Start Ollama server first
ollama serve

# Configure Amplifier
amplifier provider add ollama
```

No API key needed - runs locally on your machine.

## Verify Installation

```bash
# Check version
amplifier --version

# Test with a simple prompt
amplifier run "Hello, world!"
```

## Next Steps

- **[Quick Start Guide](../quick_start.md)** - Learn basic commands
- **[Bundle Guide](../bundles/index.md)** - Configure your agent
- **[Examples](../examples/index.md)** - See Amplifier in action

## Troubleshooting

### Command Not Found

If `amplifier` command is not found after installation:

1. **Check UV installation**:
   ```bash
   uv --version
   ```

2. **Verify tool installation**:
   ```bash
   uv tool list
   ```

3. **Add to PATH** (if needed):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

### API Key Issues

If provider setup fails:

1. **Verify environment variable**:
   ```bash
   echo $ANTHROPIC_API_KEY  # Should print your key
   ```

2. **Check provider configuration**:
   ```bash
   amplifier provider list
   ```

3. **Test provider connectivity**:
   ```bash
   amplifier provider test anthropic
   ```

### Module Loading Errors

If modules fail to load:

1. **Update Amplifier**:
   ```bash
   uv tool upgrade amplifier
   ```

2. **Clear module cache**:
   ```bash
   rm -rf ~/.amplifier/modules/
   ```

3. **Reinstall with fresh dependencies**:
   ```bash
   uv tool uninstall amplifier
   uv tool install git+https://github.com/microsoft/amplifier
   ```
