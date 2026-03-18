---
title: Logging Hook
description: JSONL event logging for observability
---

# Logging Hook

Provides visibility into agent execution through lifecycle event logging.

## Module ID

`hooks-logging`

## Installation

```yaml
hooks:
  - module: hooks-logging
    source: git+https://github.com/microsoft/amplifier-module-hooks-logging@main
    config:
      priority: 100
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `priority` | int | `100` | Hook priority (lower runs first) |
| `session_log_template` | string | `~/.amplifier/projects/{project}/sessions/{session_id}/events.jsonl` | Path template for session logs |
| `auto_discover` | bool | `true` | Auto-discover module events |
| `strip_raw` | bool | `false` | Strip `raw` field from event data |
| `additional_events` | list | `[]` | Extra events to log |

## Features

- **Zero code changes** - Pure configuration
- **Auto-discovery** - Modules declare observable events
- **Standard Python logging** - No external dependencies
- **Flexible output** - Console, file, or both

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-hooks-logging)**
