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

```bash
# Use a specific model
amplifier run --model gpt-5.1 "General task"
```

## Azure OpenAI

Azure OpenAI uses your Azure-hosted deployments.

### Prerequisites

- Azure subscription with OpenAI service enabled
- Deployed GPT model in your Azure resource

### Configure

```bash
export AZURE_OPENAI_ENDPOINT="https://myresource.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"
# OR use Azure CLI authentication
az login
export AZURE_USE_DEFAULT_CREDENTIAL="true"

amplifier provider use azure-openai
```

### Deployment Mapping

Azure uses deployment names instead of model names:

```toml
[[providers]]
name = "azure-openai"
[providers.config]
azure_endpoint = "https://myresource.openai.azure.com"
default_model = "gpt-5.1"

[providers.config.deployment_mapping]
"gpt-5.1" = "my-gpt5-deployment"
```

## Ollama

Run models locally with Ollama.

### Install Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama
```

### Pull a Model

```bash
ollama pull llama3.2:3b
```

### Configure

```bash
# Ollama server runs on localhost:11434 by default
amplifier provider use ollama
```

### Popular Models

- `llama3.2:3b` - Small, fast (3B parameters)
- `llama3.2:1b` - Tiny, fastest (1B parameters)
- `mistral` - 7B model, good quality
- `codellama` - Code generation
- `deepseek-r1` - Reasoning model

See [ollama.ai/library](https://ollama.ai/library) for all models.

## vLLM

Self-hosted inference server for open-weight models.

### Prerequisites

- Running vLLM server (version 0.10.1+)
- Model served via vLLM (e.g., gpt-oss-20b)

### Start vLLM Server

```bash
vllm serve openai/gpt-oss-20b \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 2
```

### Configure

```bash
export VLLM_BASE_URL="http://192.168.128.5:8000/v1"
amplifier provider use vllm
```

## Next Steps

- [Configure Tools](../modules/tools/index.md) - Add capabilities to your agents
- [Provider Configuration](../modules/providers/index.md) - Advanced provider settings
- [Bundle Configuration](../foundation/bundles.md) - Package configurations for reuse
