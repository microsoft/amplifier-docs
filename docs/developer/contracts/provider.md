---
title: Provider Contract
description: LLM backend integration contract
---

# Provider Contract

Providers integrate LLM backends into Amplifier.

## Purpose

Providers translate between Amplifier's unified message format and vendor-specific LLM APIs.

## Detailed Specification

**See [PROVIDER_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/PROVIDER_SPECIFICATION.md)** for complete implementation guidance including:

- Protocol summary and method signatures
- Content block preservation requirements
- Role conversion patterns
- Auto-continuation handling
- Debug levels and observability

This contract document provides the quick-reference essentials. The specification contains the full details.

## Protocol

**Source**: `amplifier_core/interfaces.py` lines 54-119

```python
from typing import Protocol, runtime_checkable
from amplifier_core.models import ProviderInfo, ModelInfo
from amplifier_core.message_models import ChatRequest, ChatResponse, ToolCall

@runtime_checkable
class Provider(Protocol):
    @property
    def name(self) -> str:
        """Provider name."""
        ...

    def get_info(self) -> ProviderInfo:
        """Get provider metadata."""
        ...

    async def list_models(self) -> list[ModelInfo]:
        """List available models."""
        ...

    async def complete(
        self,
        request: ChatRequest,
        **kwargs
    ) -> ChatResponse:
        """Generate completion from ChatRequest."""
        ...

    def parse_tool_calls(
        self,
        response: ChatResponse
    ) -> list[ToolCall]:
        """Parse tool calls from response."""
        ...
```

**Note**: `ToolCall` is from `amplifier_core.message_models` (see [REQUEST_ENVELOPE_V1](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/PROVIDER_SPECIFICATION.md) for details)

## ModelInfo Extensions (Model Class Routing)

The `list_models()` method returns `list[ModelInfo]`. Beyond the required fields (`id`, `display_name`, `context_window`, `max_output_tokens`), ModelInfo supports optional extension fields for model class routing and cost-aware selection:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `cost_per_input_token` | `float \| None` | `None` | Cost per input token in USD (e.g., `3e-6` for $3/MTok) |
| `cost_per_output_token` | `float \| None` | `None` | Cost per output token in USD |
| `metadata` | `dict[str, Any]` | `{}` | Extensible metadata bag for cost tier, model class, provider-specific tags |

### Cost Fields

Providers **SHOULD** populate `cost_per_input_token` and `cost_per_output_token` when pricing information is available. These enable cost-aware model selection and budget tracking.

### Metadata: `cost_tier`

Providers **SHOULD** set `metadata["cost_tier"]` to one of the well-known cost tier strings:

| Tier | Description |
|------|-------------|
| `free` | No-cost models (local, free-tier) |
| `low` | Budget-friendly models (e.g., Haiku-class) |
| `medium` | Standard pricing (e.g., Sonnet-class) |
| `high` | Premium pricing (e.g., Opus-class) |
| `extreme` | Highest-cost models (e.g., deep research) |

### Capabilities

