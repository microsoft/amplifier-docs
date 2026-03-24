---
title: streaming-ui
description: Progressive display for thinking blocks, tool invocations, and token usage
---

# streaming-ui Hook

Progressive display for thinking blocks, tool invocations, and token usage in the Amplifier console.

## Overview

The `hooks-streaming-ui` module provides real-time console output for:

- **Thinking blocks** - Formatted display of LLM reasoning
- **Tool invocations** - Shows tool name and truncated arguments
- **Tool results** - Success/failure status with truncated output
- **Token usage** - Input/output/total token counts with caching info
- **Sub-agent context** - Visual distinction for delegated agent sessions

## Configuration

```yaml
hooks:
  - module: hooks-streaming-ui
    source: git+https://github.com/microsoft/amplifier-module-hooks-streaming-ui@main
```

Configuration is controlled via the `[ui]` section of your profile (not hook config):

```toml
# In ~/.amplifier/profiles/your-profile.toml
[ui]
show_thinking_stream = true   # Display thinking blocks (default: true)
show_tool_lines = 5           # Max lines to show for tool I/O (default: 5)
show_token_usage = true       # Display token usage after each turn (default: true)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_thinking_stream` | boolean | `true` | Display thinking blocks as they complete |
| `show_tool_lines` | integer | `5` | Maximum lines to show for tool input/output |
| `show_token_usage` | boolean | `true` | Display token usage statistics after each LLM response |

## Events Hooked

| Event | Purpose | Action |
|-------|---------|--------|
| `content_block:start` | Detect thinking block start | Display "Thinking..." indicator |
| `content_block:end` | Complete thinking block | Display formatted thinking content |
| `tool:pre` | Tool invocation | Display tool name and arguments |
| `tool:post` | Tool result | Display success/failure with output |
| `llm:response` | LLM response received | Capture model/provider info for token display |

## Display Format

### Thinking Blocks (Parent Session)

```
🧠 Thinking...

============================================================
Thinking:
------------------------------------------------------------
[thinking content here - formatted as markdown]
============================================================
```

### Thinking Blocks (Sub-Agent)

```
    🤔 [agent-name] Thinking...

    ========================================================
    [agent-name] Thinking:
    --------------------------------------------------------
    [thinking content here - formatted as markdown, indented]
    ========================================================
```

### Tool Invocations (Parent Session)

```
🔧 Using tool: bash
   command: ls -la
   timeout: 30
```

### Tool Invocations (Sub-Agent)

```
    ┌─ 🔧 [agent-name] Using tool: bash
    │  command: ls -la
    │  timeout: 30
```

### Tool Results (Parent Session)

```
✅ Tool result: bash
   total 24
   drwxr-xr-x  5 user  staff   160 Mar 24 12:00 .
   drwxr-xr-x  8 user  staff   256 Mar 24 11:30 ..
   ... (5 lines shown)
```

### Tool Results (Sub-Agent)

```
    └─ ✅ [agent-name] Tool result: bash
       total 24
       drwxr-xr-x  5 user  staff   160 Mar 24 12:00 .
       ... (5 lines shown, indented)
```

### Token Usage

```
│  📊 Token Usage (anthropic/claude-sonnet-4-5) [2.3s]
└─ Input: 1,234 (90% cached) | Output: 567 | Total: 1,801
```

For sub-agents, the display is indented with a 4-space prefix.

### Intermediate Text Blocks

Text blocks that accompany tool calls (not the final response) are displayed with special styling:

**Whisper mode** (< 3 lines):
```
▸ Short text here
  continuation line
```

**Rail mode** (3+ lines):
```
▏ First line
▏ Second line
▏ Third line
```

## Visual Hierarchy

The module uses careful visual hierarchy to distinguish context:

| Context | Indicator | Color | Indentation |
|---------|-----------|-------|-------------|
| Parent thinking | 🧠 | Cyan status, dim content | None |
| Sub-agent thinking | 🤔 | Cyan status, dim content | 4 spaces |
| Parent tool invocation | 🔧 | Cyan status, dim args | None |
| Sub-agent tool invocation | 🔧 + box drawing | Cyan status, dim args | 4 spaces |
| Parent tool result | ✅/❌ | Cyan status, dim output | None |
| Sub-agent tool result | ✅/❌ + box drawing | Cyan status, dim output | 4 spaces |
| Token usage | 📊 | Dim | Based on context |
| Intermediate text | ▸ or ▏ | Muted blue/lavender | Based on context |

