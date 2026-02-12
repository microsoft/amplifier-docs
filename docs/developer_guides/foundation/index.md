---
title: Foundation Developer Guide
description: Building with amplifier-core and contributing to the foundation
---

# Foundation Developer Guide

This guide is for developers who want to **work with the Amplifier foundation** - the core kernel, libraries, and architectural components that power all Amplifier applications.

## Who This Guide Is For

This guide is for you if you want to:

- ✅ **Build applications** using amplifier-core (like building your own CLI, web UI, or automation tool)
- ✅ **Contribute** to amplifier-core, amplifier-profiles, or other foundation libraries
- ✅ **Understand** the kernel internals and how the foundation works
- ✅ **Use libraries** (profiles, collections, config, module-resolution) in your applications

## Not What You're Looking For?

- **Using the Amplifier CLI?** → See the [CLI User Guide](../../user_guide/)
- **Creating custom modules (tools/providers)?** → See the [Module Developer Guide](../modules/index.md)
- **Building applications on Amplifier?** → Start here, then see [Application Developer Guide](../applications/)

## Understanding the Architecture

Amplifier is built in layers, inspired by the Linux kernel model:

```
┌─────────────────────────────────────────────┐
│        Applications Layer                   │
│  (amplifier-app-cli, your-app, etc.)       │
│                                             │
│  • User interaction                         │
│  • Configuration resolution                 │
│  • Mount Plan creation                      │
│  • Uses libraries                           │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│        Libraries Layer                       │
│  (amplifier-foundation, amplifier-profiles,  │
│   amplifier-collections, amplifier-config,   │
│   amplifier-module-resolution)               │
│                                              │
│  • Bundle composition                        │
│  • Profile loading & inheritance            │
│  • Configuration management                 │
│  • Module resolution strategies             │
│  • NOT used by runtime modules              │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│        Kernel Layer                          │
│  (amplifier-core ~2,600 lines)              │
│                                              │
│  • Session lifecycle                         │
│  • Mount Plan validation                     │
│  • Module discovery and loading             │
│  • Event emission                            │
│  • Coordinator infrastructure               │
│  • Mechanism, not policy                    │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│        Modules Layer                         │
│  (providers, tools, orchestrators, contexts, │
│   hooks - loaded at runtime)                │
│                                              │
│  • Only depend on amplifier-core            │
│  • Implement specific capabilities          │
│  • Swappable at runtime                     │
└──────────────────────────────────────────────┘
```

### Key Principle: Separation of Concerns

- **Kernel (amplifier-core)**: Provides mechanisms, not policy. Small, stable, boring.
- **Libraries**: Application-layer concerns. Profile loading, config resolution, etc.
- **Applications**: Build on kernel + libraries. Decide what gets loaded and when.
- **Modules**: Extend capabilities. No dependencies on libraries.

## Foundation Components

### amplifier-foundation (Bundle Composition Library)

Foundational library for the Amplifier ecosystem: bundle composition, utilities, and reference content.

**What it does:**
- Load, compose, validate, and resolve bundles from local and remote sources
- @Mention system: parse and resolve `@namespace:path` references in instructions
- Utilities: YAML/frontmatter I/O, dict merging, path handling, caching
- Reference content: reusable providers, agents, behaviors, and context files

**When to use:**
- Building applications with reusable configurations
- You want human-readable YAML + Markdown bundles
- You need bundle composition (base + overlays)

