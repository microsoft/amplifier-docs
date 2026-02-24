---
title: Case Study - Amplifier CLI Application
description: How amplifier-app-cli is built on amplifier-core
---

# Case Study: Amplifier CLI Application

Learn how **amplifier-app-cli** is built on top of amplifier-core. This case study shows real-world patterns for building applications on the Amplifier foundation.

## Overview

amplifier-app-cli is a command-line application that provides:

- **Interactive REPL** - Chat-style interface with the AI
- **Single-shot execution** - `amplifier run "prompt"`
- **Session management** - Resume previous conversations
- **Bundle system** - Pre-configured capability sets
- **Provider switching** - Easy model/provider changes

All built on amplifier-core using the libraries and following best practices.

## Architecture

```
amplifier-app-cli/
├── CLI Layer (Click)
│   ├── Command parsing
│   ├── Argument handling
│   └── Help text
│
├── Application Layer
│   ├── Configuration resolution
│   │   └── Uses: amplifier-foundation
│   ├── Bundle loading
│   │   └── Uses: amplifier-foundation
│   ├── Module resolution
│   │   └── Uses: amplifier-foundation
│   └── Session initialization (session_runner.py)
│
├── Display Layer
│   ├── Rich console formatting
│   ├── Markdown rendering
│   ├── Progress indicators
│   └── Error presentation
│
├── Agent Delegation Layer
│   └── Session spawning (session_spawner.py)
│
└── Session Layer
    └── Uses: amplifier-core
        ├── Session lifecycle
        ├── Prompt execution
        └── Event handling
```

## Key Components

### 1. Configuration Resolution

**Challenge:** Users configure providers, bundles, and settings through multiple sources:
- Environment variables (`ANTHROPIC_API_KEY`)
- Config files (`~/.amplifier/config.toml`)
- CLI arguments (`--provider anthropic`)
- Bundle defaults

**Solution:** Priority-based resolution with clear precedence:

```
CLI args > Environment variables > Config file > Bundle defaults
```

**Implementation:**
- `KeyManager` loads API keys from `~/.amplifier/keys.env`
- Configuration files follow TOML format
- CLI arguments override all other sources

### 2. Bundle Integration

**Challenge:** Load and compose bundles from various sources (git, local, registered).

**Solution:** Uses `amplifier-foundation` library for all bundle operations:

```python
from amplifier_foundation import load_bundle, BundleRegistry

# Load from registry
registry = BundleRegistry()
bundle = await registry.load("foundation")

# Compose with provider
provider = await load_bundle("git+https://github.com/...")
composed = bundle.compose(provider)

# Prepare and execute
prepared = await composed.prepare()
session = await prepared.create_session()
```

**Key patterns:**
- Bundle registry for named bundles (`amplifier bundle list`)
- Automatic module download and caching
- Composition for provider/tool selection

### 3. Agent Delegation

**Challenge:** Enable users to delegate tasks to specialized agents without complex configuration.

**Solution:** Multi-layered agent resolution with environment variable overrides:

**Agent Resolution (first-match-wins):**

```
1. Environment Variables
   AMPLIFIER_AGENT_ZEN_ARCHITECT=~/test-zen.md
   → For testing changes before committing

2. User Directory
   ~/.amplifier/agents/zen-architect.md
   → Personal overrides and custom agents

3. Project Directory
   .amplifier/agents/project-reviewer.md
   → Project-specific agents (committed to git)

4. Bundle Agents
   bundles/developer-expertise/agents/zen-architect.md
   → Agents bundled with bundles
```

**Implementation:**

```python
from amplifier_foundation import AgentResolver, AgentLoader

# Build search paths
search_paths = [
    Path(".amplifier/agents"),                    # Project
    Path.home() / ".amplifier" / "agents",        # User
    # Bundle agents added via bundle discovery
]

# Create resolver
resolver = AgentResolver(search_paths=search_paths)

# Check environment variable override first
agent_name = "zen-architect"
env_var = f"AMPLIFIER_AGENT_{agent_name.upper().replace('-', '_')}"
agent_path = os.environ.get(env_var)

if not agent_path:
    agent_path = resolver.resolve(agent_name)

# Load agent
loader = AgentLoader(resolver=resolver)
agent = loader.load_agent(agent_name)
```

**Usage in interactive mode:**

```bash
amplifier
amplifier> @zen-architect Design a caching system
```

### 4. Multi-Turn Sub-Session Resumption

**Challenge:** Support iterative conversations with agents across multiple turns.

**Solution:** Automatic state persistence for sub-sessions.

**State Persistence:**

After each sub-session execution, state is saved:

