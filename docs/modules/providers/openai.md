---
title: OpenAI Provider
description: OpenAI GPT model integration for Amplifier via the Responses API
---

# OpenAI Provider

> **Repository**: [`amplifier-module-provider-openai`](https://github.com/microsoft/amplifier-module-provider-openai)

GPT model integration for Amplifier via OpenAI's Responses API.

## Contract

| Field | Value |
|-------|-------|
| **Module Type** | `provider` |
| **Mount Point** | `providers` |
| **Entry Point** | `amplifier_module_provider_openai:mount` |

## Supported Models

- `gpt-5.5` — Default model; latest GPT-5 generation
- `gpt-5-mini` — Smaller, faster GPT-5
- `gpt-5-nano` — Smallest GPT-5 variant

## Configuration

```toml
[[providers]]
module = "provider-openai"
name = "openai"
config = {
    base_url = null,                       # Optional custom endpoint (null = OpenAI default)
    default_model = "gpt-5.5",
    max_tokens = 4096,
    temperature = 0.7,
    reasoning = null,                      # Reasoning effort: minimal|low|medium|high|xhigh; null = not sent
    reasoning_summary = "detailed",        # Reasoning verbosity: auto|concise|detailed
    truncation = null,                     # null omits the field; OpenAI errors on context overflow.
                                           # Opt in to legacy auto-drop with truncation = "auto" (busts cache).
    prompt_cache_key = "",                 # Stable cache-routing identifier; empty = unset
    prompt_cache_retention = "24h",        # "24h" | "in_memory" | null (use model default)
    enable_response_chaining = "auto",     # "auto" | true | false  (reasoning-model chaining)
    enable_state = false,
    debug = false,                         # Enable standard debug events
    raw_debug = false                      # Enable ultra-verbose raw API I/O logging
}
```

> **Note**: `safety_identifier` is intentionally NOT a deployment config field. It is a per-end-user signal (abuse tracking) and must be set per-call via `kwargs`.

## Config Reference

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `base_url` | string | null | Custom API endpoint; null uses OpenAI default |
| `default_model` | string | `"gpt-5.5"` | Default model for requests |
| `max_tokens` | integer | `4096` | Maximum output tokens |
| `temperature` | float | `0.7` | Sampling temperature |
| `reasoning` | string | null | Reasoning effort: `minimal\|low\|medium\|high\|xhigh`; null = not sent |
| `reasoning_summary` | string | `"detailed"` | Reasoning verbosity: `auto\|concise\|detailed` |
| `truncation` | string | null | null omits the field (errors on overflow); `"auto"` silently drops oldest messages (busts prompt cache) |
| `prompt_cache_key` | string | `""` | Stable cache-routing identifier; empty = unset |
| `prompt_cache_retention` | string | `"24h"` | Cache TTL: `"24h"` \| `"in_memory"` \| null |
| `enable_response_chaining` | string/bool | `"auto"` | `"auto"` (auto-detect reasoning models) \| `true` \| `false` |
| `enable_state` | boolean | `false` | Enable OpenAI server-side state storage |
| `max_concurrent` | integer | `0` | Process-wide concurrency limit; `0` = unlimited |
| `timeout` | float | `600.0` | Request timeout in seconds |
| `debug` | boolean | `false` | Enable standard debug events |
| `raw_debug` | boolean | `false` | Enable ultra-verbose raw API I/O logging |

## Prompt Caching

The provider exposes OpenAI's prompt-caching parameters for maximizing cache hit rates.

### Default Behavior

- `prompt_cache_retention = "24h"` — Extended GPU-local KV storage on every supported model, instead of OpenAI's per-model `"in_memory"` default (5–10 min) for gpt-5.4 and below.
- `enable_response_chaining = "auto"` — For reasoning-capable models, the provider sends `store = true` and `previous_response_id` on subsequent turns. Empirical results show 85% prefix cache hit on turn 2 with chaining on, vs 0% off.
- `truncation = null` — The field is omitted from requests so the cached prefix is never silently rewritten on context overflow. Opt back into legacy auto-drop with `truncation = "auto"`.

### `prompt_cache_retention` Values

| Value | Meaning |
|-------|---------|
| `"24h"` | Extended GPU-local KV storage. Provider default for all supported models. |
| `"in_memory"` | 5–10 min in-process cache. OpenAI's per-model default for gpt-5.4 and below. |
| `null` | Field omitted; OpenAI picks the per-model default. |

The capability layer auto-drops values a model would reject (e.g., gpt-5.5+ rejects `"in_memory"`).

### `enable_response_chaining` Values

| Value | Behavior |
|-------|---------|
| `"auto"` | On iff model supports reasoning. Default. Right answer for most deployments. |
| `true` | Force on regardless of model. |
| `false` | Force off. Use for ZDR / regulated-industry deployments that cannot retain server-side state. |

When chaining is active for a reasoning model: `store = true` is set automatically, `previous_response_id` is sent on subsequent turns, and encrypted reasoning blocks are not re-inserted inline.

### `prompt_cache_key`

OpenAI shards Responses API traffic by hashing the first ~256 input tokens. A stable `prompt_cache_key` keeps a logical conversation pinned to one machine regardless of small prefix drift.

| Deployment Shape | Recommended Key |
|-----------------|----------------|
| Single-user agent loop (typical Amplifier) | conversation/session ID, e.g. `"conv_abc123"` |
| Multi-tenant with shared system prompt | `f"{tenant_id}:{system_prompt_version}"` |
| Low-volume single-session | leave unset; prefix-hash routing is sufficient |

## Deep Research Models

The provider supports OpenAI's deep research models which run as background tasks:

| Model | ID |
|-------|-----|
| `o3-deep-research` | `o3-deep-research-2025-06-26` |
| `o4-mini-deep-research` | `o4-mini-deep-research-2025-06-26` |

Deep research models poll for completion with:
- Poll interval: `5.0` seconds
- Background timeout: `1800.0` seconds (30 minutes)

## Authentication

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=sk-...
```

Or for Azure OpenAI:

```bash
export AZURE_OPENAI_API_KEY=...
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

Use [`provider-azure-openai`](../providers/azure_openai.md) for managed identity support.

## Observability

The provider emits standard provider events:

| Event | When |
|-------|------|
| `provider:request` | Before API call |
| `provider:response` | After successful response |
| `provider:retry` | On retry attempt |
| `provider:error` | On unrecoverable error |
| `provider:response_chain_invalidated` | When `previous_response_id` is rejected by the server |

## Installation

```bash
amplifier provider install provider-openai
```

Or in a bundle:

```yaml
providers:
  - module: provider-openai
    source: git+https://github.com/microsoft/amplifier-module-provider-openai@main
```
