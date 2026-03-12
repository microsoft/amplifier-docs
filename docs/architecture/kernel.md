---
title: Kernel Philosophy
description: Design principles for the Amplifier kernel
---

# Kernel Philosophy

The Amplifier kernel follows the Linux kernel model: a tiny, stable center that provides mechanisms while pushing all policy decisions to the edges.

## Core Principles

### 1. Mechanism, Not Policy

The kernel provides **capabilities** and **stable contracts**. Modules decide **behavior**.

| Kernel Provides (Mechanism) | Modules Decide (Policy) |
|----------------------------|-------------------------|
| Module loading | Which modules to load |
| Event emission | What to log, where |
| Session lifecycle | Orchestration strategy |
| Hook registration | Security policies |

**Litmus test**: "Could two teams want different behavior?" → If yes, it's policy → Module, not kernel.

### 2. Ruthless Simplicity

- KISS taken to heart: as simple as possible, but no simpler
- Minimize abstractions - every layer must justify existence
- Start minimal, grow as needed (avoid future-proofing)
- Code you don't write has no bugs

### 3. Small, Stable, Boring Kernel

- Kernel changes rarely, maintains backward compatibility always
- Easy to reason about by single maintainer
- Favor deletion over accretion in kernel
- Innovation happens at edges (modules)

### 4. Modular Design (Bricks & Studs)

