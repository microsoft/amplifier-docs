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

**Challenge:** Merge user settings, project config, bundle config, and command-line flags

**Solution:** Layered configuration with clear precedence:

```python
from amplifier_foundation import resolve_config

# Layer 1: User settings (~/.amplifier/config.yaml)
user_config = load_user_settings()

# Layer 2: Project config (.amplifier/config.yaml)
project_config = load_project_config()

# Layer 3: Bundle config (if specified)
bundle_config = load_bundle(bundle_name) if bundle_name else {}

# Layer 4: CLI flags (highest priority)
cli_overrides = {
    "providers": [{"module": provider, "config": {"model": model}}]
} if model else {}

# Merge with clear precedence
final_config = resolve_config(
    base=user_config,
    project=project_config,
    bundle=bundle_config,
    overrides=cli_overrides
)
```

**Key Files:**
- `effective_config.py` - Configuration resolution and merging

### 2. Session Initialization

**Challenge:** Set up amplifier-core session with all dependencies

**Solution:** `create_initialized_session()` centralized setup:

```python
from amplifier_app_cli.session_runner import create_initialized_session, SessionConfig

# Create session config
session_config = SessionConfig(
    config=mount_plan,
    search_paths=module_search_paths,
    verbose=verbose,
    session_id=session_id,
    bundle_name=bundle_name,
    initial_transcript=transcript,  # For resume
    prepared_bundle=prepared_bundle  # For bundle mode
)

# Initialize session (handles all setup)
initialized = await create_initialized_session(session_config, console)
session = initialized.session
session_id = initialized.session_id

# Use session
response = await session.execute(prompt)

# Cleanup
await initialized.cleanup()
```

**What it handles:**
- Session creation with amplifier-core
- Module loading and mounting
- Bundle preparation (if applicable)
- Transcript restoration (for resume)
- Approval/display system injection
- Cleanup function registration

**Key Files:**
- `session_runner.py` - Session initialization logic

### 3. Agent Delegation

**Challenge:** Enable agents to spawn sub-agents with config overlays

**Solution:** Session spawning with inheritance:

```python
from amplifier_app_cli.session_spawner import spawn_sub_session

# Spawn child session with agent overlay
result = await spawn_sub_session(
    agent_name="zen-architect",
    instruction="Design authentication system",
    parent_session=parent_session,
    agent_configs=agent_configs,
    tool_inheritance={"exclude_tools": ["tool-task"]},  # Prevent recursion
    provider_preferences=[  # Override model selection
        {"provider": "anthropic", "model": "claude-haiku-*"}
    ]
)

# Returns: {"output": str, "session_id": str}
```

**Features:**
- Configuration merging (parent + agent overlay)
- Tool/hook inheritance filtering
- Provider preference overrides
- State persistence for multi-turn
- Working directory inheritance

