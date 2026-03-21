---
title: Tool Contract
description: Agent capability contract
---

# Tool Contract

Tools provide capabilities that agents can invoke.

## Purpose

Tools extend what agents can do: read files, execute commands, search the web, delegate to sub-agents, etc.

## Protocol

```python
from typing import Protocol, runtime_checkable, Any
from amplifier_core.models import ToolResult

@runtime_checkable
class Tool(Protocol):
    @property
    def name(self) -> str:
        """Unique tool identifier."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description for LLM."""
        ...

    @property
    def input_schema(self) -> dict[str, Any]:
        """JSON Schema describing the tool's input parameters.

        Returns an empty dict by default for backward compatibility
        with tools that predate this convention.
        """
        return {}

    async def execute(
        self,
        input: dict[str, Any]
    ) -> ToolResult:
        """Execute the tool."""
        ...
```

!!! note "Input Schema"
    `input_schema` has a concrete default (`return {}`) and is excluded from `isinstance()` structural checks so that tools written before this field was introduced continue to satisfy the protocol without modification. Callers that need the schema should always use `getattr(tool, "input_schema", {})` for maximum compatibility.

## Mount Function

```python
async def mount(coordinator, config=None):
    config = config or {}
    tool = MyTool(config)
    await coordinator.mount("tools", tool, name=tool.name)
    return cleanup_function  # or None
```

## ToolResult

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ToolResult:
    success: bool = True                 # Whether execution succeeded
    output: Any | None = None            # Output for LLM context
    error: dict[str, Any] | None = None  # Error details if failed
```

## Input Schema

Tools declare their parameters using JSON Schema:

```python
@property
def input_schema(self) -> dict[str, Any]:
    """JSON schema defining the tool's parameters"""
    return {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read"
            },
            "encoding": {
                "type": "string",
                "description": "File encoding (default: utf-8)",
                "default": "utf-8"
            }
        },
        "required": ["file_path"]
    }
```

Orchestrators use this schema to generate tool definitions for LLMs.

## Example Implementation

```python
from amplifier_core.models import ToolResult

class CalculatorTool:
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Perform arithmetic calculations"

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"]
                },
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["operation", "a", "b"]
        }

    async def execute(self, input: dict) -> ToolResult:
        try:
            op = input["operation"]
            a = input["a"]
            b = input["b"]

            if op == "add":
                result = a + b
            elif op == "subtract":
                result = a - b
            elif op == "multiply":
                result = a * b
            elif op == "divide":
                if b == 0:
                    return ToolResult(
                        success=False,
                        error={"message": "Division by zero"}
                    )
                result = a / b
            else:
                return ToolResult(
                    success=False,
                    error={"message": f"Unknown operation: {op}"}
                )

            return ToolResult(
                success=True,
                output=str(result)
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error={"message": str(e), "type": type(e).__name__}
            )


async def mount(coordinator, config=None):
    """Entry point for module loading."""
    tool = CalculatorTool()
    await coordinator.mount("tools", tool, name=tool.name)
    return None  # No cleanup needed
```

## Configuration

Tools receive configuration via Mount Plan:

```yaml
tools:
  - module: my-tool
    source: git+https://github.com/org/my-tool@main
    config:
      max_size: 1048576
      allowed_paths:
        - /home/user/projects
```

See [MOUNT_PLAN_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/MOUNT_PLAN_SPECIFICATION.md) for full schema.

## Observability

Register lifecycle events:

```python
coordinator.register_contributor(
    "observability.events",
    "my-tool",
    lambda: ["my-tool:started", "my-tool:completed", "my-tool:error"]
)
```

Standard tool events emitted by orchestrators:
- `tool:pre` - Before tool execution
- `tool:post` - After successful execution
- `tool:error` - On execution failure

## Canonical Example

**Reference implementation**: [amplifier-module-tool-filesystem](https://github.com/microsoft/amplifier-module-tool-filesystem)

Study this module for:
- Tool protocol implementation
- Input validation patterns
- Error handling and result formatting
- Configuration integration

Additional examples:
- [amplifier-module-tool-bash](https://github.com/microsoft/amplifier-module-tool-bash) - Command execution
- [amplifier-module-tool-web](https://github.com/microsoft/amplifier-module-tool-web) - Web access

## Validation Checklist

### Required

- [ ] Implements Tool protocol (name, description, execute)
- [ ] `mount()` function with entry point in pyproject.toml
- [ ] Returns `ToolResult` from execute()
- [ ] Handles errors gracefully (returns success=False, doesn't crash)

### Recommended

- [ ] Provides JSON schema via `input_schema` property
- [ ] Validates input before processing
- [ ] Logs operations at appropriate levels
- [ ] Registers observability events

## Testing

Use test utilities from `amplifier_core/testing.py`:

```python
from amplifier_core.testing import MockTool

@pytest.mark.asyncio
async def test_tool_execution():
    tool = MyTool(config={})

    result = await tool.execute({
        "required_param": "value"
    })

    assert result.success
    assert result.error is None
```

### MockTool for Testing Orchestrators

```python
from amplifier_core.testing import MockTool

mock_tool = MockTool(
    name="test_tool",
    description="Test tool",
    return_value="mock result"
)

# After use
assert mock_tool.call_count == 1
assert mock_tool.last_input == {...}
```

## Quick Validation Command

```bash
# Structural validation
amplifier module validate ./my-tool --type tool
```

---

**Related**: [README.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/README.md) | [HOOK_CONTRACT.md](hook.md)
