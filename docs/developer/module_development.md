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

## Source of Truth

**Protocols are in code**, not docs:

- **Protocol definitions**: `amplifier_core/interfaces.py`
- **Data models**: `amplifier_core/models.py`
- **Message models**: `amplifier_core/message_models.py` (Pydantic models for request/response envelopes)
- **Content models**: `amplifier_core/content_models.py` (dataclass types for events and streaming)

Always read the code docstrings first - they are authoritative.

## Creating a Tool

Tools provide capabilities to agents.

### Tool Contract

**Protocol definition**: `amplifier_core/interfaces.py` lines 129-152

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

**Data models**:
- `ToolCall` - Input model from `amplifier_core/message_models.py`
- `ToolResult` - Output model from `amplifier_core/models.py`

**Reference implementation**: [amplifier-module-tool-filesystem](https://github.com/microsoft/amplifier-module-tool-filesystem)

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

### Testing Tools

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import MockTool

# Create mock tool for testing orchestrators
mock_tool = MockTool(
    name="test_tool",
    description="Test tool",
    return_value="mock result"
)

# After use
assert mock_tool.call_count == 1
assert mock_tool.last_input == {...}
```

## Creating a Provider

Providers integrate LLM APIs.

### Provider Contract

**Protocol definition**: `amplifier_core/interfaces.py` lines 62-125

**Detailed specification**: See [PROVIDER_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/PROVIDER_SPECIFICATION.md) for complete implementation guidance including:
- Content block preservation requirements
- Role conversion patterns
- Auto-continuation handling
- Debug levels and observability

```python
from amplifier_core.message_models import ChatRequest, ChatResponse
from amplifier_core.models import ProviderInfo, ModelInfo
from typing import Protocol

class Provider(Protocol):
    @property
    def name(self) -> str:
        """Provider identifier."""
        ...

    def get_info(self) -> ProviderInfo:
        """Provider metadata."""
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

    def parse_tool_calls(self, response: ChatResponse) -> list[ToolCall]:
        """Parse tool calls from response."""
        ...
```

**Data models**:
- `ChatRequest`, `ChatResponse` - From `amplifier_core/message_models.py`
- `ProviderInfo`, `ModelInfo` - From `amplifier_core/models.py`
- `ToolCall` - From `amplifier_core/message_models.py`

**Reference implementation**: [amplifier-module-provider-anthropic](https://github.com/microsoft/amplifier-module-provider-anthropic)

### Example Provider

```python
from amplifier_core.message_models import ChatRequest, ChatResponse, Message, Usage
from amplifier_core.models import ProviderInfo, ModelInfo

class MockProvider:
    """Simple mock provider for testing."""

    name = "mock"

    def __init__(self, config: dict):
        self.config = config
        self.default_model = config.get("default_model", "mock-model")

    def get_info(self) -> ProviderInfo:
        """Return provider metadata."""
        return ProviderInfo(
            name=self.name,
            version="1.0.0",
            supported_features=["chat"]
        )

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

    def parse_tool_calls(self, response: ChatResponse) -> list[ToolCall]:
        """Parse tool calls from response."""
        return []  # Mock provider doesn't support tools
```

## Creating a Hook

Hooks intercept events for observability and modification.

### Hook Contract

**Protocol definition**: `amplifier_core/interfaces.py` lines 206-220

**Detailed API reference**: See [HOOKS_API.md](https://github.com/microsoft/amplifier-core/blob/main/docs/HOOKS_API.md) for complete documentation including:
- HookResult actions and fields
- Registration patterns
- Common patterns with examples
- Best practices

```python
from amplifier_core.interfaces import HookHandler
from amplifier_core.models import HookResult
from typing import Protocol, Any

@runtime_checkable
class HookHandler(Protocol):
    async def __call__(self, event: str, data: dict[str, Any]) -> HookResult:
        """
        Handle a lifecycle event.

        Args:
            event: Event name (e.g., "tool:pre", "execution:start")
            data: Event-specific data

        Returns:
            HookResult indicating action to take
        """
        ...
```

**HookResult actions**:
- `continue` - Proceed normally
- `deny` - Block operation
- `modify` - Transform data
- `inject_context` - Add to agent's context
- `ask_user` - Request approval

**Reference implementation**: [amplifier-module-hooks-logging](https://github.com/microsoft/amplifier-module-hooks-logging)

### Example Hook

```python
from amplifier_core.models import HookResult
import logging

logger = logging.getLogger(__name__)

class LoggingHook:
    """Log all events."""

    def __init__(self, config: dict):
        self.config = config
        self.verbose = config.get("verbose", False)

    async def __call__(self, event: str, data: dict) -> HookResult:
        """Log event."""
        if self.verbose:
            logger.info(f"Event: {event}, Data: {data}")
        else:
            logger.info(f"Event: {event}")

        return HookResult(action="continue")
```

### Testing Hooks

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import EventRecorder

# Record events for testing
recorder = EventRecorder()
await recorder.record("tool:pre", {"tool_name": "Write"})

# Assert
events = recorder.get_events()
assert len(events) == 1
assert events[0][0] == "tool:pre"  # events are (event_name, data) tuples
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

**Reference implementations**:
- [amplifier-module-loop-events](https://github.com/microsoft/amplifier-module-loop-events)
- [amplifier-module-loop-streaming](https://github.com/microsoft/amplifier-module-loop-streaming)

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

**Reference implementation**: [amplifier-module-context-simple](https://github.com/microsoft/amplifier-module-context-simple)

## Package Configuration

### pyproject.toml

```toml
[project]
name = "amplifier-module-tool-greet"
version = "0.1.0"
description = "Greeting tool for Amplifier"
requires-python = ">=3.11"
dependencies = []  # amplifier-core is a peer dependency

[project.entry-points."amplifier.modules"]
tool-greet = "amplifier_module_tool_greet:mount"
```

**Important**: Don't declare `amplifier-core` as a runtime dependency. It's a **peer dependency** provided by the runtime environment.

## Testing

```python
import pytest
from amplifier_module_tool_greet import GreetTool
from amplifier_core.testing import TestCoordinator

@pytest.mark.asyncio
async def test_greet():
    """Test greeting tool."""
    tool = GreetTool()
    result = await tool.execute({"name": "Alice"})

    assert result.success
    assert result.output["message"] == "Hello, Alice!"

@pytest.mark.asyncio
async def test_mount():
    """Test tool mounting."""
    coordinator = TestCoordinator()
    cleanup = await mount(coordinator, {})
    
    assert "greet" in coordinator.get_mounted("tools")
    
    if cleanup:
        await cleanup()
```

## Best Practices

1. **Single Responsibility**: Each module does one thing well
2. **Clear Contracts**: Use type hints and protocols
3. **Fail Gracefully**: Return errors, don't crash
4. **Async By Default**: Use async/await for I/O
5. **Minimal Dependencies**: Depend only on what you need (amplifier-core is peer dependency)
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

## Module Types Reference

| Module Type | Contract | Purpose |
|-------------|----------|---------|
| **Provider** | [PROVIDER_CONTRACT.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/PROVIDER_CONTRACT.md) | LLM backend integration |
| **Tool** | [TOOL_CONTRACT.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/TOOL_CONTRACT.md) | Agent capabilities |
| **Hook** | [HOOK_CONTRACT.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/HOOK_CONTRACT.md) | Lifecycle observation and control |
| **Orchestrator** | [ORCHESTRATOR_CONTRACT.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/ORCHESTRATOR_CONTRACT.md) | Agent loop execution strategy |
| **Context** | [CONTEXT_CONTRACT.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/CONTEXT_CONTRACT.md) | Conversation memory management |

## Examples

See official modules for reference implementations:

- **Tools**: [amplifier-module-tool-filesystem](https://github.com/microsoft/amplifier-module-tool-filesystem), [amplifier-module-tool-bash](https://github.com/microsoft/amplifier-module-tool-bash)
- **Providers**: [amplifier-module-provider-anthropic](https://github.com/microsoft/amplifier-module-provider-anthropic)
- **Hooks**: [amplifier-module-hooks-logging](https://github.com/microsoft/amplifier-module-hooks-logging), [amplifier-module-hooks-approval](https://github.com/microsoft/amplifier-module-hooks-approval)
- **Orchestrators**: [amplifier-module-loop-events](https://github.com/microsoft/amplifier-module-loop-events), [amplifier-module-loop-streaming](https://github.com/microsoft/amplifier-module-loop-streaming)

## Resources

- **[Module Contracts](https://github.com/microsoft/amplifier-core/tree/main/docs/contracts)** - Detailed contract specifications
- **[MOUNT_PLAN_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/MOUNT_PLAN_SPECIFICATION.md)** - Configuration contract
- **[MODULE_SOURCE_PROTOCOL.md](https://github.com/microsoft/amplifier-core/blob/main/docs/MODULE_SOURCE_PROTOCOL.md)** - Module loading mechanism
- **[DESIGN_PHILOSOPHY.md](https://github.com/microsoft/amplifier-core/blob/main/docs/DESIGN_PHILOSOPHY.md)** - Kernel design principles
