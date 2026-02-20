---
title: Module Development
description: Creating custom Amplifier modules
---

# Module Development

This guide covers creating custom modules for Amplifier: providers, tools, hooks, orchestrators, and context managers.

## Module Structure

Every module follows the same structure:

```
amplifier-module-{type}-{name}/
├── amplifier_module_{type}_{name}/
│   └── __init__.py         # Module code with mount() function
├── tests/
│   └── test_module.py      # Tests
├── pyproject.toml          # Package configuration with entry point
├── README.md               # Documentation
└── LICENSE
```

## The Mount Function

Every module exposes a `mount` function:

```python
from typing import Any, Callable

async def mount(
    coordinator: "ModuleCoordinator",
    config: dict
) -> Callable | None:
    """
    Mount the module.

    Args:
        coordinator: Infrastructure context from kernel
        config: Configuration from Mount Plan

    Returns:
        Optional cleanup function (async callable) or None for graceful degradation
    """
    config = config or {}

    # Create your module instance
    module = MyModule(config)

    # Mount to appropriate mount point
    await coordinator.mount("tools", module, name="my-tool")

    # Optional: return cleanup function
    async def cleanup():
        await module.close()

    return cleanup
```

## Creating a Tool

Tools provide capabilities to agents.

### Tool Contract

```python
from amplifier_core.interfaces import Tool
from amplifier_core.models import ToolResult
from typing import runtime_checkable, Protocol, Any

@runtime_checkable
class Tool(Protocol):
    @property
    def name(self) -> str:
        """Unique identifier."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description."""
        ...

    async def execute(self, input: dict[str, Any]) -> ToolResult:
        """Execute the tool with input data."""
        ...
```

### Example Tool

```python
from amplifier_core import ToolResult
import logging

logger = logging.getLogger(__name__)

class GreetTool:
    """Simple greeting tool."""

    @property
    def name(self) -> str:
        return "greet"

    @property
    def description(self) -> str:
        return "Greet a person by name"

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name to greet"
                }
            },
            "required": ["name"]
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Execute greeting."""
        try:
            name = input_data.get("name", "World")
            message = f"Hello, {name}!"

            return ToolResult(
                success=True,
                output={"message": message}
            )
        except Exception as e:
            logger.error(f"Greeting failed: {e}")
            return ToolResult(
                success=False,
                error={"message": str(e)}
            )
```

### Mount Function for Tool

```python
async def mount(coordinator, config: dict | None = None):
    """Mount the greet tool."""
    config = config or {}
    tool = GreetTool()
    await coordinator.mount("tools", tool, name="greet")
    logger.info("Mounted GreetTool")
    return None  # No cleanup needed
```

## Creating a Provider

Providers integrate LLM APIs.

### Provider Contract

```python
from amplifier_core.message_models import ChatRequest, ChatResponse
from typing import Protocol

class Provider(Protocol):
    @property
    def name(self) -> str:
        """Provider identifier."""
        ...

    async def complete(
        self,
        request: ChatRequest,
        **kwargs
    ) -> ChatResponse:
        """Generate completion from ChatRequest."""
        ...

    async def list_models(self) -> list[ModelInfo]:
        """List available models."""
        ...
```

### Example Provider

```python
from amplifier_core.message_models import ChatRequest, ChatResponse, Message, Usage

class MockProvider:
    """Simple mock provider for testing."""

    name = "mock"

    def __init__(self, config: dict):
        self.config = config
        self.default_model = config.get("default_model", "mock-model")

    async def complete(
        self,
        request: ChatRequest,
        **kwargs
    ) -> ChatResponse:
        """Return mock response."""
        return ChatResponse(
            content="Mock response",
            usage=Usage(
                input_tokens=10,
                output_tokens=5,
                total_tokens=15
            ),
            finish_reason="stop"
        )

    async def list_models(self):
        """Return mock model list."""
        return [
            ModelInfo(
                id="mock-model",
                display_name="Mock Model",
                context_window=8192,
                max_output_tokens=4096
            )
        ]
```

