---
title: Mock Provider
description: Reference provider for testing and development without API calls
---

# Mock Provider

Reference provider module for testing and development without making real LLM API calls.

## Module ID

`provider-mock`

## Installation

```yaml
providers:
  - module: provider-mock
    source: git+https://github.com/microsoft/amplifier-module-provider-mock@main
    config:
      responses:
        - "Response 1"
        - "Response 2"
        - "Response 3"
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `responses` | list | `["I'll help you with that task.", "Task completed successfully.", "Here's the result of your request."]` | List of pre-configured responses to return in rotation |
| `debug` | bool | `false` | Gate for raw debug events (requires `raw_debug: true` to activate) |
| `raw_debug` | bool | `false` | Enable ultra-verbose raw API I/O logging |
| `use_streaming` | bool | `true` | Use streaming token delivery |
| `stream_delay_ms` | int | `0` | Artificial delay between tokens in milliseconds |

## Debug Configuration

### Raw Debug (`debug: true, raw_debug: true`)

- Emits `llm:request:raw` and `llm:response:raw` events
- Contains complete mock request/response objects
- Useful for testing logging infrastructure

Setting `debug: true` alone (without `raw_debug: true`) does not emit any additional events.

## Behavior

- Returns responses from configured list in rotation
- Can simulate tool calls when prompt contains "read"
- No external API calls
- No authentication required

## Use Cases

- **Unit testing** - Test orchestrators and tools without API costs
- **Integration testing** - Verify event flows and hook behavior
- **Development** - Rapid iteration without rate limits
- **CI/CD** - Automated tests without API keys

## Example

```yaml
providers:
  - module: provider-mock
    config:
      debug: true
      raw_debug: true
      responses:
        - "I'll help you with that task."
        - "The operation completed successfully."
```

## Repository

**-> [GitHub](https://github.com/microsoft/amplifier-module-provider-mock)**
