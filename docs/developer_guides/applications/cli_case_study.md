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

**Solution:** Layered composition:

```python
# From runtime/config.py
def resolve_config(bundle_name, app_settings, console):
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
    # Create session
    session = AmplifierSession(
        config=session_config.config,
        loader=loader,
        session_id=session_config.session_id,
        is_resumed=session_config.is_resume
    )
    
    # Initialize (mount modules)
    await session.initialize()
    
    # Restore transcript if resuming
    if session_config.initial_transcript:
        await restore_transcript(session, session_config.initial_transcript)
    
    return InitializedSession(session, cleanup_func)
```

**Key insight:** Single code path for all session creation modes prevents drift.

### 3. Agent Delegation

**Challenge:** Spawn sub-sessions for agent delegation with proper configuration inheritance.

**Implementation:** See [Agent Delegation Implementation](https://github.com/microsoft/amplifier-app-cli/blob/main/docs/AGENT_DELEGATION_IMPLEMENTATION.md) for complete details.

**Key components:**

```python
# From session_spawner.py
async def spawn_sub_session(parent_session, agent_name, instruction):
    # 1. Load agent config
    agent = await load_bundle(agent_path)
    
    # 2. Merge parent config with agent overlay
    merged_config = merge_configs(parent_config, agent.to_mount_plan())
    
    # 3. Apply spawn policy (tool inheritance)
    filtered_config = apply_spawn_tool_policy(merged_config)
    
    # 4. Create child session
    child_session = AmplifierSession(
        config=filtered_config,
        parent_id=parent_session.session_id
    )
    
    # 5. Execute and return
    result = await child_session.execute(instruction)
    return {"output": result, "session_id": child_session.session_id}
```

**Features:**
- Multi-turn sub-session support (sessions persist and can be resumed)
- Provider preferences for agent delegation
- Tool inheritance control via spawn policy

### 4. Interactive Commands

**Challenge:** Support slash commands in REPL without mixing command and prompt parsing.

**Solution:** Command processor with mode support:

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

**Mode shortcuts:** Dynamic shortcuts populated from mode definitions (e.g., `/plan` → `/mode plan`)

### 5. Cancellation Handling

**Challenge:** Graceful cancellation (finish current tool) vs immediate (force cancel).

**Solution:** Two-stage Ctrl+C handling:

```python
# From main.py - interactive_chat
def sigint_handler(signum, frame):
    cancellation = session.coordinator.cancellation
    
    if cancellation.is_cancelled:
        # Second Ctrl+C - immediate
        cancellation.request_immediate()
        console.print("Cancelling immediately...")
    else:
        # First Ctrl+C - graceful
        cancellation.request_graceful()
        console.print("Cancelling after current operation completes...")
```

**Key insight:** Synchronous state updates prevent race conditions with rapid double Ctrl+C.

### 6. Output Formatting

**Challenge:** Support both human-readable and machine-readable output.

**Solution:** Multiple output formats:

```python
# From main.py - execute_single
if output_format == "json":
    output = {
        "status": "success",
        "response": response,
        "session_id": session_id,
        "bundle": bundle_name,
        "model": model_name,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    print(json.dumps(output, indent=2))
elif output_format == "json-trace":
    output = {
        ...
        "execution_trace": trace_collector.get_trace(),
        "metadata": trace_collector.get_metadata(),
    }
    print(json.dumps(output, indent=2))
else:
    # Text - markdown rendering
    console.print(Markdown(response))
```

**Stream isolation:** In JSON mode, all output redirected to stderr except final JSON to stdout.

### 7. Session Persistence

**Challenge:** Save sessions for resumption without blocking the REPL.

**Solution:** Incremental save hooks:

```python
# From incremental_save.py
def register_incremental_save(session, store, session_id, bundle_name, config):
    """Register hook for incremental saves during tool execution."""
    hooks = session.coordinator.get("hooks")
    
    async def on_tool_post(event, data):
        # Save after each tool completes (crash recovery)
        context = session.coordinator.get("context")
        messages = await context.get_messages()
        store.save(session_id, messages, metadata)
    
    hooks.register("tool:post", on_tool_post)
```

**Key insight:** Save after tool execution, not after every token, balances performance and crash recovery.

### 8. Session Fork

**Challenge:** Create branches from existing sessions to explore alternatives.

**Solution:** Uses amplifier-foundation's session utilities:

```python
# From main.py - CommandProcessor._fork_session
from amplifier_foundation.session import fork_session, count_turns

# Fork at specific turn
result = fork_session(
    session_dir,
    turn=turn,
    new_session_id=custom_name,
    include_events=True,
)

# Returns: ForkResult with session_id, message_count, forked_from_turn
```

**Features:**
- Preview turns before forking
- Custom naming for forked sessions
- Event log preservation

## Design Patterns

### Pattern 1: Mechanism vs Policy Separation

**Kernel (amplifier-core):**
- Provides session lifecycle
- Emits events
- Validates contracts

**Foundation (amplifier-foundation):**
- Provides bundle composition
- Loads and activates modules
- Resolves @mentions

**Application (amplifier-app-cli):**
- Decides which bundles to load
- Configures providers with API keys
- Manages session storage location
- Formats output for users

### Pattern 2: Unified Entry Points

Instead of separate functions for each mode:

```python
# ❌ OLD: Separate functions drift over time
async def interactive_chat(config): ...
async def interactive_chat_with_session(config, transcript): ...
async def execute_single(prompt, config): ...
async def execute_single_with_session(prompt, config, transcript): ...

# ✅ NEW: Unified with optional parameters
async def interactive_chat(
    config,
    initial_transcript=None,  # Resume if provided
    initial_prompt=None,      # Auto-execute if provided
):
    # Single code path handles all modes
```

**Key insight:** Optional parameters better than function proliferation.

### Pattern 3: Progressive Enhancement

**Base experience works, enhancements add features:**

```python
# Base: File history with InMemoryHistory fallback
try:
    history = FileHistory(str(history_path))
except OSError:
    history = InMemoryHistory()  # Graceful degradation
```

**Applied to:**
- History persistence (fallback to in-memory)
- Shell completion (manual instructions if auto-install fails)
- Mode shortcuts (works without mode system)

### Pattern 4: Event-Driven Extensibility

**The CLI hooks into kernel events:**

```python
# Register hooks
hooks.register("prompt:complete", on_prompt_complete)
hooks.register("session:end", on_session_end)

# Hooks handle:
# - Incremental session saving
# - Session naming
# - Notifications
# - Cost tracking
```

**Key insight:** Hooks decouple features from core flow.

## Implementation Highlights

### Multi-Line Input Support

```python
# From main.py - _create_prompt_session
kb = KeyBindings()

@kb.add("c-j")  # Ctrl-J inserts newline
def insert_newline(event):
    event.current_buffer.insert_text("\n")

@kb.add("enter")  # Enter submits
def accept_input(event):
    event.current_buffer.validate_and_handle()

prompt_session = PromptSession(
    history=history,
    key_bindings=kb,
    multiline=True,
    prompt_continuation="  ",  # Clean alignment
)
```

**Philosophy:** Ctrl-J is terminal-reliable (works everywhere), multi-line display for readability.

### Dynamic Prompt with Mode Indicator

```python
# Shows active mode in prompt
def get_prompt():
    active_mode = session.coordinator.session_state.get("active_mode")
    if active_mode:
        return HTML(f"\n<ansicyan>[{active_mode}]</ansicyan><ansigreen><b>></b></ansigreen> ")
    return HTML("\n<ansigreen><b>></b></ansigreen> ")
```

**Visual feedback:** Mode indicator helps user track context.

### Runtime @Mention Processing

```python
# From main.py - _process_runtime_mentions
async def _process_runtime_mentions(session, prompt):
    """Process @mentions in user input at runtime."""
    if not has_mentions(prompt):
        return
    
    # Load @mentioned files
    loader = MentionLoader(resolver=mention_resolver)
    context_messages = loader.load_mentions(prompt, relative_to=Path.cwd())
    
    # Add to session context
    context = session.coordinator.get("context")
    for msg in context_messages:
        await context.add_message(msg.model_dump())
```

**User experience:** Reference files inline with `@path/to/file.md` in prompts.

### First-Run Initialization

```python
# From commands/init.py
def check_first_run():
    """Check if this is first run (no settings.yaml)."""
    return not settings_file.exists()

# Auto-init from environment
def auto_init_from_env(console):
    """Initialize from ANTHROPIC_API_KEY env var."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        save_provider_config("anthropic", api_key)
```

**Pattern:** Interactive prompt for TTY, auto-init from env vars for CI/Docker.

## Lessons for Application Builders

### 1. Use Foundation's Abstractions

```python
# ✅ DO THIS - use foundation
from amplifier_foundation import load_bundle

bundle = await load_bundle("foundation")
prepared = await bundle.prepare()

# ❌ DON'T DO THIS - manually construct mount plans
config = {
    "session": {"orchestrator": {"module": "loop-streaming", ...}, ...},
    "providers": [{...}],
    "tools": [{...}],
}
```

**Why:** Foundation handles composition, validation, module activation.

### 2. Separate Mechanism from Policy

**Mechanism (reusable):**
- Session creation
- Module loading
- Event emission

**Policy (app-specific):**
- Where to store sessions
- Which bundle to use by default
- How to format errors

### 3. Progressive Enhancement

Build base experience first, add features incrementally:

1. Basic execution ✅
2. Session resume ✅
3. Interactive mode ✅
4. Slash commands ✅
5. Mode system ✅
6. Agent delegation ✅

Each layer works independently.

### 4. Event-Driven Features

Use hooks for cross-cutting concerns:

- Session naming
- Incremental saves
- Notifications
- Cost tracking

**Benefit:** Features don't bloat core execution path.

### 5. Explicit Configuration

```python
# ✅ Explicit SessionConfig
session_config = SessionConfig(
    config=config,
    search_paths=search_paths,
    verbose=verbose,
    session_id=session_id,
    bundle_name=bundle_name,
    initial_transcript=initial_transcript,
    prepared_bundle=prepared_bundle,
)
```

**Why:** Single struct better than 7 parameters.

## Code Organization

### Module Structure

```
amplifier_app_cli/
├── main.py                    # Entry point, REPL loop
├── session_runner.py          # Session initialization
├── session_spawner.py         # Agent delegation
├── session_store.py           # Session persistence
├── commands/                  # CLI commands
│   ├── run.py
│   ├── session.py
│   ├── bundle.py
│   └── ...
├── ui/                        # Display components
│   ├── error_display.py
│   └── render_message.py
├── lib/                       # Core libraries
│   ├── settings.py
│   ├── bundle_loader.py
│   └── mention_loading.py
└── utils/                     # Utilities
    ├── error_format.py
    └── version.py
```

**Philosophy:**
- `commands/` - Click command definitions
- `lib/` - Reusable logic (no Click dependencies)
- `ui/` - Display-only (no business logic)
- Top-level - Composition and orchestration

### Dependency Flow

```
Click commands → session_runner → amplifier-core
            ↓
       lib/ modules → amplifier-foundation
            ↓
       ui/ modules → Rich console
```

**No circular dependencies.** Clean layering.

## Performance Considerations

### Module Activation Caching

**Problem:** Downloading and installing modules on every run is slow.

**Solution:** `prepare()` saves install state:

```python
prepared = await bundle.prepare()  # First run: downloads/installs
# Creates ~/.amplifier/cache/ with activated modules

prepared = await bundle.prepare()  # Subsequent: instant (cached)
```

### Session Store Optimization

**Problem:** Loading large transcripts is slow.

**Solution:** Lazy metadata loading:

```python
# Fast: Load only metadata
sessions = store.list_sessions(limit=20)

# Slow: Load full transcript only when needed
transcript, metadata = store.load(session_id)
```

## Testing Strategies

### Agent Override Pattern

Test agent changes without committing:

```bash
export AMPLIFIER_AGENT_ZEN_ARCHITECT=~/test-zen.md
amplifier run "design system"
```

**Use case:** Iterate on agent instructions during development.

### Mock Provider Pattern

Test without API calls:

```python
test_config = {
    "providers": [{
        "module": "provider-mock",
        "config": {"responses": ["Test response"]}
    }]
}
```

### Session Replay

Debug issues by replaying sessions:

```bash
amplifier continue --replay --replay-speed 1.0
```

## Common Patterns from CLI Code

### 1. First-Run Detection

```python
# Check if settings.yaml exists
def check_first_run():
    return not (Path.home() / ".amplifier" / "settings.yaml").exists()
```

### 2. Safe Error Display

```python
# Never crash on display errors
try:
    console.print(Markdown(response))
except Exception:
    console.print(response)  # Fallback to plain text
```

### 3. Project-Scoped Storage

```python
# Sessions stored per-project
project_slug = get_project_slug()  # Derived from cwd
session_dir = Path.home() / ".amplifier" / "projects" / project_slug / "sessions"
```

### 4. Configuration Layering

```
Foundation bundle → User settings → CLI flags → Session overrides
(mechanisms)        (policy)        (runtime)    (temporary)
```

## Extension Points

### Adding New Commands

```python
# In commands/new_command.py
@click.group()
def my_command():
    """My command description."""
    pass

@my_command.command()
def subcommand():
    """Subcommand."""
    pass

# In main.py
cli.add_command(my_command)
```

### Adding New Slash Commands

```python
# In main.py - CommandProcessor
COMMANDS["/new"] = {
    "action": "handle_new",
    "description": "New command description"
}

async def handle_command(self, action, data):
    if action == "handle_new":
        return await self._handle_new(data)
```

### Adding New Output Formats

```python
# In commands/run.py
@click.option(
    "--output-format",
    type=click.Choice(["text", "json", "json-trace", "yaml"]),  # Add yaml
)

# In main.py - execute_single
if output_format == "yaml":
    import yaml
    print(yaml.dump({"response": response, ...}))
```

## Related Documentation

- **[Agent Delegation Implementation](https://github.com/microsoft/amplifier-app-cli/blob/main/docs/AGENT_DELEGATION_IMPLEMENTATION.md)** - Complete agent delegation details
- **[amplifier-foundation](https://github.com/microsoft/amplifier-foundation)** - Bundle system
- **[amplifier-core](https://github.com/microsoft/amplifier-core)** - Kernel contracts
- **[CLI Reference](../../user_guide/cli.md)** - User-facing documentation

## Key Takeaways

1. **Composition over configuration** - Bundle system enables flexible capability assembly
2. **Separation of concerns** - Mechanism (kernel/foundation) vs policy (app)
3. **Unified code paths** - Single implementation for all modes prevents drift
4. **Progressive enhancement** - Base experience works, features add value
5. **Event-driven extensibility** - Hooks enable features without coupling
6. **Explicit over implicit** - Clear data structures better than magic
7. **Graceful degradation** - Fallbacks ensure reliability

The CLI demonstrates how to build production applications on Amplifier's foundation while maintaining simplicity and extensibility.
