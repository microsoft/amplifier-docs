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

## Shell Completion

Install shell completion with `--install-completion`. The shell is auto-detected from `$SHELL`:

```bash
amplifier --install-completion
```

Supported shells and their config files:

| Shell | Config File |
|-------|-------------|
| bash | `~/.bashrc` or `~/.bash_profile` |
| zsh | `~/.zshrc` |
| fish | `~/.config/fish/completions/amplifier.fish` |

To activate after installation:

```bash
source ~/.bashrc  # or ~/.zshrc for zsh
```

The command is idempotent — running it again when completion is already installed is a no-op.

## Architecture

```
amplifier-app-cli/
├── main.py              # Entry point, CLI group
├── commands/            # Command implementations
│   ├── run.py
│   ├── session.py
│   ├── bundle.py
│   ├── provider.py
│   ├── module.py
│   ├── source.py
│   ├── routing.py
│   ├── agents.py
│   ├── allowed_dirs.py
│   ├── denied_dirs.py
│   ├── tool.py
│   ├── notify.py
│   ├── init.py
│   ├── update.py
│   ├── version.py
│   └── reset.py
├── session_runner.py    # Session initialization
├── session_spawner.py   # Agent delegation
├── console.py           # Rich console utilities
└── ui/                  # UI components
    ├── error_display.py
    ├── render_message.py
    └── approval_system.py
```

## Session Management

The CLI uses `SessionStore` for persistent session storage and `SessionConfig` for configuration. Sessions are created via `create_initialized_session()` which handles:

- Session initialization
- Bundle preparation
- Configuration resolution
- Transcript restoration (for resume)

## Agent Delegation

Agent delegation is implemented in `session_spawner.py` using:

- `spawn_sub_session()` - Create child sessions with agent overlays
- `resume_sub_session()` - Resume existing sub-sessions
- Configuration merging with tool/hook inheritance filtering
- State persistence for multi-turn conversations

## Interactive Mode

Interactive sessions use `interactive_chat()` which provides:

- REPL loop with prompt history
- Ctrl+C cancellation handling
- Multi-line input support (Ctrl-J for newline)
- Session state persistence

Slash commands available in interactive mode (`CommandProcessor.COMMANDS`):

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/mode <name>` | Set or toggle a mode (e.g., `/mode plan`) |
| `/modes` | List available modes |
| `/status` | Show session status |
| `/config` | Show current configuration |
| `/tools` | List available tools |
| `/agents` | List available agents |
| `/save [filename]` | Save conversation transcript |
| `/clear` | Clear conversation context |
| `/rename <name>` | Rename current session |
| `/fork [turn] [name]` | Fork session at turn N: `/fork [turn]` |
| `/skills` | List available skills |
| `/skill <name>` | Load a skill (e.g., `/skill simplify`) |
| `/allowed-dirs` | Manage allowed write directories |
| `/denied-dirs` | Manage denied write directories |

## Related

- [CLI Reference](../../user_guide/cli.md) - User documentation
- [Session Guide](../../user_guide/sessions.md) - Session concepts
- [CLI Case Study](../../developer_guides/applications/cli_case_study.md) - Implementation patterns
