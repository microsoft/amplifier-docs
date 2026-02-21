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
```

## Contract

See [Tool Contract](../../developer/contracts/tool.md) for implementation details.
