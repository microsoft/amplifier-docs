---
title: Tools
description: Agent capabilities
---

# Tools

Tools provide capabilities that agents can invoke to interact with the environment.

## Available Tools

| Tool | Description | Repository |
|------|-------------|------------|
| **[Filesystem](filesystem.md)** | Read/write files | [GitHub](https://github.com/microsoft/amplifier-module-tool-filesystem) |
| **[Bash](bash.md)** | Execute shell commands | [GitHub](https://github.com/microsoft/amplifier-module-tool-bash) |
| **[Web](web.md)** | Search and fetch web content | [GitHub](https://github.com/microsoft/amplifier-module-tool-web) |
| **[Search](search.md)** | Search codebases | [GitHub](https://github.com/microsoft/amplifier-module-tool-search) |
| **[Task](task.md)** | Delegate to sub-agents | [GitHub](https://github.com/microsoft/amplifier-module-tool-task) |
| **[Todo](todo.md)** | AI self-accountability for complex tasks | [GitHub](https://github.com/microsoft/amplifier-module-tool-todo) |

<!-- MODULE_LIST_TOOL -->

## Configuration

```toml
[[tools]]
module = "tool-filesystem"
config = {
    allowed_read_paths = null,  # null = allow all reads (default), or ["path1", "path2"]
    allowed_write_paths = ["."],  # Default: current directory and subdirectories only
    require_approval = false
}

[[tools]]
module = "tool-bash"
config = {
    working_dir = ".",           # Working directory (defaults to session.working_dir capability)
    timeout = 30,                # Default timeout in seconds
    require_approval = false,
    safety_profile = "strict",   # Safety profile: strict, standard, permissive, unrestricted
    allowed_commands = [],       # Allowlist patterns (supports wildcards)
    denied_commands = [],        # Additional custom blocked patterns
    safety_overrides = {         # Fine-grained overrides
        allow = [],              # Patterns to allow (even if normally blocked)
        block = []               # Patterns to block (even if normally allowed)
    }
}

[[tools]]
module = "tool-task"
config = {
    max_recursion_depth = 1  # Maximum recursion depth (default: 1)
}
```

## Filesystem Tool

Provides file operations:

- `read_file` - Read with line numbering and pagination
- `write_file` - Write/overwrite files
- `edit_file` - Exact string replacements

**Security:**
- Reads permissive by default (`allowed_read_paths = null`)
- Writes restrictive by default (`allowed_write_paths = ["."]`)

## Bash Tool

Execute shell commands with platform-appropriate safety.

**Platform Behavior:**
- **Linux/macOS/WSL**: Full bash shell with pipes, redirects, variables
- **Windows**: Limited to simple commands

**Safety Profiles:**

| Profile | `sudo` | `rm -rf /` | Use Case |
|---------|--------|------------|----------|
| `strict` (default) | ✗ | ✗ | Workstations, shared environments |
| `standard` | ✗ | ✗ | Trusted environments |
| `permissive` | ✓ | ✗ | Containers, VMs |
| `unrestricted` | ✓ | ✓ | Dedicated hardware |

## Task Tool

Delegate complex subtasks to specialized sub-agents:

```python
{
    "agent": "zen-architect",
    "instruction": "Analyze the authentication system"
}
```

**Features:**
- Multi-turn conversations via `session_id`
- Context inheritance control
- Provider preferences
- Depth limiting

## Contract

See [Tool Contract](../../developer/contracts/tool.md) for implementation details.
