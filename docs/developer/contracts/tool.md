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

    async def execute(
        self,
        input: dict[str, Any]
    ) -> ToolResult:
        """Execute the tool."""
        ...
```

!!! note "Input Schema"
    The `input_schema` property is not part of the formal Protocol but is commonly implemented by tools as a class attribute. Orchestrators use it to generate tool definitions for LLMs.

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
    success: bool                    # Whether execution succeeded
    output: str | None = None        # Output for LLM context
    error: dict | None = None        # Error details if failed
    metadata: dict = field(default_factory=dict)  # Additional metadata
    
    def get_serialized_output(self) -> str:
        """Serialize output for context inclusion."""
        if self.error:
            return f"Error: {self.error.get('message', 'Unknown error')}"
        return self.output or ""
```

## Input Schema

Tools declare their parameters using JSON Schema:

```python
input_schema = {
    "type": "object",
    "properties": {
        "file_path": {
            "type": "string",
            "description": "Path to the file"
        },
        "content": {
            "type": "string",
            "description": "Content to write"
        }
    },
    "required": ["file_path", "content"]
}
```

## Configuration

Tools receive configuration via Mount Plan:

```yaml
tools:
  - module: my-tool
    config:
      max_retries: 3
      timeout: 30
```

Access config in mount function:

```python
async def mount(coordinator, config=None):
    config = config or {}
    max_retries = config.get("max_retries", 3)
    tool = MyTool(max_retries=max_retries)
    await coordinator.mount("tools", tool, name=tool.name)
```

## Error Handling

Tools should return errors rather than raise exceptions:

```python
async def execute(self, input: dict[str, Any]) -> ToolResult:
    try:
        result = await self._do_work(input)
        return ToolResult(success=True, output=result)
    except FileNotFoundError as e:
        return ToolResult(
            success=False,
            error={"type": "not_found", "message": str(e)}
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error={"type": "unknown", "message": str(e)}
        )
```

## Example: Complete Tool

```python
from amplifier_core.interfaces import Tool
from amplifier_core.models import ToolResult

class ReadFileTool:
    """Read file contents."""
    
    input_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to file to read"
            }
        },
        "required": ["file_path"]
    }
    
    @property
    def name(self) -> str:
        return "read_file"
    
    @property
    def description(self) -> str:
        return "Read the contents of a file"
    
    async def execute(self, input: dict) -> ToolResult:
        file_path = input.get("file_path")
        if not file_path:
            return ToolResult(
                success=False,
                error={"message": "file_path is required"}
            )
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return ToolResult(success=True, output=content)
        except FileNotFoundError:
            return ToolResult(
                success=False,
                error={"message": f"File not found: {file_path}"}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error={"message": str(e)}
            )

# Entry point
async def mount(coordinator, config=None):
    tool = ReadFileTool()
    await coordinator.mount("tools", tool, name=tool.name)
    return None  # No cleanup needed
```

## Testing

```python
import pytest
from amplifier_core.testing import MockCoordinator

@pytest.mark.asyncio
async def test_read_file_tool():
    tool = ReadFileTool()
    
    # Test successful read
    result = await tool.execute({"file_path": "test.txt"})
    assert result.success
    assert result.output is not None
    
    # Test file not found
    result = await tool.execute({"file_path": "nonexistent.txt"})
    assert not result.success
    assert result.error is not None
```

## See Also

- [Hook Contract](hook.md) - Tool execution hooks
- [Orchestrator Contract](orchestrator.md) - Tool invocation
- [Module Contracts](index.md) - All contracts
