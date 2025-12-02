---
title: Contributing
description: How to contribute to Amplifier
---

# Contributing

Amplifier is an experimental platform with a multi-repository ecosystem. Contributing typically means **creating your own repositories** rather than submitting PRs to a monolithic codebase.

## Understanding the Ecosystem

Amplifier's architecture is modular by design:

- **Core kernel** (`amplifier-core`) - Small, stable, boring. High bar for changes.
- **CLI application** (`amplifier-app-cli`) - Reference CLI for building and validating new capabilities. Not user-focused.
- **Reference implementations** - Canonical examples for each module type and application pattern
- **Community ecosystem** - Your own modules, tools, apps, and collections

!!! tip "Reference vs. Official"
    Current modules and apps are **reference implementations**, not "official" requirements. You can build alternatives, improvements, or entirely new capabilities. Users choose what to install based on their needs.

**See the [Showcase](../showcase/index.md) for examples of what the community has built.**

---

## Choose Your Contribution Type

### Applications

Full CLI applications built on Amplifier's kernel and libraries.

**Getting Started:**

1. Browse the [Showcase](../showcase/index.md) for application examples
2. Clone a reference app closest to your idea
3. Study the structure and patterns
4. Create your own repo: `amplifier-app-yourname`
5. Build your application
6. Publish and add back to the Showcase

**Learn More:** [Developer Guide](../developer/index.md)

---

### Modules

Extend Amplifier's runtime capabilities. Modules are loaded dynamically based on profile configuration.

#### Providers

LLM backend integrations.

**Reference Implementations:**
- [provider-anthropic](https://github.com/microsoft/amplifier-module-provider-anthropic)
- [provider-openai](https://github.com/microsoft/amplifier-module-provider-openai)
- [provider-mock](https://github.com/microsoft/amplifier-module-provider-mock) - Minimal testing reference

**Contract:** [Provider Contract](../developer/contracts/provider.md) | **Examples:** [Showcase](../showcase/index.md)

#### Tools

Agent capabilities for interacting with systems and data.

**Reference Implementations:**
- [tool-filesystem](https://github.com/microsoft/amplifier-module-tool-filesystem)
- [tool-bash](https://github.com/microsoft/amplifier-module-tool-bash)
- [tool-web](https://github.com/microsoft/amplifier-module-tool-web)

**Contract:** [Tool Contract](../developer/contracts/tool.md) | **Examples:** [Showcase](../showcase/index.md)

#### Orchestrators

Control execution flow and conversation loops.

**Reference Implementations:**
- [orchestrator-loop-basic](https://github.com/microsoft/amplifier-module-orchestrator-loop-basic)
- [orchestrator-loop-streaming](https://github.com/microsoft/amplifier-module-orchestrator-loop-streaming)
- [orchestrator-loop-events](https://github.com/microsoft/amplifier-module-orchestrator-loop-events)

**Contract:** [Orchestrator Contract](../developer/contracts/orchestrator.md) | **Examples:** [Showcase](../showcase/index.md)

#### Contexts

Manage conversation memory and state.

**Reference Implementations:**
- [context-simple](https://github.com/microsoft/amplifier-module-context-simple)
- [context-persistent](https://github.com/microsoft/amplifier-module-context-persistent)

**Contract:** [Context Contract](../developer/contracts/context.md) | **Examples:** [Showcase](../showcase/index.md)

#### Hooks

Observe, guide, and control agent behavior.

**Reference Implementations:**
- [hook-logging](https://github.com/microsoft/amplifier-module-hook-logging)
- [hook-approval](https://github.com/microsoft/amplifier-module-hook-approval)
- [hook-redaction](https://github.com/microsoft/amplifier-module-hook-redaction)

**Contract:** [Hook Contract](../developer/contracts/hook.md) | **Examples:** [Showcase](../showcase/index.md)

---

### Collections

Package agents, context files, and philosophy documents for specific workflows.

**Reference Implementations:**
- [collection-toolkit](https://github.com/microsoft/amplifier-collection-toolkit)
- [collection-design-intelligence](https://github.com/microsoft/amplifier-collection-design-intelligence)
- [collection-recipes](https://github.com/microsoft/amplifier-collection-recipes)

**Learn More:** [Collections Guide](../user_guide/collections.md) | **Examples:** [Showcase](../showcase/index.md)

---

## The Contribution Process

### 1. Choose What to Build

Pick an application, module type, or collection that interests you.

### 2. Find Your Starting Point

Look at reference implementations or community examples closest to your idea. Clone or fork as a starting point.

!!! tip "Reference Implementations"
    Some module types have special reference implementations designed for learning:
    
    - `provider-mock` - Minimal provider for testing
    - Most official modules serve as production-ready references

### 3. Create Your Repository

Follow naming conventions:

- Applications: `amplifier-app-{name}`
- Modules: `amplifier-module-{type}-{name}`
- Collections: `amplifier-collection-{name}`

### 4. Build Following Contracts

Each module type has a contract defining the interface. Follow it so your module works with the kernel.

**See:** [Developer Contracts](../developer/contracts/index.md)

### 5. Test Thoroughly

- Test with current Amplifier versions
- Ensure your module works in isolation
- Verify integration with other modules
- Document any dependencies

### 6. Publish to GitHub

Make your code publicly reviewable. Include:

- Comprehensive README
- Installation instructions
- Usage examples
- Tests
- License (typically MIT)

### 7. Add to Showcase

Submit a PR to add your project to the [Showcase](../showcase/index.md) catalog.

---

## What NOT to Contribute To

### ❌ amplifier-core (The Kernel)

The kernel has an extremely high bar for changes:

- Must be backward compatible
- Requires ≥2 modules to justify new features
- Needs spec-first design
- Complete test coverage required
- If you think you need to change the kernel, you probably don't

**Instead:** Build a module that works within existing contracts.

### ⚠️ amplifier-app-cli

The reference CLI is used by the core team to build and validate new capabilities. It changes frequently to adopt new features, stays lean to adapt quickly, and is not focused on user experience. Not a good place for easy first issues or incremental improvements.

**Instead:** Build your own application, use hooks to modify behavior, or package workflows as collections.

---

## Security Considerations

!!! danger "Critical Security Warning"
    Modules and applications execute arbitrary code with full system access. Users must review code before installation. Build with security in mind:
    
    - Validate all inputs
    - Handle credentials safely
    - Document security implications
    - Never include hardcoded secrets

---

## See Also

- [Module Development Guide](../developer/module_development.md) - Detailed module creation
- [Developer Contracts](../developer/contracts/index.md) - Module interfaces
- [Showcase](../showcase/index.md) - Community projects
- [Ecosystem](../ecosystem/index.md) - Available modules
