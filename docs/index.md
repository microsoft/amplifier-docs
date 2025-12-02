---
title: Amplifier - Modular AI Agent Framework
description: Amplify human capability through AI partnership
---

# Amplifier

<div class="hero">
<p style="font-size: 1.4rem; opacity: 0.9;">
Amplify human capability through AI partnership
</p>
</div>

**Amplifier** is an experimental platform that multiplies what you can explore and build by making AI assistants dramatically more effective through domain knowledge, context, and modular capabilities.

## Quick Start

```bash
# Install
uv tool install git+https://github.com/microsoft/amplifier@next

# Configure
amplifier init

# Run
amplifier
```

!!! tip "Stay Updated"
    Amplifier is in active development. Run `amplifier update` daily to get the latest features and fixes.

[Get Started →](getting_started/index.md){ .md-button .md-button--primary }
[View on GitHub →](https://github.com/microsoft/amplifier/tree/next){ .md-button }

---

## The Challenge

**"I have more ideas than time to try them out."**

Modern AI tools are powerful, but they start from zero every time. They lack your domain knowledge, patterns, context from previous work, and ability to explore multiple approaches simultaneously.

## How Amplifier Helps

Amplifier creates a supercharged environment where AI assistants become dramatically more effective:

<div class="grid">

<div class="card">
<h3>Knowledge & Context</h3>
<p>Provides AI with your domain knowledge, patterns, and previous work. Every interaction builds on what came before.</p>
</div>

<div class="card">
<h3>Parallel Exploration</h3>
<p>Test multiple approaches simultaneously. Where you might explore 1-2 solutions, Amplifier enables exploring 20 in parallel.</p>
</div>

<div class="card">
<h3>Modular Capabilities</h3>
<p>Swap providers, tools, and execution strategies. Build custom workflows that fit your needs.</p>
</div>

<div class="card">
<h3>Compounding Progress</h3>
<p>Each capability you add makes the system more capable of building the next. Fast iteration, learning, and evolution.</p>
</div>

</div>

## The Platform

Modular architecture inspired by the Linux kernel model:

<div class="grid">

<div class="card">
<h3>Modular by Design</h3>
<p>Swap providers (Anthropic, OpenAI, Azure, Ollama), tools, and orchestration strategies without changing your code.</p>
</div>

<div class="card">
<h3>Kernel Philosophy</h3>
<p>Tiny, stable core (~2,600 lines) that rarely changes. All features live at the edges as replaceable modules.</p>
</div>

<div class="card">
<h3>Agent Delegation</h3>
<p>Spawn specialized sub-agents for focused tasks. Each agent has its own tools, context, and capabilities.</p>
</div>

<div class="card">
<h3>Profile System</h3>
<p>Pre-configured capability sets from minimal to full-featured. Create your own profiles for repeatable workflows.</p>
</div>

</div>

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  amplifier-core (KERNEL) - ~2,600 lines                     │
│  • Ultra-thin, stable, boring                               │
│  • Mechanisms ONLY (loading, coordinating, events)          │
│  • NEVER decides policy                                     │
└─────────────────────────────────────────────────────────────┘
                             ▲
                             │ stable contracts
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  MODULES (Userspace - Swappable)                            │
│  • Providers: LLM backends (Anthropic, OpenAI, Azure, etc.) │
│  • Tools: Capabilities (filesystem, bash, web, search)      │
│  • Orchestrators: Execution loops (basic, streaming, events)│
│  • Contexts: Memory management (simple, persistent)         │
│  • Hooks: Observability (logging, approval, redaction)      │
└─────────────────────────────────────────────────────────────┘
```

The center stays still so the edges can move fast.

[Learn More →](architecture/overview.md)

## Ecosystem

Amplifier provides a rich ecosystem of swappable modules and libraries.

| Type | Examples | Purpose |
|------|----------|---------|
| **Providers** | Anthropic, OpenAI, Azure, Ollama | LLM backend integrations |
| **Tools** | Filesystem, Bash, Web, Search | Agent capabilities |
| **Orchestrators** | Basic, Streaming, Events | Execution loop strategies |
| **Contexts** | Simple, Persistent | Conversation memory |
| **Hooks** | Logging, Approval, Redaction | Observability & control |
| **Libraries** | Profiles, Collections, Config | App-layer functionality |

[Browse Ecosystem →](ecosystem/index.md){ .md-button } [Community Showcase →](showcase/index.md){ .md-button }

## Target Outcomes

We're discovering what's possible when AI partnership amplifies human capability:

- **Ideas that take weeks → hours** - Rapid exploration of possibilities
- **Test 10x more approaches** - Parallel experimentation at scale
- **Knowledge compounds** - Every project accelerates the next
- **Time from idea to prototype → near zero** - Fast iteration and learning

This is an experimental journey. We're building Amplifier with Amplifier, progressively discovering what amplification makes possible.

## Who Is This For?

<div class="grid">

<div class="card">
<h3>Explorers</h3>
<p>Fork and build your own amplification systems. Share discoveries and push boundaries of what's possible.</p>
</div>

<div class="card">
<h3>Teams</h3>
<p>Share profiles and collections across your organization. Consistent AI workflows for everyone.</p>
</div>

<div class="card">
<h3>Developers</h3>
<p>Build AI-powered development workflows. Code review, refactoring, debugging, and documentation assistance.</p>
</div>

<div class="card">
<h3>Module Authors</h3>
<p>Create custom providers, tools, or hooks. Stable contracts make modules independently developable.</p>
</div>

</div>

## Next Steps

- **[Installation](getting_started/installation.md)** - Get Amplifier running
- **[Getting Started](getting_started/index.md)** - Your first AI session
- **[CLI Reference](user_guide/cli.md)** - All available commands
- **[Architecture](architecture/overview.md)** - How it all fits together
- **[Module Development](developer/module_development.md)** - Build your own modules

## Community

- [GitHub Repository](https://github.com/microsoft/amplifier/tree/next)
- [Issue Tracker](https://github.com/microsoft/amplifier/issues)
- [Contributing Guide](community/contributing.md)

---

<div style="text-align: center; opacity: 0.7; margin-top: 2rem;">
<p>Amplifier is a Microsoft open source project.</p>
</div>
