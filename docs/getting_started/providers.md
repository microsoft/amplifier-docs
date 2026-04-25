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
| **OpenAI** | GPT-5.5, GPT-5-mini, GPT-5-nano | Broad capabilities, function calling |
| **Azure OpenAI** | GPT-5.4 via Azure | Enterprise, compliance requirements |
| **Ollama** | Llama, Mistral, etc. | Local/offline, privacy, experimentation |

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
      max_tokens: 8192  # Output tokens remain separate from context window
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

# Or add to shell profile
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc

# Select as provider
amplifier provider use openai
```

### Available Models

| Model | Description |
|-------|-------------|
| `gpt-5.5` | Optimized for code, recommended (default) |
| `gpt-5-mini` | Smaller, faster GPT-5 |
| `gpt-5-nano` | Smallest GPT-5 variant |

```bash
# Use a specific model
amplifier run --model gpt-5.5 "Complex analysis task"
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
      reasoning: "low"              # Reasoning effort: none|low|medium|high|xhigh
      reasoning_summary: "detailed" # Reasoning verbosity: auto|concise|detailed
```

**Automatic Context Management:**
```yaml
providers:
  - module: provider-openai
    config:
      truncation: "auto"  # Automatic context management (default: "auto")
      # OR
      truncation: null    # Disables automatic truncation (manual control)
```

## Azure OpenAI

### Prerequisites

1. Azure subscription
2. Azure OpenAI resource created
3. Model deployment created

### Configure

**With API Key:**
```bash
# Set environment variables
export AZURE_OPENAI_ENDPOINT="https://myresource.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key-here"
export AZURE_OPENAI_DEFAULT_MODEL="gpt-5.4"

# Select as provider
amplifier provider use azure-openai
```

**With DefaultAzureCredential (Recommended):**
```bash
# Login to Azure
az login

# Set environment variables
export AZURE_OPENAI_ENDPOINT="https://myresource.openai.azure.com"
export AZURE_USE_DEFAULT_CREDENTIAL="true"
export AZURE_OPENAI_DEFAULT_MODEL="gpt-5.4"

# Select as provider
amplifier provider use azure-openai
```

### Deployment Mapping

Azure uses deployment names instead of model names:

```yaml
providers:
  - module: provider-azure-openai
    config:
      azure_endpoint: "https://myresource.openai.azure.com"
      api_key: "${AZURE_OPENAI_API_KEY}"
      deployment_mapping:
        "gpt-5.4": "my-gpt5-deployment"
        "gpt-5-mini": "my-mini-deployment"
      default_deployment: "fallback-deployment"
```

### Advanced Configuration

**Debug Logging:**
```yaml
providers:
  - module: provider-azure-openai
    config:
      debug: true      # Enable standard debug events
      raw_debug: true  # Enable ultra-verbose raw API I/O logging
```

**Managed Identity:**
```yaml
providers:
  - module: provider-azure-openai
    config:
      azure_endpoint: "https://myresource.openai.azure.com"
      use_managed_identity: true
      # Optional: for user-assigned managed identity
      managed_identity_client_id: "client-id-here"
```

## Ollama (Local Models)

### Prerequisites

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3.2:3b`
3. Start Ollama server (usually automatic)

### Configure

```bash
# Set environment variable (optional, defaults to localhost)
export OLLAMA_HOST="http://localhost:11434"

# Select as provider
amplifier provider use ollama
```

### Available Models

Any model from https://ollama.ai/library:

| Model | Description |
|-------|-------------|
| `llama3.2:3b` | Small, fast (recommended) |
| `llama3.2:1b` | Tiny, fastest |
| `mistral` | 7B general purpose |
| `codellama` | Code generation |
| `deepseek-r1` | Reasoning/thinking |
| `qwen3` | Reasoning + tools |

```bash
# Use a specific model
amplifier run --model llama3.2:3b "Explain this code"
```

### Advanced Configuration

**Debug Logging:**
```yaml
providers:
  - module: provider-ollama
    config:
      debug: true      # Enable standard debug events
      raw_debug: true  # Enable ultra-verbose raw API I/O logging
```

**Auto-pull Models:**
```yaml
providers:
  - module: provider-ollama
    config:
      host: "http://localhost:11434"
      default_model: "llama3.2:3b"
      auto_pull: true  # Automatically pull missing models
      timeout: 300     # Request timeout in seconds (default: 5 minutes)
```

**Thinking/Reasoning:**
```yaml
providers:
  - module: provider-ollama
    config:
      default_model: "deepseek-r1"  # Or qwen3, qwq, phi4-reasoning
      # Enable thinking in ChatRequest with enable_thinking=True
```

## Troubleshooting

### Common Issues

**Anthropic:**
- Invalid API key → Check `ANTHROPIC_API_KEY` format
- Rate limits → Adjust retry configuration
- 529 Overloaded → Provider retries automatically with 10x backoff

**OpenAI:**
- Invalid API key → Check `OPENAI_API_KEY` format
- Incomplete responses → Provider auto-continues up to 5 attempts
- Context limits → Enable `truncation: "auto"` for automatic management

**Azure OpenAI:**
- Authentication errors → Verify endpoint URL and credentials
- Deployment not found → Check deployment name mapping
- WSL2 + Managed Identity → Use `DefaultAzureCredential` instead

**Ollama:**
- Server offline → Check `ollama serve` is running
- Model not found → Run `ollama pull <model>` or enable `auto_pull`
- Connection issues → Verify `OLLAMA_HOST` or `host` config

### Debug Mode

Enable debug logging to see detailed request/response information:

```yaml
providers:
  - module: provider-anthropic  # or provider-openai, provider-azure-openai, provider-ollama
    config:
      debug: true      # Standard debug events
      raw_debug: true  # Ultra-verbose raw API I/O (use sparingly)
```

## Next Steps

- [Configure Tools](../tools/index.md) - Add capabilities to your agent
- [Session Management](../user_guide/sessions.md) - Manage conversation history
- [Profiles](../profiles/index.md) - Create reusable configurations
