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

**Challenge:** Users configure Amplifier at multiple scopes (local, project, global). The CLI must merge these into a single effective configuration.

**Solution:** Uses amplifier-foundation's bundle composition system.

**Implementation:**

```python
from amplifier_foundation import load_bundle, resolve_bundle

# Load active bundle (from settings)
bundle = await load_bundle(bundle_path)

# Compose with user overrides
effective_config = bundle.to_mount_plan()
```

### 2. Bundle Loading

**Challenge:** Users need pre-configured capability sets (bundles) for different workflows.

**Solution:** Bundle management system with source resolution.

**Implementation:**

```python
from amplifier_foundation import load_bundle

# Load bundle from git URL or local path
bundle = await load_bundle("git+https://github.com/user/bundle@main")
prepared = await bundle.prepare()  # Download modules

# Create session from prepared bundle
async with prepared.create_session() as session:
    response = await session.execute("Hello!")
```

### 3. Session Management

**Challenge:** Users need to pause and resume conversations across multiple CLI invocations.

**Solution:** Project-scoped session storage with incremental saves.

**Storage Location:** `~/.amplifier/projects/<project-slug>/sessions/<session-id>/`

**Files:**
- `transcript.jsonl` - Conversation history
- `metadata.json` - Session metadata (bundle, model, turn count)
- `events.jsonl` - Event log for debugging

**Implementation:**

```python
from amplifier_app_cli.session_store import SessionStore

store = SessionStore()

# Save after each turn
messages = await context.get_messages()
metadata = {
    "session_id": session_id,
    "bundle": bundle_name,
    "model": model_name,
    "turn_count": len([m for m in messages if m.get("role") == "user"]),
    "working_dir": str(Path.cwd().resolve()),
}
store.save(session_id, messages, metadata)

# Resume later
transcript = store.get_transcript(session_id)
metadata = store.get_metadata(session_id)
```

### 4. Agent Delegation

**Challenge:** Enable specialized agents to handle subtasks with isolated contexts.

**Solution:** Multi-turn sub-session spawning and resumption using amplifier-foundation's agent system and amplifier-core's session forking.

**Implementation:**

```python
from amplifier_foundation import AgentResolver, AgentLoader
from amplifier_app_cli.session_spawner import spawn_sub_session, resume_sub_session

# Spawn new sub-session
result = await spawn_sub_session(
    agent_name="zen-architect",
    instruction="Design authentication system",
    parent_session=parent_session
)
# Returns: {"output": str, "session_id": str}

# Resume existing sub-session (multi-turn)
result = await resume_sub_session(
    sub_session_id="parent-123-zen-architect-abc456",
    instruction="Add OAuth 2.0 support"
)
```

**Agent Search Paths** (first-match-wins):

1. Environment Variables - `AMPLIFIER_AGENT_<NAME>` (for testing)
2. User Directory - `~/.amplifier/agents/`
3. Project Directory - `.amplifier/agents/`
4. Bundle Agents - Discovered from loaded bundles

**State Persistence:**

Sub-sessions support multi-turn conversations through automatic state persistence:

- Transcript and configuration saved after each execution
- Resume across multiple parent turns
- Survives parent session restarts and crashes

See [Agent Delegation Implementation](../../references/agent_delegation.md) for detailed documentation.

### 5. Interactive REPL

**Challenge:** Provide responsive chat interface with history, editing, and multi-line support.

**Solution:** prompt_toolkit with project-scoped history.

**Implementation:**

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

# Project-scoped history
project_slug = get_project_slug()
history_path = Path.home() / ".amplifier" / "projects" / project_slug / "repl_history"

# Create prompt session with features
prompt_session = PromptSession(
    history=FileHistory(str(history_path)),
    multiline=True,
    enable_history_search=True,  # Ctrl-R
)