**Key Files:**
- `session_spawner.py` - Agent delegation implementation
- See [AGENT_DELEGATION_IMPLEMENTATION.md](https://github.com/microsoft/amplifier-app-cli/blob/main/docs/AGENT_DELEGATION_IMPLEMENTATION.md)

### 4. Interactive REPL

**Challenge:** Provide smooth interactive experience with history, editing, cancellation

**Solution:** `interactive_chat()` with prompt_toolkit integration:

```python
from amplifier_app_cli.main import interactive_chat

# Interactive session
await interactive_chat(
    config=mount_plan,
    search_paths=module_search_paths,
    verbose=verbose,
    bundle_name=bundle_name,
    prepared_bundle=prepared_bundle,
    initial_prompt="Start task",  # Optional auto-execution
    initial_transcript=transcript  # For resume
)
```

**Features:**
- Persistent history (project-scoped)
- Multi-line input (Ctrl-J)
- Ctrl+C cancellation (graceful/immediate)
- Command processing (`/help`, `/mode`, `/config`)
- Dynamic mode indicators
- Session state persistence

**Key Files:**
- `main.py` - `interactive_chat()`, `CommandProcessor`

### 5. Session Persistence

**Challenge:** Save/restore session state across runs

**Solution:** `SessionStore` for project-scoped storage:

```python
from amplifier_app_cli.session_store import SessionStore
from pathlib import Path

store = SessionStore()  # Uses ~/.amplifier/projects/{project-slug}/sessions/

# Save session
context = session.coordinator.get("context")
messages = await context.get_messages()
metadata = {
    "session_id": session_id,
    "created": datetime.now(UTC).isoformat(),
    "bundle": bundle_name,
    "model": model_name,
    "turn_count": len([m for m in messages if m.get("role") == "user"]),
    "working_dir": str(Path.cwd().resolve())
}
store.save(session_id, messages, metadata)

# Resume session
if store.exists(session_id):
    transcript, metadata = store.load(session_id)
```

**Storage Location:**
```
~/.amplifier/projects/{project-slug}/sessions/{session-id}/
├── transcript.jsonl     # Conversation history
├── events.jsonl         # Complete event log
└── metadata.json        # Session metadata
```

**Key Files:**
- `session_store.py` - Storage implementation
- `project_utils.py` - Project slug generation

### 6. Bundle Integration

**Challenge:** Support bundles for pre-configured setups

**Solution:** amplifier-foundation bundle system:

```python
from amplifier_foundation.bundle import prepare_bundle

# Prepare bundle (resolves modules, agents, context)
prepared = await prepare_bundle(
    bundle_path=bundle_path,
    resolver=module_resolver
)

# Use with session
await interactive_chat(
    config=prepared.config,  # Fully resolved mount plan
    prepared_bundle=prepared,  # For module resolution
    bundle_name=bundle_name
)
```

**What bundles provide:**
- Pre-configured modules (providers, tools, hooks)
- Agent definitions
- Context files (system instructions, examples)
- Module source mappings

**Key Files:**
- `paths.py` - Bundle path resolution
- `lib/bundle_loader.py` - Bundle integration

### 7. Error Display

**Challenge:** Present errors clearly to users

**Solution:** Structured error display with Rich:

```python
from amplifier_app_cli.ui.error_display import display_llm_error, display_validation_error

try:
    response = await session.execute(prompt)
except LLMError as e:
    display_llm_error(console, e, verbose=verbose)
except ModuleValidationError as e:
    display_validation_error(console, e, verbose=verbose)
```

**Features:**
- Structured error panels
- Context-specific guidance
- Verbose mode for debugging
- LLM error details (status, headers)

**Key Files:**
- `ui/error_display.py` - Error display logic

## Patterns and Practices

### Pattern 1: Unified Entry Points

Both single-shot and interactive modes use same core functions:

```python
# Single-shot
await execute_single(
    prompt=prompt,
    config=config,
    ...
)

# Interactive
await interactive_chat(
    config=config,
    initial_prompt=prompt,  # Optional
    ...
)
```

**Benefit:** Shared logic, consistent behavior, easier maintenance

### Pattern 2: Session Reuse

Resume functionality reuses initialization:

```python
# New session
initialized = await create_initialized_session(session_config, console)

# Resumed session (same code path)
session_config.initial_transcript = transcript
initialized = await create_initialized_session(session_config, console)
```

**Benefit:** Single code path, consistent behavior, less duplication

### Pattern 3: Capability Injection

Infrastructure capabilities injected via coordinator:

```python
# Register working directory capability (for tools)
session.coordinator.register_capability("session.working_dir", working_dir)

# Register spawning capabilities (for delegation)
session.coordinator.register_capability("session.spawn", spawn_capability)

# Tools and modules use capabilities
working_dir = coordinator.get_capability("session.working_dir")
```

**Benefit:** Loose coupling, testable, flexible

### Pattern 4: Graceful Degradation

Features gracefully degrade when unavailable:

```python
# Optional mode system
discovery = session.coordinator.session_state.get("mode_discovery")
if discovery:
    modes = discovery.list_modes()
else:
    # Mode system not available - continue without it
    pass
```

**Benefit:** Partial functionality better than crashes

### Pattern 5: Event-Driven Hooks

Hooks observe lifecycle without tight coupling:

```python
# Hooks register for events
hooks.register("tool:pre", approval_hook)
hooks.register("prompt:complete", notification_hook)

# CLI emits events
await hooks.emit("prompt:complete", {
    "prompt": prompt,
    "response": response,
    "session_id": session_id
})
```

**Benefit:** Extensibility without modifying core code

## Testing Strategy

### Unit Tests

Test components in isolation:

```python
def test_config_merge():
    """Test configuration merging logic."""
    base = {"providers": [{"module": "a"}]}
    overlay = {"tools": [{"module": "b"}]}
    result = merge_configs(base, overlay)
    assert result["providers"] == [{"module": "a"}]
    assert result["tools"] == [{"module": "b"}]
```

### Integration Tests

Test component interactions:

```python
async def test_session_creation():
    """Test session initialization flow."""
    config = create_test_config()
    session_config = SessionConfig(config=config, ...)
    initialized = await create_initialized_session(session_config, console)
    assert initialized.session is not None
    await initialized.cleanup()
```

### End-to-End Tests

Test full workflows:

```python
async def test_single_execution():
    """Test single-shot execution."""
    result = await execute_single(
        prompt="test prompt",
        config=test_config,
        ...
    )
    assert result
```

## Related Documentation

- [AGENT_DELEGATION_IMPLEMENTATION.md](https://github.com/microsoft/amplifier-app-cli/blob/main/docs/AGENT_DELEGATION_IMPLEMENTATION.md) - Agent delegation details
- [amplifier-foundation](https://github.com/microsoft/amplifier-foundation) - Foundation library
- [amplifier-core](https://github.com/microsoft/amplifier-core) - Core kernel

## Lessons Learned

### Do's

- **Centralize setup** - `create_initialized_session()` pattern
- **Reuse code paths** - Single functions for new/resume
- **Use capabilities** - Loose coupling via coordinator
- **Graceful degradation** - Features optional, not required
- **Event-driven hooks** - Extensibility without tight coupling

### Don'ts

- **Duplicate setup logic** - Leads to divergence
- **Tight coupling** - Hard to test and extend
- **Silent failures** - User-facing errors need clear messages
- **Blocking operations** - Use async throughout
- **Global state** - Pass dependencies explicitly

## Conclusion

amplifier-app-cli demonstrates how to build a full-featured application on amplifier-core while maintaining simplicity and extensibility. Key takeaways:

1. **Centralize initialization** - Single source of truth for setup
2. **Reuse code paths** - Same logic for new/resume sessions
3. **Use capabilities** - Loose coupling via coordinator
4. **Graceful degradation** - Optional features don't break core functionality
5. **Clear error display** - Help users understand and fix issues

These patterns apply to any application built on Amplifier.
