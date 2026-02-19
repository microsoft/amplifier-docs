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
| Providers | 8 | Anthropic, OpenAI, Azure, Gemini, Ollama, GitHub Copilot, vLLM, Mock |
| Tools | 9 | Filesystem, Bash, Web, Search, Task, Todo, Skills, MCP, Slash Command |
| Orchestrators | 3 | Basic, Streaming, Events |
| Contexts | 2 | Simple, Persistent |
| Hooks | 11 | Logging, Approval, Redaction, Backup, Streaming UI, Schedulers, etc. |
| Libraries | 1 | amplifier-foundation |
| Bundles | 12 | Recipes, Design Intelligence, Python Dev, Stories, Superpowers, Shadow, etc. |

---

## Using Modules

Modules are specified in profiles:

```yaml
# ~/.amplifier/profiles/my-profile.md
---
profile:
  name: my-profile
  extends: base

tools:
  - module: tool-web
    source: git+https://github.com/microsoft/amplifier-module-tool-web@main
---
```

Or managed via CLI:

```bash
# List installed modules
amplifier module list

# Show module details
amplifier module show tool-filesystem
```

See the [User Guide](../user_guide/profiles.md) for complete profile documentation.
