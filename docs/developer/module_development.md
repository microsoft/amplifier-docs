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
    config: dict[str, Any] | None = None
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

class Tool:
    name: str               # Unique identifier
    description: str        # Human-readable description

    async def execute(self, input: dict[str, Any]) -> ToolResult:
        """Execute the tool with given input."""
        ...
```

### Example: Calculator Tool

```python
# amplifier_module_tool_calculator/__init__.py

from typing import Any
from amplifier_core.models import ToolResult

async def mount(coordinator, config=None):
    tool = CalculatorTool(config or {})
    await coordinator.mount("tools", tool, name="calculator")
    return None

class CalculatorTool:
    name = "calculator"
    description = "Perform mathematical calculations"
    input_schema = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate"
            }
        },
        "required": ["expression"]
    }

    def __init__(self, config: dict):
        self.config = config

    async def execute(self, input: dict[str, Any]) -> ToolResult:
        expression = input.get("expression", "")
        try:
            # Safe evaluation (in production, use proper parser)
            result = eval(expression, {"__builtins__": {}}, {})
            return ToolResult(
                success=True,
                output=str(result)
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error={"message": str(e), "type": type(e).__name__}
            )
```

### pyproject.toml

```toml
[project]
name = "amplifier-module-tool-calculator"
version = "1.0.0"
description = "Calculator tool for Amplifier"
requires-python = ">=3.11"
dependencies = []

[project.entry-points."amplifier.modules"]
tool-calculator = "amplifier_module_tool_calculator:mount"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["amplifier_module_tool_calculator"]
```

## Creating a Provider

Providers integrate LLM backends.

### Provider Contract

```python
from amplifier_core.interfaces import Provider
from amplifier_core.models import ProviderInfo, ModelInfo
from amplifier_core.message_models import ChatRequest, ChatResponse, ToolCall

class Provider:
    name: str

    def get_info(self) -> ProviderInfo: ...
    async def list_models(self) -> list[ModelInfo]: ...
    async def complete(self, request: ChatRequest, **kwargs) -> ChatResponse: ...
    def parse_tool_calls(self, response: ChatResponse) -> list[ToolCall]: ...
```

### Example: Mock Provider

```python
from amplifier_core.models import ProviderInfo, ModelInfo

async def mount(coordinator, config=None):
    config = config or {}
    api_key = config.get("api_key")
    if not api_key:
        # Graceful degradation - return None if not configured
        return None
    
    provider = MockProvider(config)
    await coordinator.mount("providers", provider, name="mock")
    
    async def cleanup():
        pass  # Close any connections
    
    return cleanup

class MockProvider:
    name = "mock"

    def __init__(self, config):
        self.response = config.get("response", "Mock response")
        self.default_model = config.get("default_model", "mock-model")

    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            id="mock",
            display_name="Mock Provider",
            credential_env_vars=[],
            capabilities=["streaming"],
            defaults={
                "context_window": 100000,
                "max_output_tokens": 4096
            }
        )

    async def list_models(self) -> list[ModelInfo]:
        return [ModelInfo(
            id="mock-model",
            display_name="Mock Model",
            context_window=100000,
            max_output_tokens=4096,
            capabilities=["tools"]
        )]

    async def complete(self, request, **kwargs):
        return {
            "content": [{"type": "text", "text": self.response}],
            "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}
        }

    def parse_tool_calls(self, response):
        return []
```

## Creating a Hook

Hooks observe and control operations.

### Hook Contract

```python
from amplifier_core.models import HookResult

async def handler(event: str, data: dict) -> HookResult:
    """Handle an event."""
    return HookResult(action="continue")
```

### HookResult Actions

| Action | Effect |
|--------|--------|
| `continue` | Proceed normally |
| `deny` | Block the operation |
| `modify` | Modify event data |
| `inject_context` | Add to conversation |
| `ask_user` | Request approval |

### Example: Timing Hook

```python
import time
from amplifier_core.models import HookResult

async def mount(coordinator, config=None):
    handler = TimingHook(config or {})

    # Register for specific events
    coordinator.hooks.register("tool:pre", handler.on_tool_pre, priority=10)
    coordinator.hooks.register("tool:post", handler.on_tool_post, priority=10)

    def cleanup():
        # Unregister handlers if needed
        pass

    return cleanup

