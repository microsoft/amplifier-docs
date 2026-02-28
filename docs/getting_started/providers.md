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

**Retry Configuration:**
```yaml
providers:
  - module: provider-anthropic
    config:
      max_retries: 5              # Maximum retry attempts (default: 5)
      min_retry_delay: 1.0        # Base delay in seconds (default: 1.0)
      max_retry_delay: 60.0       # Cap on base delay (default: 60.0)
      retry_jitter: 0.2           # Jitter fraction 0.0-1.0 (default: 0.2)
      overloaded_delay_multiplier: 10.0  # Multiplier for 529 errors (default: 10.0)
```

**Beta Headers (1M Token Context):**
```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
      beta_headers: "context-1m-2025-08-07"  # Enable 1M token context window
```

## OpenAI

### Get an API Key

1. Visit [platform.openai.com](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new API key

### Configure

```bash
# Set environment variable
export OPENAI_API_KEY="sk-..."

# Select as provider
amplifier provider use openai
```

### Available Models

| Model | Description |
|-------|-------------|
| `gpt-5.1-codex` | Optimized for code (default) |
| `gpt-5.1` | Latest GPT-5 model |
| `gpt-5-mini` | Smaller, faster |
| `gpt-5-nano` | Smallest variant |

```bash
# Use a specific model
amplifier run --model gpt-5.1 "General task"
```

### Advanced Configuration

**Reasoning Control:**
```yaml
providers:
  - module: provider-openai
    config:
      reasoning: "high"                    # minimal|low|medium|high
      reasoning_summary: "detailed"        # auto|concise|detailed
```

**Automatic Context Management:**
```yaml
providers:
  - module: provider-openai
    config:
      truncation: "auto"  # Automatic conversation history management
```

**Debug Logging:**
```yaml
providers:
  - module: provider-openai
    config:
      debug: true      # Enable standard debug events
      raw_debug: true  # Enable ultra-verbose raw API I/O logging
```

## Azure OpenAI

### Prerequisites

1. Azure OpenAI resource deployed
2. GPT model deployment created
3. API key or Azure AD authentication

### Configure

**With API Key:**
```bash
export AZURE_OPENAI_ENDPOINT="https://myresource.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"

amplifier provider use azure-openai
```

**With Azure CLI (Recommended for Development):**
```bash
# Login to Azure
az login

# Configure endpoint
export AZURE_OPENAI_ENDPOINT="https://myresource.openai.azure.com"
export AZURE_USE_DEFAULT_CREDENTIAL="true"

amplifier provider use azure-openai
```

### Deployment Mapping

Azure uses deployment names instead of model names. Configure mapping:

```yaml
providers:
  - module: provider-azure-openai
    config:
      azure_endpoint: "https://myresource.openai.azure.com"
      deployment_mapping:
        "gpt-5.1": "my-gpt5-deployment"
        "gpt-5-mini": "my-mini-deployment"
      default_deployment: "fallback-deployment"
```

### Debug Logging

```yaml
providers:
  - module: provider-azure-openai
    config:
      debug: true      # Enable standard debug events
      raw_debug: true  # Enable ultra-verbose raw API I/O logging
```

## Ollama (Local)

### Prerequisites

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull a model: `ollama pull llama3.2:3b`
3. Start Ollama server (usually auto-starts)

### Configure

```bash
# Set server URL if not default
export OLLAMA_HOST="http://localhost:11434"

amplifier provider use ollama
```

### Available Models

Any model in the Ollama library:

- `llama3.2:3b` - Small, fast
- `llama3.2:1b` - Tiny, fastest
- `mistral` - 7B general purpose
- `deepseek-r1` - Reasoning/thinking
- `qwen3` - Reasoning + tools

See: https://ollama.ai/library

### Advanced Configuration

```yaml
providers:
  - module: provider-ollama
    config:
      host: "http://localhost:11434"
      default_model: "llama3.2:3b"
      auto_pull: true      # Automatically pull missing models
      timeout: 300         # Request timeout (seconds)
      debug: true          # Enable debug logging
```

## vLLM (Self-Hosted)

### Prerequisites

1. vLLM server running (v0.10.1+)
2. Model loaded (e.g., openai/gpt-oss-20b)

### Configure

```yaml
providers:
  - module: provider-vllm
    source: git+https://github.com/microsoft/amplifier-module-provider-vllm@main
    config:
      base_url: "http://192.168.128.5:8000/v1"  # Your vLLM server
      default_model: "openai/gpt-oss-20b"
```

### Advanced Configuration

**Reasoning:**
```yaml
providers:
  - module: provider-vllm
    config:
      reasoning: "high"                 # minimal|low|medium|high
      reasoning_summary: "detailed"     # auto|concise|detailed
```

**Debug Logging:**
```yaml
providers:
  - module: provider-vllm
    config:
      debug: true          # Enable standard debug events
      raw_debug: true      # Enable ultra-verbose raw API I/O logging
```

**State Management:**
```yaml
providers:
  - module: provider-vllm
    config:
      enable_state: false      # Server-side state (requires vLLM config)
      truncation: "auto"       # Automatic context management
```

## Troubleshooting

### No API Key Found

```bash
# Check environment variables
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
echo $AZURE_OPENAI_ENDPOINT

# Set in current session
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Model Not Found

```bash
# For Ollama, pull the model
ollama pull llama3.2:3b

# For Azure, check deployment names match
# For others, check model name spelling
```

### Rate Limits

Configure retry behavior:

```yaml
providers:
  - module: provider-anthropic
    config:
      max_retries: 5
      max_retry_delay: 60.0
```

## Next Steps

- [Module Reference](../modules/providers/index.md) - Complete provider configuration
- [Core Concepts](../architecture/core_concepts.md) - Understanding Amplifier
- [Writing Your First Agent](writing_agents.md) - Build custom agents
