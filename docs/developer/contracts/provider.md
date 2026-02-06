---
title: Provider Contract
description: LLM backend integration contract
---

# Provider Contract

Providers integrate LLM backends into Amplifier.

## Purpose

Providers translate between Amplifier's unified message format and vendor-specific LLM APIs.

## Protocol

```python
from typing import Protocol, runtime_checkable
from amplifier_core.models import ProviderInfo, ModelInfo
from amplifier_core.message_models import ChatRequest, ChatResponse, ToolCall

@runtime_checkable
class Provider(Protocol):
    @property
    def name(self) -> str:
        """Unique provider identifier."""
        ...

    def get_info(self) -> ProviderInfo:
        """Return provider metadata."""
        ...

    async def list_models(self) -> list[ModelInfo]:
        """List available models."""
        ...

    async def complete(
        self,
        request: ChatRequest,
        **kwargs
    ) -> ChatResponse:
        """Complete a chat request."""
        ...

    def parse_tool_calls(
        self,
        response: ChatResponse
    ) -> list[ToolCall]:
        """Extract tool calls from response."""
        ...
```

## Mount Function

```python
async def mount(coordinator, config=None):
    config = config or {}
    
    # Check for required credentials
    api_key = config.get("api_key") or os.environ.get("MY_API_KEY")
    if not api_key:
        # Graceful degradation - don't mount if not configured
        return None
    
    provider = MyProvider(config)
    await coordinator.mount("providers", provider, name=provider.name)
    
    async def cleanup():
        await provider.close()  # Close HTTP connections
    
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

## Related Contracts

- **[Orchestrator Contract](orchestrator.md)** - Orchestrators call providers
- **[Context Contract](context.md)** - Context managers use provider info for budgets

## Authoritative Reference

**→ [Provider Contract](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/PROVIDER_CONTRACT.md)** - Complete specification
