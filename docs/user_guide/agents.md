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
3. Agent-specific tools and instructions are applied
4. The agent executes your request
5. Results return to your main session

```
Main Session
    │
    ├── @explorer "Analyze codebase"
    │       └── Sub-session with explorer config
    │           └── Returns analysis
    │
    └── Continue main conversation
```

## Agent Descriptions

### `explorer`

**Purpose**: Breadth-first exploration of codebases with citations.

**Capabilities**:

- Scans directory structures
- Reads and summarizes files
- Identifies patterns and architecture
- Provides cited references

**Best for**:

- Understanding new projects
- Finding specific functionality
- Architecture overview

**Example**:
```bash
@explorer How does the authentication flow work?
```

### `bug-hunter`

**Purpose**: Systematic debugging and issue identification.

**Capabilities**:

- Analyzes error messages
- Traces code paths
- Identifies root causes
- Suggests fixes

**Best for**:

- Debugging errors
- Finding edge cases
- Security analysis

**Example**:
```bash
@bug-hunter Why is this test failing?
@bug-hunter Review auth.py for security issues
```

### `zen-architect`

**Purpose**: System design with ruthless simplicity.

**Capabilities**:

- Evaluates design trade-offs
- Proposes minimal solutions
- Questions complexity
- Creates architecture diagrams

**Best for**:

- New feature design
- Refactoring decisions
- Architecture review

**Example**:
```bash
@zen-architect Design a notification system
```

### `web-research`

**Purpose**: Research and information synthesis.

**Capabilities**:

- Web search
- Document analysis
- Information synthesis
- Source citation

**Best for**:

- Gathering information
- Comparing options
- Documentation research

**Example**:
```bash
@web-research What are the best practices for API versioning?
```

### `modular-builder`

**Purpose**: Focused code implementation.

**Capabilities**:

- Writes clean code
- Follows existing patterns
- Creates tests
- Documents code

**Best for**:

- Implementing features
- Writing utilities
- Creating tests

**Example**:
```bash
@modular-builder Create a rate limiter class
```

## Creating Custom Agents

Define agents in your profile or a separate agent file.

### In a Profile

```yaml
---
name: my-profile
extends: dev
agents:
  my-agent:
    description: My specialized agent
    tools:
      - tool-filesystem
      - tool-bash
    system:
      instruction: |
        You are a specialist in database optimization.
        Always explain your reasoning.
---
```

### Standalone Agent File

Create `.amplifier/agents/my-agent.md`:

```yaml
---
name: my-agent
description: Database optimization specialist
tools:
  - tool-filesystem
  - tool-bash
  - tool-search
providers:
  - module: provider-anthropic
    config:
      default_model: claude-opus-4-6
---

# Database Optimization Specialist

You are an expert in database performance optimization.

## Your Approach

1. Analyze the current schema and queries
2. Identify performance bottlenecks
3. Suggest specific improvements
4. Explain trade-offs

## Guidelines

- Always explain your reasoning
- Consider read vs write patterns
- Account for data growth
```

### Agent Schema

```yaml
---
name: agent-name
description: What this agent does

# Optional - specific tools for this agent
tools:
  - tool-filesystem
  - tool-bash

# Optional - specific provider/model
providers:
  - module: provider-anthropic
    config:
      default_model: claude-opus-4-6
      temperature: 0.3

# Optional - override hooks
hooks:
  - module: hooks-logging

# System instruction
system:
  instruction: |
    Detailed instructions for the agent...
---

# Markdown content becomes additional system instructions
```

## Agent Inheritance

Agents inherit from the parent session:

| Setting | Behavior |
|---------|----------|
| Provider | Inherited (can override) |
| Tools | Replaced if specified |
| Hooks | Inherited (can add) |
| Context | Fresh (isolated) |

### Overriding Provider

```yaml
agents:
  deep-thinker:
    providers:
      - module: provider-anthropic
        config:
          default_model: claude-opus-4-6
```

### Limiting Tools

```yaml
agents:
  read-only:
    tools:
      - tool-filesystem  # Only filesystem, no bash
```

## Agent Search Path

Agents are loaded from (in order):

1. Current profile's `agents` section
2. `.amplifier/agents/` (project)
3. `~/.amplifier/agents/` (user)
4. Installed collections
5. Bundled agents

## Multi-Turn Agent Sessions

Agents can maintain context across multiple invocations:

```bash
amplifier> @explorer Analyze the API layer
[Agent analyzes...]

amplifier> @explorer Now focus on the authentication endpoints
[Agent continues with context from previous analysis]
```

## Agent Best Practices

1. **Focused purpose**: Each agent should do one thing well
2. **Clear instructions**: Be specific about behavior and approach
3. **Appropriate tools**: Only include tools the agent needs
4. **Test thoroughly**: Try various prompts to ensure consistent behavior

## Troubleshooting

### Agent Not Found

```bash
# Check agent exists
amplifier agents list

# Check agent locations
ls ~/.amplifier/agents/
ls .amplifier/agents/
```

### Agent Behavior Issues

```bash
# Show agent configuration
amplifier agents show my-agent

# Check profile includes agent
amplifier profile show --resolved
```

## See Also

- [CLI Reference](cli.md) - Agent commands
- **→ [Agent Authoring Guide](https://github.com/microsoft/amplifier-foundation/blob/main/docs/AGENT_AUTHORING.md)** - Complete reference
