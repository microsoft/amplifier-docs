---
title: Providers
description: LLM backend integrations
---

# Providers

Providers integrate LLM backends into Amplifier. They translate between Amplifier's unified message format and vendor-specific APIs.

## Available Providers

| Provider | Description | Repository |
|----------|-------------|------------|
| **[Anthropic](anthropic.md)** | Claude models | [GitHub](https://github.com/microsoft/amplifier-module-provider-anthropic) |
| **[OpenAI](openai.md)** | GPT models | [GitHub](https://github.com/microsoft/amplifier-module-provider-openai) |
| **[Azure OpenAI](azure.md)** | Azure-hosted GPT | [GitHub](https://github.com/microsoft/amplifier-module-provider-azure-openai) |
| **[Ollama](ollama.md)** | Local models | [GitHub](https://github.com/microsoft/amplifier-module-provider-ollama) |

<!-- MODULE_LIST_PROVIDER -->

## Configuration

All providers support common configuration:

```yaml
providers:
  - module: provider-anthropic
    source: git+https://github.com/microsoft/amplifier-module-provider-anthropic@main
    config:
      api_key: ${ANTHROPIC_API_KEY}
      default_model: claude-sonnet-4-5
      max_tokens: 8192
      temperature: 1.0
```

## Switching Providers

```bash
# Via CLI
amplifier provider use openai

# Via profile
amplifier run --provider ollama "Hello"
```

## Contract

See [Provider Contract](../../developer/contracts/provider.md) for implementation details.
