---
title: Ecosystem
description: All available components in the Amplifier ecosystem — core, apps, libraries, bundles, and runtime modules
---

# Amplifier Ecosystem

Amplifier's modular architecture allows you to mix and match capabilities. This page catalogs all available components — core infrastructure, applications, libraries, bundles, and runtime modules.

## Core Infrastructure

The foundational kernel that everything builds on.

| Component | Description | Repository |
|-----------|-------------|------------|
| **amplifier-core** | Ultra-thin kernel for modular AI agent system | [amplifier-core](https://github.com/microsoft/amplifier-core) |

## Applications

User-facing applications that compose libraries and modules.

| Component | Description | Repository |
|-----------|-------------|------------|
| **amplifier** | Main Amplifier project and entry point — installs amplifier-app-cli via `uv tool install` | [amplifier](https://github.com/microsoft/amplifier) |
| **amplifier-app-cli** | Reference CLI application implementing the Amplifier platform | [amplifier-app-cli](https://github.com/microsoft/amplifier-app-cli) |
| **amplifier-app-log-viewer** | Web-based log viewer for debugging sessions with real-time updates | [amplifier-app-log-viewer](https://github.com/microsoft/amplifier-app-log-viewer) |
| **amplifier-app-benchmarks** | Benchmarking and evaluating Amplifier | [amplifier-app-benchmarks](https://github.com/DavidKoleczek/amplifier-app-benchmarks) |
| **amplifierd** | Localhost HTTP daemon exposing amplifier-core and amplifier-foundation over REST and SSE — drive sessions from any language or framework | [amplifierd](https://github.com/microsoft/amplifierd) |
| **amplifier-chat** | Chat UI plugin for amplifierd — browser-based conversational interface for creating and managing Amplifier sessions | [amplifier-chat](https://github.com/microsoft/amplifier-chat) |
| **amplifier-voice** | Voice plugin for amplifierd — WebRTC voice interface using the OpenAI Realtime API, standalone or as a plugin | [amplifier-voice](https://github.com/microsoft/amplifier-voice) |

**Note**: When you install `amplifier`, you get amplifier-app-cli as the executable application. `amplifierd` is a separate daemon that exposes Amplifier capabilities over HTTP, and `amplifier-chat` and `amplifier-voice` are plugins that extend it with web-based chat and voice interfaces.

## Libraries

Foundational libraries used by **applications** (not used directly by runtime modules).

| Component | Description | Repository |
|-----------|-------------|------------|
| **amplifier-foundation** | Foundational library for bundles, module resolution, and shared utilities | [amplifier-foundation](https://github.com/microsoft/amplifier-foundation) |

**Architectural Boundary**: Libraries are consumed by applications (like amplifier-app-cli). Runtime modules only depend on amplifier-core and never use these libraries directly.

## Bundles

Composable configuration packages that combine providers, behaviors, agents, and context into reusable units.

| Bundle | Description | Repository |
|--------|-------------|------------|
| **amplifier-tester** | Validates Amplifier ecosystem changes in isolated Digital Twin Universe environments — dynamically generates profiles, mirrors repos to Gitea, and runs targeted validation checks | [amplifier-bundle-amplifier-tester](https://github.com/microsoft/amplifier-bundle-amplifier-tester) |
| **recipes** | Multi-step AI agent orchestration with behavior overlays and standalone options | [amplifier-bundle-recipes](https://github.com/microsoft/amplifier-bundle-recipes) |
| **browser-tester** | Browser automation and testing with 3 specialized agents (operator, researcher, visual documenter) | [amplifier-bundle-browser-tester](https://github.com/microsoft/amplifier-bundle-browser-tester) |
| **context-managed** | LLM-powered rolling context summarization with persistent transcript and on-demand history recovery | [amplifier-bundle-context-managed](https://github.com/microsoft/amplifier-bundle-context-managed) |
| **design-intelligence** | Comprehensive design intelligence with 7 specialized agents, design philosophy framework, and knowledge base | [amplifier-bundle-design-intelligence](https://github.com/microsoft/amplifier-bundle-design-intelligence) |
| **digital-twin-universe** | On-demand isolated environments from declarative profiles — Incus containers with URL rewriting, PyPI overrides, and LLM API passthrough | [amplifier-bundle-digital-twin-universe](https://github.com/microsoft/amplifier-bundle-digital-twin-universe) |
| **dot-graph** | DOT/Graphviz infrastructure — knowledge, validation, rendering, and graph intelligence | [amplifier-bundle-dot-graph](https://github.com/microsoft/amplifier-bundle-dot-graph) |
| **evaluation** | One-stop-shop for evaluating AI agents, bundles, and recipes — evaluation mode and Python harness for pre-defined tasks | [amplifier-bundle-evaluation](https://github.com/microsoft/amplifier-bundle-evaluation) |
| **execution-environments** | Instance-based execution environments — create, target, and destroy local, Docker, and SSH environments on demand | [amplifier-bundle-execution-environments](https://github.com/microsoft/amplifier-bundle-execution-environments) |
| **foreman** | Assistant pattern where the conversation assistant manages a fleet of other assistants with their own sessions | [amplifier-bundle-foreman](https://github.com/payneio/amplifier-bundle-foreman) |
| **gitea** | On-demand ephemeral Gitea instances for isolated git workflows — mirror repos from GitHub, work freely, promote results back | [amplifier-bundle-gitea](https://github.com/microsoft/amplifier-bundle-gitea) |
| **issues** | Persistent issue tracking with dependency management, priority scheduling, and session linking | [amplifier-bundle-issues](https://github.com/microsoft/amplifier-bundle-issues) |
| **llm-wiki** | Karpathy LLM Wiki pattern as composable workflow modes — wiki-init, wiki-ingest, wiki-lint, wiki-publish, wiki-query | [amplifier-bundle-llm-wiki](https://github.com/microsoft/amplifier-bundle-llm-wiki) |
| **lsp** | Core Language Server Protocol support for code intelligence operations | [amplifier-bundle-lsp](https://github.com/microsoft/amplifier-bundle-lsp) |
| **notify** | Desktop and push notifications when assistant turns complete — works over SSH, supports ntfy.sh for mobile | [amplifier-bundle-notify](https://github.com/microsoft/amplifier-bundle-notify) |
| **observers** | Background observer sessions that run in parallel to provide the main session with actionable observations | [amplifier-bundle-observers](https://github.com/microsoft/amplifier-bundle-observers) |
| **orchestration** | Event-driven orchestration primitives (bundle spawning, events, triggers) for multi-session coordination | [amplifier-bundle-orchestration](https://github.com/microsoft/amplifier-bundle-orchestration) |
| **python-dev** | Comprehensive Python development tools — code quality (ruff, pyright), LSP integration, and expert agent | [amplifier-bundle-python-dev](https://github.com/microsoft/amplifier-bundle-python-dev) |
| **reality-check** | Intent-driven verification of built software — derives acceptance tests from user conversations, deploys in Digital Twin Universe | [amplifier-bundle-reality-check](https://github.com/microsoft/amplifier-bundle-reality-check) |
| **routing-matrix** | Declarative model routing with 13 semantic roles, 7 curated matrices, and CLI tooling | [amplifier-bundle-routing-matrix](https://github.com/microsoft/amplifier-bundle-routing-matrix) |
| **rust-dev** | Comprehensive Rust development tools — code quality (cargo fmt, clippy), LSP integration, and expert agent | [amplifier-bundle-rust-dev](https://github.com/microsoft/amplifier-bundle-rust-dev) |
| **shadow** | OS-level sandboxed environments for testing local Amplifier ecosystem changes safely | [amplifier-bundle-shadow](https://github.com/microsoft/amplifier-bundle-shadow) |
| **skills** | Skills tool and Microsoft-curated skills collection | [amplifier-bundle-skills](https://github.com/microsoft/amplifier-bundle-skills) |
| **stories** | Autonomous storytelling engine with 11 specialist agents and 4 output formats | [amplifier-bundle-stories](https://github.com/microsoft/amplifier-bundle-stories) |
| **superpowers** | TDD-driven development workflows with brainstorm, plan, execute, verify, and finish modes | [amplifier-bundle-superpowers](https://github.com/microsoft/amplifier-bundle-superpowers) |
| **terminal-tester** | Terminal application testing with 3 specialist agents using dual-mode capture | [amplifier-bundle-terminal-tester](https://github.com/microsoft/amplifier-bundle-terminal-tester) |
| **ts-dev** | Comprehensive TypeScript/JavaScript development tools — code quality, LSP, and expert agent | [amplifier-bundle-ts-dev](https://github.com/microsoft/amplifier-bundle-ts-dev) |

**Usage**:

```bash
# Add a bundle to the registry
amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-recipes@main

# Use a bundle by name
amplifier bundle use recipes

# Check for updates
amplifier bundle update --check

# Update to latest
amplifier bundle update
```

## Runtime Modules

Modules are loaded dynamically at runtime based on bundle configuration.

### Orchestrators

Control the AI agent execution loop.

| Module | Description | Repository |
|--------|-------------|------------|
| **loop-basic** | Standard sequential execution — simple request/response flow | [amplifier-module-loop-basic](https://github.com/microsoft/amplifier-module-loop-basic) |
| **loop-streaming** | Real-time streaming responses with extended thinking support | [amplifier-module-loop-streaming](https://github.com/microsoft/amplifier-module-loop-streaming) |
| **loop-events** | Event-driven orchestrator with hook integration | [amplifier-module-loop-events](https://github.com/microsoft/amplifier-module-loop-events) |

### Providers

Connect to AI model providers.

| Module | Description | Repository |
|--------|-------------|------------|
| **provider-anthropic** | Anthropic Claude integration (Sonnet 4.5, Opus, etc.) | [amplifier-module-provider-anthropic](https://github.com/microsoft/amplifier-module-provider-anthropic) |
| **provider-openai** | OpenAI GPT integration via the Responses API | [amplifier-module-provider-openai](https://github.com/microsoft/amplifier-module-provider-openai) |
| **provider-openai-chatgpt** | ChatGPT subscription backend (Plus/Pro/Team/Enterprise) via Codex CLI OAuth | [amplifier-module-provider-openai-chatgpt](https://github.com/microsoft/amplifier-module-provider-openai-chatgpt) |
| **provider-azure-openai** | Azure OpenAI with managed identity support | [amplifier-module-provider-azure-openai](https://github.com/microsoft/amplifier-module-provider-azure-openai) |
| **provider-chat-completions** | OpenAI Chat Completions wire-format integration (llama.cpp, vLLM, LM Studio, LocalAI, etc.) | [amplifier-module-provider-chat-completions](https://github.com/microsoft/amplifier-module-provider-chat-completions) |
| **provider-gemini** | Google Gemini integration with 1M context and thinking | [amplifier-module-provider-gemini](https://github.com/microsoft/amplifier-module-provider-gemini) |
| **provider-vllm** | vLLM server integration for self-hosted models | [amplifier-module-provider-vllm](https://github.com/microsoft/amplifier-module-provider-vllm) |
| **provider-ollama** | Local Ollama models for offline development | [amplifier-module-provider-ollama](https://github.com/microsoft/amplifier-module-provider-ollama) |
| **provider-github-copilot** | GitHub Copilot models via the Copilot SDK | [amplifier-module-provider-github-copilot](https://github.com/microsoft/amplifier-module-provider-github-copilot) |
| **provider-mock** | Mock provider for testing without API calls | [amplifier-module-provider-mock](https://github.com/microsoft/amplifier-module-provider-mock) |

### Tools

Extend AI capabilities with actions.

| Module | Description | Repository |
|--------|-------------|------------|
| **tool-filesystem** | File operations (read, write, edit, list, glob) | [amplifier-module-tool-filesystem](https://github.com/microsoft/amplifier-module-tool-filesystem) |
| **tool-bash** | Shell command execution | [amplifier-module-tool-bash](https://github.com/microsoft/amplifier-module-tool-bash) |
| **tool-web** | Web search and content fetching | [amplifier-module-tool-web](https://github.com/microsoft/amplifier-module-tool-web) |
| **tool-search** | Code search capabilities (grep/glob) | [amplifier-module-tool-search](https://github.com/microsoft/amplifier-module-tool-search) |
| **tool-task** | Agent delegation and sub-session spawning | [amplifier-module-tool-task](https://github.com/microsoft/amplifier-module-tool-task) |
| **tool-todo** | AI self-accountability and todo list management | [amplifier-module-tool-todo](https://github.com/microsoft/amplifier-module-tool-todo) |
| **tool-skills** | Load domain knowledge from skills following the Anthropic Skills format | [amplifier-module-tool-skills](https://github.com/microsoft/amplifier-module-tool-skills) |
| **tool-mcp** | Model Context Protocol integration for MCP servers | [amplifier-module-tool-mcp](https://github.com/microsoft/amplifier-module-tool-mcp) |
| **tool-slash-command** | Extensible slash command system with custom commands defined as Markdown files | [amplifier-module-tool-slash-command](https://github.com/microsoft/amplifier-module-tool-slash-command) |

### Context Managers

Manage conversation state and history.

| Module | Description | Repository |
|--------|-------------|------------|
| **context-simple** | In-memory context with automatic compaction | [amplifier-module-context-simple](https://github.com/microsoft/amplifier-module-context-simple) |
| **context-persistent** | File-backed persistent context across sessions | [amplifier-module-context-persistent](https://github.com/microsoft/amplifier-module-context-persistent) |

### Hooks

Extend lifecycle events and observability.

| Module | Description | Repository |
|--------|-------------|------------|
| **hooks-logging** | Unified JSONL event logging to per-session files | [amplifier-module-hooks-logging](https://github.com/microsoft/amplifier-module-hooks-logging) |
| **hooks-redaction** | Privacy-preserving data redaction for secrets/PII | [amplifier-module-hooks-redaction](https://github.com/microsoft/amplifier-module-hooks-redaction) |
| **hooks-approval** | Interactive approval gates for sensitive operations | [amplifier-module-hooks-approval](https://github.com/microsoft/amplifier-module-hooks-approval) |
| **hooks-backup** | Automatic session transcript backup | [amplifier-module-hooks-backup](https://github.com/microsoft/amplifier-module-hooks-backup) |
| **hooks-explanatory** | Inject explanatory output style with educational Insight blocks | [amplifier-module-hooks-explanatory](https://github.com/michaeljabbour/amplifier-module-hooks-explanatory) |
| **hooks-streaming-ui** | Real-time console UI for streaming responses | [amplifier-module-hooks-streaming-ui](https://github.com/microsoft/amplifier-module-hooks-streaming-ui) |
| **hooks-status-context** | Inject git status and datetime into agent context | [amplifier-module-hooks-status-context](https://github.com/microsoft/amplifier-module-hooks-status-context) |
| **hooks-todo-reminder** | Inject todo list reminders into AI context | [amplifier-module-hooks-todo-reminder](https://github.com/microsoft/amplifier-module-hooks-todo-reminder) |
| **hooks-scheduler-cost-aware** | Cost-aware model routing for event-driven orchestration | [amplifier-module-hooks-scheduler-cost-aware](https://github.com/microsoft/amplifier-module-hooks-scheduler-cost-aware) |
| **hooks-scheduler-heuristic** | Heuristic-based model selection scheduler | [amplifier-module-hooks-scheduler-heuristic](https://github.com/microsoft/amplifier-module-hooks-scheduler-heuristic) |
| **hook-shell** | Shell-based hooks with Claude Code format compatibility | [amplifier-module-hook-shell](https://github.com/microsoft/amplifier-module-hook-shell) |

## Using Modules

### In Bundles

```yaml
tools:
  - module: tool-web
    source: git+https://github.com/microsoft/amplifier-module-tool-web@main
```

### Command Line

```bash
amplifier module add tool-web --source git+https://github.com/microsoft/amplifier-module-tool-web@main
amplifier module list
amplifier module show tool-filesystem
```

## Module Contracts

All runtime modules follow the same pattern and implement one of five contract types:

| Module Type | Contract | Purpose |
|-------------|----------|---------|
| **Provider** | [PROVIDER_CONTRACT.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/PROVIDER_CONTRACT.md) | LLM backend integration |
| **Tool** | [TOOL_CONTRACT.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/TOOL_CONTRACT.md) | Agent capabilities |
| **Hook** | [HOOK_CONTRACT.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/HOOK_CONTRACT.md) | Lifecycle observation and control |
| **Orchestrator** | [ORCHESTRATOR_CONTRACT.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/ORCHESTRATOR_CONTRACT.md) | Agent loop execution strategy |
| **Context** | [CONTEXT_CONTRACT.md](https://github.com/microsoft/amplifier-core/blob/main/docs/contracts/CONTEXT_CONTRACT.md) | Conversation memory management |

### Quick Start Pattern

```python
# 1. Implement the Protocol from interfaces.py
class MyModule:
    pass  # implement required methods

# 2. Provide mount() function
async def mount(coordinator, config):
    instance = MyModule(config)
    await coordinator.mount("category", instance, name="my-module")
    return instance

# 3. Register entry point in pyproject.toml
# [project.entry-points."amplifier.modules"]
# my-module = "my_package:mount"
```

## Community Modules

### Providers

| Module | Description | Author | Repository |
|--------|-------------|--------|------------|
| **provider-bedrock** | AWS Bedrock integration with cross-region inference support | [@brycecutt-msft](https://github.com/brycecutt-msft) | [amplifier-module-provider-bedrock](https://github.com/brycecutt-msft/amplifier-module-provider-bedrock) |
| **provider-perplexity** | Perplexity AI integration for chat completions | [@colombod](https://github.com/colombod) | [amplifier-module-provider-perplexity](https://github.com/colombod/amplifier-module-provider-perplexity) |
| **provider-openai-realtime** | OpenAI Realtime API for native speech-to-speech | [@robotdad](https://github.com/robotdad) | [amplifier-module-provider-openai-realtime](https://github.com/robotdad/amplifier-module-provider-openai-realtime) |

### Tools

| Module | Description | Author | Repository |
|--------|-------------|--------|------------|
| **tool-youtube-dl** | Download audio and video from YouTube | [@robotdad](https://github.com/robotdad) | [amplifier-module-tool-youtube-dl](https://github.com/robotdad/amplifier-module-tool-youtube-dl) |
| **tool-whisper** | Speech-to-text transcription using Whisper | [@robotdad](https://github.com/robotdad) | [amplifier-module-tool-whisper](https://github.com/robotdad/amplifier-module-tool-whisper) |
| **tool-rlm** | Recursive Language Model for 10M+ token contexts | [@michaeljabbour](https://github.com/michaeljabbour) | [amplifier-module-tool-rlm](https://github.com/michaeljabbour/amplifier-module-tool-rlm) |

### Hooks

| Module | Description | Author | Repository |
|--------|-------------|--------|------------|
| **hooks-concise-display** | Cleaner, condensed terminal output | [@obra](https://github.com/obra) | [amplifier-module-hooks-concise-display](https://github.com/obra/amplifier-module-hooks-concise-display) |
| **hooks-compact** | Compress verbose bash stdout via command-aware filters | [@samueljklee](https://github.com/samueljklee) | [amplifier-module-hooks-compact](https://github.com/samueljklee/amplifier-module-hooks-compact) |

> **Security Warning**: Community modules execute arbitrary code in your environment. Only use modules from sources you trust.
