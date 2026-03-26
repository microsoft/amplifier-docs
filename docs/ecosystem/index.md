---
title: Ecosystem
description: Amplifier ecosystem components and modules
---

# Ecosystem

The Amplifier ecosystem consists of modular components that combine to create AI agent systems. This page provides an overview of the ecosystem structure and available components.

## Ecosystem Layers

```
┌─────────────────────────────────────────────┐
│  Applications                               │
│  User-facing apps that compose capabilities │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Bundles                                    │
│  Composable configuration packages          │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Runtime Modules                            │
│  Providers, Tools, Orchestrators, Hooks     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Kernel (amplifier-core)                    │
│  Ultra-thin kernel providing mechanisms     │
└─────────────────────────────────────────────┘
```

## Core Components

### Kernel

The foundational layer that provides module loading, event emission, and coordination.

| Component | Description | Repository |
|-----------|-------------|------------|
| **amplifier-core** | Ultra-thin kernel for modular AI agent system | [amplifier-core](https://github.com/microsoft/amplifier-core) |

### Applications

User-facing applications that compose libraries and modules.

| Component | Description | Repository |
|-----------|-------------|------------|
| **amplifier** | Main Amplifier project and entry point - installs amplifier-app-cli via `uv tool install` | [amplifier](https://github.com/microsoft/amplifier) |
| **amplifier-app-cli** | Reference CLI application implementing the Amplifier platform | [amplifier-app-cli](https://github.com/microsoft/amplifier-app-cli) |
| **amplifier-app-log-viewer** | Web-based log viewer for debugging sessions with real-time updates | [amplifier-app-log-viewer](https://github.com/microsoft/amplifier-app-log-viewer) |
| **amplifier-app-benchmarks** | Benchmarking and evaluating Amplifier | [amplifier-app-benchmarks](https://github.com/DavidKoleczek/amplifier-app-benchmarks) |

**Note**: When you install `amplifier`, you get the amplifier-app-cli as the executable application.

### Libraries

Foundational libraries used by applications (not used directly by runtime modules).

| Component | Description | Repository |
|-----------|-------------|------------|
| **amplifier-foundation** | Foundational library for bundles, module resolution, and shared utilities | [amplifier-foundation](https://github.com/microsoft/amplifier-foundation) |

**Architectural Boundary**: Libraries are consumed by applications (like amplifier-app-cli). Runtime modules only depend on amplifier-core and never use these libraries directly.

## Runtime Modules

Runtime modules implement specific capabilities and are loaded dynamically based on configuration.

### Module Types

- **[Providers](../modules/providers/)** - LLM backend integrations (Anthropic, OpenAI, Gemini, etc.)
- **[Tools](../modules/tools/)** - Agent capabilities (filesystem, bash, web, etc.)
- **[Orchestrators](../modules/orchestrators/)** - Execution loop strategies (basic, streaming, events)
- **[Contexts](../modules/contexts/)** - Memory management (simple, persistent)
- **[Hooks](../modules/hooks/)** - Observability and control (logging, approval, redaction, etc.)

See the [full module catalog](https://github.com/microsoft/amplifier/blob/main/docs/MODULES.md) for complete listings of:

- Official runtime modules (providers, tools, orchestrators, contexts, hooks)
- Bundles (recipes, browser-tester, design-intelligence, python-dev, etc.)
- Community applications and bundles
- Community modules

## Bundles

Composable configuration packages that combine providers, behaviors, agents, and context into reusable units.

Bundles enable:

- **Reusable configurations** - Pre-configured setups for common use cases
- **Behavior composition** - Combine multiple capabilities
- **Agent libraries** - Collections of specialized agents
- **Context resources** - Skills, prompts, and knowledge bases

### Using Bundles

```bash
# Add a bundle to the registry
amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-recipes@main

# Use a bundle
amplifier bundle use recipes

# Check for updates
amplifier bundle update --check
```

See the [Bundle Guide](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md) for creating your own bundles.

## Module Discovery

Modules are discovered via:

1. **Python Entry Points** - Standard entry points in `pyproject.toml`
2. **Environment Variables** - `AMPLIFIER_MODULES=/path/to/modules`
3. **Explicit Search Paths** - `ModuleLoader(search_paths=[...])`

## Module Contracts

All modules implement standard protocols:

| Module Type | Required Interface | Purpose |
|-------------|-------------------|---------|
| Provider | `complete()`, `parse_tool_calls()`, `get_info()`, `list_models()` | LLM backends |
| Tool | `name`, `description`, `input_schema`, `execute()` | Agent actions |
| Orchestrator | `execute()` | Execution loops |
| Context | `add_message()`, `get_messages()`, `compact()` | Memory |
| Hook | `__call__(event, data) -> HookResult` | Lifecycle observation and control |

See [Module Contracts](../reference/contracts/) for detailed specifications.

## Community Contributions

The Amplifier community builds:

- **Applications** - Domain-specific UIs and tools
- **Bundles** - Specialized capability packages
- **Modules** - Custom providers, tools, and hooks

> **SECURITY WARNING**: Community components execute arbitrary code in your environment with full access to your filesystem, network, and credentials. Only use components from sources you trust. Review code before installation.

See the [full community catalog](https://github.com/microsoft/amplifier/blob/main/docs/MODULES.md#community-applications) for:

- Community applications
- Community bundles
- Community modules (providers, tools, hooks)

## Building Components

Amplifier can help you build Amplifier components! See:

- [Module Development Guide](../developer/module_development.md) - Creating custom modules
- [Bundle Guide](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md) - Creating custom bundles
- [DEVELOPER.md](https://github.com/microsoft/amplifier/blob/main/docs/DEVELOPER.md) - Using AI to create modules

## Module Source Resolution

Modules can come from:

- **Git repositories** - `git+https://github.com/org/repo@branch`
- **Local paths** - `/path/to/module`
- **Python packages** - `amplifier-module-tool-bash`

The `ModuleSourceResolver` handles flexible module sourcing.

## Next Steps

- **[Module Catalog](https://github.com/microsoft/amplifier/blob/main/docs/MODULES.md)** - Complete catalog of all components
- **[Module Contracts](../reference/contracts/)** - Protocol specifications
- **[Architecture Overview](../architecture/overview/)** - How components fit together
- **[Module System](../architecture/modules/)** - Module loading and coordination
