---
title: OpenAI Provider
description: GPT model integration
---

# OpenAI Provider

Integrates OpenAI's GPT models into Amplifier.

## Module ID

`provider-openai`

## Installation

```yaml
providers:
  - module: provider-openai
    source: git+https://github.com/microsoft/amplifier-module-provider-openai@main
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | string | `$OPENAI_API_KEY` | API key |
| `base_url` | string | null | Optional custom endpoint (`$OPENAI_BASE_URL`); null = OpenAI default |
| `default_model` | string | `gpt-5.1-codex` | Default model |
| `max_tokens` | integer | `4096` | Maximum output tokens |
| `temperature` | float | null | Sampling temperature; null = not sent (some models don't support it) |
| `reasoning` | string | null | Reasoning effort: `minimal\|low\|medium\|high`; null = not sent |
| `reasoning_summary` | string | `detailed` | Reasoning verbosity: `auto\|concise\|detailed` |
| `truncation` | string | `auto` | Automatic context management |
| `enable_state` | boolean | `false` | Enable stateful conversations |
| `debug` | boolean | `false` | Enable standard debug events |
| `raw_debug` | boolean | `false` | Enable ultra-verbose raw API I/O logging |
| `priority` | int | 100 | Provider priority for selection |
| `timeout` | float | 600.0 | API timeout in seconds |
| `max_retries` | int | 5 | Retry attempts before failing |
| `retry_jitter` | float | 0.2 | Randomness in retry delays (0.0-1.0) |
| `min_retry_delay` | float | 1.0 | Minimum delay between retries |
| `max_retry_delay` | float | 60.0 | Maximum delay between retries |

## Supported Models

| Model | Description |
|-------|-------------|
| `gpt-5.1-codex` | GPT-5 optimized for code (default) |
| `gpt-5.1` | Latest GPT-5 model |
| `gpt-5-mini` | Smaller, faster GPT-5 |
| `gpt-5-nano` | Smallest GPT-5 variant |
| `o3-deep-research` | o3 Deep Research |
| `o4-mini-deep-research` | o4-mini Deep Research |

## Features

### Responses API Capabilities

- **Reasoning Control** - Adjust reasoning effort (minimal, low, medium, high)
- **Reasoning Summary Verbosity** - Control detail level (auto, concise, detailed)
- **Extended Thinking Toggle** - Enables high-effort reasoning with automatic token budgeting
- **Explicit Reasoning Preservation** - Re-inserts reasoning items for robust multi-turn reasoning
- **Automatic Context Management** - Optional truncation parameter
- **Stateful Conversations** - Optional conversation persistence
- **Native Tools** - Built-in web search, image generation, code interpreter
- **Structured Output** - JSON schema-based output formatting
- **Function Calling** - Custom tool use support
- **Token Counting** - Usage tracking and management

### Reasoning Summary Levels

The `reasoning_summary` config controls verbosity of reasoning blocks:

- **`auto`** - Model decides appropriate detail level
- **`concise`** - Brief reasoning summaries (faster, fewer tokens)
- **`detailed`** (default) - Verbose reasoning output similar to Anthropic's extended thinking

**Example:**

```yaml
# Detailed reasoning (verbose like Anthropic's thinking blocks)
providers:
  - module: provider-openai
    config:
      reasoning: "high"
      reasoning_summary: "detailed"
```

### Automatic Context Management

The provider supports automatic conversation history management via the `truncation` parameter (enabled by default):

```yaml
config:
  truncation: "auto"  # Enables automatic context management (default)
  # OR
  truncation: null    # Disables automatic truncation (manual control)
```

**How it works:**
- OpenAI automatically removes oldest messages when context limit approached
- FIFO (first-in, first-out) - most recent messages preserved
- Transparent to application - no errors or warnings

### Incomplete Response Auto-Continuation

The provider automatically handles incomplete responses:

**The Problem**: OpenAI may return `status: "incomplete"` when generation is cut off.

**The Solution**: Automatic continuation using `previous_response_id` (up to 5 attempts).

**Benefits:**
- Transparent continuation - Makes follow-up calls automatically
- Output accumulation - Merges reasoning items and messages from all continuations
- Single response - Returns complete ChatResponse to orchestrator
- Full observability - Emits `provider:incomplete_continuation` events

### Reasoning State Preservation

The provider preserves reasoning state across conversation **steps** for improved multi-turn performance:

**The Problem**: Reasoning models produce internal reasoning traces that improve subsequent responses when preserved.

**Important Distinction**:
- **Turn**: User prompt → (possibly multiple API calls) → final assistant response
- **Step**: Each individual API call within a turn (tool call loops = multiple steps per turn)

**The Solution**: Explicit reasoning re-insertion for robust step-by-step reasoning:

1. **Requests encrypted content** - API call includes `include=["reasoning.encrypted_content"]`
2. **Stores complete reasoning state** - Both encrypted content and reasoning ID stored in `ThinkingBlock.content`
3. **Re-inserts reasoning items** - Explicitly converts reasoning blocks back to OpenAI format
4. **Maintains metadata** - Also tracks reasoning IDs in metadata

### Graceful Error Recovery

The provider implements graceful degradation for incomplete tool call sequences:

**The Problem**: Missing tool results cause API rejection.

**The Solution**: Automatic detection and synthetic result injection.

**How it works:**
1. Detects missing tool results before API call
2. Injects synthetic results with `[SYSTEM ERROR: Tool result missing]` message
3. API accepts request, session continues
4. LLM can acknowledge error and ask user to retry
5. Emits `provider:tool_sequence_repaired` event

## Debugging

### Standard Debug

```yaml
config:
  debug: true  # Summary logging with truncated values
```

### Raw Debug

```yaml
config:
  debug: true
  raw_debug: true  # Complete API I/O logging
```

## Environment Variables

```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional
```

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-provider-openai)**
