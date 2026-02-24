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
3. The agent's specialized tools and instructions are loaded
4. Your request is processed in the sub-session
5. Results are returned to your main session
6. Sub-session state is persisted for potential resumption

### LSP-Enhanced Capabilities

Many agents have access to **Language Server Protocol (LSP)** for semantic code intelligence:

| Capability | Use Case |
|------------|----------|
| `findReferences` | Find all usages of a symbol |
| `goToDefinition` | Jump to exact definition |
| `hover` | Get type signatures and documentation |
| `incomingCalls`/`outgoingCalls` | Trace call graphs |

Agents like `explorer`, `zen-architect`, and code-navigation specialists use LSP to understand code relationships beyond text search.

## Multi-Turn Conversations

Agents support multi-turn conversations through automatic state persistence. You can continue a conversation with an agent across multiple turns:

### Initial Delegation

```bash
amplifier> @zen-architect Design a caching system
```

The agent responds with a design and returns a session ID.

### Resume Conversation

To continue the conversation with the same agent:

```bash
amplifier> @zen-architect Add TTL support to the cache
```

The system automatically resumes the previous sub-session, maintaining full conversation history.

### How It Works

1. **State Persistence**: After each agent execution, state (transcript and configuration) is saved to `~/.amplifier/projects/{project}/sessions/`
2. **Automatic Resume**: When you invoke the same agent again, the system detects the previous session and resumes it
3. **Full Context**: The agent has access to the entire conversation history
4. **Cross-Session**: Sessions survive parent session restarts and crashes

### Session Storage

Sub-session data is stored at:
- `transcript.jsonl` - Conversation history
- `metadata.json` - Session configuration and metadata
- `bundle.md` - Bundle snapshot (if applicable)

## Agent Resolution

Agents are discovered from multiple locations (first-match-wins):

1. **Environment Variables** - `AMPLIFIER_AGENT_<NAME>` for testing
2. **User Directory** - `~/.amplifier/agents/` for personal overrides
3. **Project Directory** - `.amplifier/agents/` for project-specific agents
4. **Bundle Agents** - Agents included with installed bundles

### Testing Agent Changes

Use environment variables to test agent modifications:

```bash
# Test modified agent without committing
export AMPLIFIER_AGENT_ZEN_ARCHITECT=~/work/test-zen.md
amplifier run "design system"  # Uses test version

# Unset to use normal resolution
unset AMPLIFIER_AGENT_ZEN_ARCHITECT
```

## Agent Capabilities

### Explorer

Deep local-context reconnaissance for codebase understanding.

**Activation Triggers:**
- Broad discovery across code, docs, or content
- Understanding codebase structure
- Orientation before implementation or debugging

**Capabilities:**
- Breadth-first exploration
- LSP semantic analysis
- Pattern discovery with grep
- Structured reporting with file references

**Example:**

```bash
amplifier> @explorer What is the event handling flow?
```

### Zen Architect

System design agent embodying ruthless simplicity and Wabi-sabi philosophy.

**Operating Modes:**
- **ANALYZE**: Break down problems, design solutions, create specifications
- **ARCHITECT**: System design with module specifications
- **REVIEW**: Code quality assessment and recommendations

**Capabilities:**
- LSP-enhanced architecture analysis
- Module specification creation
- Philosophy compliance review
- Design decision framework

**Example:**

```bash
amplifier> @zen-architect Design a caching system
amplifier> @zen-architect Review this module for complexity
```

### Foundation Expert

Authoritative expert for Amplifier Foundation applications and agent authoring.

**Expertise:**
- Bundle composition and the thin bundle pattern
- Behavior creation and reusability
- Agent authoring (WHY, WHEN, WHAT, HOW)
- Working examples and patterns
- Implementation and modular design philosophy

**Example:**

```bash
amplifier> @foundation-expert How do I create a bundle?
amplifier> @foundation-expert Show me the behavior pattern
```

