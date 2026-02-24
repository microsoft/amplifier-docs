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

### Advanced Configuration

**Debug Logging:**
```yaml
providers:
  - module: provider-anthropic
    config:
      debug: true      # Enable standard debug events
      raw_debug: true  # Enable ultra-verbose raw API I/O logging
```

**Rate Limit Control:**
```yaml
providers:
  - module: provider-anthropic
    config:
      max_retries: 5  # Number of retry attempts (default: 2)
```

**Beta Headers (1M Token Context):**
```yaml
providers:
  - module: provider-anthropic
    config:
      beta_headers: "context-1m-2025-08-07"  # Enable 1M token context window
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
amplifier run --model gpt-5.1 "Analyze this code"
```

### Advanced Configuration

**Debug Logging:**
```yaml
providers:
  - module: provider-openai
    config:
      debug: true      # Enable standard debug events
      raw_debug: true  # Enable ultra-verbose raw API I/O logging
```

**Reasoning Control:**
```yaml
providers:
  - module: provider-openai
    config:
      reasoning: "high"              # Reasoning effort: minimal|low|medium|high
      reasoning_summary: "detailed"  # Reasoning verbosity: auto|concise|detailed
```

**Automatic Context Management:**
```yaml
providers:
  - module: provider-openai
    config:
      truncation: "auto"  # Automatic context management (default)
      # OR
      truncation: null    # Disable automatic truncation
```

## Azure OpenAI

### Prerequisites

1. Azure subscription with OpenAI service enabled
2. Deployed model in Azure OpenAI resource
3. API key or Azure AD credentials

### Quick Start

**For local development (recommended):**
```bash
# Login to Azure
az login

# Set up endpoint
export AZURE_OPENAI_ENDPOINT="https://myresource.openai.azure.com"
export AZURE_USE_DEFAULT_CREDENTIAL="true"

# Start amplifier
amplifier
```

**For API key authentication:**
```bash
export AZURE_OPENAI_ENDPOINT="https://myresource.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key-here"
amplifier
```

### Configuration

```yaml
providers:
  - module: provider-azure-openai
    config:
      azure_endpoint: "https://myresource.openai.azure.com"
      api_key: "${AZURE_OPENAI_API_KEY}"
      default_model: "gpt-5.1"
      
      # Optional: Map model names to Azure deployment names
      deployment_mapping:
        "gpt-5.1": "my-gpt5-deployment"
        "gpt-5-mini": "my-mini-deployment"
```

### Authentication Options

The provider supports multiple authentication methods:

1. **API Key** (simplest)
2. **Azure AD Token**
3. **Managed Identity** (for Azure resources)
4. **DefaultAzureCredential** (recommended - works locally and in Azure)

**DefaultAzureCredential** tries multiple methods in order:
- Environment variables
- Managed identity (if running in Azure)
- Azure CLI (if logged in locally with `az login`)
- Azure PowerShell
- Interactive browser authentication

### Advanced Configuration

**Debug Logging:**
```yaml
providers:
  - module: provider-azure-openai
    config:
      debug: true      # Enable standard debug events
      raw_debug: true  # Enable ultra-verbose raw API I/O logging
```

## Ollama

### Prerequisites

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull a model: `ollama pull llama3.2:3b`
3. Start Ollama server (usually starts automatically)

### Configure

```bash
export OLLAMA_HOST="http://localhost:11434"
amplifier provider use ollama
```

### Available Models

| Model | Description |
|-------|-------------|
| `llama3.2:3b` | Small, fast (recommended) |
| `llama3.2:1b` | Tiny, fastest |
| `mistral` | 7B general purpose |
| `mixtral` | 8x7B mixture of experts |
| `codellama` | Code generation |
| `deepseek-r1` | Reasoning/thinking |
| `qwen3` | Reasoning + tools |

See [ollama.ai/library](https://ollama.ai/library) for complete list.

### Advanced Configuration

**Debug Logging:**
```yaml
providers:
  - module: provider-ollama
    config:
      debug: true      # Enable standard debug events
      raw_debug: true  # Enable ultra-verbose raw API I/O logging
```

**Automatic Model Pulling:**
```yaml
providers:
  - module: provider-ollama
    config:
      auto_pull: true  # Automatically pull missing models
```

**Thinking/Reasoning Support:**

For compatible models like DeepSeek R1 and Qwen 3:
```python
request = ChatRequest(
    model="deepseek-r1",
    messages=[...],
    enable_thinking=True
)
```

The response includes both the thinking process (ThinkingBlock) and the final answer (TextBlock).

## vLLM

### Prerequisites

1. vLLM server running with OpenAI-compatible API
2. Model loaded in vLLM

### Configure

```bash
export VLLM_API_BASE="http://localhost:8000/v1"
amplifier provider use vllm
```

### Configuration

```yaml
providers:
  - module: provider-vllm
    config:
      base_url: "http://localhost:8000/v1"
      default_model: "meta-llama/Llama-3-8b"
```

## Switching Providers

```bash
# List configured providers
amplifier provider list

# Switch active provider
amplifier provider use anthropic

# Use specific provider for one command
amplifier run --provider openai "Task"
```

## Next Steps

- [CLI Reference](../user_guide/cli.md) - Learn all CLI commands
- [Configuration](../user_guide/configuration.md) - Advanced configuration options
- [Provider Modules](../modules/providers/index.md) - Deep dive into each provider
