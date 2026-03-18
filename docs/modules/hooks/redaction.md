---
title: Redaction Hook
description: Sensitive data masking for logs
---

# Redaction Hook

Masks secrets and PII before logging.

## Module ID

`hooks-redaction`

## Installation

```yaml
hooks:
  - module: hooks-redaction
    source: git+https://github.com/microsoft/amplifier-module-hooks-redaction@main
```

## Behavior

Scans messages for sensitive patterns and replaces them with `[REDACTED]`:

- Email addresses
- Phone numbers
- Credit card numbers
- AWS keys, JWT tokens
- Custom regex patterns

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `rules` | list | `["secrets", "pii-basic"]` | Redaction rule sets to apply |
| `allowlist` | list | `[]` | Field names to never redact (merged with defaults) |
| `priority` | int | `10` | Hook priority (lower runs first) |
| `skip_events` | list | `["tool:pre", "tool:post"]` | Events to skip redaction (feed into LLM context) |

## Usage

```yaml
hooks:
  - module: hooks-redaction
    config:
      rules:
        - "secrets"
        - "pii-basic"
      allowlist:
        - "custom_field_name"
```

!!! important "Priority"
    Register redaction hook with **higher priority** than logging to ensure sensitive data is masked before it reaches logs.

```yaml
hooks:
  - module: hooks-redaction
    priority: 10  # High priority - runs first

  - module: hooks-logging
    priority: 100   # Lower priority - runs after redaction
```

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-hooks-redaction)**
