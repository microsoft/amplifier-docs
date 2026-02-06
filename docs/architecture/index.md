---
title: Architecture
description: Understanding Amplifier's architecture
---

# Architecture

Amplifier follows a Linux kernel-inspired architecture where a tiny, stable core provides mechanisms while all features live at the edges as replaceable modules.

## Core Principle

> **"The center stays still so the edges can move fast."**

## Topics

<div class="grid">

<div class="card">
<h3><a href="overview/">Overview</a></h3>
<p>High-level architecture and component relationships.</p>
</div>

<div class="card">
<h3><a href="kernel/">Kernel Philosophy</a></h3>
<p>Why the kernel is tiny, stable, and boring.</p>
</div>

<div class="card">
<h3><a href="modules/">Module System</a></h3>
<p>How modules are discovered, loaded, and coordinated.</p>
</div>

<div class="card">
<h3><a href="mount_plans/">Mount Plans</a></h3>
<p>The configuration contract between apps and the kernel.</p>
</div>

<div class="card">
<h3><a href="events/">Event System</a></h3>
<p>Canonical events and observability.</p>
</div>

</div>

## Quick Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Application Layer (amplifier-app-cli)                          │
│  • Resolves configuration → Creates Mount Plans                 │
│  • Provides approval/display systems                            │
│  • Manages sessions and agents                                  │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  Kernel (amplifier-core) - ~2,600 lines                         │
│  • Validates Mount Plans                                        │
│  • Loads modules via entry points                               │
│  • Coordinates session lifecycle                                │
│  • Emits canonical events via hooks                             │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  Modules (Userspace)                                            │
│  • Providers: LLM backends (Anthropic, OpenAI, Azure, Ollama)   │
│  • Tools: Agent capabilities (filesystem, bash, web, search)    │
│  • Orchestrators: Execution loops (basic, streaming, events)    │
│  • Contexts: Memory management (simple, persistent)             │
│  • Hooks: Observability & control (logging, approval, redaction)│
└─────────────────────────────────────────────────────────────────┘
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Kernel** | Ultra-thin core providing mechanisms only |
| **Module** | Swappable component implementing a contract |
| **Mount Plan** | Configuration specifying which modules to load |
| **Event** | Observable occurrence in the system |
| **Hook** | Module that observes/controls events |
| **Session** | Single conversation lifecycle |
| **Coordinator** | Infrastructure context for modules |
| **Context Manager** | Memory management with compaction |
| **Agent** | Configuration overlay for specialized sub-sessions |

## Design Principles

### Mechanism, Not Policy

The kernel provides **capabilities** without **decisions**:

| Kernel Provides (Mechanism) | Modules Decide (Policy) |
| --------------------------- | ----------------------- |
| Module loading              | Which modules to load   |
| Event emission              | What to log, where      |
| Session lifecycle           | Orchestration strategy  |
| Hook registration           | Security policies       |
| Context plumbing            | Compaction strategy     |

### Directness Over Abstraction

- Clear code paths over layered abstractions
- Explicit dependencies over hidden coupling
- Direct communication over complex messaging
- Simple data flow over elaborate state management

### Hooks for Everything Observable

- All important operations emit events
- Hooks can observe, modify, or block
- Streaming output via hooks, not callbacks
- Validation and approval via hooks
- Debug logging via hooks

## Module Types

| Type | Purpose | Examples |
|------|---------|----------|
| **Provider** | LLM backends | Anthropic, OpenAI, Azure, Ollama |
| **Tool** | Agent capabilities | Filesystem, Bash, Web, Search |
| **Orchestrator** | Execution loops | Basic, Streaming, Events |
| **Context** | Memory management | Simple, Persistent |
| **Hook** | Observability | Logging, Approval, Redaction, Streaming UI |

## Configuration Layers

```
Bundle (YAML/Markdown)
    ↓ compose
Mount Plan (dict)
    ↓ validate
Session (running)
```

- **Bundles**: Composable configuration units (amplifier-foundation)
- **Mount Plans**: Final configuration for the kernel
- **Sessions**: Running instances with mounted modules
