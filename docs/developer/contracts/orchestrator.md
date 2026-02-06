---
title: Orchestrator Contract
description: Execution loop strategy contract
---

# Orchestrator Contract

Orchestrators control how agents execute: the loop structure, tool handling, and response generation.

## Purpose

Orchestrators define the execution strategy:

- **Basic**: Simple request/response loop
- **Streaming**: Real-time token streaming via hooks
- **Events**: Event-driven architecture with callbacks

## Protocol

```python
from typing import Protocol, runtime_checkable
from amplifier_core.interfaces import ContextManager, Provider, Tool
from amplifier_core.hooks import HookRegistry

@runtime_checkable
class Orchestrator(Protocol):
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

## Mount Function

```python
async def mount(coordinator, config=None):
    config = config or {}
    orchestrator = MyOrchestrator(config)
    await coordinator.mount("session", orchestrator, name="orchestrator")
    return None
```

## Execution Flow

Typical orchestrator flow:

```
1. Add user prompt to context
2. Loop:
   a. Get messages from context (with dynamic token budget)
   b. Emit provider:request
   c. Call provider.complete()
   d. Emit provider:response
   e. Add response to context
   f. Parse tool calls
   g. If no tools: return response
   h. For each tool:
      - Emit tool:pre
      - Execute tool
      - Emit tool:post
      - Add result to context
   i. Continue loop
3. Emit orchestrator:complete (REQUIRED)
4. Return final response
```

## Events

Orchestrators **MUST** emit these events:

| Event | When | Data |
|-------|------|------|
| `prompt:submit` | Received prompt | prompt |
| `provider:request` | Before LLM call | messages, model |
| `provider:stream` | During streaming (optional) | chunk |
| `provider:response` | After LLM response | response, usage |
| `tool:pre` | Before tool execution | tool_name, input |
| `tool:post` | After tool execution | tool_name, result |
| `prompt:complete` | Final response | response |
| `orchestrator:complete` | Loop finished | orchestrator, turn_count, status |

The `orchestrator:complete` event is **required** and must include:
- `orchestrator`: Name of the orchestrator module
- `turn_count`: Number of LLM turns executed
- `status`: "success", "incomplete", or "error"

## Configuration

Common configuration options:

| Option | Type | Description |
|--------|------|-------------|
| `max_iterations` | int | Maximum loop iterations |
| `parallel_tools` | bool | Execute tools in parallel |
| `streaming` | bool | Enable streaming output |
| `debug` | bool | Enable debug logging |

## Example Implementation

```python
from amplifier_core.models import HookResult

class BasicOrchestrator:
    def __init__(self, config):
        self.max_iterations = config.get("max_iterations", 10)
        self.parallel_tools = config.get("parallel_tools", False)

    async def execute(self, prompt, context, providers, tools, hooks):
        # Emit prompt received
        await hooks.emit("prompt:submit", {"prompt": prompt})
        
        # Add user message
        await context.add_message({"role": "user", "content": prompt})
        
        # Get first provider
        provider = list(providers.values())[0]
        iteration = 0

        for iteration in range(self.max_iterations):
            # Get messages with dynamic token budget from provider
            messages = await context.get_messages_for_request(provider=provider)

            # Emit request event
            await hooks.emit("provider:request", {
                "messages": messages,
                "iteration": iteration
            })

            # Call provider
            response = await provider.complete({"messages": messages})

            # Emit response event
            await hooks.emit("provider:response", {
                "response": response,
                "usage": response.get("usage", {})
            })

            # Add response to context
            await context.add_message({
                "role": "assistant",
                "content": response["content"]
            })

            # Parse tool calls
            tool_calls = provider.parse_tool_calls(response)

            if not tool_calls:
                # No tools - complete successfully
                final_text = self._extract_text(response)
                
                await hooks.emit("prompt:complete", {"response": final_text})
                await hooks.emit("orchestrator:complete", {
                    "orchestrator": "basic",
                    "turn_count": iteration + 1,
                    "status": "success"
                })
                
                return final_text

            # Execute tools
            for call in tool_calls:
                tool = tools.get(call["name"])
                if tool:
                    # Emit pre-execution
                    await hooks.emit("tool:pre", {
                        "tool_name": call["name"],
                        "input": call["input"]
                    })

                    # Execute tool
                    result = await tool.execute(call["input"])

                    # Emit post-execution
                    await hooks.emit("tool:post", {
                        "tool_name": call["name"],
                        "result": result
                    })

                    # Add result to context
                    await context.add_message({
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": result.get_serialized_output()
                    })

        # Max iterations reached
        await hooks.emit("orchestrator:complete", {
            "orchestrator": "basic",
            "turn_count": iteration + 1,
            "status": "incomplete"
        })
        
        return "Max iterations reached"

    def _extract_text(self, response):
        for block in response.get("content", []):
            if block.get("type") == "text":
                return block.get("text", "")
        return ""
