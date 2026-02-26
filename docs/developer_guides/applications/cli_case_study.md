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

**Challenge:** Merge bundle configuration, user settings, and CLI flags into a single effective config.

**Solution:** Layered composition using amplifier-foundation:

```python
# From runtime/config.py
async def resolve_config(bundle_name, app_settings, console):
    # 1. Load bundle (foundation layer)
    bundle = await load_bundle(bundle_name)
    
    # 2. Prepare bundle (download/activate modules)
    prepared = await bundle.prepare()
    
    # 3. Extract mount plan
    config = prepared.mount_plan
    
    # 4. Apply app-level settings (policy layer)
    config = apply_settings_overrides(config, app_settings)
    
    return config, prepared
```

**Key insight:** Bundle provides mechanism (what tools exist), settings provide policy (API keys, paths).

### 2. Session Lifecycle

**Challenge:** Handle both new and resumed sessions, interactive and single-shot modes, with proper cleanup.

**Solution:** Unified session creation:

```python
# From session_runner.py
async def create_initialized_session(session_config, console):
    # Create session from prepared bundle
    session = await prepared_bundle.create_session(
        session_id=session_config.session_id
    )
    
    # Initialize (mount modules)
    await session.initialize()
    
    # Restore transcript if resuming
    if session_config.initial_transcript:
        await restore_transcript(session, session_config.initial_transcript)
    
    return InitializedSession(session, cleanup_func)
```

**Entry points:**
- `interactive_chat()` - REPL mode with persistent sessions
- `execute_single()` - Single-shot execution with optional resume

**Key insight:** Single code path for all session creation modes prevents drift.

### 3. Agent Delegation

**Challenge:** Spawn sub-sessions for agent delegation with proper configuration inheritance and multi-turn support.

**Implementation:** Built on amplifier-foundation's agent system. See [AGENT_DELEGATION_IMPLEMENTATION.md](https://github.com/microsoft/amplifier-app-cli/blob/main/docs/AGENT_DELEGATION_IMPLEMENTATION.md) for complete details.

**Key components:**

```python
# From session_spawner.py
async def spawn_sub_session(parent_session, agent_name, instruction):
    # 1. Load agent config from bundle
    agent_loader = AgentLoader(resolver)
    agent = agent_loader.load_agent(agent_name)
    
    # 2. Merge parent config with agent overlay
    merged_config = merge_configs(parent_config, agent.to_mount_plan_fragment())
    
    # 3. Apply spawn policy (tool inheritance)
    filtered_config = apply_spawn_tool_policy(merged_config)
    
    # 4. Create child session via fork
    child_session = await parent_session.fork(
        config_overlay=filtered_config,
        task_description=instruction
    )
    
    # 5. Execute and persist state
    result = await child_session.execute(instruction)
    
    # 6. Save state for resumption
    await save_sub_session_state(child_session, metadata)
    
    return {"output": result, "session_id": child_session.session_id}
```

**Multi-turn sub-session support:**

```python
# Resume existing sub-session
async def resume_sub_session(sub_session_id, instruction):
    # 1. Load transcript and metadata from SessionStore
    transcript, metadata = store.load(sub_session_id)
    
    # 2. Recreate session with stored configuration
    session = await create_session_from_metadata(metadata)
    
    # 3. Restore transcript
    await restore_transcript(session, transcript)
    
    # 4. Execute new instruction with full context
    result = await session.execute(instruction)
    
    # 5. Save updated state
    await save_sub_session_state(session, metadata)
    
    return {"output": result, "session_id": sub_session_id}
```

**Features:**
- Multi-turn conversations via session persistence
- Provider preferences for agent delegation
- Tool inheritance control via spawn policy
- Environment variable overrides for testing (`AMPLIFIER_AGENT_ZEN_ARCHITECT`)

**Search paths** (first-match-wins):
1. Environment variables (`AMPLIFIER_AGENT_<NAME>`)
2. User directory (`~/.amplifier/agents/`)
3. Project directory (`.amplifier/agents/`)
4. Bundle agents (from bundle discovery)

### 4. Interactive Commands

**Challenge:** Support slash commands in REPL without mixing command and prompt parsing.

**Solution:** Command processor with dynamic mode support:

```python
# From main.py - CommandProcessor
COMMANDS = {
    "/mode": "handle_mode",
    "/modes": "list_modes",
    "/save": "save_transcript",
    "/status": "show_status",
    "/clear": "clear_context",
    "/help": "show_help",
    "/config": "show_config",
    "/tools": "list_tools",
    "/agents": "list_agents",
    "/allowed-dirs": "manage_allowed_dirs",
    "/denied-dirs": "manage_denied_dirs",
    "/rename": "rename_session",
    "/fork": "fork_session",
}
```

**Mode shortcuts:** Dynamic shortcuts populated from mode definitions (e.g., `/plan` → `/mode plan on`)

**Trailing prompt support:**
```python
# "/plan design a caching system" activates plan mode AND executes prompt
action, data = command_processor.process_input(user_input)
if action == "handle_mode" and "trailing_prompt" in data:
    # Activate mode first
    await command_processor.handle_command(action, data)
    # Then execute trailing prompt
    await session.execute(data["trailing_prompt"])
```

**Key insight:** Commands are prefix-only; everything else is a prompt.

### 5. Session Persistence

**Challenge:** Save and restore sessions across CLI invocations.

**Solution:** SessionStore with JSONL format:

