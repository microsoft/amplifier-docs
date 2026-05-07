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
        "orchestrator": str,           # Required: orchestrator module ID
        "orchestrator_source": str,    # Optional: orchestrator source URI
        "context": str,                # Required: context manager module ID
        "context_source": str,         # Optional: context source URI
        "injection_budget_per_turn": int | None,  # Optional: max tokens hooks can inject per turn (default: 10000, None for unlimited)
        "injection_size_limit": int | None        # Optional: max bytes per hook injection (default: 10240, None for unlimited)
    },
    "orchestrator": {
        "config": dict        # Optional: orchestrator-specific configuration
    },
    "context": {
        "config": dict        # Optional: context-specific configuration
    },
    "providers": [            # Optional: list of provider configurations
        {
            "module": str,     # Required: provider module ID
            "source": str,     # Optional: source URI (git, file, package)
            "config": dict     # Optional: provider-specific config
        }
    ],
    "tools": [                # Optional: list of tool configurations
        {
            "module": str,     # Required: tool module ID
            "source": str,     # Optional: source URI (git, file, package)
            "config": dict     # Optional: tool-specific config
        }
    ],
    "agents": {               # Optional: agent configuration overlays (app-layer data)
        "<agent-name>": {
            "description": str,         # Agent description (for task tool display)
            "session": dict,            # Optional: override orchestrator/context
            "providers": list,          # Optional: override providers
            "tools": list,              # Optional: override tools
            "hooks": list,              # Optional: override hooks
            "system": {"instruction": str}  # System instruction for agent persona
        }
    },
    "hooks": [                # Optional: list of hook configurations
        {
            "module": str,     # Required: hook module ID
            "source": str,     # Optional: source URI (git, file, package)
            "config": dict     # Optional: hook-specific config
        }
    ]
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
- File: `file:///absolute/path` or `/absolute/path` or `./relative/path`
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

Validation happens in two phases: structural validation (before loading) and runtime validation (during initialization).

### Pre-Load Structural Validation

Use `MountPlanValidator` to validate mount plan structure before attempting to load modules:

```python
from amplifier_core.validation import MountPlanValidator

validator = MountPlanValidator()
result = validator.validate(mount_plan)

if not result.passed:
    print(result.format_errors())
    sys.exit(1)

# Safe to proceed with session creation
session = AmplifierSession(mount_plan)
```

`MountPlanValidator` checks:
- Root structure is a dict with required `session` section
- Session section has required `orchestrator` and `context` fields
- Module specs have required `module` field
- Config and source fields are correct types when present
- Unknown sections generate warnings (not errors)

### Runtime Validation

`AmplifierSession` performs additional validation on initialization:

- `session.orchestrator` must be loadable
- `session.context` must be loadable
- At least one provider must be configured (required for agent loops)

### Module Loading

- All specified module IDs must be discoverable
- Module loading failures are logged but non-fatal (except orchestrator and context)
- Invalid config for a module causes that module to fail loading

### Error Handling

- Missing required fields: `ValueError` raised immediately
- Module not found: Logged as warning, session continues
- Invalid module config: Logged as warning, module skipped

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