**Repository:** [microsoft/amplifier-foundation](https://github.com/microsoft/amplifier-foundation)

**Documentation:** See [amplifier-foundation Library](amplifier_foundation/) for detailed guide with examples

### amplifier-core (The Kernel)

The heart of Amplifier. ~2,600 lines of mechanism-only code.

**What it does:**
- Validates and loads Mount Plans
- Manages session lifecycle
- Emits canonical events
- Provides coordinator infrastructure
- Enforces contracts

**What it doesn't do:**
- Choose which modules to load (applications do this)
- Format output (applications do this)
- Decide execution strategy (orchestrator modules do this)
- Store configuration (libraries do this)

**Repository:** [microsoft/amplifier-core](https://github.com/microsoft/amplifier-core)

### amplifier-profiles

Profile and agent loading, inheritance, and Mount Plan compilation.

**What it does:**
- Load profiles and agents from multiple sources
- Handle profile inheritance and overlays
- Compile profiles to Mount Plans
- Resolve @mentions in configuration

**Used by:** Applications (not modules)

**Repository:** [microsoft/amplifier-profiles](https://github.com/microsoft/amplifier-profiles)

### amplifier-collections

Convention-based collection discovery and management.

**What it does:**
- Discover collection resources by convention from search paths
- Resolve collection names to filesystem paths
- Install and uninstall collections with lock file tracking
- Load profiles, agents, and context from collections

**Used by:** Applications (not modules)

**Repository:** [microsoft/amplifier-collections](https://github.com/microsoft/amplifier-collections)

### amplifier-config

Three-scope configuration management.

**What it does:**
- User scope: `~/.amplifier/settings.yaml`
- Project scope: `.amplifier/settings.yaml`
- Local scope: `.amplifier/settings.local.yaml`
- Deep merge semantics
- Module source overrides

**Used by:** Applications (not modules)

**Repository:** [microsoft/amplifier-config](https://github.com/microsoft/amplifier-config)

### amplifier-module-resolution

Module source resolution with pluggable strategies.

**What it does:**
- Resolve module IDs to sources
- Git repository resolution
- File path resolution
- Package resolution
- Source override management

**Used by:** Applications (not modules)

**Repository:** [microsoft/amplifier-module-resolution](https://github.com/microsoft/amplifier-module-resolution)

## Quick Start Options

### Option 1: Using amplifier-foundation (Recommended)

High-level API with bundle composition:

```python
from amplifier_foundation import load_bundle

# Load and compose bundles
foundation = await load_bundle("git+https://github.com/microsoft/amplifier-foundation@main")
provider = await load_bundle("./providers/anthropic.yaml")
composed = foundation.compose(provider)

# Prepare and execute
prepared = await composed.prepare()
async with await prepared.create_session() as session:
    response = await session.execute("Hello!")
```

See [amplifier-foundation Library](amplifier_foundation/) for detailed documentation.

### Option 2: Using amplifier-core directly

Lower-level API with manual mount plans:

```python
from amplifier_core import AmplifierSession

# Define a Mount Plan
mount_plan = {
    "session": {
        "orchestrator": "loop-basic",
        "context": "context-simple"
    },
    "providers": [
        {
            "module": "provider-anthropic",
            "source": "git+https://github.com/microsoft/amplifier-module-provider-anthropic@main",
            "config": {
                "default_model": "claude-sonnet-4-5"
            }
        }
    ],
    "tools": [
        {
            "module": "tool-bash",
            "source": "git+https://github.com/microsoft/amplifier-module-tool-bash@main"
        }
    ]
}

# Create and use a session
async with AmplifierSession(mount_plan) as session:
    # Execute a prompt
    response = await session.execute("What is 2 + 2?")
    print(response)
```

That's it! The kernel handles:
- Validating the mount plan
- Loading the modules
- Coordinating the execution
- Emitting events

## What's Next?

<div class="grid">

<div class="card">
<h3><a href="../applications/">Building Applications</a></h3>
<p>Learn how to build applications on amplifier-core. Session management, mount plans, and library integration.</p>
</div>

<div class="card">
<h3><a href="../../architecture/overview/">Architecture Overview</a></h3>
<p>Deep dive into the architecture, kernel philosophy, and design decisions.</p>
</div>

<div class="card">
<h3><a href="using_libraries/">Using Libraries</a></h3>
<p>How to integrate amplifier-profiles, amplifier-collections, and other libraries in your application.</p>
</div>

<div class="card">
<h3><a href="contributing/">Contributing</a></h3>
<p>Guidelines for contributing to amplifier-core, libraries, and the foundation.</p>
</div>

</div>

## Philosophy & Principles

When working with the foundation, keep these principles in mind:

### 1. Mechanism, Not Policy

The kernel provides capabilities, not decisions. If two teams could want different behavior, it's policy → belongs outside the kernel.

**Example:**
- ✅ Kernel: "Emit a `tool:pre` event before tool execution"
- ❌ Kernel: "Log tool execution to stdout in JSON format"

The first is mechanism (event emission). The second is policy (what to do with events).

### 2. Backward Compatibility is Sacred

Kernel interfaces must not break existing modules or applications. Evolution is additive only.

### 3. Small and Stable

The kernel is intentionally minimal (~2,600 lines). Changes are rare and boring. Innovation happens at the edges (modules), not in the kernel.

### 4. Test in Isolation

Mock the coordinator when testing. Modules and applications should be testable without running the full kernel.

### 5. Libraries are for Applications

Runtime modules never import libraries. Only applications use libraries. This keeps the module boundary clean.

```python
# ✅ In your application
from amplifier_profiles import ProfileLoader
from amplifier_config import ConfigManager

# ❌ In a module (provider, tool, etc.)
from amplifier_profiles import ProfileLoader  # Never do this!
```

## Resources

- **[Architecture Documentation](../../architecture/)** - Kernel philosophy, module system, events
- **[Kernel Philosophy](../../architecture/kernel/)** - Deep dive into kernel design
- **[Module Contracts](../modules/contracts/)** - Reference for module interfaces
- **[Application Developer Guide](../applications/)** - Building applications on amplifier-core
- **[Contributing Guide](../../community/contributing/)** - How to contribute

## Getting Help

- **GitHub Discussions:** [Amplifier Discussions](https://github.com/microsoft/amplifier/discussions)
- **Issues:** [Report bugs or request features](https://github.com/microsoft/amplifier/issues)
- **Architecture Questions:** Read the [Design Philosophy](https://github.com/microsoft/amplifier-core/blob/main/docs/DESIGN_PHILOSOPHY.md)