## Sub-Agent Session Detection

The module detects sub-agent sessions via W3C Trace Context session ID format:

```
{parent-span}-{child-span}_{agent-name}
```

Examples:
- Parent: `12345678-1234-1234-1234-123456789012` (no underscore)
- Sub-agent: `0000000000000000-7cc787dd22d54f6c_foundation-explorer`

Agent name is extracted from the portion after the underscore.

## Truncation Behavior

### Line Truncation

Multi-line output is truncated to `show_tool_lines`:

```
Line 1
Line 2
Line 3
Line 4
Line 5
... (3 more lines)
```

### Character Truncation

Single-line output over 200 characters is truncated:

```
Long single line text here...
... (150 more chars)
```

## YAML-Style Formatting

Tool input/output is formatted as YAML-style for cleaner display:

```yaml
# Instead of JSON:
{"command": "ls -la", "timeout": 30}

# YAML-style:
command: ls -la
timeout: 30
```

This removes quote noise and makes structure clear.

## Token Usage Display

### Basic Display

```
│  📊 Token Usage
└─ Input: 1,234 | Output: 567 | Total: 1,801
```

### With Model Info

```
│  📊 Token Usage (anthropic/claude-sonnet-4-5) [2.3s]
└─ Input: 1,234 | Output: 567 | Total: 1,801
```

### With Caching

```
│  📊 Token Usage (anthropic/claude-sonnet-4-5) [2.3s]
└─ Input: 10,234 (90% cached) | Output: 567 | Total: 10,801
```

Cache info shows:
- **Percentage cached** when cache hits occur
- **"(caching...)"** when cache is being created (first request)

The module computes total input from Anthropic's split buckets:
```python
total_input = input_tokens + cache_read_input_tokens + cache_creation_input_tokens
```

## Bash Output Handling

Special handling for bash tool results:

```python
# Success (returncode = 0): show stdout, or stderr if no stdout
if success:
    output = stdout or stderr or "(no output)"

# Failure (returncode != 0): show both stdout and stderr
else:
    output = stdout
    if stderr:
        output = f"{output}\n[stderr]: {stderr}"
```

## Use Cases

### 1. Interactive Development

```toml
[ui]
show_thinking_stream = true   # See reasoning
show_tool_lines = 10          # More tool output
show_token_usage = true       # Monitor costs
```

### 2. Minimal Output

```toml
[ui]
show_thinking_stream = false  # Skip thinking
show_tool_lines = 3           # Minimal tool output
show_token_usage = false      # No usage stats
```

### 3. Debugging

```toml
[ui]
show_thinking_stream = true   # See agent reasoning
show_tool_lines = 50          # Full tool output
show_token_usage = true       # Track token usage
```

## Implementation Notes

- Uses Rich Console for markdown rendering with line wrapping
- Thinking blocks use `highlight=False` to preserve code block formatting
- Sub-agent output uses 4-space indentation consistently
- Token usage display cleared after each response to avoid stale data
- ANSI escape codes for colors and dim text
- Intermediate text rendering uses 256-color ANSI codes for precise color control

## Best Practices

### 1. Tune Line Limits

```toml
[ui]
show_tool_lines = 5   # Quick overview
# or
show_tool_lines = 20  # Detailed debugging
```

### 2. Disable for Scripting

```toml
[ui]
show_thinking_stream = false
show_tool_lines = 0
show_token_usage = false
```

When piping output or running headless.

### 3. Enable for Learning

```toml
[ui]
show_thinking_stream = true  # Learn agent reasoning
show_token_usage = true      # Understand costs
```

## See Also

- [Event System](../../architecture/events/) - Canonical events reference
- [Hook Contract](../../reference/contracts/hook.md) - Hook interface specification
- [loop-streaming](../orchestrators/loop_streaming.md) - Streaming orchestrator
