---
title: Agents
description: Specialized sub-agents for focused tasks
---

# Agents

Agents are specialized configurations that can be invoked as sub-sessions for focused tasks. Each agent has its own tools, system instructions, and capabilities.

## Built-in Agents

| Agent | Purpose | Best For |
|-------|---------|----------|
| `explorer` | Deep codebase exploration and reconnaissance | Understanding new codebases |
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
| `shell-exec` | Shell command execution | Build, test, package management tasks |
| `post-task-cleanup` | Post-task codebase hygiene | Cleaning up after task completion |

## Using Agents

### In Interactive Mode

Agents are invoked automatically by the AI when you describe a task that matches an agent's expertise. The system uses the `tool-task` module to delegate to the appropriate agent:

```bash
amplifier
amplifier> What is the architecture of this project?
# → AI delegates to explorer agent via task tool

amplifier> Find issues in the authentication module
# → AI delegates to bug-hunter agent via task tool

amplifier> Design a caching system
# → AI delegates to zen-architect agent via task tool
```

### List Available Agents

```bash
amplifier agent list
```

### Show Agent Details

```bash
amplifier agent show explorer
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
- **Model role** - Declared model role preference (e.g., `reasoning`, `general`) resolved via routing matrix
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

### Model Role Override

Agents can declare a preferred model role in their frontmatter:

```yaml
model_role: reasoning  # Single role
# or
model_role: [reasoning, general]  # Multiple roles with fallback
```

The routing matrix resolves the role to a concrete provider/model. The caller can override this per-delegation.

**Precedence** (highest to lowest):
1. `provider_preferences` on the delegation call
2. `model_role` on the delegation call
3. Agent's declared `model_role` in frontmatter
4. No preference — session default (resolved from the `general` role)

If both `model_role` and `provider_preferences` are provided in the same call, `provider_preferences` wins.

**Available roles:**

| Role | Use for |
|------|---------|
| `general` | Versatile catch-all, no specialization needed |
| `fast` | Quick parsing, classification, file ops, bulk work |
| `coding` | Code generation, implementation, debugging |
| `ui-coding` | Frontend/UI code — components, layouts, styling, spatial reasoning |
| `security-audit` | Vulnerability assessment, attack surface analysis, code auditing |
| `reasoning` | Deep architectural reasoning, system design, complex multi-step analysis |
| `critique` | Analytical evaluation — finding flaws in existing work |
| `creative` | Design direction, aesthetic judgment, high-quality creative output |
| `writing` | Long-form content — documentation, marketing, case studies, storytelling |
| `research` | Deep investigation, information synthesis across multiple sources |
| `vision` | Understanding visual input — screenshots, diagrams, UI mockups |
| `image-gen` | Image generation, visual mockup creation, visual ideation |
| `critical-ops` | High-reliability operational tasks — infrastructure, orchestration |

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
amplifier> Survey the authentication system
# → delegates to explorer agent

# Design the changes
amplifier> Design improvements to the auth system
# → delegates to zen-architect agent

# Implement
amplifier> Implement the auth improvements from the spec
# → delegates to modular-builder agent
```

### Bug Hunting → Fix → Review

```bash
# Find the issue
amplifier> Debug the login timeout issue
# → delegates to bug-hunter agent

# Review the fix
amplifier> Review the authentication fix for vulnerabilities
# → delegates to security-guardian agent

# Commit
amplifier> Commit the authentication timeout fix
# → delegates to git-ops agent
```

### Research → Design → Build

```bash
# Research approaches
amplifier> Find best practices for rate limiting
# → delegates to web-research agent

# Design the solution
amplifier> Design a rate limiting system
# → delegates to zen-architect agent

# Implement
amplifier> Build the rate limiter from the spec
# → delegates to modular-builder agent
```

## Creating Custom Agents

Agents are bundles - they use the same file format and composition model. To create a custom agent:

1. **Create an agent file** (markdown with YAML frontmatter):

```markdown
---
meta:
  name: my-agent
  description: "Clear description with WHY, WHEN, WHAT, HOW"

model_role: general  # Optional: semantic role for model selection

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

3. **Invoke**: The AI will automatically delegate to your agent when the task matches its description

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
amplifier> Survey the API endpoints
# → delegates to explorer agent, completes first task

amplifier> Now check which endpoints handle authentication
# → explorer agent resumes with previous context
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
amplifier> Find all authentication-related files in src/

# ❌ Less effective: Vague request
amplifier> Look around

# ✅ Good: Clear design objective
amplifier> Design a caching layer for the API

# ❌ Less effective: Open-ended
amplifier> Make things better
```

## Troubleshooting

### Agent Not Found

```bash
# Check available agents
amplifier agent list

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
- Use `amplifier agent show <name>` to verify which agent will be used

## Advanced: Agent Composition

Since agents ARE bundles, they use the same file format and composition model as regular bundles:

```yaml
# custom-agent.md
---
meta:
  name: custom-agent
  description: "My specialized agent"

model_role: general

tools:
  - module: tool-filesystem
  - module: tool-search
---

# Custom Agent

Specialized instructions...
```

**See Also:** [Bundle System Documentation](../developer_guides/foundation/amplifier_foundation/bundle_system.md)