class TimingHook:
    def __init__(self, config):
        self.timings = {}
        self.debug = config.get("debug", False)

    async def on_tool_pre(self, event, data) -> HookResult:
        tool_name = data.get("tool_name")
        self.timings[tool_name] = time.time()
        return HookResult(action="continue")

    async def on_tool_post(self, event, data) -> HookResult:
        tool_name = data.get("tool_name")
        if tool_name in self.timings:
            duration = time.time() - self.timings[tool_name]
            if self.debug:
                return HookResult(
                    action="continue",
                    user_message=f"Tool {tool_name} took {duration:.2f}s",
                    user_message_level="info"
                )
        return HookResult(action="continue")
```

## Creating an Orchestrator

Orchestrators control execution flow.

### Orchestrator Contract

```python
from amplifier_core.interfaces import Orchestrator, ContextManager, Provider, Tool
from amplifier_core.hooks import HookRegistry

class Orchestrator:
    async def execute(
        self,
        prompt: str,
        context: ContextManager,
        providers: dict[str, Provider],
        tools: dict[str, Tool],
        hooks: HookRegistry,
    ) -> str:
        """Execute the orchestration loop."""
        ...
```

### Example: Simple Orchestrator

```python
async def mount(coordinator, config=None):
    orchestrator = SimpleOrchestrator(config or {})
    await coordinator.mount("session", orchestrator, name="orchestrator")
    return None

class SimpleOrchestrator:
    def __init__(self, config):
        self.max_iterations = config.get("max_iterations", 10)

    async def execute(self, prompt, context, providers, tools, hooks):
        # Add user message
        await context.add_message({"role": "user", "content": prompt})

        # Get first provider
        provider = list(providers.values())[0]
        iteration = 0

        for iteration in range(self.max_iterations):
            # Get messages (context handles compaction internally)
            messages = await context.get_messages_for_request(provider=provider)

            # Call provider
            await hooks.emit("provider:request", {"messages": messages})
            response = await provider.complete({"messages": messages})
            await hooks.emit("provider:response", {"response": response})

            # Add response to context
            await context.add_message({
                "role": "assistant",
                "content": response["content"]
            })

            # Check for tool calls
            tool_calls = provider.parse_tool_calls(response)
            if not tool_calls:
                # Emit orchestrator:complete event (REQUIRED)
                await hooks.emit("orchestrator:complete", {
                    "orchestrator": "simple",
                    "turn_count": iteration + 1,
                    "status": "success"
                })
                return response["content"][0]["text"]

            # Execute tools
            for call in tool_calls:
                tool = tools.get(call["name"])
                if tool:
                    await hooks.emit("tool:pre", {"tool_name": call["name"]})
                    result = await tool.execute(call["input"])
                    await hooks.emit("tool:post", {"result": result})
                    await context.add_message({
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": result.get_serialized_output()
                    })

        # Emit orchestrator:complete for max iterations case
        await hooks.emit("orchestrator:complete", {
            "orchestrator": "simple",
            "turn_count": iteration + 1,
            "status": "incomplete"
        })
        return "Max iterations reached"
```

## Creating a Context Manager

Context managers handle conversation memory.

### Context Contract

```python
from amplifier_core.interfaces import ContextManager

class ContextManager:
    async def add_message(self, message: dict) -> None: ...
    async def get_messages_for_request(
        self, token_budget: int | None = None, provider: Any | None = None
    ) -> list[dict]: ...
    async def get_messages(self) -> list[dict]: ...
    async def set_messages(self, messages: list[dict]) -> None: ...
    async def clear(self) -> None: ...
```

### Example: Simple Context

```python
async def mount(coordinator, config=None):
    context = SimpleContext(config or {})
    await coordinator.mount("session", context, name="context")
    return context