```python
from amplifier_app_cli.session_store import SessionStore

# Capture current state
context = child_session.coordinator.get("context")
transcript = await context.get_messages() if context else []

metadata = {
    "session_id": sub_session_id,
    "parent_id": parent_session.session_id,
    "agent_name": agent_name,
    "created": datetime.now(UTC).isoformat(),
    "config": merged_config,  # Full merged mount plan
    "agent_overlay": agent_config,  # Original agent config
}

# Persist to storage
store = SessionStore()  # Project-scoped: ~/.amplifier/projects/{project}/sessions/
store.save(sub_session_id, transcript, metadata)
```

**Storage Location:** `~/.amplifier/projects/{project-slug}/sessions/{session-id}/`
- `transcript.jsonl` - Conversation history
- `metadata.json` - Session configuration and metadata
- `bundle.md` - Bundle snapshot (if applicable)

**Resuming Existing Sessions:**

```python
from amplifier_app_cli.session_spawner import resume_sub_session

# Resume by session ID
result = await resume_sub_session(
    sub_session_id="parent-123-zen-architect-abc456",
    instruction="Now add OAuth 2.0 support"
)
# Returns: {"output": str, "session_id": str}
```

**Resume Process:**
1. Load transcript and metadata from `SessionStore`
2. Recreate `AmplifierSession` with stored configuration
3. Restore transcript to context via `add_message()`
4. Execute new instruction with full conversation history
5. Save updated state
6. Cleanup and return

**Key Design Points:**
- **Stateless**: Each resume loads fresh from disk (no in-memory caching)
- **Deterministic**: Uses stored merged config (independent of parent changes)
- **Self-contained**: All state needed for reconstruction persists with session
- **Resumable**: Survives parent session restarts and crashes

### 5. Session Forking

**Challenge:** Create sub-sessions for agent delegation while maintaining parent context.

**Solution:** Uses amplifier-core's `session.fork()` with agent config overlay:

```python
# In parent session
parent_session = AmplifierSession(config=parent_mount_plan)

# Load agent config
agent = agent_loader.load_agent("zen-architect")
agent_mount_plan_fragment = agent.to_mount_plan_fragment()

# Fork session with agent overlay
sub_session = await parent_session.fork(
    config_overlay=agent_mount_plan_fragment,
    task_description="Design authentication system"
)

# Execute in sub-session
result = await sub_session.execute("Design the auth system")
```

**Spawn Tool Policy:**

Bundles can control which tools spawned agents inherit using the `spawn` section:

```yaml
# In bundle.md
spawn:
  exclude_tools: [tool-task]  # Agents inherit all tools EXCEPT these
  # OR
  tools: [tool-a, tool-b]     # Agents get ONLY these tools
```

**Common pattern:** Prevent delegation recursion by excluding `tool-task`:

```yaml
tools:
  - module: tool-task      # Coordinator can delegate
  - module: tool-filesystem
  - module: tool-bash

spawn:
  exclude_tools: [tool-task]  # But agents can't delegate further
```

### 6. Provider Preferences

**Challenge:** Allow flexible provider/model selection for spawned agents.

**Solution:** Ordered fallback chain with glob pattern support:

```python
result = await task_tool.execute({
    "agent": "foundation:explorer",
    "instruction": "Quick analysis",
    "provider_preferences": [
        {"provider": "anthropic", "model": "claude-haiku-*"},
        {"provider": "openai", "model": "gpt-4o-mini"},
    ]
})
```

- System tries each preference in order until finding an available provider
- Model names support glob patterns (e.g., `claude-haiku-*` → latest haiku)
- Enables cost optimization (prefer cheaper models) with fallback

### 7. Display and User Experience

**Challenge:** Present AI responses and system state in a readable, helpful format.

**Solution:** Rich console formatting with markdown rendering:

```python
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

# Render markdown responses
console.print(Markdown(response))

# Display panels for structure
console.print(Panel("Configuration loaded", title="Status"))

# Progress indicators for long operations
with console.status("Preparing modules..."):
    prepared = await bundle.prepare()
```

**Key patterns:**
- Markdown rendering for AI responses
- Panels for structured information
- Progress indicators for async operations
- Color coding for status (success, warning, error)

## Interactive Mode Commands

The CLI provides special commands in interactive mode:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/config` | Show current configuration |
| `/tools` | List available tools |
| `/agents` | List available agents |
| `/history` | Show conversation history |
| `/fork` | Fork current session |
| `/exit` | Exit interactive mode |
| `@agent` | Invoke a specific agent |

**Implementation:** Command detection in REPL input handler with routing to appropriate handlers.

## Session Management

### Session Storage

Sessions are stored in project-specific directories:

```
~/.amplifier/projects/
└── {project-slug}/
    └── sessions/
        └── {session-id}/
            ├── transcript.jsonl
            ├── metadata.json
            └── events.jsonl
