---
title: Contributing
description: How to contribute to Amplifier
---

# Contributing

Amplifier is an experimental platform with a multi-repository ecosystem. Contributing typically means **creating your own repositories** rather than submitting PRs to a monolithic codebase.

## Understanding the Ecosystem

Amplifier's architecture is modular by design:

- **Core kernel** (`amplifier-core`) - Small, stable, boring. Rust kernel with Python bindings via PyO3. High bar for changes.
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
- [provider-mock](https://github.com/microsoft/amplifier-module-provider-mock)

**Getting Started:**

1. Review the [Provider Contract](../modules/providers/index.md)
2. Clone a reference provider as template
3. Implement the Provider protocol
4. Test with the reference CLI
5. Publish your provider module

**Learn More:** [Provider Development](../developer/providers.md)

---

#### Tools

Agent capabilities like filesystem access, web browsing, code execution.

**Reference Implementations:**
- [tool-filesystem](https://github.com/microsoft/amplifier-module-tool-filesystem)
- [tool-bash](https://github.com/microsoft/amplifier-module-tool-bash)
- [tool-web](https://github.com/microsoft/amplifier-module-tool-web)

**Getting Started:**

1. Review the [Tool Contract](../modules/tools/index.md)
2. Clone a reference tool as template
3. Implement the Tool protocol
4. Define your tool's schema
5. Test with the reference CLI
6. Publish your tool module

**Learn More:** [Tool Development](../developer/tools.md)

---

#### Orchestrators

Execution loop strategies (basic, streaming, events).

**Reference Implementations:**
- [loop-basic](https://github.com/microsoft/amplifier-module-loop-basic)
- [loop-streaming](https://github.com/microsoft/amplifier-module-loop-streaming)
- [loop-events](https://github.com/microsoft/amplifier-module-loop-events)

**Getting Started:**

1. Review the [Orchestrator Contract](../modules/orchestrators/index.md)
2. Study reference orchestrators
3. Implement the Orchestrator protocol
4. Test with various tool combinations
5. Publish your orchestrator module

**Learn More:** [Orchestrator Development](../developer/orchestrators.md)

---

#### Contexts

Memory management strategies (simple, persistent).

**Reference Implementations:**
- [context-simple](https://github.com/microsoft/amplifier-module-context-simple)

**Getting Started:**

1. Review the [Context Contract](../modules/contexts/index.md)
2. Study the reference context
3. Implement the ContextManager protocol
4. Test compaction strategies
5. Publish your context module

**Learn More:** [Context Development](../developer/contexts.md)

---

#### Hooks

Observability and control (logging, redaction, approval).

**Reference Implementations:**
- [hooks-logging](https://github.com/microsoft/amplifier-module-hooks-logging)
- [hooks-redaction](https://github.com/microsoft/amplifier-module-hooks-redaction)

**Getting Started:**

1. Review the [Hook Contract](../modules/hooks/index.md)
2. Study reference hooks
3. Implement hook handlers
4. Test with event emission
5. Publish your hook module

**Learn More:** [Hook Development](../developer/hooks.md)

---

## Publishing Your Work

### Module Naming

Follow the convention: `amplifier-module-{type}-{name}`

Examples:
- `amplifier-module-provider-gemini`
- `amplifier-module-tool-database`
- `amplifier-module-hook-metrics`

### Repository Structure

```
amplifier-module-tool-yourname/
├── amplifier_module_tool_yourname/
│   ├── __init__.py          # mount() function
│   └── ...
├── tests/
├── pyproject.toml
└── README.md
```

### Entry Point

Register in `pyproject.toml`:

```toml
[project.entry-points."amplifier.modules"]
tool-yourname = "amplifier_module_tool_yourname:mount"
```

### Documentation

Include in your README:

- Purpose and use cases
- Configuration options
- Example usage
- Contract compliance

---

## Core Contributions

!!! note "External Contributions"
    This project is not currently accepting external contributions, but we're actively working toward opening this up. We value community input and look forward to collaborating in the future. For now, feel free to fork and experiment!

The kernel has a high bar for changes. Most functionality belongs in modules.

**When to contribute to core:**

- Bug fixes in existing contracts
- Performance improvements
- Protocol clarifications
- Documentation improvements

**How to contribute:**

1. Open an issue describing the problem
2. Discuss the solution approach
3. Submit a PR with tests
4. Reference the issue in your PR

!!! note "Rust Toolchain Required"
    The `amplifier-core` kernel is implemented in Rust with Python bindings via PyO3. Contributing to core requires the Rust toolchain (`rustup`) and `maturin` for building the Python extension.

---

## License

By contributing, you agree to the [Contributor License Agreement](https://cla.opensource.microsoft.com).