## Creating Custom Agents

Agents are bundles with special frontmatter. To create a custom agent:

1. Create a markdown file with YAML frontmatter
2. Use `meta:` section (not `bundle:`) with `name` and `description`
3. Write detailed `description` field with:
   - **WHY**: Value proposition
   - **WHEN**: Activation triggers
   - **WHAT**: Domain terms and concepts
   - **HOW**: Examples with `<example>` blocks
4. Include agent instructions in the markdown body

### Example Agent Structure

```yaml
---
meta:
  name: my-agent
  description: "Purpose and when to use this agent. Include examples showing context, user request, assistant response, and commentary."

tools:
  - module: tool-filesystem
  - module: tool-search
---

# My Agent

You are a specialized agent for [purpose].

## When to Activate

Use this agent when:
- [Trigger 1]
- [Trigger 2]

## Operating Principles

- [Principle 1]
- [Principle 2]
```

### Agent File Locations

Save custom agents to:
- `~/.amplifier/agents/` - Personal agents (all projects)
- `.amplifier/agents/` - Project-specific agents (committed to git)

## Provider Preferences

Control which provider/model an agent uses:

```python
# In task tool delegation
{
    "agent": "foundation:explorer",
    "instruction": "Quick analysis",
    "provider_preferences": [
        {"provider": "anthropic", "model": "claude-haiku-*"},
        {"provider": "openai", "model": "gpt-4o-mini"},
    ]
}
```

The system tries each preference in order until finding an available provider. Model names support glob patterns (e.g., `claude-haiku-*` matches the latest haiku model).

## Tool Inheritance

Bundles can control which tools spawned agents inherit using the `spawn` section:

```yaml
# In bundle.md
tools:
  - module: tool-task      # Coordinator can delegate
  - module: tool-filesystem
  - module: tool-bash

spawn:
  exclude_tools: [tool-task]  # Agents can't delegate further
```

**Common pattern**: Exclude `tool-task` to prevent delegation recursion.

## Best Practices

### When to Use Agents

- **Complex analysis tasks** - Delegate to specialized agents to avoid context bloat
- **Multi-step workflows** - Use agents for focused sub-tasks
- **Domain expertise** - Leverage agent-specific knowledge and tools
- **Context management** - Agents serve as "context sinks" for heavy documentation

### Agent Selection Tips

| Task | Recommended Agent |
|------|-------------------|
| Understanding codebase | `explorer` |
| System design | `zen-architect` |
| Implementation | `modular-builder` |
| Debugging | `bug-hunter` |
| Bundle creation | `foundation-expert` |
| Security review | `security-guardian` |
| Git operations | `git-ops` |

### Multi-Turn Strategies

- **Iterative refinement**: Start with broad request, refine in subsequent turns
- **Context building**: Each turn builds on previous context
- **Session IDs**: Save session IDs for resuming specific conversations later

## Advanced Topics

### Agent as Context Sink

Agents serve as **context sinks** - they carry heavy documentation that would bloat the main session if always loaded.

**Benefits:**
- Main session stays lightweight
- Agent loads heavy docs only when spawned
- Results return with minimal context overhead
- Critical strategy for longer-running sessions

### Agent Composition

Agents are bundles, so they support the same composition patterns:

- Include other bundles via `includes:`
- Reference context files via `context.include:`
- Declare tools, hooks, and providers
- Use behaviors for reusable capabilities

For detailed agent authoring guidance, see the [Bundle Guide](../developer_guides/foundation/amplifier_foundation/bundle_system.md).

## Next Steps

- [CLI Reference](cli.md) - Learn all CLI commands for agent management
- [Bundle System](../developer_guides/foundation/amplifier_foundation/bundle_system.md) - Create custom agents
- [Agent Authoring](https://github.com/microsoft/amplifier-foundation/blob/main/docs/AGENT_AUTHORING.md) - Deep dive into agent design