```

**SessionStore** handles:
- Project slug generation from working directory
- Session metadata persistence
- Transcript storage and retrieval
- Session listing and filtering

### Session Commands

Implemented via `commands/session.py`:

- `session list` - List all sessions with filters
- `session show` - Display session details
- `session resume` - Resume specific session
- `session delete` - Delete sessions with various criteria
- `session history` - Show conversation history
- `session search` - Search sessions by content

## Environment Variable Overrides

**Testing Agent Changes:**

```bash
# Test modified agent without committing
export AMPLIFIER_AGENT_ZEN_ARCHITECT=~/work/test-zen.md
amplifier run "design system"  # Uses test version

# Unset to use normal resolution
unset AMPLIFIER_AGENT_ZEN_ARCHITECT
```

**Format:** `AMPLIFIER_AGENT_<NAME>` (uppercase, dashes → underscores)

This enables rapid iteration on agent definitions during development.

## Integration with amplifier-foundation Library

amplifier-app-cli uses amplifier-foundation library for ALL agent functionality:

**What CLI provides** (policy):
- CLI-specific search paths (user, project, bundle directories)
- Environment variable override mechanism
- CLI commands for listing/showing agents
- Integration with bundle system

**What library provides** (mechanism):
- Agent file format parsing (markdown + YAML frontmatter)
- AgentResolver (path-based resolution)
- AgentLoader (loading and parsing agent files)
- Agent schemas (Agent, AgentMeta, SystemConfig)
- First-match-wins resolution logic

**Boundary**: CLI calls library APIs, library doesn't know about CLI.

## Best Practices Demonstrated

### 1. Separation of Concerns

- **CLI layer**: Command parsing only
- **Application layer**: Business logic
- **Display layer**: UI/formatting
- **Session layer**: Kernel interaction

Each layer has clear responsibilities and dependencies flow downward.

### 2. Configuration Management

- Environment variables for sensitive data (API keys)
- Config files for user preferences
- CLI arguments for per-command overrides
- Clear precedence rules

### 3. Error Handling

```python
from amplifier_core import ModuleValidationError

try:
    session = await create_initialized_session(config)
except ModuleValidationError as e:
    display_validation_error(e, console)
    sys.exit(1)
```

**Patterns:**
- Specific exception types for different errors
- User-friendly error messages
- Recovery suggestions
- Exit codes for scripting

### 4. Session Lifecycle

```python
# Create session with context manager
async with prepared.create_session(session_cwd=Path.cwd()) as session:
    response = await session.execute(prompt)
    # Automatic cleanup on exit
```

**Benefits:**
- Automatic resource cleanup
- Exception safety
- Clear lifecycle boundaries

### 5. Observability

**Event handling** for debugging and monitoring:

```python
# Subscribe to events
session.coordinator.on("llm:request", handle_request)
session.coordinator.on("llm:response", handle_response)
session.coordinator.on("tool:execute", handle_tool)
```

**Use cases:**
- Debug logging
- Performance monitoring
- Token usage tracking
- Error diagnostics

## Command Structure

The CLI uses Click for command management:

```python
@click.group(cls=AmplifierGroup)
def cli():
    """Amplifier CLI application."""
    pass

# Register command groups
cli.add_command(run)
cli.add_command(bundle_group)
cli.add_command(session_group)
cli.add_command(provider_group)
cli.add_command(agents_group)
```

**Key files:**
- `main.py` - Main CLI entry point and interactive mode
- `commands/run.py` - Run command implementation
- `commands/session.py` - Session management commands
- `commands/bundle.py` - Bundle management commands
- `commands/provider.py` - Provider management commands
- `commands/agents.py` - Agent management commands

## Related Documentation

**Agent System:**
- [Agent Delegation Implementation](https://github.com/microsoft/amplifier-app-cli/blob/main/docs/AGENT_DELEGATION_IMPLEMENTATION.md) - How CLI implements agent delegation
- [Bundle Guide](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md) - How to create bundles and agents

**Kernel Mechanism:**
- [Session Fork Specification](https://github.com/microsoft/amplifier-core/blob/main/docs/SESSION_FORK_SPECIFICATION.md) - Session forking contract

## Key Takeaways

1. **Leverage libraries:** Use amplifier-foundation for bundle/agent management
2. **Clear boundaries:** Separate CLI, application, and session concerns
3. **Mechanism vs Policy:** Library provides mechanism, CLI adds policy
4. **User experience:** Rich console formatting and helpful error messages
5. **State persistence:** Project-scoped session storage with resumption
6. **Multi-turn support:** Agents maintain conversation context across turns
7. **Testing support:** Environment variable overrides for rapid iteration

## Next Steps

- [CLI Reference](../../user_guide/cli.md) - Complete CLI command reference
- [Agents Guide](../../user_guide/agents.md) - Using and creating agents
- [Bundle System](../foundation/amplifier_foundation/bundle_system.md) - Understanding bundles
- [amplifier-foundation Examples](../foundation/amplifier_foundation/examples/index.md) - Foundation examples
