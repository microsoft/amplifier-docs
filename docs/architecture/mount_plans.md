---
title: Mount Plans
description: The configuration contract between apps and kernel
---

# Mount Plans

A Mount Plan is the configuration contract that tells the kernel which modules to load and how to configure them.

## Overview

Mount Plans are the **only way** applications communicate configuration to the kernel. They specify:

- Which orchestrator and context manager to use (required)
- Which providers, tools, and hooks to load (optional)
- Configuration for each module
- Agent definitions for sub-session delegation

## Structure

```python
{
    "session": {
        "orchestrator": str,    # Required: module ID
        "context": str,         # Required: module ID
        "injection_budget_per_turn": int | None,
        "injection_size_limit": int | None
    },
    "orchestrator": {
        "config": dict          # Orchestrator-specific config
    },
    "context": {
        "config": dict          # Context-specific config
    },
    "providers": [
        {
            "module": str,      # Module ID
            "source": str,      # Git URL or path
            "config": dict      # Provider-specific config
        }
    ],
    "tools": [
        {
            "module": str,
            "source": str,
            "config": dict
        }
    ],
    "hooks": [
        {
            "module": str,
            "source": str,
            "config": dict
        }
    ],
    "agents": {
        "agent-name": {
            "description": str,
            "session": dict,
            "providers": list,
            "tools": list,
            "hooks": list,
            "system": {
                "instruction": str
            }
        }
    }
}
```

## Example Mount Plan

```python
{
    "session": {
        "orchestrator": "loop-streaming",
        "context": "context-persistent"
    },
    "providers": [
        {
            "module": "provider-anthropic",
            "source": "git+https://github.com/microsoft/amplifier-module-provider-anthropic@main",
            "config": {
                "model": "claude-sonnet-4-5",
                "api_key": "${ANTHROPIC_API_KEY}"
            }
        }
    ],
    "tools": [
        {
            "module": "tool-filesystem",
            "config": {
                "allowed_paths": ["."],
                "require_approval": False
            }
        },
        {"module": "tool-bash"},
        {"module": "tool-web"}
    ],
    "hooks": [
        {
            "module": "hooks-logging",
            "config": {
                "output_dir": ".amplifier/logs"
            }
        }
    ]
}
```

## Session Configuration

The `session` section controls orchestrator, context, and injection limits:

```python
"session": {
    "orchestrator": "loop-streaming",
    "context": "context-persistent",
    "injection_budget_per_turn": 10000,  # Max tokens hooks can inject per turn (None for unlimited)
    "injection_size_limit": 10240        # Max bytes per hook injection (None for unlimited)
}
```

### Injection Limits

Injection limits control hook context injection:

- `injection_budget_per_turn`: Maximum total tokens hooks can inject in a single turn
- `injection_size_limit`: Maximum bytes per individual injection

Default values provide safety while allowing meaningful feedback. Set to `None` for unlimited (use with caution).

## Module Sources

All module references support an optional `source` field:

```python
{
    "module": "tool-custom",
    "source": "git+https://github.com/org/tool-custom@main"
}
```

**Source URI formats:**
- Git: `git+https://github.com/org/repo@ref`
- File: `file:///absolute/path` or `./relative/path`
- Package: `package-name` (or omit source to use installed package)

## Module Configuration

Each module can have an optional `config` dictionary:

```python
{
    "module": "tool-filesystem",
    "config": {
        "allowed_paths": ["/app/data"],
        "require_approval": True
    }
}
```

### Environment Variables

Config values can reference environment variables using `${VAR_NAME}` syntax:

```python
{
    "module": "provider-anthropic",
    "config": {
        "api_key": "${ANTHROPIC_API_KEY}",
        "model": "claude-sonnet-4-5"
    }
}
```

### Context Config

The context manager gets its config from a top-level `context.config` key:

```python
{
    "context": {
        "config": {
            "max_tokens": 200000,
            "compact_threshold": 0.92,
            "auto_compact": True
        }
    }
}
```

## Agents Section

The `agents` section defines configuration overlays for spawning child sessions:

```python
{
    "agents": {
        "bug-hunter": {
            "description": "Specialized agent for debugging",
            "session": {
                "orchestrator": "loop-basic"
            },
            "tools": [
                {"module": "tool-grep"},
                {"module": "tool-lsp"}
            ],
            "system": {
                "instruction": "You are a debugging specialist..."
            }
        }
    }
}
```

**Important**: The `agents` section has different semantics from other sections:
- Other sections (`providers`, `tools`, `hooks`): Lists of modules to load NOW
- `agents` section: Dict of configuration overlays for future use by app layer

Agent configurations are partial mount plans that get merged with a parent session's config when creating a child session.

## Validation

Use `MountPlanValidator` to validate structure before loading:

```python
from amplifier_core.validation import MountPlanValidator

validator = MountPlanValidator()
result = validator.validate(mount_plan)

if not result.passed:
    print(result.format_errors())
    sys.exit(1)
```

`MountPlanValidator` checks:
- Root structure is a dict with required `session` section
- Session section has required `orchestrator` and `context` fields
- Module specs have required `module` field
- Config and source fields are correct types when present

## Creating Sessions

```python
from amplifier_core import AmplifierSession

# Create session with mount plan
session = AmplifierSession(mount_plan)

# Initialize and execute
await session.initialize()
response = await session.execute("Hello, world!")
await session.cleanup()

# Or use context manager
async with AmplifierSession(mount_plan) as session:
    response = await session.execute("Hello, world!")
```

## Philosophy

The Mount Plan embodies the kernel philosophy:

- **Mechanism, not policy**: Says _what_ to load, not _why_
- **Policy at edges**: All decisions about _which_ modules live in the app layer
- **Stable contract**: Schema is the stable boundary between app and kernel
- **Text-first**: Simple dictionaries, easily serializable and inspectable
- **Deterministic**: Same mount plan always produces same configuration

## Related Documentation

- **[Module Contracts](../developer/contracts/index.md)** - Interface definitions
- **[MOUNT_PLAN_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/MOUNT_PLAN_SPECIFICATION.md)** - Complete specification
