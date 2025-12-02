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

## Configuration Reference

| Option | Type | Env Var | Description |
|--------|------|---------|-------------|
| `azure_endpoint` | string | `AZURE_OPENAI_ENDPOINT` | Azure resource endpoint URL |
| `api_key` | string | `AZURE_OPENAI_API_KEY` | API key (if not using managed identity) |
| `api_version` | string | `AZURE_OPENAI_API_VERSION` | API version (default: `2024-10-01-preview`) |
| `deployment_name` | string | - | Default deployment name |
| `use_managed_identity` | boolean | `AZURE_USE_MANAGED_IDENTITY` | Enable managed identity auth |
| `managed_identity_client_id` | string | `AZURE_MANAGED_IDENTITY_CLIENT_ID` | Client ID for user-assigned identity |
| `use_default_credential` | boolean | `AZURE_USE_DEFAULT_CREDENTIAL` | Use DefaultAzureCredential chain |

## Capabilities

- Streaming responses
- Tool/function calling
- Vision (image inputs)
- Reasoning models
- Batch processing
- JSON mode

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-provider-azure-openai)**
