---
title: Bash Tool
description: Shell command execution
---

# Bash Tool

Executes shell commands for agents.

## Module ID

`tool-bash`

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `working_dir` | string | `"."` | Working directory for command execution. Falls back to `session.working_dir` capability if not set. |
| `timeout` | int | `30` | Command timeout in seconds |
| `require_approval` | bool | `true` | Require approval for commands |
| `safety_profile` | string | `"strict"` | Safety profile: `strict`, `standard`, `permissive`, `unrestricted` |
| `allowed_commands` | list | `[]` | Allowlist of allowed command patterns (supports wildcards) |
| `denied_commands` | list | `[]` | Additional custom blocklist patterns |
| `safety_overrides` | dict | — | Fine-grained overrides with `allow` and `block` lists |
| `max_output_bytes` | int | `100000` | Maximum output size before truncation (~100KB) |

## Tool Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | ✓ | Bash command to execute |
| `timeout` | int | | Per-call timeout in seconds (default: 30). Increase for builds, tests, or monitoring. Use `run_in_background` for truly indefinite processes. |
| `run_in_background` | bool | | Run command in background, returning immediately with PID (default: `false`) |

## Safety Profiles

| Profile | `sudo` | `rm -rf /` | Use Case |
|---------|--------|------------|----------|
| `strict` (default) | Blocked | Blocked | Workstations, shared environments |
| `standard` | Blocked (allowlist can override) | Blocked | Trusted environments with specific needs |
| `permissive` | Allowed | Blocked | Containers, VMs, dedicated instances |
| `unrestricted` | Allowed | Allowed | Dedicated hardware (e.g., Raspberry Pi) |

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-tool-bash)**