```

## Streaming Orchestrator

Streaming output is handled via hooks, not callbacks:

```python
class StreamingOrchestrator:
    def __init__(self, config):
        self.max_iterations = config.get("max_iterations", 10)

    async def execute(self, prompt, context, providers, tools, hooks):
        await hooks.emit("prompt:submit", {"prompt": prompt})
        await context.add_message({"role": "user", "content": prompt})
        
        provider = list(providers.values())[0]
        iteration = 0

        for iteration in range(self.max_iterations):
            messages = await context.get_messages_for_request(provider=provider)

            await hooks.emit("provider:request", {"messages": messages})

            # Use streaming completion
            full_response = None
            async for chunk in provider.stream_complete({"messages": messages}):
                # Emit streaming event - hooks handle display
                await hooks.emit("provider:stream", {"chunk": chunk})
                full_response = chunk  # Last chunk has full response

            await hooks.emit("provider:response", {"response": full_response})

            await context.add_message({
                "role": "assistant",
                "content": full_response["content"]
            })

            tool_calls = provider.parse_tool_calls(full_response)
            if not tool_calls:
                final = self._extract_text(full_response)
                await hooks.emit("prompt:complete", {"response": final})
                await hooks.emit("orchestrator:complete", {
                    "orchestrator": "streaming",
                    "turn_count": iteration + 1,
                    "status": "success"
                })
                return final

            # Execute tools...
            for call in tool_calls:
                tool = tools.get(call["name"])
                if tool:
                    await hooks.emit("tool:pre", {"tool_name": call["name"], "input": call["input"]})
                    result = await tool.execute(call["input"])
                    await hooks.emit("tool:post", {"tool_name": call["name"], "result": result})
                    await context.add_message({
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": result.get_serialized_output()
                    })

        await hooks.emit("orchestrator:complete", {
            "orchestrator": "streaming",
            "turn_count": iteration + 1,
            "status": "incomplete"
        })
        return "Max iterations reached"

    def _extract_text(self, response):
        for block in response.get("content", []):
            if block.get("type") == "text":
                return block.get("text", "")
        return ""
```

## Graceful Degradation

Orchestrators should handle errors gracefully:

```python
async def execute(self, prompt, context, providers, tools, hooks):
    try:
        # Normal execution...
        return await self._execute_loop(prompt, context, providers, tools, hooks)
    except Exception as e:
        # Emit error event
        await hooks.emit("orchestrator:complete", {
            "orchestrator": "basic",
            "turn_count": 0,
            "status": "error",
            "error": str(e)
        })
        raise
```

## Validation

Orchestrators should validate inputs:

```python
async def execute(self, prompt, context, providers, tools, hooks):
    if not providers:
        raise ValueError("At least one provider required")
    
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    # Continue with execution...
```

## Related Contracts

- **[Context Contract](context.md)** - Orchestrators manage context
- **[Provider Contract](provider.md)** - Orchestrators call providers
- **[Tool Contract](tool.md)** - Orchestrators execute tools
- **[Hook Contract](hook.md)** - Orchestrators emit events

## Authoritative Reference

**→ [Orchestrator Contract](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/ORCHESTRATOR_CONTRACT.md)** - Complete specification
