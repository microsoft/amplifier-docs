---
title: Provider Setup
description: Configure your LLM provider
---

# Provider Setup

Amplifier supports multiple LLM providers. This guide covers setting up each one.

## Supported Providers

| Provider | Models | Best For |
|----------|--------|----------|
| **Anthropic** | Claude 4, Claude 3.5 | General purpose, coding, analysis |
| **OpenAI** | GPT-4, GPT-4o | Broad capabilities, function calling |
| **Azure OpenAI** | GPT-4, GPT-4o | Enterprise, compliance requirements |
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
| `claude-sonnet-4-5` | Latest, balanced performance (default) |
| `claude-opus-4-1` | Most capable, best for complex tasks |
| `claude-haiku-3-5` | Fastest, good for simple tasks |

```bash
# Use a specific model
amplifier run --model claude-opus-4-1 "Complex analysis task"
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
| `gpt-4o` | Latest, multimodal (default) |
| `gpt-4-turbo` | Fast, capable |
| `gpt-4` | Original GPT-4 |

## Azure OpenAI

### Prerequisites

1. Azure subscription
2. Azure OpenAI resource created
3. Model deployed in your resource

### Configure

```bash
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_DEPLOYMENT="your-deployment-name"

amplifier provider use azure
```

### Configuration File (Alternative)

Create `~/.amplifier/settings.yaml`:

```yaml
providers:
  azure:
    api_key: ${AZURE_OPENAI_API_KEY}
    endpoint: https://your-resource.openai.azure.com
    deployment: gpt-4
    api_version: "2024-02-01"
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
ollama pull llama3.1
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
amplifier run --model llama3.1 "Hello!"
```

## vLLM (Self-Hosted)

For high-throughput self-hosted inference with your own GPU servers.

### Prerequisites

- Running vLLM server (v0.10.1+)
- Model loaded in vLLM

### Configure

```bash
# Set your vLLM server URL
export VLLM_BASE_URL="http://your-server:8000/v1"

amplifier provider use vllm
```

### Configuration File

```yaml
providers:
  vllm:
    base_url: http://192.168.128.5:8000/v1
    default_model: openai/gpt-oss-20b
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
| Azure | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT` |
| Ollama | None required (local) |
| vLLM | `VLLM_BASE_URL` |

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
    default_model: gpt-4o

  ollama:
    base_url: http://localhost:11434
    default_model: llama3.1

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
