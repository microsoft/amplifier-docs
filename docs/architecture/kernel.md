---
title: Kernel Philosophy
description: Why the Amplifier kernel is tiny, stable, and boring
---

# Kernel Philosophy

The Amplifier kernel (`amplifier-core`) follows a philosophy inspired by the Linux kernel: provide mechanisms, not policy.

## Core Tenets

### 1. Mechanism, Not Policy

The kernel exposes **capabilities** and **stable contracts**. Decisions about behavior belong outside the kernel.

| Kernel Does (Mechanism) | Kernel Doesn't (Policy) |
|------------------------|-------------------------|
| Load modules | Choose which modules |
| Emit events | Decide what to log |
| Validate contracts | Format output |
| Provide hooks | Select providers |
| Manage sessions | Schedule execution |
| Context plumbing | Compaction strategy |

**Litmus test**: If two teams could want different behavior, it's policy → keep it out of the kernel.

### 2. Small, Stable, and Boring

The kernel is intentionally minimal and changes rarely.

- **Small**: Can be audited in an afternoon
- **Stable**: Backward compatibility is sacred
- **Boring**: No clever tricks, no surprises

### 3. Don't Break Modules

Backward compatibility in kernel interfaces is sacred.

- Additive evolution only
- Clear deprecation with migration paths
- Long sunset periods for changes

### 4. Extensibility Through Composition

New behavior comes from plugging in different modules, not from toggling flags.

```python
# Not this (configuration explosion)
session = Session(
    use_streaming=True,
    enable_approval=True,
    log_level="debug",
    ...
)

# This (composition)
mount_plan = {
    "orchestrator": "loop-streaming",
    "hooks": ["hooks-approval", "hooks-logging"]
}
```

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

## What Belongs in the Kernel

### Kernel Responsibilities (Mechanisms)

- **Stable contracts**: Protocol definitions for modules
- **Lifecycle coordination**: Load, unload, mount, unmount
- **Event emission**: Canonical events for observability
- **Capability enforcement**: Permission checks, approvals
- **Minimal context**: Session IDs, basic state
- **Hook system**: Registration and dispatch

### Kernel Non-Goals (Policies)

- Orchestration strategies
- Provider/model selection
- Tool behavior or domain rules
- Output formatting
- Logging destinations
- Business defaults
- Context compaction strategies
- Agent selection

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

## Invariants

These properties must **always** hold:

1. **Backward compatibility**: Existing modules work across kernel updates
2. **Non-interference**: Faulty modules can't crash the kernel
3. **Bounded side-effects**: Kernel doesn't make irreversible external changes
4. **Deterministic semantics**: Same inputs = same behavior
5. **Minimal dependencies**: No transitive dependency sprawl

## Evolution Rules

### 1. Additive First

Extend contracts without breaking them. Prefer optional capabilities.

```python
# Good: Optional new parameter
async def complete(self, request: ChatRequest, **kwargs) -> ChatResponse:
    thinking = kwargs.get("thinking", None)  # New, optional
    ...

# Bad: Required new parameter
async def complete(self, request: ChatRequest, thinking: ThinkingConfig) -> ChatResponse:
    ...  # Breaks existing providers
```

### 2. Two-Implementation Rule

Don't promote a concept into kernel until **≥2 independent modules** converge on the need.

```
Module A needs X  →  Prototype X in Module A
Module B needs X  →  Prototype X in Module B
A and B converge  →  Extract X to kernel
```

### 3. Spec Before Code

Kernel changes begin with a short spec:

- Purpose
- Alternatives considered
- Impact on invariants
- Test strategy
- Rollback plan

### 4. Complexity Budget

Each kernel change must justify its complexity. Additions should retire equivalent complexity elsewhere.

## Interface Guidance

### Small and Sharp

Prefer few, precise operations over broad, do-everything calls.

```python
# Good: Focused operations
coordinator.mount("providers", provider, name="anthropic")
coordinator.unmount("providers", "anthropic")

# Bad: Swiss army knife
coordinator.manage("providers", operation="mount", module=provider, name="anthropic", options={...})
```

### Stable Schemas

Version any data shapes crossing kernel boundaries.

```python
class ChatRequest(BaseModel):
    """Unified request format."""
    messages: list[Message]
    tools: list[ToolSpec] | None = None
    # New fields are optional with defaults
    temperature: float | None = None  # Added later, optional
```

