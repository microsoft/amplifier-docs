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

## Core Principles

### 1. Mechanism, Not Policy

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

| Linux Concept | Amplifier Analog | Decision Guidance |
|---------------|------------------|-------------------|
| Ring 0 kernel | `amplifier-core` | Export mechanisms (mount, emit), never policy. Keep tiny & boring. |
| Syscalls | Session operations | Few and sharp: `create_session()`, `mount()`, `emit()`. Stable ABI. |
| Loadable drivers | Modules (providers, tools, hooks, orchestrators) | Compete at edges; comply with protocols; regeneratable. |
| Signals/Netlink | Event bus / hooks | Kernel emits lifecycle events; hooks observe; non-blocking. |
| /proc & dmesg | Unified JSONL log | One canonical stream; redaction before logging. |
| Capabilities/LSM | Approval & capability checks | Least privilege; deny-by-default; policy at edges. |
| Scheduler | Orchestrator modules | Swap strategies by replacing module, not changing kernel. |
| VM/Memory | Context manager | Deterministic compaction; emit `context:*` events. |

## Polyglot Module Loading

Modules can be written in any language. Four transport types determine how a module integrates with its host:

- **python**: Direct import into Python host. Dependencies managed via `uv pip install` at load time.
- **rust**: Rust host links directly as a native library. Non-Rust host spawns the compiled binary as a gRPC sidecar.
- **wasm**: Loaded in-process via a WASM runtime. Sandboxed execution with no host OS access unless explicitly granted.
- **grpc**: Connects to an external gRPC service at the runtime endpoint declared in `amplifier.toml`.

### The Module Declares What It IS, The Host Decides How to CONSUME

The `amplifier.toml` manifest declares the module's transport. The host runtime reads this declaration and selects the appropriate loading strategy:

- **Rust host + `transport=rust`** → direct native link. Zero serialization overhead.
- **Python host + `transport=rust`** → gRPC sidecar. The host spawns the compiled binary and communicates over gRPC.
- **Any host + `transport=grpc`** → remote endpoint. The host connects to the service address at startup.

This separation keeps module authors free from host concerns. A module declares what it is; it does not dictate how it is consumed. A Rust module written for direct linking works transparently as a sidecar in any non-Rust host without modification.

### gRPC as Universal Cross-Language Bridge

gRPC bridges exist for all six module types (tool, hook, orchestrator, context, provider, and scaffold). Any module type can cross a language boundary through gRPC without changing its external contract.

The gRPC sidecar pattern is symmetric with Architecture Decision #3: the same binary that a non-Rust host launches as a sidecar is the binary that a CI environment or container deployment runs as a standalone service. No separate packaging or build step is required for cross-language deployment.

## Next Steps

- **[Overview](overview/)** - Understand how all pieces fit together
- **[Kernel Philosophy](kernel/)** - Learn what belongs in the kernel (and what doesn't)
- **[Module System](modules/)** - Discover how modules are loaded and coordinated
- **[Mount Plans](mount_plans/)** - Understand the configuration contract
- **[Event System](events/)** - Explore the observability infrastructure