Providers **SHOULD** populate the `capabilities` list using well-known constants from `amplifier_core.capabilities`. See the [Capabilities Taxonomy](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/PROVIDER_SPECIFICATION.md#capabilities-taxonomy) in the Provider Specification for the full list.

### Backward Compatibility

All extension fields are optional with sensible defaults. Existing providers that do not populate these fields continue to work unchanged — they simply won't participate in cost-aware or capability-based routing.

## Mount Function

```python
async def mount(coordinator: ModuleCoordinator, config: dict) -> Provider | Callable | None:
    """
    Initialize and return provider instance.

    Returns:
        - Provider instance (registered automatically)
        - Cleanup callable (for resource cleanup on unmount)
        - None for graceful degradation (e.g., missing API key)
    """
    api_key = config.get("api_key") or os.environ.get("MY_API_KEY")
    if not api_key:
        logger.warning("No API key - provider not mounted")
        return None

    provider = MyProvider(api_key=api_key, config=config)
    await coordinator.mount("providers", provider, name="my-provider")

    async def cleanup():
        await provider.client.close()

    return cleanup
```

## Data Models

### ProviderInfo

```python
@dataclass
class ProviderInfo:
    id: str                      # Unique identifier
    display_name: str            # Human-readable name
    credential_env_vars: list[str]  # Required environment variables
    capabilities: list[str]      # ["streaming", "vision", "tools"]
    defaults: dict               # Default configuration
```

The `defaults` dict should include:
- `context_window`: Maximum input tokens
- `max_output_tokens`: Maximum output tokens

### ModelInfo

```python
@dataclass
class ModelInfo:
    id: str                      # Model identifier
    display_name: str            # Human-readable name
    context_window: int          # Maximum context tokens
    max_output_tokens: int       # Maximum output tokens
    capabilities: list[str]      # Model-specific capabilities
```

## Configuration

Providers receive configuration via Mount Plan:

```yaml
providers:
  - module: my-provider
    source: git+https://github.com/org/my-provider@main
    config:
      api_key: "${MY_API_KEY}"
      default_model: model-v1
      debug: true
```

See [MOUNT_PLAN_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/MOUNT_PLAN_SPECIFICATION.md) for full schema.

Common configuration options:

| Option | Type | Description |
|--------|------|-------------|
| `api_key` | string | API authentication key |
| `default_model` | string | Default model to use |
| `max_tokens` | int | Maximum response tokens |
| `temperature` | float | Sampling temperature |
| `timeout` | float | Request timeout in seconds |

!!! note "Environment Variables"
    Providers should check both config and environment variables for credentials. This allows flexible configuration in different deployment scenarios.

## Events

Providers should emit these events:

| Event | When | Data |
|-------|------|------|
| `llm:request` | Before API call | model, message_count |
| `llm:response` | After API response | usage, duration |
| `llm:request:debug` | Debug logging | Request summary |
| `llm:response:debug` | Debug logging | Response summary |

## Observability

Register custom events via contribution channels:

```python
coordinator.register_contributor(
    "observability.events",
    "my-provider",
    lambda: ["my-provider:rate_limit", "my-provider:retry"]
)
```

See [CONTRIBUTION_CHANNELS.md](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/CONTRIBUTION_CHANNELS.md) for the pattern.

## Example Implementation

```python
import os
import httpx
from amplifier_core.models import ProviderInfo, ModelInfo, ToolResult

class MyProvider:
    name = "my-provider"

    def __init__(self, config):
        self.api_key = config.get("api_key") or os.environ.get("MY_PROVIDER_API_KEY")
        self.default_model = config.get("default_model", "my-model-v1")
        self.timeout = config.get("timeout", 60.0)
        self.base_url = config.get("base_url", "https://api.myprovider.com")
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def close(self):
        await self._client.aclose()

    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            id=self.name,
            display_name="My Provider",
            credential_env_vars=["MY_PROVIDER_API_KEY"],
            capabilities=["streaming", "tools"],
            defaults={
                "context_window": 128000,
                "max_output_tokens": 4096
            }
        )

    async def list_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(
                id="my-model-v1",
                display_name="My Model v1",
                context_window=128000,
                max_output_tokens=4096,
                capabilities=["tools", "streaming"]
            ),
            ModelInfo(
                id="my-model-v2",
                display_name="My Model v2",
                context_window=200000,
                max_output_tokens=8192,
                capabilities=["tools", "streaming", "vision"]
            )
        ]

    async def complete(self, request: ChatRequest, **kwargs) -> ChatResponse:
        model = request.model or self.default_model
        messages = request.messages
        
        # Convert to vendor format
        vendor_messages = self._convert_messages(messages)
        
        # Make API request
        response = await self._client.post(
            f"{self.base_url}/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": model,
                "messages": vendor_messages,
                "max_tokens": request.max_tokens or 4096,
                "temperature": request.temperature or 1.0
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Convert response back
        return self._convert_response(data)

    def parse_tool_calls(self, response: ChatResponse) -> list[ToolCall]:
        """Extract tool calls from response."""
        tool_calls = []
        for block in response.get("content", []):
            if block.get("type") == "tool_use":
                tool_calls.append({
                    "id": block.get("id"),
                    "name": block.get("name"),
                    "input": block.get("input", {})
                })
        return tool_calls

    def _convert_messages(self, messages):
        """Convert Amplifier messages to vendor format."""
        # Implementation depends on vendor API
        return messages

    def _convert_response(self, data):
        """Convert vendor response to Amplifier format."""
        return {
            "content": [{"type": "text", "text": data["choices"][0]["message"]["content"]}],
            "usage": {
                "input_tokens": data["usage"]["prompt_tokens"],
                "output_tokens": data["usage"]["completion_tokens"],
                "total_tokens": data["usage"]["total_tokens"]
            }
        }
```

## Graceful Degradation

Providers should handle missing credentials gracefully:

```python
async def mount(coordinator, config=None):
    config = config or {}
    
    api_key = config.get("api_key") or os.environ.get("MY_API_KEY")
    if not api_key:
        # Return None to indicate provider not available
        # Don't raise - let the system continue without this provider
        return None
    
    provider = MyProvider(config)
    await coordinator.mount("providers", provider, name=provider.name)
    return provider.close
```

## Retry and Validation

Providers should implement appropriate retry logic:

```python
import asyncio
from httpx import HTTPStatusError

async def complete(self, request, **kwargs) -> dict:
    max_retries = 3
    retry_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            return await self._make_request(request)
        except HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limited
                await asyncio.sleep(retry_delay * (2 ** attempt))
                continue
            raise
    
    raise Exception("Max retries exceeded")
```

## Validation Checklist

### Required

- [ ] Implements all 5 Provider protocol methods
- [ ] `mount()` function with entry point in pyproject.toml
- [ ] Preserves all content block types (especially `signature` in ThinkingBlock)
- [ ] Reports `Usage` (input/output/total tokens)
- [ ] Returns `ChatResponse` from `complete()`

### Recommended

- [ ] Graceful degradation on missing config (return None from mount)
- [ ] Validates tool call/result sequences
- [ ] Supports debug configuration flags
- [ ] Registers cleanup function for resource management
- [ ] Registers observability events via contribution channels

## Testing

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import TestCoordinator, create_test_coordinator

@pytest.mark.asyncio
async def test_provider_mount():
    coordinator = create_test_coordinator()
    cleanup = await mount(coordinator, {"api_key": "test-key"})

    assert "my-provider" in coordinator.get_mounted("providers")

    if cleanup:
        await cleanup()
```

## Quick Validation Command

```bash
# Structural validation
amplifier module validate ./my-provider --type provider
```

## Related Contracts

- **[Orchestrator Contract](orchestrator.md)** - Orchestrators call providers
- **[Context Contract](context.md)** - Context managers use provider info for budgets

## Canonical Example

**Reference implementation**: [amplifier-module-provider-anthropic](https://github.com/microsoft/amplifier-module-provider-anthropic)

Study this module for:
- Complete Provider protocol implementation
- Content block handling patterns
- Configuration and credential management
- Debug logging integration

## Authoritative Reference

**→ [Provider Contract](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/PROVIDER_CONTRACT.md)** - Complete specification

**→ [PROVIDER_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/PROVIDER_SPECIFICATION.md)** - Detailed implementation guidance