### Explicit Errors

Fail closed with actionable diagnostics. No silent fallbacks.

```python
# Good: Clear error
raise ModuleNotFoundError(
    f"Module '{module_id}' not found. "
    f"Available modules: {available}. "
    f"Check your mount plan configuration."
)

# Bad: Silent fallback
if module not found:
    use_default_module()  # Hidden behavior
```

## Security Posture

### Deny by Default

Kernel offers no ambient authority. Modules must request capabilities explicitly.

```python
# Module must explicitly request
coordinator.register_capability("file_system", implementation)

# And explicitly use
fs = coordinator.get_capability("file_system")
```

### Sandbox Boundaries

All calls across boundaries are validated, attributed, and observable.

```python
# Every tool call is observable
await coordinator.hooks.emit("tool:pre", {
    "tool_name": tool.name,
    "input": sanitized_input,
    "session_id": session_id
})
```

### Non-Interference

Module failures are isolated. The kernel stays up.

```python
try:
    result = await tool.execute(input)
except Exception as e:
    # Log error, don't crash kernel
    await coordinator.hooks.emit("tool:error", {"error": str(e)})
    return ToolResult(success=False, error=str(e))
```

## Context Window Awareness

The kernel provides mechanisms for context management without dictating policy:

- **Token budgets**: Context managers receive provider info to calculate budgets
- **Dynamic limits**: `context_window - max_output_tokens - safety_margin`
- **Graceful compaction**: Non-destructive compaction preserves full history

```python
# Context manager calculates budget from provider
async def get_messages_for_request(self, provider=None):
    if provider:
        info = provider.get_info()
        budget = info.defaults.get("context_window") - info.defaults.get("max_output_tokens") - 1000
    return self._compact_to_budget(budget)
```

## Module Design: Bricks & Studs

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

## Red Flags

Watch for these anti-patterns:

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| "Add a flag for this use case" | Flags accumulate; use modules |
| "Pass whole context for flexibility" | Violates minimal capability |
| "Break API now, adoption is small" | Sets bad precedent |
| "Add to kernel now, figure out policy later" | Policy will leak in |
| "It's only one more dependency" | Dependencies compound |
| "We need this for debugging" | Use hooks, not kernel changes |
| "This is simpler than using hooks" | Directness in modules, not kernel |

## Decision Framework

When evaluating kernel changes, ask:

1. **Necessity**: "Do we actually need this right now?"
2. **Simplicity**: "What's the simplest way to solve this?"
3. **Directness**: "Can we solve this more directly?"
4. **Value**: "Does the complexity add proportional value?"
5. **Maintenance**: "How easy will this be to understand later?"

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

## Quick Reference

### For Kernel Work

**Questions before adding to kernel**:
1. Is this a mechanism many policies could use?
2. Do ≥2 modules need this?
3. Does it preserve backward compatibility?
4. Is the interface minimal and stable?

**If any "no"** → Prototype as module first

### For Module Work

**Module author checklist**:
- [ ] Implements protocol only (no kernel internals)
- [ ] Emits canonical events where appropriate
- [ ] Uses `context.log` (no private logging)
- [ ] Handles own failures (non-interference)
- [ ] Tests include isolation verification

### For Design Decisions

**Use the Linux kernel lens**:
- Scheduling strategy? → Orchestrator module (userspace)
- Provider selection? → App layer policy
- Tool behavior? → Tool module
- Security policy? → Hook module
- Logging destination? → Hook module

**Remember**: If two teams might want different behavior → Module, not kernel.

## North Star

- **Unshakeable center**: A kernel so small and stable it can be maintained by one person
- **Explosive edges**: A flourishing ecosystem of competing modules
- **Forever upgradeable**: Ship improvements weekly at edges, kernel updates are rare and boring

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

## References

- **[DESIGN_PHILOSOPHY.md](https://github.com/microsoft/amplifier-core/blob/main/docs/DESIGN_PHILOSOPHY.md)** - Complete design philosophy document
- **[Module Contracts](https://github.com/microsoft/amplifier-core/tree/main/docs/contracts)** - Detailed contract specifications
- **[MOUNT_PLAN_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/docs/specs/MOUNT_PLAN_SPECIFICATION.md)** - Configuration contract
