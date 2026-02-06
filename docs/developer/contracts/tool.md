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
        "path": {
            "type": "string",
            "description": "File path to read"
        },
        "encoding": {
            "type": "string",
            "description": "File encoding",
            "default": "utf-8"
        }
    },
    "required": ["path"]
}
```

## Events

Tools are wrapped with events by the orchestrator:

| Event | When | Data |
|-------|------|------|
| `tool:pre` | Before execution | tool_name, input |
| `tool:post` | After execution | tool_name, result |
| `tool:error` | On failure | tool_name, error |

### Debug Events

For detailed logging:

| Event | When | Data |
|-------|------|------|
| `tool:pre:debug` | Debug logging | Full input details |
| `tool:post:debug` | Debug logging | Full result details |

## Example Implementations

### Read File Tool

```python
from pathlib import Path
from amplifier_core.models import ToolResult

class ReadFileTool:
    name = "read_file"
    description = "Read the contents of a file"
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path"},
            "encoding": {"type": "string", "default": "utf-8"}
        },
        "required": ["path"]
    }

    def __init__(self, config):
        self.allowed_paths = config.get("allowed_paths", [])
        self.max_size = config.get("max_size", 1048576)  # 1MB default

    async def execute(self, input: dict) -> ToolResult:
        path = input.get("path")
        encoding = input.get("encoding", "utf-8")

        # Validate path
        if not self._is_allowed(path):
            return ToolResult(
                success=False,
                error={"message": "Path not allowed", "type": "PermissionError"}
            )

        try:
            file_path = Path(path)
            
            # Check file size
            if file_path.stat().st_size > self.max_size:
                return ToolResult(
                    success=False,
                    error={"message": f"File exceeds max size ({self.max_size} bytes)", "type": "FileTooLarge"}
                )
            
            content = file_path.read_text(encoding=encoding)
            return ToolResult(
                success=True,
                output=content,
                metadata={"path": str(path), "size": len(content)}
            )
        except FileNotFoundError:
            return ToolResult(
                success=False,
                error={"message": f"File not found: {path}", "type": "FileNotFoundError"}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error={"message": str(e), "type": type(e).__name__}
            )

    def _is_allowed(self, path: str) -> bool:
        if not self.allowed_paths:
            return True  # No restrictions
        path = Path(path).resolve()
        return any(
            path.is_relative_to(Path(allowed).resolve())
            for allowed in self.allowed_paths
        )
```

### Bash Tool

```python
import asyncio
from amplifier_core.models import ToolResult

class BashTool:
    name = "bash"
    description = "Execute shell commands"
    input_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Command to execute"},
            "timeout": {"type": "integer", "default": 30}
        },
        "required": ["command"]
    }

    def __init__(self, config):
        self.default_timeout = config.get("timeout", 30)
        self.blocked_commands = config.get("blocked_commands", ["rm -rf /"])

    async def execute(self, input: dict) -> ToolResult:
        command = input.get("command", "")
        timeout = input.get("timeout", self.default_timeout)

        # Safety check
        for blocked in self.blocked_commands:
            if blocked in command:
                return ToolResult(
                    success=False,
                    error={"message": f"Blocked command pattern: {blocked}", "type": "SecurityError"}
                )

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            output = stdout.decode() if stdout else ""
            error_output = stderr.decode() if stderr else ""

            if process.returncode != 0:
                return ToolResult(
                    success=False,
                    output=output,
                    error={"message": error_output, "type": "CommandFailed", "exit_code": process.returncode}
                )

            return ToolResult(
                success=True,
                output=output + (f"\nstderr: {error_output}" if error_output else ""),
                metadata={"exit_code": process.returncode}
            )

        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                error={"message": f"Command timed out after {timeout}s", "type": "TimeoutError"}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error={"message": str(e), "type": type(e).__name__}
            )
```

## Graceful Degradation

Tools should handle errors gracefully and return structured errors:

```python
async def execute(self, input: dict) -> ToolResult:
    try:
        # Normal execution
        result = await self._do_work(input)
        return ToolResult(success=True, output=result)
    except PermissionError as e:
        return ToolResult(
            success=False,
            error={"message": str(e), "type": "PermissionError"}
        )
    except Exception as e:
        # Catch-all for unexpected errors
        return ToolResult(
            success=False,
            error={"message": f"Unexpected error: {e}", "type": type(e).__name__}
        )
```

## Token-Aware Output

Tools should be mindful of output size to avoid consuming excessive context:

```python
async def execute(self, input: dict) -> ToolResult:
    content = await self._fetch_content(input)
    
    # Truncate if too large
    max_output = 50000  # ~12.5k tokens
    if len(content) > max_output:
        content = content[:max_output] + f"\n\n[Truncated: {len(content) - max_output} chars remaining]"
    
    return ToolResult(success=True, output=content)
```

## Related Contracts

- **[Orchestrator Contract](orchestrator.md)** - Orchestrators execute tools
- **[Hook Contract](hook.md)** - Hooks can observe/block tool execution

## Authoritative Reference

**→ [Tool Contract](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/TOOL_CONTRACT.md)** - Complete specification
