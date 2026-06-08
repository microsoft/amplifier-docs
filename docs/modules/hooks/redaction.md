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

Scans messages for sensitive patterns and replaces matched content with a typed redaction marker:

**`secrets` rule** → replaces with `[REDACTED:SECRET]`:
- AWS Access Keys
- Slack and Google API keys
- JWT tokens

**`pii-basic` rule** → replaces with `[REDACTED:PII]`:
- Email addresses
- Phone numbers

Events listed in `skip_events` are passed through unmodified to preserve data the LLM needs verbatim (e.g. tool results containing session IDs or timestamps).

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `rules` | list | `["secrets", "pii-basic"]` | Redaction rule sets to apply |
| `allowlist` | list | `[]` | Additional field names to never redact (merged with built-in structural defaults) |
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
