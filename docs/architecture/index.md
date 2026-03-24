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
       │ Mount Plan (config dictionary)
       │
┌──────▼──────────────────────────────────────────────────────────┐
│  Kernel Layer (amplifier-core)                                  │
│  • Validates Mount Plans                                        │
│  • Discovers and loads modules                                  │
│  • Provides Coordinator infrastructure                          │
│  • Emits canonical events                                       │
└──────┬──────────────────────────────────────────────────────────┘
       │
       │ Coordinator (session_id, config, hooks, mount points)
       │
┌──────▼──────────────────────────────────────────────────────────┐
│  Module Layer (Competing Implementations)                       │
│                                                                  │
│  Providers         Tools            Orchestrators               │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐                │
│  │ Anthropic│     │Filesystem│     │  Basic   │                │
│  │  OpenAI  │     │   Bash   │     │Streaming │                │
│  │  Gemini  │     │   Web    │     │  Events  │                │
│  └──────────┘     └──────────┘     └──────────┘                │
│                                                                  │
│  Context Managers  Hooks                                        │
│  ┌──────────┐     ┌──────────┐                                 │
│  │  Simple  │     │ Logging  │                                 │
│  │Persistent│     │Redaction │                                 │
│  └──────────┘     │ Approval │                                 │
│                    └──────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Core Principles

### 1. Mechanisms, Not Policies

The kernel provides **capabilities**, not **decisions**:

- ✅ Kernel: "You can load modules, emit events, register hooks"
- ❌ Kernel: "Use this specific provider, log to this location"

**Litmus test**: "Could two teams want different behavior?" → If yes, it's policy → Module, not kernel.

### 2. Ruthless Simplicity

- KISS taken to heart: as simple as possible, but no simpler
- Minimize abstractions - every layer must justify existence
- Start minimal, grow as needed
- Code you don't write has no bugs

### 3. Small, Stable, Boring Kernel

- Kernel changes rarely, maintains backward compatibility always
- Easy to reason about by single maintainer
- Favor deletion over accretion
- Innovation happens at edges (modules)

### 4. Modular Design ("Bricks & Studs")

- Each module = self-contained "brick" with clear responsibility
- Interfaces = "studs" that allow independent regeneration
- Prefer regeneration over editing
- Stable contracts enable parallel development

### 5. Event-First Observability

- If it's important → emit a canonical event
- If it's not observable → it didn't happen
- One JSONL stream = single source of truth
- Hooks observe without blocking

### 6. Text-First, Inspectable

- Human-readable, diffable, versionable representations
- JSON schemas for validation
- No hidden state, no magic globals
- Explicit > implicit

## The Linux Kernel Analogy

Amplifier mirrors Linux kernel concepts:

| Linux Concept | Amplifier Analog | Purpose |
|---------------|------------------|---------|
| Ring 0 kernel | `amplifier-core` | Mechanisms only, never policy |
| Syscalls | Session operations | Few, sharp APIs |
| Loadable drivers | Modules | Compete at edges |
| Signals/Netlink | Event bus / hooks | Observe and control |
| /proc & dmesg | JSONL logs | Single canonical stream |
| Capabilities | Approval system | Deny-by-default |
| Scheduler | Orchestrator modules | Swap execution strategies |
| VM/Memory | Context manager | Conversation memory |

## Next Steps

- **[Overview](overview/)** - Understand how all pieces fit together
- **[Kernel Philosophy](kernel/)** - Learn what belongs in the kernel (and what doesn't)
- **[Module System](modules/)** - Discover how modules are loaded and coordinated
- **[Mount Plans](mount_plans/)** - Understand the configuration contract
- **[Event System](events/)** - Explore the observability infrastructure
