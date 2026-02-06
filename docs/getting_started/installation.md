---
title: Installation
description: Installing Amplifier CLI
---

# Installation

This guide covers installing the Amplifier CLI application.

## Requirements

- **Python**: 3.11 or higher
- **Operating System**: macOS, Linux, or Windows (WSL recommended)
- **API Key**: At least one LLM provider (Anthropic, OpenAI, Azure, or Ollama)

## Installation Methods

### Using pipx (Recommended)

[pipx](https://pipx.pypa.io/) installs Python applications in isolated environments:

```bash
# Install pipx if you don't have it
pip install pipx
pipx ensurepath

# Install Amplifier
pipx install amplifier-app-cli
```

### Using pip

```bash
pip install amplifier-app-cli
```

### Using uv

[uv](https://github.com/astral-sh/uv) is a fast Python package manager:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Amplifier
uv pip install amplifier-app-cli
```

### From Source

```bash
git clone https://github.com/microsoft/amplifier-app-cli.git
cd amplifier-app-cli
pip install -e .
```

## Configuration

### API Keys

Configure at least one LLM provider:

=== "Anthropic (Recommended)"
    ```bash
    export ANTHROPIC_API_KEY=your-key-here
    ```

=== "OpenAI"
    ```bash
    export OPENAI_API_KEY=your-key-here
    ```

=== "Azure OpenAI"
    ```bash
    export AZURE_OPENAI_API_KEY=your-key
    export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
    ```

=== "Ollama (Local)"
    ```bash
    # No API key needed - just start Ollama
    ollama serve
    ```

!!! note "Environment Variables"
    Add these to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) for persistence:
    ```bash
    echo 'export ANTHROPIC_API_KEY=your-key' >> ~/.zshrc
    ```

### Verifying Installation

```bash
# Check version
amplifier --version

# Run a simple test
amplifier run "Hello! What's 2+2?"
```

## Provider Configuration

### Supported Models

| Provider | Recommended Model | Capabilities |
|----------|-------------------|--------------|
| Anthropic | `claude-sonnet-4-5` | Tools, streaming, vision |
| Anthropic | `claude-haiku-20250110` | Fast, efficient |
| OpenAI | `gpt-4o` | Tools, streaming, vision |
| OpenAI | `gpt-4o` | Tools, streaming, vision |
| Azure | Deployment-specific | Depends on deployment |
| Ollama | Local models | Varies by model |

### Context Window Considerations

Different models have different context windows:

| Model | Context Window | Max Output |
|-------|---------------|------------|
| claude-sonnet-4-5 | 200,000 tokens | 8,192 tokens |
| gpt-4o | 128,000 tokens | 16,384 tokens |
| gpt-4o | 128,000 tokens | 16,384 tokens |

Amplifier automatically manages context within these limits.

### Custom Configuration

Create `~/.amplifier/config.yaml` for persistent settings:

```yaml
default_profile: dev

profiles:
  dev:
    providers:
      - module: provider-anthropic
        config:
          default_model: claude-sonnet-4-5
  
  fast:
    providers:
      - module: provider-anthropic
        config:
          default_model: claude-haiku-20250110
```

## Optional Dependencies

### For Development

```bash
# Install with development extras
pip install "amplifier-app-cli[dev]"
```

### For Testing

```bash
# Install with test extras
pip install "amplifier-app-cli[test]"
```

## Troubleshooting

### Command Not Found

If `amplifier` command isn't found after installation:

```bash
# For pipx
pipx ensurepath
source ~/.bashrc  # or restart terminal

# For pip, ensure Scripts directory is in PATH
# Linux/macOS: ~/.local/bin
# Windows: %USERPROFILE%\AppData\Local\Programs\Python\PythonXX\Scripts
```

### API Key Issues

```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY

# Test API key (Anthropic)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-5","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

### Token Validation Errors

If you see token-related errors:

1. Check your model's context window limits
2. Reduce the size of your input
3. Amplifier will automatically compact context if it exceeds limits

### Python Version Issues

```bash
# Check Python version
python --version

# If < 3.11, install newer version
# macOS
brew install python@3.11

# Ubuntu
sudo apt install python3.11
```

## Updating

### Using pipx

```bash
pipx upgrade amplifier-app-cli
```

### Using pip

```bash
pip install --upgrade amplifier-app-cli
```

## Uninstalling

### Using pipx

```bash
pipx uninstall amplifier-app-cli
```

### Using pip

```bash
pip uninstall amplifier-app-cli
```

## Next Steps

- [Configuration](configuration.md) - Detailed configuration options
- [First Session](first_session.md) - Walk through your first session
- [User Guide](../user_guide/) - Complete CLI reference
