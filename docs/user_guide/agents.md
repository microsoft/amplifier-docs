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
4. Results are returned to your main session
5. The sub-session state is preserved for potential resumption

### Agent Configuration

Agents are bundles (using the same file format as regular bundles) with:

- **Specialized instructions** - Domain expertise and operating procedures
- **Curated tools** - Only the tools needed for their specific tasks
- **Provider preferences** - Optimal model selections for their work
- **Context loading** - Heavy documentation loaded only when the agent runs

## Agent Delegation Patterns

### Context Sink Pattern

Agents serve as **context sinks** - they carry heavy documentation that would bloat your main session if always loaded.

**Benefits:**
- Main session stays lightweight
- Agent consumes tokens doing specialized work
- Results return with minimal context overhead
- Critical strategy for long-running sessions

### Tool Inheritance

Agents inherit tools from your main session, with optional filtering via spawn policies:

```yaml
# In bundle configuration
spawn:
  exclude_tools: [tool-task]  # Agents inherit all tools EXCEPT these
```

This prevents delegation loops (agents delegating to other agents).

## Agent Search Paths

Agents are discovered from multiple locations (first-match-wins):

1. **Environment variables** - `AMPLIFIER_AGENT_<NAME>` for testing
2. **User directory** - `~/.amplifier/agents/` for personal overrides
3. **Project directory** - `.amplifier/agents/` for project-specific agents
4. **Bundle agents** - Agents included in your active bundles

**Example:** Testing an agent modification:

```bash
export AMPLIFIER_AGENT_ZEN_ARCHITECT=~/test-zen.md
amplifier run "design system"  # Uses test version
```

## Common Agent Workflows

### Exploration → Architecture → Implementation

```bash
amplifier
# First, understand the codebase
amplifier> @explorer Survey the authentication system

# Design the changes
amplifier> @zen-architect Design improvements to the auth system

# Implement
amplifier> @modular-builder Implement the auth improvements from the spec
```

### Bug Hunting → Fix → Review

```bash
# Find the issue
amplifier> @bug-hunter Debug the login timeout issue

# Review the fix
amplifier> @security-guardian Review the authentication fix for vulnerabilities

# Commit
amplifier> @git-ops Commit the authentication timeout fix
```

### Research → Design → Build

```bash
# Research approaches
amplifier> @web-research Find best practices for rate limiting

# Design the solution
amplifier> @zen-architect Design a rate limiting system

# Implement
amplifier> @modular-builder Build the rate limiter from the spec
```

## Creating Custom Agents

Agents are bundles - they use the same file format and composition model. To create a custom agent:

1. **Create an agent file** (markdown with YAML frontmatter):

```markdown
---
meta:
  name: my-agent
  description: "Clear description with WHY, WHEN, WHAT, HOW"

tools:
  - module: tool-filesystem
  - module: tool-search
---

# My Agent Instructions

Your agent's system instructions here...
```

2. **Place in search path**:
   - User-wide: `~/.amplifier/agents/my-agent.md`
   - Project-specific: `.amplifier/agents/my-agent.md`

3. **Invoke**: `@my-agent your task`

### Agent Description Requirements

The `meta.description` field is critical - it's how the system matches requests to agents. Include:

- **WHY**: Value proposition (what problem it solves)
- **WHEN**: Activation triggers (when to use this agent)
- **WHAT**: Domain concepts and capabilities
- **HOW**: Examples with context/user/assistant/commentary

**See Also:** [Bundle Guide - Agent Authoring](https://github.com/microsoft/amplifier-foundation/blob/main/docs/AGENT_AUTHORING.md)

## Multi-Turn Agent Conversations

Agents support multi-turn conversations through automatic state persistence:

```bash
amplifier> @explorer Survey the API endpoints
# ... agent completes first task ...

amplifier> @explorer Now check which endpoints handle authentication
# ... agent resumes with previous context ...
```

The system automatically:
- Persists agent sub-session state after each execution
- Restores conversation history on subsequent invocations
- Maintains the same configuration and tools

## Agent Tool Access

### LSP (Language Server Protocol)

Several agents have access to LSP for semantic code intelligence:

- `explorer` - Understands code structure semantically
- `zen-architect` - Analyzes dependencies and contracts
- `python-dev:code-intel` - Python-specific semantic analysis

**LSP provides:**
- `hover` - Type signatures and documentation
- `goToDefinition` - Jump to implementation
- `findReferences` - Find all usages of a symbol
- `incomingCalls` / `outgoingCalls` - Trace call graphs

This enables agents to understand code relationships beyond text search.

## Tips

### When to Delegate

- **Complex tasks** requiring specialized expertise
- **Context-heavy work** that would bloat your main session
- **Multi-step workflows** where each step needs focused attention
- **Domain-specific tasks** where an expert agent exists

### When NOT to Delegate

- **Simple queries** you can answer directly
- **Quick file reads** or edits
- **Tasks requiring main session context** that agents won't have

### Efficient Delegation

```bash
# ✅ Good: Specific task with clear scope
amplifier> @explorer Find all authentication-related files in src/

# ❌ Less effective: Vague request
amplifier> @explorer Look around

# ✅ Good: Clear design objective
amplifier> @zen-architect Design a caching layer for the API

# ❌ Less effective: Open-ended
amplifier> @zen-architect Make things better
```

## Troubleshooting

### Agent Not Found

```bash
# Check available agents
amplifier agents list

# Check search paths (in order):
# 1. $AMPLIFIER_AGENT_<NAME>
# 2. ~/.amplifier/agents/
# 3. .amplifier/agents/
# 4. Bundle agents
```

### Agent Fails to Execute

- Check the agent file syntax (YAML frontmatter + markdown)
- Ensure required tools are available
- Review agent logs in session events

### Wrong Agent Invoked

- Check for name collisions in search paths
- More specific agents in higher-priority paths override bundled agents
- Use `amplifier agents show <name>` to verify which agent will be used

## Advanced: Agent Composition

Since agents ARE bundles, they support full bundle composition:

```yaml
# custom-agent.md
---
meta:
  name: custom-agent
  description: "My specialized agent"

includes:
  - bundle: foundation  # Inherit base capabilities

tools:
  - module: my-custom-tool  # Add specialized tools
---

# Custom Agent

Specialized instructions...
```

This allows building agents that:
- Inherit from other agents
- Compose multiple capability sets
- Override specific configurations
- Share tools and context across agents

**See Also:** [Bundle System Documentation](../developer_guides/foundation/amplifier_foundation/bundle_system.md)
