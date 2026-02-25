---
title: Agents
description: Specialized sub-agents for focused tasks
---

# Agents

Agents are specialized configurations that can be invoked as sub-sessions for focused tasks. Each agent has its own tools, system instructions, and capabilities.

## Built-in Agents

| Agent | Purpose | Best For |
|-------|---------|----------|
| `explorer` | Breadth-first codebase exploration | Understanding new codebases |
| `bug-hunter` | Systematic debugging | Finding and fixing bugs |
| `zen-architect` | System design with simplicity | Architecture decisions |
| `modular-builder` | Code implementation | Writing new code |
| `web-research` | Research and synthesis | Gathering information |
| `file-ops` | Targeted file operations | Reading, writing, searching files |
| `git-ops` | Git and GitHub operations | Commits, PRs, branch management |
| `session-analyst` | Session analysis and debugging | Investigating session issues |
| `security-guardian` | Security review and auditing | Pre-deployment security checks |
| `test-coverage` | Test coverage analysis | Identifying test gaps |
| `foundation-expert` | Bundle and agent authoring guidance | Creating bundles and agents |
| `ecosystem-expert` | Multi-repo coordination | Cross-repo workflows |
| `integration-specialist` | External service integration | API and MCP server setup |
| `post-task-cleanup` | Post-task codebase hygiene | Cleaning up after task completion |

## Using Agents

### In Interactive Mode

Use the `@` prefix to invoke an agent:

```bash
amplifier
amplifier> @explorer What is the architecture of this project?
amplifier> @bug-hunter Find issues in the authentication module
amplifier> @zen-architect Design a caching system
```

### List Available Agents

```bash
amplifier agents list
```

### Show Agent Details

```bash
amplifier agents show explorer
```

## How Agents Work

When you invoke an agent:

1. A **sub-session** is created with the agent's configuration
2. The agent inherits base settings from your current session
3. The agent executes with its specialized tools and instructions
4. Results return to your main session
5. The sub-session can be resumed for multi-turn conversations

### Multi-Turn Agent Sessions

Agents support multi-turn conversations. When you delegate to an agent, the system saves its state, allowing you to continue the conversation:

```bash
# Turn 1: Initial delegation
amplifier> @zen-architect Design a caching system
# Agent responds with design...

# Turn 2: Resume and refine
amplifier> @zen-architect Add TTL support to the cache
# Agent builds on previous context...

# Turn 3: Continue iteration
amplifier> @zen-architect Add eviction policies
```

The agent maintains context across turns, building on previous exchanges.

## Agent Configuration

Agents are bundles with specialized frontmatter:

```yaml
---
meta:
  name: my-agent
  description: What this agent does and when to use it

tools:
  - module: tool-filesystem
  - module: tool-search
---

# Agent Instructions

Your specialized instructions here...
```

### Creating Custom Agents

Place agent files in:

- `.amplifier/agents/` (project-specific)
- `~/.amplifier/agents/` (personal)

Agents use the same bundle format as bundles. See the [Bundle Guide](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md) for details.

## Environment Variable Overrides

For testing agent changes:

```bash
export AMPLIFIER_AGENT_ZEN_ARCHITECT=~/test-zen.md
amplifier run "design system"  # Uses test version
```

Format: `AMPLIFIER_AGENT_<NAME>` (uppercase, dashes → underscores)

## Agent Resolution

Agents are resolved in priority order:

1. **Environment Variables** - `AMPLIFIER_AGENT_<NAME>`
2. **User Directory** - `~/.amplifier/agents/`
3. **Project Directory** - `.amplifier/agents/`
4. **Bundle Agents** - Agents included in bundles

First match wins.

## Context Management

Agents serve as **context sinks** - they carry heavy documentation that would bloat your main session:

- Delegating to agents frees your session from token consumption
- Sub-sessions burn their context doing the work
- Results return with less context than doing the work in-session
- **Critical strategy for longer-running session success**

## Tool Inheritance

Bundles can control which tools agents inherit using the `spawn` section:

```yaml
# In bundle.md
spawn:
  exclude_tools: [tool-task]  # Agents inherit all tools EXCEPT these
  # OR
  tools: [tool-a, tool-b]     # Agents get ONLY these tools
```

Common pattern: Prevent delegation recursion by excluding `tool-task`.

## Provider Preferences

Control which provider/model an agent uses:

```python
# Via task tool
{
  "agent": "foundation:explorer",
  "instruction": "Quick analysis",
  "provider_preferences": [
    {"provider": "anthropic", "model": "claude-haiku-*"},
    {"provider": "openai", "model": "gpt-4o-mini"}
  ]
}
```

The system tries each preference in order until finding an available provider.

## Session Storage

Agent sub-sessions are stored at:

```
~/.amplifier/projects/<project-slug>/sessions/<session-id>/
├── transcript.jsonl     # Conversation history
├── metadata.json        # Session configuration and metadata
└── events.jsonl         # Complete event log
```

This enables multi-turn conversations and resumption.

## Related Documentation

- **[Bundle Guide](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md)** - How to create agents
- **[Agent Authoring](https://github.com/microsoft/amplifier-foundation/blob/main/docs/AGENT_AUTHORING.md)** - Agent-specific guidance
- **[Agent Delegation Implementation](https://github.com/microsoft/amplifier-app-cli/blob/main/docs/AGENT_DELEGATION_IMPLEMENTATION.md)** - CLI implementation details
