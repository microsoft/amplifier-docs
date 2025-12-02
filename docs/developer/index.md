---
title: Developer Guide
description: Building modules and contributing to Amplifier
---

# Developer Guide

This guide covers developing custom modules for Amplifier.

## Topics

<div class="grid">

<div class="card">
<h3><a href="module_development/">Module Development</a></h3>
<p>Create custom providers, tools, hooks, orchestrators, and context managers.</p>
</div>

<div class="card">
<h3><a href="contracts/">Module Contracts</a></h3>
<p>Reference documentation for module interfaces.</p>
</div>

</div>

## Quick Start

### Creating a Module

```bash
# Create module directory
mkdir amplifier-module-tool-myname
cd amplifier-module-tool-myname

# Initialize project
cat > pyproject.toml << 'EOF'
[project]
name = "amplifier-module-tool-myname"
version = "1.0.0"
dependencies = []

[project.entry-points."amplifier.modules"]
tool-myname = "amplifier_module_tool_myname:mount"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF

# Create module code
mkdir amplifier_module_tool_myname
cat > amplifier_module_tool_myname/__init__.py << 'EOF'
async def mount(coordinator, config=None):
    tool = MyTool(config or {})
    await coordinator.mount("tools", tool, name="myname")
    return None

class MyTool:
    name = "myname"
    description = "My custom tool"
    input_schema = {"type": "object", "properties": {}}

    def __init__(self, config):
        self.config = config

    async def execute(self, input):
        return {"success": True, "output": "Hello!"}
EOF
```

### Testing Locally

```bash
# Install in development mode
uv pip install -e .

# Test with Amplifier
amplifier source add tool-myname file://$(pwd)
amplifier run --profile dev "Test my new tool"
```

## Philosophy

Amplifier's development philosophy emphasizes:

1. **Modules are independent**: No peer dependencies
2. **Contracts are stable**: Backward compatibility is sacred
3. **Test in isolation**: Mock the coordinator
4. **Regenerate, don't edit**: Rebuild modules from spec

## Module Types

| Type | Purpose | Contract |
|------|---------|----------|
| Provider | LLM backends | [Provider Contract](contracts/provider.md) |
| Tool | Agent capabilities | [Tool Contract](contracts/tool.md) |
| Hook | Observability | [Hook Contract](contracts/hook.md) |
| Orchestrator | Execution loops | [Orchestrator Contract](contracts/orchestrator.md) |
| Context | Memory management | [Context Contract](contracts/context.md) |
