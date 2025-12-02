---
title: Installation Options
description: Alternative installation methods and troubleshooting
---

# Installation Options

Most users should follow the [Getting Started](index.md) guide. This page covers alternative installation methods and troubleshooting.

## Alternative Install Methods

### Using pipx

If you prefer [pipx](https://pipx.pypa.io/) over uv:

```bash
pipx install git+https://github.com/microsoft/amplifier@next
```

### Development Installation

For contributors or those who want to modify Amplifier:

```bash
# Clone the repository (next branch)
git clone -b next https://github.com/microsoft/amplifier.git
cd amplifier

# Install in development mode
uv pip install -e .
```

## Manual Configuration

If you prefer manual setup:

### 1. Set Your API Key

=== "Anthropic"

    ```bash
    export ANTHROPIC_API_KEY="your-api-key"
    ```

=== "OpenAI"

    ```bash
    export OPENAI_API_KEY="your-api-key"
    ```

=== "Azure OpenAI"

    ```bash
    export AZURE_OPENAI_API_KEY="your-api-key"
    export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
    ```

=== "Ollama"

    ```bash
    # Ollama runs locally, no API key needed
    # Just ensure Ollama is running: ollama serve
    ```

### 2. Select Your Provider

```bash
amplifier provider use anthropic  # or openai, azure, ollama
```

### 3. Verify Setup

```bash
amplifier run "Hello! Are you working?"
```

## Shell Completion

Enable tab completion for your shell:

```bash
amplifier --install-completion
```

Supports bash, zsh, fish, and PowerShell.

## Updating

Update to the latest version:

```bash
amplifier update
```

Or reinstall:

```bash
uv tool install --force git+https://github.com/microsoft/amplifier@next
```

## Troubleshooting

### "Command not found: amplifier"

Ensure your tool bin directory is in PATH:

```bash
# For uv
export PATH="$HOME/.local/bin:$PATH"

# For pipx
export PATH="$HOME/.local/bin:$PATH"
```

Add this to your shell profile (`.bashrc`, `.zshrc`, etc.).

### "No API key found"

Make sure your API key environment variable is set:

```bash
echo $ANTHROPIC_API_KEY  # Should show your key
```

Or run `amplifier init` to configure it.

### "Module not found" errors

Try reinstalling with a clean state:

```bash
uv tool uninstall amplifier
uv tool install git+https://github.com/microsoft/amplifier@next
```

## Next Steps

- [Getting Started →](index.md) - Run your first AI session
- [Provider Setup →](providers.md) - Configure your LLM provider
