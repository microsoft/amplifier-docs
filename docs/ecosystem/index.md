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
| Providers | 8 | Anthropic, OpenAI, Azure, Gemini, Ollama, GitHub ... |
| Tools | 9 | Filesystem, Bash, Web, Search, Task, Todo, Skills, MCP ... |
| Contexts | 2 | Simple (in-memory), Persistent (file-backed) |
| Hooks | 10+ | Logging, Redaction, Approval, Backup, Status ... |
| Orchestrators | 3 | Basic, Streaming, Events |

---

## Explore Components

**Browse by category:**

- **[Providers](../modules/providers/index.md)** - Connect to AI model backends
- **[Tools](../modules/tools/index.md)** - Extend agent capabilities
- **[Orchestrators](../modules/orchestrators/index.md)** - Control execution flow
- **[Contexts](../modules/contexts/index.md)** - Manage conversation memory
- **[Hooks](../modules/hooks/index.md)** - Observe and control behavior

**Build your own:**

- **[Developer Guide](../developer_guides/index.md)** - Learn to build custom modules
- **[Module Contracts](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/README.md)** - Technical specifications
