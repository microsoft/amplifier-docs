---
title: Simple Context
description: Basic in-memory conversation context
---

# Simple Context

Basic message list context manager for conversation state. This is the default context manager.

## Module ID

`context-simple`

## Installation

```yaml
contexts:
  - module: context-simple
    source: git+https://github.com/microsoft/amplifier-module-context-simple@main
    config:
      max_tokens: 200000
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_tokens` | int | `200000` | Maximum context size in tokens |
| `compact_threshold` | float | `0.92` | Trigger compaction at this usage ratio (0.0-1.0) |
| `target_usage` | float | `0.50` | Compact down to this usage ratio (0.0-1.0) |
| `protected_recent` | float | `0.30` | Always protect last N% of messages (0.0-1.0) |
| `protected_tool_results` | int | `5` | Always protect last N tool results from truncation |
| `truncate_chars` | int | `250` | Characters to keep when truncating tool results |
| `compaction_notice_enabled` | bool | `true` | Enable compaction notice injection |
| `compaction_notice_token_reserve` | int | `800` | Tokens to reserve for notice |
| `compaction_notice_verbosity` | string | `normal` | Notice detail level (`minimal`/`normal`/`verbose`) |
| `compaction_notice_min_level` | int | `1` | Only show notice if compaction level >= this |
| `output_reserve_fraction` | float | `0.5` | Fraction of max_output_tokens to reserve for responses (0.0-1.0) |

## Behavior

- **In-memory message list**
- **No persistence** across sessions
- **Automatic compaction** when approaching token limit
- **Preserves tool pairs** as atomic units during compaction

## Compaction Strategy

Compacts automatically when token usage reaches threshold (default: 92% of max_tokens):

- **Keeps**: All system messages + recent messages
- **Preserves tool pairs**: Tool_use and tool_result messages stay together

## Usage

```toml
[session]
context = "context-simple"
```

Perfect for:

- Development and testing
- Short conversations
- Stateless applications

Not suitable for:

- Cross-session persistence
- Custom compaction strategies

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-context-simple)**
