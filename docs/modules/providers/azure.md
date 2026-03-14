---
title: Azure OpenAI Provider
description: Azure-hosted GPT models
---

# Azure OpenAI Provider

Integrates Azure OpenAI Service into Amplifier.

## Module ID

`provider-azure-openai`

## Installation

```yaml
providers:
  - module: provider-azure-openai
    source: git+https://github.com/microsoft/amplifier-module-provider-azure-openai@main
    config:
      azure_endpoint: https://your-resource.openai.azure.com
      deployment_name: your-deployment-name
```

## Authentication

The provider supports three authentication methods:

### API Key (Default)

```yaml
config:
  azure_endpoint: https://your-resource.openai.azure.com
  api_key: ${AZURE_OPENAI_API_KEY}
```

Or via environment variable:
```bash
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
```

### Managed Identity

For Azure-hosted environments (VMs, App Service, AKS, etc.), use managed identity for passwordless authentication.

!!! note "Prerequisite"
    Requires the `azure-identity` package: `pip install azure-identity`

=== "System-Assigned Identity"

    ```yaml
    config:
      azure_endpoint: https://your-resource.openai.azure.com
      use_managed_identity: true
    ```

    Or via environment:
    ```bash
    export AZURE_USE_MANAGED_IDENTITY=true
    ```

=== "User-Assigned Identity"

    ```yaml
    config:
      azure_endpoint: https://your-resource.openai.azure.com
      use_managed_identity: true
      managed_identity_client_id: your-client-id
    ```

    Or via environment:
    ```bash
    export AZURE_USE_MANAGED_IDENTITY=true
    export AZURE_MANAGED_IDENTITY_CLIENT_ID="your-client-id"
    ```

### Default Azure Credential

Uses the Azure SDK's `DefaultAzureCredential` chain (CLI, environment, managed identity fallback):

```yaml
config:
  azure_endpoint: https://your-resource.openai.azure.com
  use_default_credential: true
```

Or via environment:
```bash
export AZURE_USE_DEFAULT_CREDENTIAL=true
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `azure_endpoint` | string | `$AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource endpoint |
| `api_key` | string | `$AZURE_OPENAI_API_KEY` | API key (if using key auth) |
| `api_version` | string | `2024-10-01-preview` | Azure API version |
| `deployment_name` | string | null | Azure deployment name (maps to model) |
| `default_model` | string | `gpt-5.4` | Default model name |
| `max_tokens` | integer | `4096` | Maximum output tokens |
| `temperature` | float | null | Sampling temperature |
| `reasoning` | string | null | Reasoning effort: `minimal\|low\|medium\|high` |
| `reasoning_summary` | string | `detailed` | Reasoning verbosity: `auto\|concise\|detailed` |
| `truncation` | string | `auto` | Automatic context management |
| `enable_state` | boolean | `false` | Enable stateful conversations |
| `use_managed_identity` | boolean | `false` | Use Azure Managed Identity |
| `use_default_credential` | boolean | `false` | Use DefaultAzureCredential |
| `managed_identity_client_id` | string | null | Client ID for user-assigned identity |
| `debug` | boolean | `false` | Enable standard debug events |
| `raw_debug` | boolean | `false` | Enable ultra-verbose raw API I/O logging |
| `timeout` | float | 600.0 | API timeout in seconds |
| `max_retries` | int | 5 | Retry attempts before failing |

## Deployment Mapping

Azure uses deployment names instead of model names. Map them:

```yaml
providers:
  - module: provider-azure-openai
    config:
      azure_endpoint: https://your-resource.openai.azure.com
      deployment_name: my-gpt5-deployment
      default_model: gpt-5.4
```

Or use environment variables:
```bash
export AZURE_OPENAI_DEPLOYMENT_NAME="my-gpt5-deployment"
```

## Reasoning Configuration

Control reasoning effort and verbosity:

```yaml
providers:
  - module: provider-azure-openai
    config:
      reasoning: "medium"
      reasoning_summary: "detailed"
```

## Tool Calling

Supports OpenAI Responses API tool calling:

```yaml
providers:
  - module: provider-azure-openai
    config:
      azure_endpoint: https://your-resource.openai.azure.com
      deployment_name: my-deployment
```

Tools are automatically available when declared in your configuration.

## Environment Variables

```bash
# Required
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"

# Authentication (choose one)
export AZURE_OPENAI_API_KEY="your-api-key"
# OR
export AZURE_USE_MANAGED_IDENTITY=true
# OR
export AZURE_USE_DEFAULT_CREDENTIAL=true

# Optional
export AZURE_OPENAI_API_VERSION="2024-10-01-preview"
export AZURE_OPENAI_DEPLOYMENT_NAME="my-deployment"
export AZURE_OPENAI_DEFAULT_MODEL="gpt-5.1-codex"
```

## Example Configuration

### API Key Authentication

```yaml
providers:
  - module: provider-azure-openai
    source: git+https://github.com/microsoft/amplifier-module-provider-azure-openai@main
    config:
      azure_endpoint: https://myresource.openai.azure.com
      api_key: ${AZURE_OPENAI_API_KEY}
      deployment_name: my-gpt5-deployment
      default_model: gpt-5.4
      max_tokens: 4096
```

### Managed Identity Authentication

```yaml
providers:
  - module: provider-azure-openai
    source: git+https://github.com/microsoft/amplifier-module-provider-azure-openai@main
    config:
      azure_endpoint: https://myresource.openai.azure.com
      use_managed_identity: true
      deployment_name: my-gpt5-deployment
      default_model: gpt-5.4
```

### DefaultAzureCredential (Development)

```yaml
providers:
  - module: provider-azure-openai
    source: git+https://github.com/microsoft/amplifier-module-provider-azure-openai@main
    config:
      azure_endpoint: https://myresource.openai.azure.com
      use_default_credential: true
      deployment_name: my-gpt5-deployment
      default_model: gpt-5.4
```
