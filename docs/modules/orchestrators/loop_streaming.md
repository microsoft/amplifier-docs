---
title: loop-streaming
description: Token-level streaming orchestration for real-time response delivery
---

# loop-streaming Orchestrator

Token-level streaming orchestration for real-time response delivery with parallel tool execution.

## Overview

The `loop-streaming` orchestrator provides progressive response rendering by streaming tokens as they arrive from the LLM. Tool calls execute in parallel for improved performance.

## Configuration

```yaml
session:
  orchestrator: loop-streaming

orchestrators:
  - module: loop-streaming
    source: git+https://github.com/microsoft/amplifier-module-loop-streaming@main
    config:
      max_iterations: -1              # Maximum iterations (-1 = unlimited)
      extended_thinking: false        # Enable extended thinking mode (default: false)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_iterations` | integer | `-1` | Maximum loop iterations (`-1` = unlimited) |
| `extended_thinking` | boolean | `false` | Enable extended thinking mode for supported models |

## Behavior

### Streaming Flow

```
1. Receive user prompt
2. Add to context
3. Loop:
   a. Get messages from context
   b. Call provider.complete() → streaming generator
   c. For each token/chunk:
      - Emit content_block:delta event
      - Stream token to output
   d. Parse tool calls from streamed response
   e. If tool calls → execute in parallel
   f. Add results to context (deterministic order)
   g. Repeat from step 3
4. Return final response
```

### Parallel Tool Execution

Multiple tool calls execute **concurrently**:

```
tool_call_1 ──┐
tool_call_2 ──┼─→ await gather() → all complete
tool_call_3 ──┘
```

Results are added to context in **original order** (deterministic):

```
[tool_result_1, tool_result_2, tool_result_3]  # Always same order
```

This ensures:
- ✅ Fast execution (parallel)
- ✅ Deterministic context (ordered results)
- ✅ Reproducible behavior

## Events

### Streaming-Specific Events

- `content_block:start` - Content block begins
  ```python
  {
      "block_type": "text",  # or "thinking", "tool_use"
      "block_index": 0
  }
  ```

- `content_block:delta` - Token received
  ```python
  {
      "block_index": 0,
      "delta": "token text"
  }
  ```

- `content_block:end` - Content block completes
  ```python
  {
      "block_index": 0,
      "block": {...},  # Complete block data
      "usage": {...}   # Token usage
  }
  ```

### Standard Events

Also emits standard orchestrator events:
- `execution:start`, `execution:end`
- `tool:pre`, `tool:post`, `tool:error`
- `provider:request`, `provider:response`, `provider:error`
- `prompt:submit`, `prompt:complete`
- `orchestrator:complete`

## Extended Thinking

When `extended_thinking: true`:

```python
response = await provider.complete(chat_request, extended_thinking=True)
```

Providers supporting extended thinking (Anthropic Claude) will include thinking blocks in the stream:

```
content_block:start → type="thinking"
content_block:delta → thinking tokens stream
content_block:end   → complete thinking block
```

Hooks (e.g., `hooks-streaming-ui`) can display thinking blocks progressively.

## Comparison with Other Orchestrators

| Feature | loop-basic | loop-streaming | loop-events |
|---------|------------|----------------|-------------|
| Tool execution | Sequential | **Parallel** | Sequential |
| Response delivery | Buffered | **Streaming** | Buffered |
| Token-level events | No | **Yes** | No |
| Best for | Testing | **Interactive UIs** | Multi-agent |

## Use Cases

### 1. Interactive CLI

```yaml
session:
  orchestrator: loop-streaming

hooks:
  - module: hooks-streaming-ui
    config:
      show_thinking_stream: true
      show_tool_lines: 5
```

User sees tokens appear in real-time with progressive tool output.

### 2. Web UIs

```python
async for event in session.execute_streaming(prompt):
    if event["type"] == "content_block:delta":
        await websocket.send(event["delta"])
```

Stream tokens to browser for progressive rendering.

### 3. Long-Form Content

Stream tokens to render long-form content progressively - articles, documentation, stories.

## Best Practices

### 1. Monitor Streaming Performance

Monitor token delivery and network latency for optimal user experience.

### 2. Use Streaming-Aware Hooks

```yaml
hooks:
  - module: hooks-streaming-ui  # Designed for streaming
```

### 3. Set Iteration Limits

```yaml
config:
  max_iterations: 20  # Prevent infinite loops
```

### 4. Handle Interrupts

Streaming responses can be interrupted mid-stream. Ensure your application handles partial responses gracefully.

## Performance Considerations

### Parallel Tool Execution

Parallel execution significantly improves multi-tool performance:

```
Sequential (loop-basic):
  tool1 (2s) + tool2 (3s) + tool3 (2s) = 7s total

Parallel (loop-streaming):
  max(2s, 3s, 2s) = 3s total
```

### Network Streaming

When streaming over network (WebSocket, SSE):
- Consider network latency
- Implement client-side buffering
- Handle connection drops gracefully

## Implementation Notes

- Uses async generators for streaming responses
- Tool results added in deterministic order despite parallel execution
- Context compaction handled automatically
- Supports cancellation mid-stream
- Thinking blocks stream token-by-token (if provider supports)

## Error Handling

### Provider Errors

On streaming error:
1. Emit `provider:error` event
2. Return partial response if available
3. Exit loop

### Tool Errors

On tool execution error (during parallel batch):
1. Other tools continue executing
2. Error added as tool result
3. Loop continues (LLM sees error)

### Stream Interruption

If stream interrupted:
- Partial response returned
- Context updated with what was received
- Session remains valid for next turn

## See Also

- [loop-basic](loop_basic.md) - Sequential execution with complete events
- [loop-events](loop_events.md) - Event-driven with scheduler integration
- [hooks-streaming-ui](../hooks/streaming_ui.md) - Streaming display hook
- [Orchestrator Contract](../../reference/contracts/orchestrator.md) - Interface specification
