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

Layered configuration with clear precedence:

1. **User settings** (`~/.amplifier/config.yaml`) — base defaults
2. **Project config** (`.amplifier/config.yaml`) — project-level overrides
3. **Bundle config** (if a bundle is specified) — bundle-provided settings
4. **CLI flags** (highest priority) — explicit command-line overrides

See `effective_config.py` for the implementation details.

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
    tool_inheritance={"exclude_tools": ["tool-task"]},  # Prevent recursion
    provider_preferences=[  # Override model selection
        {"provider": "anthropic", "model": "claude-haiku-*"}
    ]
)

# Returns: {"response": str, "session_id": str}
```

**Features:**
- Configuration merging (parent + agent overlay)
- Tool inheritance filtering (allowlist or blocklist)
- Provider preference overrides
- State persistence for multi-turn
- Working directory inheritance

**Key Files:**
- `session_spawner.py` - Agent delegation implementation
- See [AGENT_DELEGATION_IMPLEMENTATION.md](https://github.com/microsoft/amplifier-app-cli/blob/main/docs/AGENT_DELEGATION_IMPLEMENTATION.md)

#### Spawn Tool Policy

Bundles control which tools spawned agents inherit using the `spawn` section:

```yaml
# In bundle.md
spawn:
  exclude_tools: [tool-task]  # Agents inherit all tools EXCEPT these
  # OR
  tools: [tool-a, tool-b]     # Agents get ONLY these tools
```

**Common pattern** — prevent delegation recursion by excluding `tool-task`:

```yaml
tools:
  - module: tool-task      # Coordinator can delegate
  - module: tool-filesystem
  - module: tool-bash

spawn:
  exclude_tools: [tool-task]  # But agents can't delegate further
```

Default behavior: if no `spawn` section, agents inherit all parent tools.

#### Multi-Turn Sub-Session Resumption

Sub-sessions support multi-turn conversations through automatic state persistence. When a sub-session completes, its state (transcript and configuration) is saved to persistent storage, enabling the parent session to resume the conversation across multiple turns.

##### State Persistence

The system automatically persists sub-session state after each execution:

```python
# After sub-session execution, before cleanup
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

**Storage Location**: `~/.amplifier/projects/{project-slug}/sessions/{session-id}/`
- `transcript.jsonl` - Conversation history
- `metadata.json` - Session configuration and metadata
- `bundle.md` - Bundle snapshot (if applicable)

##### Resuming Existing Sessions

Resume a previous sub-session by providing its `session_id`:

```python
from amplifier_app_cli.session_spawner import resume_sub_session

# Resume by session ID
result = await resume_sub_session(
    sub_session_id="parent-123-zen-architect-abc456",
    instruction="Now add OAuth 2.0 support"
)
# Returns: {"output": str, "session_id": str}
```

**Resume Process**:
1. Load transcript and metadata from `SessionStore`
2. Recreate `AmplifierSession` with stored configuration
3. Restore transcript to context via `add_message()`
4. Execute new instruction with full conversation history
5. Save updated state
6. Cleanup and return

**Key Design Points**:
- **Stateless**: Each resume loads fresh from disk (no in-memory caching)
- **Deterministic**: Uses stored merged config (independent of parent changes)
- **Self-contained**: All state needed for reconstruction persists with session
- **Resumable**: Survives parent session restarts and crashes

##### Multi-Turn Example

```python
# Turn 1: Initial delegation
response1 = await task_tool.execute({
    "agent": "zen-architect",
    "instruction": "Design a caching system"
})
session_id = response1["session_id"]  # Save for later

# Turn 2: Resume with refinement
response2 = await task_tool.execute({
    "session_id": session_id,
    "instruction": "Add TTL support to the cache"
})

# Turn 3: Continue iteration
response3 = await task_tool.execute({
    "session_id": session_id,
    "instruction": "Add eviction policies"
})

# Each turn builds on previous context
```

##### Error Handling

**Missing Session**:
```python
# Attempting to resume non-existent session
try:
    await resume_sub_session("fake-id", "test")
except FileNotFoundError as e:
    print(f"Session not found: {e}")
    # Error: "Sub-session 'fake-id' not found. Session may have expired..."
```

**Corrupted Metadata**:
```python
# If metadata.json is corrupted
try:
    await resume_sub_session("corrupted-id", "test")
except RuntimeError as e:
    print(f"Session corrupted: {e}")
    # Error: "Corrupted session metadata for 'corrupted-id'..."
```

**Observability**: Resume operations emit `session:resume` events for monitoring and debugging.

#### Provider Preferences

Control which provider/model a spawned agent uses via `provider_preferences`:

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
- See [amplifier-foundation](https://github.com/microsoft/amplifier-foundation) for `ProviderPreference` details

#### Model Role Override

The `model_role` parameter lets the caller override the agent's default model role for a specific delegation:

```python
# Via task tool
result = tool_execute({
    "agent": "foundation:explorer",
    "instruction": "Analyze these UI screenshots",
    "model_role": "vision"
})
```

**Precedence** (highest to lowest):

1. `provider_preferences` on the delegation call — explicit provider/model pinning
2. `model_role` on the delegation call — semantic role override
3. Agent frontmatter `model_role` — the agent's own declared preference
4. No preference — session default (resolved from the `general` role)

If both `model_role` and `provider_preferences` are provided in the same call, `provider_preferences` wins.

**Available roles**:

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

**Task tool input schema:**
```python
{
    "agent": str,          # Optional - required for spawn, not needed for resume
    "instruction": str,     # Required - task for agent to execute
    "session_id": str,     # Optional - when provided, triggers resume instead of spawn
    "model_role": str,     # Optional - semantic role override (e.g., "coding", "fast")
    "provider_preferences": list,  # Optional - ordered fallback chain for provider/model
}
```

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
    session_id=None,  # Optional - generated if not provided
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
- Command processing (`/help`, `/mode`, `/config`, `/rename`, `/fork`, `/skills`, `/skill`)
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
├── metadata.json        # Session metadata
└── bundle.md            # Bundle snapshot (if applicable)
```

**Key Files:**
- `session_store.py` - Storage implementation
- `project_utils.py` - Project slug generation

### 6. Bundle Integration

**Challenge:** Support bundles for pre-configured setups

**Solution:** amplifier-foundation bundle system:

```python
from amplifier_foundation import load_bundle

# Load and prepare bundle (resolves modules, agents, context)
bundle = await load_bundle(bundle_path)
prepared = await bundle.prepare()

# Use with session
await interactive_chat(
    config=prepared.mount_plan,  # Fully resolved mount plan
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
