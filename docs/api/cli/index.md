---
title: CLI API
description: amplifier-app-cli API reference
---

# CLI API

The `amplifier-app-cli` package provides the reference CLI implementation.

**Source**: [github.com/microsoft/amplifier-app-cli](https://github.com/microsoft/amplifier-app-cli)

## Main Entry Point

The CLI entry point is `amplifier_app_cli.main:main`.

```python
from amplifier_app_cli.main import main

# Run the CLI
main()
```

## Commands

CLI commands are implemented in `amplifier_app_cli.commands`:

| Command | Description |
|---------|-------------|
| `run` | Execute prompts (single command or interactive) |
| `continue` | Resume the most recent session |
| `resume` | Interactively select and resume a session |
| `session` | Session management (list, show, resume, fork, delete, cleanup) |
| `bundle` | Bundle management (list, show, use, clear, current, add, remove, update) |
| `provider` | Provider management (install, add, list, remove, edit, test, models, manage) |
| `module` | Module management (list, show, add, remove, current, update, validate, override) |
| `source` | Source override management (add, remove, list, show) |
| `routing` | Model routing configuration (list, use, show, manage, create) |
| `agents` | Agent management (list, show, dirs) |
| `allowed-dirs` | Allowed write directory management (list, add, remove) |
| `denied-dirs` | Denied write directory management (list, add, remove) |
| `tool` | Tool management and invocation (list, info, invoke) |
| `notify` | Notification configuration (status, desktop, ntfy, reset) |
| `init` | First-run initialization wizard |
| `update` | Update Amplifier and modules |
| `version` | Show version information |
| `reset` | Reset Amplifier configuration |

See [CLI Reference](../../user_guide/cli.md) for complete usage documentation.

## Architecture

```
amplifier-app-cli/
├── main.py              # Entry point, CLI group
├── commands/            # Command implementations
│   ├── run.py          # Run command
│   ├── session.py      # Session commands
│   ├── bundle.py       # Bundle management
│   ├── provider.py     # Provider management
│   ├── module.py       # Module management
│   ├── routing.py      # Routing configuration
│   └── ...
├── session_runner.py    # Session initialization
├── session_spawner.py   # Agent delegation
└── console.py          # Rich UI components
```

## Related Documentation

- [CLI Reference](../../user_guide/cli.md) - Complete command reference
- [CLI Case Study](../../developer_guides/applications/cli_case_study.md) - Implementation patterns