```python
# From session_store.py
class SessionStore:
    """Project-scoped session storage."""
    
    def save(self, session_id, messages, metadata):
        # Location: ~/.amplifier/projects/{project-slug}/sessions/{id}/
        session_dir = self.base_dir / session_id
        
        # Save transcript
        with open(session_dir / "transcript.jsonl", "w") as f:
            for msg in messages:
                f.write(json.dumps(msg) + "\n")
        
        # Save metadata
        with open(session_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
    
    def load(self, session_id):
        # Load and return (transcript, metadata)
        pass
```

**Storage structure:**
```
~/.amplifier/projects/{project-slug}/sessions/{session-id}/
├── transcript.jsonl  # Conversation history
├── metadata.json     # Session config and metadata
└── events.jsonl      # Event log (if logging enabled)
```

**Key insight:** Project-scoped storage enables per-project session isolation.

### 6. Incremental Save

**Challenge:** Preserve work during crashes or Ctrl+C interruptions.

**Solution:** Hook-based incremental save:

```python
# From incremental_save.py
def register_incremental_save(session, store, session_id, bundle_name, config):
    """Register hook that saves after each tool execution."""
    
    async def on_tool_post(event_name, data):
        # Save current state after successful tool execution
        context = session.coordinator.get("context")
        messages = await context.get_messages()
        await store.save(session_id, messages, metadata)
    
    hooks = session.coordinator.get("hooks")
    hooks.register("tool:post", on_tool_post)
```

**Key insight:** Hooks enable transparent crash recovery without changing session logic.

### 7. Cancellation Handling

**Challenge:** Support graceful and immediate cancellation without corrupting session state.

**Solution:** Two-stage cancellation with CancellationToken:

```python
# From main.py - interactive_chat()
def sigint_handler(signum, frame):
    cancellation = session.coordinator.cancellation
    
    if cancellation.is_cancelled:
        # Second Ctrl+C - immediate cancellation
        cancellation.request_immediate()
        console.print("Cancelling immediately...")
    else:
        # First Ctrl+C - graceful cancellation
        cancellation.request_graceful()
        running_tools = cancellation.running_tool_names
        if running_tools:
            console.print(f"Cancelling after {', '.join(running_tools)} completes...")
```

**Key insight:** Synchronous state updates in signal handler prevent race conditions on rapid Ctrl+C.

### 8. Display Layer

**Challenge:** Render AI responses with syntax highlighting, code blocks, and thinking blocks.

**Solution:** Rich-based message renderer:

```python
# From ui/message_renderer.py
def render_message(message, console, show_thinking=False):
    role = message.get("role")
    
    if role == "user":
        # User messages: cyan prompt marker
        console.print(f"[bold cyan]>[/bold cyan] {content}")
    
    elif role == "assistant":
        # Assistant messages: markdown rendering
        console.print(Markdown(content))
        
        # Show thinking block if present and enabled
        if show_thinking and message.get("thinking_block"):
            render_thinking_block(message["thinking_block"])
```

**Key insight:** Shared renderer ensures consistency between live chat and resumed sessions.

## Design Patterns

### Pattern: Unified Entry Points

**Problem:** Duplicate code for interactive vs single-shot modes.

**Solution:** Single functions with mode parameter:

```python
# Both modes use same function
async def interactive_chat(
    config, search_paths, verbose,
    session_id=None,
    initial_prompt=None,        # Auto-execute before REPL
    initial_transcript=None     # Resume mode
)

async def execute_single(
    prompt, config, search_paths, verbose,
    session_id=None,
    initial_transcript=None     # Resume mode
)
```

**Benefit:** Resume logic works identically in both modes.

### Pattern: PreparedBundle Integration

**Problem:** Need to download modules, apply overrides, and create sessions consistently.

**Solution:** Use amplifier-foundation's PreparedBundle:

```python
# From runtime/config.py
async def resolve_config(bundle_name, app_settings, console):
    # Load and prepare bundle
    bundle = await load_bundle(bundle_name)
    prepared = await bundle.prepare()  # Downloads modules, builds resolver
    
    # Apply CLI-specific provider overrides
    inject_user_providers(prepared.mount_plan, prepared)
    
    # Session creation uses prepared bundle
    session = await prepared.create_session(session_cwd=Path.cwd())
    
    return prepared.mount_plan, prepared
```

**Benefit:** Single source of truth for module resolution and loading.

### Pattern: Session Forking for Sub-Sessions

**Problem:** Agent delegation needs isolated contexts with controlled tool inheritance.

**Solution:** Use amplifier-core's `session.fork()`:

```python
# Fork creates isolated sub-session
child_session = await parent_session.fork(
    config_overlay=agent_mount_plan_fragment,
    task_description="Design authentication system"
)

# Overlay merges with parent config
# Spawn policy controls tool inheritance
```

**Benefit:** Kernel handles state isolation; app layer only provides config overlay.

## Related Documentation

**Core Concepts:**
- **→ [amplifier-core](https://github.com/microsoft/amplifier-core)** - Session, orchestrator, and event system
- **→ [amplifier-foundation](https://github.com/microsoft/amplifier-foundation)** - Bundle system and agent loading

**Implementation Details:**
- **→ [AGENT_DELEGATION_IMPLEMENTATION.md](https://github.com/microsoft/amplifier-app-cli/blob/main/docs/AGENT_DELEGATION_IMPLEMENTATION.md)** - Complete agent delegation guide
- **→ [SESSION_FORK_SPECIFICATION.md](https://github.com/microsoft/amplifier-core/blob/main/docs/SESSION_FORK_SPECIFICATION.md)** - Session forking contract

**Philosophy:**
- **→ [IMPLEMENTATION_PHILOSOPHY.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/IMPLEMENTATION_PHILOSOPHY.md)** - Guiding principles