## Creating a Hook

Hooks intercept events for observability and modification.

### Hook Contract

```python
from typing import Protocol, Any

class Hook(Protocol):
    async def on_event(
        self,
        event: str,
        data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Handle an event.

        Args:
            event: Event name (e.g., "tool:pre")
            data: Event data

        Returns:
            Modified data or None to pass through unchanged
        """
        ...
```

### Example Hook

```python
import logging

logger = logging.getLogger(__name__)

class LoggingHook:
    """Log all events."""

    def __init__(self, config: dict):
        self.config = config
        self.verbose = config.get("verbose", False)

    async def on_event(self, event: str, data: dict) -> dict | None:
        """Log event."""
        if self.verbose:
            logger.info(f"Event: {event}, Data: {data}")
        else:
            logger.info(f"Event: {event}")

        return None  # Pass through unchanged
```

## Creating an Orchestrator

Orchestrators control the agent loop.

### Orchestrator Contract

```python
from typing import Protocol, Any

class Orchestrator(Protocol):
    async def execute(
        self,
        prompt: str,
        context: Any,
        providers: dict[str, Any],
        tools: dict[str, Any],
        hooks: Any,
        coordinator: Any | None = None
    ) -> str:
        """
        Execute agent loop.

        Args:
            prompt: User input
            context: Context manager
            providers: Available providers
            tools: Available tools
            hooks: Hook registry
            coordinator: Module coordinator

        Returns:
            Final response string
        """
        ...
```

## Creating a Context Manager

Context managers handle conversation history.

### Context Contract

```python
from typing import Protocol, Any

class Context(Protocol):
    async def add_message(self, message: dict[str, Any]) -> None:
        """Add message to context."""
        ...

    async def get_messages(self) -> list[dict[str, Any]]:
        """Get all messages."""
        ...

    async def get_messages_for_request(self) -> list[dict[str, Any]]:
        """Get messages formatted for LLM request."""
        ...
```

## Package Configuration

### pyproject.toml

```toml
[project]
name = "amplifier-module-tool-greet"
version = "0.1.0"
description = "Greeting tool for Amplifier"
requires-python = ">=3.11"
dependencies = [
    "amplifier-core>=1.0.0"
]

[project.entry-points."amplifier.modules"]
tool-greet = "amplifier_module_tool_greet:mount"
```

## Testing

```python
import pytest
from amplifier_module_tool_greet import GreetTool

@pytest.mark.asyncio
async def test_greet():
    """Test greeting tool."""
    tool = GreetTool()
    result = await tool.execute({"name": "Alice"})

    assert result.success
    assert result.output["message"] == "Hello, Alice!"
```

## Best Practices

1. **Single Responsibility**: Each module does one thing well
2. **Clear Contracts**: Use type hints and protocols
3. **Fail Gracefully**: Return errors, don't crash
4. **Async By Default**: Use async/await for I/O
5. **Minimal Dependencies**: Depend only on amplifier-core
6. **Test Coverage**: Unit tests for core functionality
7. **Documentation**: Clear README with examples

## Publishing

```bash
# Build package
uv build

# Publish to PyPI
uv publish

# Or install from git
uv pip install git+https://github.com/user/amplifier-module-tool-greet@main
```

## Examples

See official modules for reference implementations:

- **Tools**: [amplifier-module-tool-bash](https://github.com/microsoft/amplifier-module-tool-bash)
- **Providers**: [amplifier-module-provider-anthropic](https://github.com/microsoft/amplifier-module-provider-anthropic)
- **Hooks**: [amplifier-module-hooks-logging](https://github.com/microsoft/amplifier-module-hooks-logging)
- **Orchestrators**: [amplifier-module-loop-events](https://github.com/microsoft/amplifier-module-loop-events)

## Resources

- [Module Contracts](./contracts/index.md) - Detailed contract specifications
- [Core API Reference](./api/core.md) - amplifier-core API documentation
- [Architecture Overview](../architecture/index.md) - System architecture
