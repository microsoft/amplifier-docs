---
title: Provider Setup
description: Configure your LLM provider
---

# Provider Setup

Amplifier supports multiple LLM providers. This guide covers setting up each one.

## Supported Providers

| Provider | Models | Best For |
|----------|--------|----------|
| **Anthropic** | Claude 4 Sonnet, Opus, Haiku | General purpose, coding, analysis |
| **OpenAI** | GPT-5.1-codex, GPT-5.1, GPT-5-mini, GPT-5-nano | Broad capabilities, function calling |
| **Azure OpenAI** | GPT-5.1 via Azure | Enterprise, compliance requirements |
| **Ollama** | Llama, Mistral, etc. | Local/offline, privacy, experimentation |
| **vLLM** | Any vLLM-compatible | Self-hosted inference, high throughput |

For detailed configuration options and advanced features, see [Provider Modules](../modules/providers/index.md).

## Anthropic (Recommended)

### Get an API Key

1. Visit [console.anthropic.com](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new API key

### Configure

```bash
# Set environment variable
export ANTHROPIC_API_KEY="sk-ant-..."

# Or add to shell profile
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc

# Select as provider
amplifier provider use anthropic
```

### Available Models

| Model | Description |
|-------|-------------|
| `claude-sonnet-4-5` | Recommended, balanced performance (default) |
| `claude-opus-4-6` | Most capable, best for complex tasks |
| `claude-haiku-4-5` | Fastest, cheapest |

```bash
# Use a specific model
amplifier run --model claude-opus-4-6 "Complex analysis task"
```

## OpenAI

### Get an API Key

1. Visit [platform.openai.com](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new secret key

### Configure

```bash
export OPENAI_API_KEY="sk-..."
amplifier provider use openai
```

### Available Models

| Model | Description |
|-------|-------------|
| `gpt-5.1-codex` | GPT-5 optimized for code (default) |
| `gpt-5.1` | Latest GPT-5 model |
| `gpt-5-mini` | Smaller, faster GPT-5 |
| `gpt-5-nano` | Smallest GPT-5 variant |

## Azure OpenAI

### Prerequisites

1. Azure subscription
2. Azure OpenAI resource created
3. Model deployed in your resource

### Configure

```bash
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"

amplifier provider use azure
```

### Configuration File (Alternative)

Create `~/.amplifier/settings.yaml`:

```yaml
providers:
  azure:
    api_key: ${AZURE_OPENAI_API_KEY}
    azure_endpoint: https://your-resource.openai.azure.com
    default_model: gpt-5.1
    api_version: "2024-10-01-preview"
```

## Ollama (Local)

### Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

### Start Ollama Server

```bash
ollama serve
```

### Pull a Model

```bash
ollama pull llama3.2
ollama pull codellama
ollama pull mistral
```

### Configure Amplifier

```bash
amplifier provider use ollama
```

### Available Models

Any model you've pulled with `ollama pull`:

```bash
# List available models
ollama list

# Use specific model
amplifier run --model llama3.2 "Hello!"
```

## vLLM (Self-Hosted)

For high-throughput self-hosted inference with your own GPU servers.

### Prerequisites

- Running vLLM server (v0.10.1+)
- Model loaded in vLLM

### Configure

vLLM is configured via settings file only (no environment variable for the server URL):

```yaml
# ~/.amplifier/settings.yaml
providers:
  vllm:
    base_url: http://your-server:8000/v1
    default_model: openai/gpt-oss-20b
```

```bash
amplifier provider use vllm
```

For vLLM server setup and advanced options, see [vLLM Provider](../modules/providers/vllm.md).

## Switching Providers

### Temporary Switch

```bash
amplifier run --provider openai "Use OpenAI for this"
```

### Change Default

```bash
amplifier provider use anthropic
```

### Check Current Provider

```bash
amplifier provider current
```

## Provider Configuration

### Via Environment Variables

| Provider | Variables |
|----------|-----------|
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Azure | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` |
| Ollama | `OLLAMA_HOST` (optional) |
| vLLM | *(config file only — see settings.yaml)* |

### Via Settings File

Create `~/.amplifier/settings.yaml`:

```yaml
default_provider: anthropic

providers:
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    default_model: claude-sonnet-4-5

  openai:
    api_key: ${OPENAI_API_KEY}
    default_model: gpt-5.1-codex

  ollama:
    host: http://localhost:11434
    default_model: llama3.2:3b

  vllm:
    base_url: http://your-server:8000/v1
    default_model: openai/gpt-oss-20b
```

## Multiple Providers

You can configure multiple providers and switch between them:

```bash
# List configured providers
amplifier provider list

# Switch provider
amplifier provider use openai

# Use specific provider for one command
amplifier run --provider ollama "Local query"
```

## Troubleshooting

### "Authentication failed"

- Verify your API key is correct
- Check the key hasn't expired
- Ensure environment variable is exported

```bash
echo $ANTHROPIC_API_KEY  # Should show your key
```

### "Model not found"

- Check the model name is correct
- For Azure, verify deployment name matches

### "Connection refused" (Ollama)

- Ensure Ollama is running: `ollama serve`
- Check it's on the default port: `http://localhost:11434`

### Rate Limits

If you hit rate limits:

- Wait and retry
- Use a different model
- Consider upgrading your API plan

## Next Steps

- [Getting Started](index.md) - Run your first session
- [CLI Reference](../user_guide/cli.md) - All commands
- [Profiles](../user_guide/profiles.md) - Configure capabilities
