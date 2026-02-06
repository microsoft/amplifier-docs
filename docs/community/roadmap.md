---
title: Roadmap
description: Amplifier project direction and opportunities
---

# Amplifier Roadmap

!!! note "Living Document"
    This roadmap is more like guidelines than firm commitments. Subject to change based on new information, priorities, and emerging opportunities.

## Vision

Think of Amplifier like a **Linux kernel project**: a small, protected core paired with a diverse and experimental userland. The kernel provides interfaces for core features central to all Amplifier experiences—capabilities, logging, audit/replay, storage, and memory. The userland (modules) is where experimentation and rapid iteration happen.

## Workstreams

### Amplifier Core

**Goal**: Use Amplifier to improve and build Amplifier.

This involves building scaffolding and climbing the ladder of metacognitive recipes, progressively driving more of the buildout through the system itself. We're shifting from current acceleration to compounding progress.

The critical path leads to Amplifier being able to:
- Take lists of ideas and explore them unattended
- Engage human drivers for review and feedback
- Operate at higher levels of automation and capability

Near-term focus: fast iteration, plumbing, and modularity rather than prematurely freezing kernel design.

### Amplifier Usage

**Goal**: Leverage emergent value beyond development.

Surface and evangelize uses that extend outside code development. Make onboarding accessible to non-developers over time.

This workstream produces:
- Regular demos of emergent value and use-cases
- Content providing visibility into project progress
- Vision for adapting capabilities to adjacent scenarios

Focus is on leveraging emergent capabilities over building desired features that don't yet exist.

## Current Opportunities

### Agentic Loop Independence

Today, Amplifier depends on external tools for the agentic loop, which enforces structures and hooks that complicate context and modularity. We're exploring providing our own agentic loop for increased flexibility.

### Multi-Amplifier and Modes

Amplifier should allow multiple configurations tailored to specific tasks:
- Creating Amplifier-powered user tools
- Self-improvement development
- General software development

**Modes** would be declared through manifests specifying:
- Sub-agents to load
- Commands and hooks
- Philosophy documents
- External sources

Having structured ways to switch between modes makes it easier to share experimental tools, reduce conflicts, and quickly reconfigure for different work.

### Metacognitive Recipes

Amplifier should evolve beyond being only a developer tool. Metacognitive recipes are structured workflows in natural language combining:
- Specific tasks and procedures
- Higher-level philosophy and decision-making rationale
- Problem-solving techniques within the recipe's domain
- Code-first approach leveraging AI where appropriate

Examples:
- Transforming raw idea dumps into blog posts with review loops
- Improving Amplifier's debug and recovery techniques
- General, context-managed workflows for non-developers

### Standard Artifacts and Templates

To encourage collaboration, Amplifier should adopt:
- Standardized templates for documentation
- Clear conventions for context files and philosophy docs
- Definitions of acceptable sub-agents
- Shared formats for team projects, ideas, priorities, and learnings

Contributors provide artifacts others can plug into their own Amplifier instances.

### Session Learning

Amplifier should include tools to:
- Parse session data and reconstruct conversation logs
- Analyze patterns across sessions
- Query "how would \<user\> approach \<challenge\>"
- Learn from prior work

This enables metacognitive recipe improvements based on actual usage rather than hoping for compliance with context notes.

### Context Sharing

Team members should share context without exposing private data publicly. Options:
- Private Git repositories
- Shared file folders mounted as context
- Version history and ease of use are key requirements

A mount-based approach treats everything as files and avoids custom API connectors, allowing individual choice of storage platforms.

## Feature Areas

### In Development

| Feature | Status | Description |
|---------|--------|-------------|
| **Streaming** | Active | Real-time token streaming via hooks |
| **Vision** | Active | Image input support across providers |
| **Debug mode** | Active | Enhanced logging and observability |

### Planned

| Feature | Priority | Description |
|---------|----------|-------------|
| **Recipe system** | High | Declarative multi-step workflows |
| **Approval gates** | High | Human-in-loop checkpoints |
| **Session analysis** | Medium | Pattern extraction from sessions |
| **Context mounts** | Medium | External context sources |

### Exploring

| Feature | Notes |
|---------|-------|
| **Custom orchestrators** | Beyond basic loop patterns |
| **Memory systems** | Long-term knowledge retention |
| **Team collaboration** | Shared context and artifacts |
| **Non-developer UX** | Simplified interfaces |

## Philosophy

### Fast Iteration

All work is treated as a candidate to be thrown away and replaced within weeks by something better, more informed by learnings, and being rebuilt faster through Amplifier itself.

### Learning Over Planning

Prioritization is on moving and learning over extensive up-front analysis. This mode is periodically revisited and re-evaluated.

### Compounding Progress

Each improvement should enable faster, more capable subsequent improvements—a virtuous cycle of self-improvement.

## Contributing

See the [Contributing Guide](../contributing/) for how to get involved. Areas where contributions are particularly welcome:

- **Module development**: New tools, providers, hooks
- **Documentation**: Guides, examples, patterns
- **Testing**: Coverage, edge cases, integration tests
- **Use cases**: Share your Amplifier workflows

## References

- **→ [ROADMAP.md](https://github.com/microsoft/amplifier/blob/main/ROADMAP.md)** - Source roadmap document
- **→ [Contributing](../contributing/)** - How to contribute
- **→ [Architecture](../architecture/)** - Technical foundation
