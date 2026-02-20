---
title: Config Library
---

# Config Library

The `amplifier-config` library provides three-scope configuration management with deep merge semantics for Amplifier applications.

## Scopes

Configuration is layered across three scopes, with higher-priority scopes overriding lower ones:

```
USER (~/.amplifier/settings.yaml)
   ↓  (lowest priority)
PROJECT (.amplifier/settings.yaml)
   ↓
LOCAL (.amplifier/settings.local.yaml)
   ↑  (highest priority)
```

Local settings override project settings, which override user settings.

## Key APIs

### ConfigManager

```python
from amplifier_config import ConfigManager, Scope

manager = ConfigManager(paths=config_paths)

# Get merged configuration
config = manager.get_merged()

# Get specific scope
user_config = manager.get(Scope.USER)

# Set value in scope
manager.set(Scope.PROJECT, "default_provider", "anthropic")

# Save changes
manager.save(Scope.PROJECT)
```

### ConfigPaths

Inject application-specific paths:

```python
from amplifier_config import ConfigPaths

paths = ConfigPaths(
    user_dir=Path("~/.amplifier"),
    project_dir=Path(".amplifier"),
    local_dir=Path(".amplifier"),  # Different filename
)
```

### deep_merge

Canonical recursive merge function:

```python
from amplifier_config import deep_merge

base = {
    "session": {"orchestrator": "loop-basic"},
    "providers": [{"module": "provider-anthropic"}]
}

overlay = {
    "session": {"context": "context-persistent"},
    "tools": [{"module": "tool-bash"}]
}

result = deep_merge(base, overlay)
# {
#     "session": {"orchestrator": "loop-basic", "context": "context-persistent"},
#     "providers": [{"module": "provider-anthropic"}],
#     "tools": [{"module": "tool-bash"}]
# }
```

### Merge Rules

| Type | Behavior |
|------|----------|
| dict | Recursive merge |
| list | Overlay replaces base |
| scalar | Overlay replaces base |
| None | Overlay removes key |

## Settings Schema

```yaml
# ~/.amplifier/settings.yaml

# Default provider
default_provider: anthropic

# Default profile
default_profile: dev

# Provider configurations
providers:
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    default_model: claude-sonnet-4-5

# Module source overrides (for development)
module_sources:
  provider-anthropic: file:///home/user/modules/provider-anthropic
```

## Module Source Overrides

For local development, override module sources:

```yaml
# .amplifier/settings.local.yaml (gitignored)
module_sources:
  provider-anthropic: file:///home/user/dev/provider-anthropic
  tool-filesystem: file:///home/user/dev/tool-filesystem
```

## Environment Variables

Settings support environment variable expansion:

```yaml
providers:
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    endpoint: ${ANTHROPIC_ENDPOINT:-https://api.anthropic.com}
```

Syntax:

- `${VAR}` - Required variable
- `${VAR:-default}` - With default value

## Best Practices

1. **User scope**: Personal preferences, API keys
2. **Project scope**: Team defaults, committed to git
3. **Local scope**: Machine-specific, gitignored

## References

- **→ [amplifier-config Repository](https://github.com/microsoft/amplifier-config)** - Full documentation