- Each module = self-contained "brick" with clear responsibility
- Interfaces = "studs" that allow independent regeneration
- Prefer regeneration over editing (rebuild from spec, don't line-edit)
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

## The Linux Kernel Decision Framework

Use Linux kernel as a metaphor when decisions are unclear.

### Metaphor Mapping

| Linux Concept | Amplifier Analog | Decision Guidance |
|---------------|------------------|-------------------|
| **Ring 0 kernel** | `amplifier-core` | Export mechanisms (mount, emit), never policy. Keep tiny & boring. |
| **Syscalls** | Session operations | Few and sharp: `create_session()`, `mount()`, `emit()`. Stable ABI. |
| **Loadable drivers** | Modules (providers, tools, hooks, orchestrators) | Compete at edges; comply with protocols; regeneratable. |
| **Signals/Netlink** | Event bus / hooks | Kernel emits lifecycle events; hooks observe; non-blocking. |
| **/proc & dmesg** | Unified JSONL log | One canonical stream; redaction before logging. |
| **Capabilities/LSM** | Approval & capability checks | Least privilege; deny-by-default; policy at edges. |
| **Scheduler** | Orchestrator modules | Swap strategies by replacing module, not changing kernel. |
| **VM/Memory** | Context manager | Deterministic compaction; emit `context:*` events. |

### Decision Playbook

When requirements are vague:

1. **Is this kernel work?**
   - If it selects, optimizes, formats, routes, plans → **module** (policy)
   - Kernel only adds mechanisms many policies could use
   - **Litmus test**: Could two teams want different behavior? → Module

2. **Do we have two implementations?**
   - Prototype at edges first
   - Extract to kernel only after ≥2 modules converge on the need

3. **Prefer regeneration**
   - Keep contracts stable
   - Regenerate modules to new spec (don't line-edit)

4. **Event-first**
   - Important actions → emit canonical event
   - Hooks observe without blocking

5. **Text-first**
   - All diagnostics → JSONL
   - External views derive from canonical stream

6. **Ruthless simplicity**
   - Fewer moving parts wins
   - Clearer failure modes wins

## Kernel vs Module Boundaries

### Kernel Responsibilities (Mechanisms)

**What kernel does**:
- Stable contracts (protocols, schemas)
- Module loading/unloading (mount/unmount)
- Event dispatch (emit lifecycle events)
- Capability checks (enforcement mechanism)
- Minimal context plumbing (session_id, request_id)

**What kernel NEVER does**:
- Select providers or models (policy)
- Decide orchestration strategy (policy)
- Choose tool behavior (policy)
- Format output or pick logging destination (policy)
- Make product decisions (policy)

### Module Responsibilities (Policies)

**Providers**: Which model, what parameters
**Tools**: How to execute capabilities
**Orchestrators**: Execution strategy (basic, streaming, planning)
**Hooks**: What to log, where to log, what to redact
**Context**: Compaction strategy, summarization approach
**Agents**: Configuration overlays for sub-sessions

### Evolution Without Breaking Modules

**Additive evolution**:
- Add optional capabilities (feature negotiation)
- Extend schemas with optional fields
- Provide deprecation windows for removals

**Two-implementation rule**:
- Need from ≥2 independent modules before adding to kernel
- Proves the mechanism is actually general

**Backward compatibility is sacred**:
- Kernel changes must not break existing modules
- Clear deprecation notices + dual-path support
- Long sunset periods

## The Rust Kernel

amplifier-core is implemented in Rust with Python bindings via PyO3:

```
+---------------------------------------------------------------+
| RUST KERNEL (crates/amplifier-core/)                          |
| * Session lifecycle       * Event system                      |
| * Coordinator             * Hook registry                     |
| * Type-safe contracts     * Cancellation tokens               |
+----------------------------+----------------------------------+
                             | PyO3 bridge (bindings/python/)
                             v
+---------------------------------------------------------------+
| PYTHON BINDINGS (python/amplifier_core/)                      |
| * Same public API          * Pydantic models                  |
| * Module loader (Python)   * Backward-compatible imports      |
+----------------------------+----------------------------------+
                             | protocols (Tool, Provider, etc.)
                             v
+---------------------------------------------------------------+
| MODULES (Userspace - Swappable)                               |
| * Providers: LLM backends (Anthropic, OpenAI, Azure, Ollama) |
| * Tools: Capabilities (filesystem, bash, web, search)        |
| * Orchestrators: Execution loops (basic, streaming, events)  |
| * Contexts: Memory management (simple, persistent)           |
| * Hooks: Observability (logging, redaction, approval)        |
+---------------------------------------------------------------+
```

**Key features**:
- **Zero changes** for Python consumers - same imports, same API
- **Type-safe core** with Protocol-based modules
- **Fast event dispatch** via Rust implementation
- **Backward compatible** - existing modules work unchanged

The `RUST_AVAILABLE` flag (on `amplifier_core._engine`) indicates whether the Rust engine loaded successfully. When available:
- Top-level imports (`from amplifier_core import AmplifierSession`) return Rust-backed types
- Submodule imports (`from amplifier_core.session import AmplifierSession`) return Python types for backward compatibility
- `HookRegistry` uses the Rust implementation for all hook dispatch
- `CancellationToken` uses the Rust implementation

## Module Design: Bricks & Studs

### The LEGO Model

Think of software as LEGO bricks:

**Brick** = Self-contained module with clear responsibility
**Stud** = Interface/protocol where bricks connect
**Blueprint** = Specification (docs define target state)
**Builder** = AI generates code from spec

### Key Practices

1. **Start with the contract** (the "stud")
   - Define: purpose, inputs, outputs, side-effects, dependencies
   - Document in README or top-level docstring
   - Keep small enough to hold in one prompt

2. **Build in isolation**
   - Code, tests, fixtures inside module directory
   - Only expose contract via `__all__` or interface file
   - No other module imports internals

3. **Regenerate, don't patch**
   - When change needed inside brick → rewrite whole brick from spec
   - Contract change → locate consumers, regenerate them too
   - Prefer clean regeneration over scattered line edits

4. **Human as architect, AI as builder**
   - Human: Write spec, review behavior, make decisions
   - AI: Generate brick, run tests, report results
   - Human rarely reads code unless tests fail

### Benefits

- Each module independently regeneratable
- Parallel development (different bricks simultaneously)
- Multiple variants possible (try different approaches)
- AI-native workflow (specify → generate → test)

## Session Management

The kernel provides session lifecycle management:

```python
from amplifier_core import AmplifierSession

# Create session with mount plan
session = AmplifierSession(
    config=config,
    session_id=None,           # Auto-generated if None
    parent_id=None,            # None for top-level, UUID for child
    approval_system=None,      # App-layer approval policy
    display_system=None,       # App-layer display policy
    is_resumed=False           # True if resuming existing session
)

# Initialize (load modules)
await session.initialize()

# Execute prompt
response = await session.execute(prompt)

# Cleanup
await session.cleanup()
```

**Session states** (tracked in `SessionStatus`):
- `created` - Session initialized but not yet executed
- `running` - Currently executing a prompt
- `completed` - Execution finished successfully
- `failed` - Execution encountered an error
- `cancelled` - User cancelled execution

**Lifecycle events** (emitted by kernel):
- `session:start` - New session begins
- `session:resume` - Session resumed
- `session:fork` - Child session created
- `session:end` - Session cleanup

### Session Forking (Child Sessions)

The kernel supports parent-child relationships:

```python
# Create child session
child_session = AmplifierSession(
    config=child_config,
    session_id="generated-child-id",
    parent_id=parent_session.session_id,  # Links to parent
    approval_system=parent_approval,
    display_system=parent_display
)
```

**W3C Trace Context pattern**:
- Root session ID becomes the `trace_id`
- All child sessions inherit the same `trace_id`
- Child sessions have unique `child_span` identifiers
- Enables distributed tracing across agent hierarchies

**Key features**:
- Kernel emits `session:fork` event with parent_id
- Child sessions inherit UX systems (approval, display)
- Full transcript saved with metadata
- Configuration preserved for resume

## Anti-Patterns (What to Resist)

### In Kernel Development

❌ Adding defaults or config resolution inside kernel
❌ File I/O or search paths in kernel (app layer responsibility)
❌ Provider selection, orchestration strategy, tool routing (policies)
❌ Logging to stdout or private files (use unified JSONL only)
❌ Breaking backward compatibility without migration path

### In Module Development

❌ Depending on kernel internals (use protocols only)
❌ Inventing ad-hoc event names (use canonical taxonomy)
❌ Private log files (write via `context.log` only)
❌ Failing to emit events for observable actions
❌ Crashing kernel on module failure (non-interference)

### In Design

❌ Over-general modules trying to do everything
❌ Copying patterns without understanding rationale
❌ Optimizing the wrong thing (looks over function)
❌ Over-engineering for hypothetical futures
❌ Clever code over clear code

### In Process

❌ "Let's add a flag in kernel for this use case" → Module instead
❌ "We'll break the API now; adoption is small" → Backward compat sacred
❌ "We'll add it to kernel and figure out policy later" → Policy first at edges
❌ "This needs to be in kernel for speed" → Prove with benchmarks first

## Governance & Evolution

### Kernel Changes

**High bar, low velocity**:
- Kernel PRs: tiny diff, invariant review, tests, docs, rollback plan
- Releases are small and boring
- Large ideas prove themselves at edges first

**Acceptance criteria**:
- ✅ Implements mechanism (not policy)
- ✅ Evidence from ≥2 modules needing it
- ✅ Preserves invariants (non-interference, backward compat)
- ✅ Interface small, explicit, text-first
- ✅ Tests and docs included
- ✅ Retires equivalent complexity elsewhere

### Module Changes

**Fast lanes at the edges**:
- Modules iterate rapidly
- Kernel doesn't chase module changes
- Modules adapt to kernel (not vice versa)
- Compete through better policies

## Summary

**Amplifier succeeds by**:
- Keeping kernel tiny, stable, boring
- Pushing innovation to competing modules
- Maintaining strong, text-first contracts
- Enabling observability without opinion
- Trusting emergence over central planning

**The center stays still so the edges can move fast.**

Build mechanisms in kernel. Build policies in modules. Use Linux kernel as your decision metaphor. Keep it simple, keep it observable, keep it regeneratable.

**When in doubt**: Could another team want different behavior? If yes → Module. If no → Maybe kernel, but prove with ≥2 implementations first.

## See Also

- [Architecture Overview](overview.md) - High-level system architecture
- [Module System](modules.md) - Module loading and coordination
- [Design Philosophy](https://github.com/microsoft/amplifier-core/blob/main/docs/DESIGN_PHILOSOPHY.md) - Complete philosophy document
