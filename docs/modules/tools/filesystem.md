---
title: Filesystem Tool
description: File read/write operations
---

# Filesystem Tool

Provides file system operations for agents.

## Module ID

`tool-filesystem`

## Tools Provided

The module provides three specialized tools:

- **read_file** - Read file contents with line numbering and pagination
- **write_file** - Write content to files (overwrites if exists)
- **edit_file** - Perform exact string replacements in files

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `allowed_read_paths` | list or null | `null` | Allowed read paths (null = allow all reads) |
| `allowed_write_paths` | list | `["."]` | Allowed write paths (current directory and subdirectories) |
| `require_approval` | bool | `false` | Require approval before executing operations |
| `working_dir` | string | (session capability) | Working directory for relative paths |

**Configuration Example:**

```toml
[[tools]]
module = "tool-filesystem"
config = {
    allowed_read_paths = null,  # null = allow all reads (default)
    allowed_write_paths = ["."],  # Current directory only
    require_approval = false
}
```

**Philosophy**: Reads are low-risk (consuming data), writes are high-risk (modifying system state).

**Note**: If `working_dir` is not set in config, the module uses the `session.working_dir` coordinator capability if available, falling back to `Path.cwd()`.

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-tool-filesystem)**