# Get user input with all features
user_input = await prompt_session.prompt_async()
```

**Features:**
- Persistent history (project-scoped)
- Multi-line input (Ctrl-J)
- History search (Ctrl-R)
- Graceful cancellation (Ctrl-C)

### 6. Slash Commands

**Challenge:** Users need quick access to session controls without leaving the REPL.

**Solution:** Command processor with slash command routing.

**Implementation:**

```python
class CommandProcessor:
    COMMANDS = {
        "/mode": {"action": "handle_mode", "description": "Set or toggle a mode"},
        "/modes": {"action": "list_modes", "description": "List available modes"},
        "/save": {"action": "save_transcript", "description": "Save conversation"},
        "/status": {"action": "show_status", "description": "Show session status"},
        "/config": {"action": "show_config", "description": "Show configuration"},
        "/tools": {"action": "list_tools", "description": "List available tools"},
        "/agents": {"action": "list_agents", "description": "List available agents"},
        "/rename": {"action": "rename_session", "description": "Rename session"},
        "/fork": {"action": "fork_session", "description": "Fork session at turn N"},
    }

    def process_input(self, user_input: str) -> tuple[str, dict]:
        if user_input.startswith("/"):
            command = user_input.split()[0].lower()
            if command in self.COMMANDS:
                return self.COMMANDS[command]["action"], {...}
        return "prompt", {"text": user_input}
```

### 7. Runtime @Mention Loading

**Challenge:** Users reference files in prompts using `@file.py` syntax. These need to be loaded and added to context.

**Solution:** Runtime mention processing with deduplication.

**Implementation:**

```python
from amplifier_app_cli.lib.mention_loading import MentionLoader

async def _process_runtime_mentions(session: AmplifierSession, prompt: str):
    if not has_mentions(prompt):
        return
    
    # Load @mentioned files
    mention_resolver = session.coordinator.get_capability("mention_resolver")
    loader = MentionLoader(resolver=mention_resolver)
    deduplicator = session.coordinator.get_capability("mention_deduplicator")
    
    context_messages = loader.load_mentions(
        prompt, 
        relative_to=Path.cwd(), 
        deduplicator=deduplicator
    )
    
    # Add to session context
    context = session.coordinator.get("context")
    for msg in context_messages:
        await context.add_message(msg.model_dump())
```

### 8. Incremental Session Saves

**Challenge:** Preserve session state even if CLI crashes mid-execution.

**Solution:** Incremental saves via event hooks.

**Implementation:**

```python
from amplifier_app_cli.incremental_save import register_incremental_save

# Register save hook
register_incremental_save(session, store, session_id, bundle_name, config)

# Hook fires after each tool execution
# Saves current transcript to storage
```

### 9. Cancellation Handling

**Challenge:** Users need graceful cancellation with Ctrl-C during long-running operations.

**Solution:** Two-stage cancellation (graceful then immediate).

**Implementation:**

```python
def sigint_handler(signum, frame):
    """Handle Ctrl+C with graceful/immediate cancellation."""
    cancellation = session.coordinator.cancellation
    
    if cancellation.is_cancelled:
        # Second Ctrl+C - immediate cancellation
        cancellation.request_immediate()
        console.print("\n[bold red]Cancelling immediately...[/bold red]")
    else:
        # First Ctrl+C - graceful cancellation
        cancellation.request_graceful()
        running_tools = cancellation.running_tool_names
        if running_tools:
            tools_str = ", ".join(running_tools)
            console.print(
                f"\n[yellow]Cancelling after [bold]{tools_str}[/bold] completes...[/yellow]"
            )

# Register handler
original_handler = signal.signal(signal.SIGINT, sigint_handler)
```

## Design Patterns

### Pattern 1: Unified Entry Points

**Problem:** Duplicate code for new vs resumed sessions.

**Solution:** Unified functions accepting optional `initial_transcript` parameter.

```python
async def execute_single(
    prompt: str,
    config: dict,
    session_id: str | None = None,
    initial_transcript: list[dict] | None = None,  # Resume if provided
):
    # Create session with optional transcript restoration
    session_config = SessionConfig(
        config=config,
        session_id=session_id,
        initial_transcript=initial_transcript,  # None for new, transcript for resume
    )
    
    initialized = await create_initialized_session(session_config, console)
    # ... execute prompt
