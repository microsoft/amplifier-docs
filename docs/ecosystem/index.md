---
title: Ecosystem
description: Amplifier modules and libraries
---

# Ecosystem

Amplifier's modular architecture provides a rich ecosystem of components you can mix and match.

---

## Runtime Modules

Modules are loaded dynamically at runtime based on your profile configuration. They extend the kernel with capabilities.

<div class="grid cards" markdown>

-   :material-cloud-outline: **[Providers](../modules/providers/index.md)**

    ---

    Connect to AI model providers like Anthropic, OpenAI, Azure, and Ollama.

-   :material-tools: **[Tools](../modules/tools/index.md)**

    ---

    Extend agent capabilities with filesystem, bash, web, search, and task delegation.

-   :material-play-circle-outline: **[Orchestrators](../modules/orchestrators/index.md)**

    ---

    Control execution loops: basic, streaming, or event-driven.

-   :material-memory: **[Contexts](../modules/contexts/index.md)**

    ---

    Manage conversation state with in-memory or persistent storage.

-   :material-hook: **[Hooks](../modules/hooks/index.md)**

    ---

    Observe, guide, and control agent behavior with logging, approval, and more.

</div>

---

## Foundation Library

The **amplifier-foundation** library provides higher-level functionality for applications (like the CLI). It is **not** used by runtime modules.

| Library | Description | Repository |
|---------|-------------|------------|
| **[amplifier-foundation](../developer_guides/foundation/amplifier_foundation/index.md)** | Bundle composition, profiles, config, module resolution, and utilities | [GitHub](https://github.com/microsoft/amplifier-foundation) |

!!! info "Architectural Boundary"
    Libraries are consumed by applications. Runtime modules only depend on `amplifier-core` and never use libraries directly.

---

## Quick Reference

**Total Official Components**: 45+

| Category | Count | Examples |
|----------|-------|----------|
| Providers | 8 | Anthropic, OpenAI, Azure, Gemini, Ollama, GitHub Copilot |
| Tools | 9 | Filesystem, Bash, Web, Search, Task, MCP, Slash Commands |
| Orchestrators | 3 | Basic, Streaming, Events |
| Contexts | 2 | Simple (in-memory), Persistent (file-backed) |
| Hooks | 10+ | Logging, Approval, Redaction, Streaming UI, Schedulers |
| Bundles | 20+ | Recipes, Browser Tester, Design Intelligence, Python Dev, LSP |

**See the full catalog**: [Amplifier Component Catalog](https://github.com/microsoft/amplifier/blob/main/docs/MODULES.md)

---

## Community Ecosystem

The Amplifier community has created applications, bundles, and modules:

- **Community Applications** - Standalone apps built with Amplifier (transcribe, blog creator, voice assistant)
- **Community Bundles** - Composable capability bundles (deepwiki, memory, parallax-discovery, perplexity)
- **Community Modules** - Providers, tools, and hooks from the community

**Browse community contributions**: [MODULES.md - Community Sections](https://github.com/microsoft/amplifier/blob/main/docs/MODULES.md#community-applications)

!!! warning "Security Notice"
    Community components execute code in your environment with full access. Only use from trusted sources. Review code before installation.

---

## Module Architecture

All modules follow the same pattern:

1. **Entry point**: Implement `mount(coordinator, config)` function
2. **Registration**: Register capabilities with the coordinator
3. **Isolation**: Handle errors gracefully, never crash the kernel
4. **Contracts**: Follow one of the stable interfaces (Tool, Provider, Hook, etc.)

For technical details, see:
- **[Module Contracts](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/README.md)** - Authoritative contract specifications
- **[Module Development Guide](../developer/module_development.md)** - How to create modules

---

## Getting Started

**Using modules**: See the [Modules Overview](../modules/index.md)

**Creating modules**: See the [Module Development Guide](../developer/module_development.md)

**Creating bundles**: See the [Bundle System Guide](../developer_guides/foundation/amplifier_foundation/bundle_system.md)
