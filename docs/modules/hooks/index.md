---
title: Hooks
description: Observability and control
---

# Hooks

Hooks observe and control operations. They can log events, block operations, inject context, and request user approval.

## Available Hooks

| Hook | Description | Repository |
|------|-------------|------------|
| **[Logging](logging.md)** | JSONL event logging | [GitHub](https://github.com/microsoft/amplifier-module-hooks-logging) |
| **[Approval](approval.md)** | User approval gates | [GitHub](https://github.com/microsoft/amplifier-module-hooks-approval) |
| **[Redaction](redaction.md)** | Sensitive data redaction | [GitHub](https://github.com/microsoft/amplifier-module-hooks-redaction) |
| **Streaming UI** | Real-time output display | [GitHub](https://github.com/microsoft/amplifier-module-hooks-streaming-ui) |
| **Backup** | File backup before writes | [GitHub](https://github.com/microsoft/amplifier-module-hooks-backup) |
| **Status Context** | Status tracking injection | [GitHub](https://github.com/microsoft/amplifier-module-hooks-status-context) |
| **Todo Reminder** | Todo list context injection | [GitHub](https://github.com/microsoft/amplifier-module-hooks-todo-reminder) |
| **Scheduler Heuristic** | Smart tool scheduling | [GitHub](https://github.com/microsoft/amplifier-module-hooks-scheduler-heuristic) |
| **Scheduler Cost-Aware** | Cost-optimized scheduling | [GitHub](https://github.com/microsoft/amplifier-module-hooks-scheduler-cost-aware) |

<!-- MODULE_LIST_HOOKS -->

## Configuration

```yaml
hooks:
  - module: hooks-logging
    config:
      level: info
      output: ~/.amplifier/logs/

  - module: hooks-approval
    config:
      require_approval_for:
        - tool-bash
        - tool-filesystem:write
```

## Hook Actions

| Action | Effect |
|--------|--------|
| `continue` | Proceed normally |
| `deny` | Block operation |
| `modify` | Transform data |
| `inject_context` | Add to conversation |
| `ask_user` | Request approval |

## Logging Hook

Provides visibility into agent execution through lifecycle event logging.

**Features:**
- Zero code changes required - pure configuration
- Auto-discovery of module events via `observability.events` capability
- Standard Python logging (no external dependencies)
- Configurable levels: DEBUG, INFO, WARNING, ERROR
- Flexible output: console, file, or both

**Auto-Discovery:**
```python
# Modules declare observable events (in mount())
coordinator.register_contributor(
    "observability.events",
    "module-name",
    lambda: ["module:event1", "module:event2"]
)
```

**Configuration:**
```yaml
hooks:
  - module: hooks-logging
    config:
      level: "INFO"           # DEBUG, INFO, WARNING, ERROR
      auto_discover: true     # Auto-discover module events (default)
      additional_events:      # Manual additions
        - "custom:event"
```

**Debug Levels:**
- `debug: false` (default) - INFO events only, no debug details
- `debug: true` - Standard debug events with summaries and previews
- `debug: true, raw_debug: true` - Ultra-verbose with complete raw API I/O

**Log Location**: `~/.amplifier/projects/<project>/sessions/<session_id>/events.jsonl`

## Approval Hook

Intercepts tool execution requests and coordinates user approval before dangerous operations.

**Features:**
- Hook-based interception via `tool:pre` events
- Pluggable approval providers (CLI, GUI, headless)
- Rule-based auto-approval configuration
- Audit trail logging (JSONL format)
- Risk-level based approval requirements

**Configuration:**
```yaml
hooks:
  - module: hooks-approval
    config:
      patterns:
        - rm -rf
        - sudo
        - dd if=
      auto_approve: false
```

## Redaction Hook

Masks secrets/PII before logging.

**Overview:**
Scans messages for patterns like email addresses, phone numbers, credit card numbers, and custom regex patterns, replacing them with `[REDACTED]`.

**Important:** Register with higher priority than logging.

## Contract

See [Hook Contract](../../developer/contracts/hook.md) for implementation details.