class SimpleContext:
    def __init__(self, config):
        self.max_tokens = config.get("max_tokens", 100000)
        self.messages = []

    async def add_message(self, message):
        self.messages.append(message)

    async def get_messages_for_request(self, token_budget=None, provider=None):
        """Return messages for LLM request, compacting internally if needed."""
        budget = self._calculate_budget(token_budget, provider)
        # Ephemeral compaction - don't modify stored messages
        if self._estimate_tokens() > budget * 0.9:
            return self._compact_messages(budget)
        return list(self.messages)

    async def get_messages(self):
        """Return full history (no compaction)."""
        return list(self.messages)

    async def set_messages(self, messages):
        self.messages = list(messages)

    async def clear(self):
        self.messages = []

    def _calculate_budget(self, token_budget, provider):
        if token_budget:
            return token_budget
        if provider:
            info = provider.get_info()
            defaults = info.defaults or {}
            context_window = defaults.get("context_window", self.max_tokens)
            max_output = defaults.get("max_output_tokens", 4096)
            return context_window - max_output - 1000
        return self.max_tokens

    def _estimate_tokens(self):
        total_chars = sum(len(str(m.get("content", ""))) for m in self.messages)
        return total_chars // 4

    def _compact_messages(self, budget):
        """Return compacted view without modifying internal state."""
        # Keep system messages and recent messages
        system = [m for m in self.messages if m["role"] == "system"]
        other = [m for m in self.messages if m["role"] != "system"]
        # Simple truncation strategy
        while self._estimate_tokens_for(system + other) > budget * 0.7 and other:
            other.pop(0)
        return system + other

    def _estimate_tokens_for(self, messages):
        return sum(len(str(m.get("content", ""))) for m in messages) // 4
```

## Observability

Modules can register observable events:

```python
async def mount(coordinator, config=None):
    # Declare events your module emits
    coordinator.register_contributor(
        "observability.events",
        "my-module",
        lambda: ["my-module:started", "my-module:completed", "my-module:error"]
    )
    
    # Later, emit events
    await coordinator.hooks.emit("my-module:started", {"version": "1.0.0"})
```

## Configuration

Modules receive configuration from Mount Plans:

```yaml
tools:
  - module: my-tool
    source: git+https://github.com/org/my-tool@main
    config:
      max_size: 1048576
      debug: true
      allowed_paths:
        - /home/user/projects
```

Configuration values can reference environment variables:

```yaml
config:
  api_key: "${MY_API_KEY}"
```

## Testing Modules

### Unit Testing

```python
import pytest
from amplifier_module_tool_calculator import CalculatorTool

@pytest.fixture
def tool():
    return CalculatorTool({})

@pytest.mark.asyncio
async def test_addition(tool):
    result = await tool.execute({"expression": "2 + 2"})
    assert result.success is True
    assert result.output == "4"

@pytest.mark.asyncio
async def test_invalid_expression(tool):
    result = await tool.execute({"expression": "invalid"})
    assert result.success is False
    assert result.error is not None
```

### Integration Testing

```python
from amplifier_core.testing import TestCoordinator, MockContextManager

@pytest.mark.asyncio
async def test_mount():
    coordinator = TestCoordinator()

    from amplifier_module_tool_calculator import mount
    cleanup = await mount(coordinator, {})

    assert "calculator" in coordinator.tools
    assert coordinator.tools["calculator"].name == "calculator"
```

## Publishing Modules

### To GitHub

```bash
# Create repository
gh repo create amplifier-module-tool-myname --public

# Push code
git init
git add .
git commit -m "Initial commit"
git push -u origin main
```

### Using Your Module

```yaml
# In bundle or mount plan
tools:
  - module: tool-myname
    source: git+https://github.com/yourname/amplifier-module-tool-myname@main
```

## Best Practices

1. **Single responsibility**: One module, one purpose
2. **Minimal dependencies**: Keep modules lightweight
3. **Clear documentation**: Include README with examples
4. **Comprehensive tests**: Unit and integration tests
5. **Semantic versioning**: Use git tags for versions
6. **Error handling**: Return errors via ToolResult, don't throw
7. **Graceful degradation**: Return None from mount() if not configured
8. **Emit events**: Register and emit observability events

## References

- **→ [Provider Contract](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/PROVIDER_CONTRACT.md)**
- **→ [Tool Contract](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/TOOL_CONTRACT.md)**
- **→ [Hook Contract](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/HOOK_CONTRACT.md)**
- **→ [Orchestrator Contract](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/ORCHESTRATOR_CONTRACT.md)**
- **→ [Context Contract](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/CONTEXT_CONTRACT.md)**
