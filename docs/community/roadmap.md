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

A partial list of areas where we see opportunities for further exploration and development:

### Orchestration Strategies

Amplifier provides several orchestrators (basic, events, streaming) that control execution flow. You could imagine more specialized orchestration strategies tailored to specific workflows, optimization goals, or interaction patterns.

### Collections and Workflows

Collections package agents, context, and philosophy documents for specific use cases. Current collections focus on toolkit building, design intelligence, and recipes. You could imagine collections for other domains, workflows, or ways of organizing reusable knowledge and patterns.

### Metacognitive Recipes

Expanding on structured workflows that mix specific tasks with higher-level philosophy, decision-making rationale, and problem-solving techniques. Making these patterns more accessible and enabling non-developers to leverage them effectively.

### Standard Artifacts and Templates

Evolving conventions for documentation, context files, philosophy documents, and sub-agent definitions. Making it easier for contributors to create artifacts that others can plug into their own Amplifier instances with clear expectations.

### Context and Memory

While Amplifier provides simple and persistent context modules, you could imagine richer approaches to memory, knowledge synthesis, session learning, and team context sharing. Different storage backends, query patterns, or ways of organizing and accessing accumulated knowledge.

### Learning from Sessions

Tools to parse session data, reconstruct conversation logs, and analyze patterns. Unlocking capabilities where shared usage data enables learning from how others approach challenges, and allowing the system to improve from accumulated experience.

---

**Want to contribute?** See [Contributing](contributing.md) for concrete guidance on where and how to plug in.

For detailed technical architecture and design principles, see the [Architecture](../architecture/index.md) section.