```

### Pattern 2: Session-Scoped Settings

**Problem:** Some settings should only apply to current session (not saved globally).

**Solution:** Session-scoped configuration layer.

```python
from amplifier_app_cli.lib.settings import AppSettings

# Get session-scoped settings
settings = AppSettings().with_session(session_id, project_slug)

# Add allowed directory (session scope only)
settings.add_allowed_write_path("/tmp/scratch", "session")
```

### Pattern 3: Lazy Client Initialization

**Problem:** Provider `get_info()` should work without valid credentials.

**Solution:** Lazy client initialization on first API call.

```python
class AnthropicProvider:
    def __init__(self, api_key: str | None = None, config: dict | None = None):
        self._api_key = api_key
        self._client: AsyncAnthropic | None = None  # Lazy init
    
    @property
    def client(self) -> AsyncAnthropic:
        """Lazily initialize client on first access."""
        if self._client is None:
            if self._api_key is None:
                raise ValueError("api_key required for API calls")
            self._client = AsyncAnthropic(api_key=self._api_key)
        return self._client
    
    def get_info(self) -> ProviderInfo:
        """Works without credentials - doesn't access self.client"""
        return ProviderInfo(id="anthropic", ...)
```

### Pattern 4: Event-Based Filtering

**Problem:** LLM errors logged by providers duplicate rich panel output in CLI.

**Solution:** Log filter attached to console handler.

```python
from amplifier_app_cli.ui.log_filter import LLMErrorLogFilter

# Attach filter to stderr handler only
_llm_error_filter = LLMErrorLogFilter()
for _handler in logging.getLogger().handlers:
    if isinstance(_handler, logging.StreamHandler) and _handler.stream is sys.stderr:
        _handler.addFilter(_llm_error_filter)
```

## Libraries Used

### Core Dependencies

| Library | Purpose |
|---------|---------|
| **amplifier-core** | Session lifecycle, orchestration, provider/tool contracts |
| **amplifier-foundation** | Bundle loading, composition, agent resolution |
| **click** | CLI framework, command routing, argument parsing |
| **rich** | Terminal formatting, markdown rendering, progress indicators |
| **prompt_toolkit** | REPL, history, multi-line input, key bindings |
| **pyyaml** | YAML configuration parsing |

### Design Principles

1. **Use foundation for composition** - Let amplifier-foundation handle bundle loading and merging
2. **Delegate to core for execution** - Let amplifier-core handle session lifecycle and tool orchestration
3. **CLI is just UI** - Business logic lives in libraries, CLI renders results
4. **Event-driven observability** - Use hooks for cross-cutting concerns (logging, notifications)
5. **Graceful degradation** - Features degrade gracefully when dependencies unavailable

## Key Takeaways

**For Application Builders:**

1. **Libraries do the work** - amplifier-foundation and amplifier-core handle heavy lifting
2. **Applications add policy** - Where to store sessions, which bundles to use, how to present results
3. **Event hooks enable features** - Notifications, logging, session naming all via hooks
4. **Configuration is composable** - Bundle system enables sharing and remixing configurations

**Architectural Decisions:**

- **Project-scoped storage** - Sessions stored per-project for isolation
- **Incremental saves** - Crash recovery via event hooks
- **Multi-turn sub-sessions** - Agent delegation with resumable conversations
- **Lazy initialization** - Credentials only required for actual API calls
- **Three-scope config** - Local > project > global precedence

## Related Documentation

- **[Agent Delegation Implementation](../../references/agent_delegation.md)** - Sub-session spawning details
- **[Bundle Guide](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md)** - Bundle system concepts
- **[Session Fork Specification](https://github.com/microsoft/amplifier-core/blob/main/docs/SESSION_FORK_SPECIFICATION.md)** - Core session forking mechanism
