---
title: Roadmap
description: Amplifier direction and current thinking
---

# Roadmap

!!! warning "Guidelines, Not Commitments"
    **This roadmap is more "guidelines" than commitments.** This is subject to change based on new information, priorities, and the occasional perfect storm.

## Project Status

Amplifier is an **experimental platform** focused on discovering what's possible when AI partnership amplifies human capability. We're building a system that makes AI assistants dramatically more effective by providing:

- Domain knowledge and context from your work
- Understanding of your patterns and preferences
- Ability to work on multiple things simultaneously
- Integration with your development workflow

**What this means for the roadmap:**

- All work is treated as candidate to be thrown away and replaced within weeks
- Prioritization is on moving and learning over extensive up-front planning
- The system is evolving rapidly as we discover what amplifies most
- We need to move fast and break things

This approach enables compounding progress — each capability we add makes the system more capable of building the next.

## Focus Areas

### Building Amplifier with Amplifier

Using Amplifier to improve and extend Amplifier. Building new capabilities, improving existing features, and climbing the ladder of metacognitive recipes. Progressively driving more of the buildout vs. building one-off solutions. Shifting from current acceleration to more compounding progress.

Think of Amplifier like a Linux-kernel project — a small, protected core (which you shouldn't need to touch) paired with a diverse and experimental userland. Work focuses on fast iteration, plumbing, and modularity in the layers above the core.

### Discovering and Sharing Emergent Value

Recognizing and amplifying use-cases that emerge from the system. Surfacing and evangelizing emergent uses, especially those extending beyond the code development space. Making onboarding more accessible to others, including improving for non-developers over time.

Producing regular demos of emergent value and use-cases, providing visibility to where the project is at and going. Focus is on leveraging emergent capabilities over seeking to provide desired capabilities that don't yet exist.

## Exploration Directions

A partial list of observed challenges and ways we're thinking about pushing forward in the short term:

### Amplifier Agentic Loop

Today, Amplifier depends on Claude Code for an agentic loop. That enforces directory structures and hooks that complicate how our own patterns and systems fit in. Exploring what it would take to provide our own agentic loop for increased flexibility.

### Multi-Amplifier and "Modes"

Allowing multiple configurations tailored to specific tasks (e.g., creating Amplifier-powered user tools, self-improvement development, general software development). These "modes" could be declared through manifests that specify which sub-agents, commands, hooks, and philosophy documents to load, including external to the repo.

### Metacognitive Recipes

Evolving beyond being only a developer tool. Building support for metacognitive recipes — structured workflows described in natural language that mix specific tasks and procedures with higher-level philosophy, decision-making rationale, and problem-solving techniques. Enabling non-developers to leverage it effectively (e.g., transforming raw idea dumps into blog posts with review loops).

### Standard Artifacts and Templates

Adopting standardized templates for documentation, clear conventions for where context files and philosophy docs live, and definitions of acceptable sub-agents. Making it easy for contributors to provide artifacts that others can plug into their own Amplifier instances.

### Leveraging Sessions for Learning

Including tools to parse session data, reconstruct conversation logs, and analyze patterns. Unlocking capabilities where shared usage data enables queries like "how would [other user] approach [challenge]". Allowing Amplifier to learn from prior work and improve its capabilities.

### Context Sharing

Enabling team members to share context without exposing private data publicly. Options include private Git repositories or shared folders mounted as context for Amplifier. A mount-based approach treats everything as files and avoids custom API connectors, allowing individual user-choice of remote storage or synchronization platforms.

---

**Want to contribute?** See [Contributing](contributing.md) for concrete guidance on where and how to plug in.

For detailed technical architecture and design principles, see the [Architecture](../architecture/index.md) section.
