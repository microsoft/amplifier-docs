---
title: bash
description: Shell command execution tool for Amplifier agents
---

# bash Tool

Shell command execution for Amplifier agents with safety features and approval mechanisms.

## Overview

The `bash` tool enables AI agents to execute shell commands in the local environment. It includes safety checks, command timeouts, and optional approval gates to protect the system.

## Configuration

```yaml
tools:
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
    config:
      timeout: 30                    # Command timeout in seconds (default: 30)
      allowed_commands: []           # Whitelist of allowed commands (default: all)
      denied_commands:               # Blocked commands (default: destructive ops)
        - "rm -rf /"
        - "sudo rm"
      working_dir: "/path/to/dir"    # Override working directory (optional)
      require_approval: true         # Require user approval per command (default: true)
```

## Safety Features

### Default Blocked Commands

The tool blocks destructive operations by default:

- `rm -rf /` (and variations)
- `sudo rm`
- `mkfs`
- `dd if=/dev/zero`
- Commands writing to critical system paths (`/etc/passwd`, `/etc/shadow`, etc.)

### Command Timeout

Commands are terminated after the configured timeout (default: 30 seconds) to prevent runaway processes:

```yaml
config:
  timeout: 60  # Increase for long-running builds/tests
```

### Working Directory Enforcement

Commands execute in the session's working directory. The `working_dir` config overrides this:

```yaml
config:
  working_dir: "/home/user/project"  # All commands run here
```

### Command Approval

Optionally require user approval before executing commands:

```yaml
config:
  require_approval: true
```

When enabled, the tool emits a `tool:approval_required` event that approval hooks can intercept.

## Tool Schema

### Input

```json
{
  "type": "object",
  "properties": {
    "command": {
      "type": "string",
      "description": "Shell command to execute"
    },
    "timeout": {
      "type": "integer",
      "description": "Command timeout in seconds (overrides config default)"
    },
    "run_in_background": {
      "type": "boolean",
      "description": "Run command in background, returning PID immediately"
    }
  },
  "required": ["command"]
}
```

### Output

```json
{
  "output": {
    "stdout": "Command output",
    "stderr": "Error output",
    "returncode": 0
  },
  "error": null
}
```

## Usage Examples

### Basic Command

```json
{
  "command": "ls -la"
}
```

Returns directory listing with full details.

### Command with Timeout

```json
{
  "command": "npm test",
  "timeout": 120
}
```

Runs tests with 2-minute timeout (overriding config default).

### Background Process

```json
{
  "command": "python server.py",
  "run_in_background": true
}
```

Starts server in background, returns PID immediately.

## Safety Profiles

The tool supports configurable safety profiles:

```yaml
# Permissive (development)
config:
  allowed_commands: []      # No whitelist
  denied_commands:          # Only critical blocks
    - "rm -rf /"
  require_approval: false

# Restrictive (production)
config:
  allowed_commands:         # Whitelist only
    - "ls"
    - "cat"
    - "grep"
  require_approval: true
```

## Error Handling

The tool returns structured errors for:

- **Command not found**: Returns error with `command not found` message
- **Permission denied**: Returns error with `permission denied` message
- **Timeout exceeded**: Terminates process and returns timeout error
- **Blocked command**: Returns error explaining why command was blocked

## Events

The tool emits standard tool events:

- `tool:pre` - Before command execution (includes command and timeout)
- `tool:post` - After command completion (includes stdout, stderr, returncode)
- `tool:error` - On execution failure
- `tool:approval_required` - When `require_approval: true` (optional hook intercept)

## Integration with Hooks

### Approval Hook

Combine with approval hooks for interactive safety:

```yaml
hooks:
  - module: hooks-approval
    config:
      require_approval_for:
        - tool: bash
          patterns:
            - "rm .*"
            - "sudo .*"
```

### Redaction Hook

Combine with redaction hooks to sanitize output:

```yaml
hooks:
  - module: hooks-redaction
    config:
      redact_patterns:
        - pattern: "password=\\w+"
          replacement: "password=***"
```

## Best Practices

### 1. Use Timeouts for Long Operations

```yaml
config:
  timeout: 300  # 5 minutes for builds/tests
```

### 2. Whitelist in Production

```yaml
config:
  allowed_commands:
    - "git status"
    - "git diff"
    - "pytest"
```

### 3. Require Approval for Destructive Operations

```yaml
config:
  require_approval: true
```

### 4. Set Working Directory

```yaml
config:
  working_dir: "/workspace/project"  # Isolate to project dir
```

## Security Considerations

⚠️ **WARNING**: The bash tool grants AI agents shell access. Use with caution:

- ✅ Enable in development environments
- ⚠️ Use whitelists in shared environments
- ❌ Avoid in untrusted multi-tenant systems

**Defense in depth**:
1. Configure `allowed_commands` whitelist
2. Enable `require_approval: true`
3. Use approval hooks for sensitive patterns
4. Set restrictive `working_dir`
5. Monitor via JSONL event logs

## Implementation Notes

- Commands execute in subprocesses with timeout enforcement
- Environment variables from parent process are inherited
- Interactive commands (requiring stdin) are not supported
- Background processes (`run_in_background: true`) are detached and won't be killed on session end

## See Also

- [Tool Contract](../../reference/contracts/tool.md) - Tool interface specification
- [Approval Hooks](../hooks/approval.md) - Interactive approval gates
- [Redaction Hooks](../hooks/redaction.md) - Output sanitization
