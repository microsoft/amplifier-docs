---
title: Application Developer Guide
description: Building applications on top of amplifier-core
---

# Application Developer Guide

Learn how to build applications on top of amplifier-core, like amplifier-app-cli does.

## What is an Application?

An **application** in the Amplifier ecosystem is any program that uses amplifier-core to provide an interface for AI interactions. Applications control:

- **User interaction** (CLI, web UI, GUI, API, etc.)
- **Configuration** (which profiles, providers, tools to load)
- **Mount Plan creation** (what gets loaded when)
- **Display and formatting** (how to present results)

### Examples of Applications

| Application | Interface | Purpose |
|-------------|-----------|---------|
| **amplifier-app-cli** | Command-line REPL | Interactive development, scripting |
| **your-app** | CLI, web, API, GUI | Your specific use case |

## Architecture: How Applications Work

```
┌─────────────────────────────────────────────────────────┐
│  Your Application                                   │
│                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   UI Layer  │  │  Config      │  │  Display  │ │
│  │  (CLI/Web)  │  │  Resolution  │  │  Formatter│ │
│  └──────┬──────┘  └──────┬───────┘  └─────┬─────┘ │
│         │                │                │       │
│         └────────────────┼────────────────┘       │
│                          │                        │
│                          ▼                        │
│               ┌─────────────────────┐             │
│               │  AmplifierSession   │             │
│               │  (amplifier-core)   │             │
│               └──────────┬──────────┘             │
└──────────────────────────┼──────────────────────────┘
                           │
                           ▼
        ┌────────────────────────────────┐
        │  Modules (Providers, Tools,    │
        │  Orchestrators, Contexts...)   │
        └────────────────────────────────┘
```

**Key points**:
- Application layer is policy (what to load, how to display)
- Kernel layer is mechanism (session management, module loading)
- Modules are swappable implementations (compete at edges)

## Building an Application

### 1. Create Mount Plan

Define which modules to load:

```python
from amplifier_core import AmplifierSession

config = {
    "session": {
        "orchestrator": "loop-basic",
        "context": "context-simple"
    },
    "providers": [
        {"module": "provider-anthropic"}
    ],
    "tools": [
        {"module": "tool-filesystem"},
        {"module": "tool-bash"}
    ]
}
```

### 2. Create Session

Initialize with configuration:

```python
session = AmplifierSession(
    config=config,
    session_id=None,           # Auto-generated if None
    parent_id=None,            # None for top-level, UUID for child
    approval_system=None,      # App-layer approval policy
    display_system=None,       # App-layer display policy
    is_resumed=False           # True if resuming existing session
)
```

**Session Parameters**:
- `config`: Required mount plan (orchestrator and context must be specified)
- `session_id`: Optional explicit ID (generates UUID if None)
- `parent_id`: Optional parent session ID for child sessions (forking)
- `approval_system`: Optional approval policy (app-layer UX)
- `display_system`: Optional display policy (app-layer UX)
- `is_resumed`: Whether session is resumed (controls event emission)

### 3. Initialize and Execute

Run the session:

```python
# With context manager (recommended)
async with AmplifierSession(config) as session:
    response = await session.execute("List files in current directory")
    print(response)

# Or manually
session = AmplifierSession(config)
await session.initialize()
response = await session.execute(prompt)
await session.cleanup()
```

## Session Lifecycle

Sessions have distinct states tracked in `SessionStatus`:

| State | Description |
|-------|-------------|
| `created` | Session initialized but not yet executed |
| `running` | Currently executing a prompt |
| `completed` | Execution finished successfully |
| `failed` | Execution encountered an error |
| `cancelled` | User cancelled execution |

The kernel emits lifecycle events:
- `session:start` - New session begins
- `session:resume` - Session resumed
- `session:fork` - Child session created
- `session:end` - Session cleanup

## Configuration Resolution

Applications resolve configuration from multiple sources:

1. **User settings** (~/.amplifier/settings.yaml)
2. **Profile configuration** (profiles define module sets)
3. **Bundle configuration** (bundles are shareable configs)
4. **Command-line overrides** (--provider, --model flags)

Example from amplifier-app-cli:

```python
# Load user settings
settings = load_settings()

# Resolve profile
profile = settings.get_profile(profile_name)

# Merge with bundle config
config = merge_configs(profile, bundle_config)

# Apply CLI overrides
if provider_override:
    config["providers"] = [{"module": provider_override}]
```

## Child Sessions (Forking)

Applications can spawn child sessions for agent delegation:

```python
# Create child session with parent linkage
child_session = AmplifierSession(
    config=child_config,
    session_id="generated-child-id",
    parent_id=parent_session.session_id,  # Links to parent
    approval_system=parent_session.coordinator.approval_system,
    display_system=parent_session.coordinator.display_system
)
```

**Key features**:
- `parent_id` establishes parent-child relationship
- Kernel emits `session:fork` event with lineage
- Child sessions inherit UX systems (approval, display)
- Enables hierarchical agent delegation patterns

**W3C Trace Context pattern**:
- Root session ID becomes the `trace_id`
- All child sessions inherit the same `trace_id`
- Enables distributed tracing across agent hierarchies

## Approval System Integration

Applications provide approval policies:

```python
from amplifier_core.interfaces import ApprovalProvider, ApprovalRequest, ApprovalResponse

class MyApprovalSystem(ApprovalProvider):
    async def request_approval(self, request: ApprovalRequest) -> ApprovalResponse:
        # Show approval dialog to user
        approved = show_dialog(request.action, request.risk_level)
        return ApprovalResponse(approved=approved)

# Inject into session
session = AmplifierSession(
    config=config,
    approval_system=MyApprovalSystem()
)
```

The kernel provides the mechanism (ApprovalProvider protocol), applications provide the policy (how to show dialogs, cache decisions).

## Display System Integration

Applications control output formatting:

```python
class MyDisplaySystem:
    def show_status(self, message: str):
        """Show status message to user."""
        print(f"[STATUS] {message}")
    
    def show_result(self, result: str):
        """Show final result to user."""
        print(f"\n{result}\n")

# Inject into session
session = AmplifierSession(
    config=config,
    display_system=MyDisplaySystem()
)
```

## Event Handling

Applications can hook into lifecycle events:

```python
from amplifier_core.hooks import HookResult

async def my_event_handler(event: str, data: dict) -> HookResult:
    if event == "tool:pre":
        print(f"About to execute tool: {data['tool_name']}")
    return HookResult(action="continue")

# Register during module mounting
coordinator.hooks.register("tool:pre", my_event_handler)
```

## Best Practices

### Configuration Management

- **Validate early**: Check required fields before session creation
- **Provide defaults**: Sensible defaults for optional fields
- **Layer configs**: User settings → profile → bundle → CLI overrides
- **Document options**: Clear documentation for all config options

### Error Handling

```python
try:
    async with AmplifierSession(config) as session:
        response = await session.execute(prompt)
except ValueError as e:
    # Config validation error
    print(f"Configuration error: {e}")
except RuntimeError as e:
    # Module mounting error
    print(f"Module error: {e}")
except Exception as e:
    # Execution error
    print(f"Execution error: {e}")
```

### Session Management

- **Use context managers**: Ensures cleanup happens
- **Track session IDs**: Enable session resumption
- **Handle cancellation**: Graceful Ctrl+C handling
- **Clean up resources**: Always call session.cleanup()

### Module Loading

```python
from amplifier_core.loader import ModuleLoader

# Create loader with coordinator for resolver injection
loader = ModuleLoader(coordinator=session.coordinator)

# Load modules from mount plan
for provider_config in config["providers"]:
    mount_fn = await loader.load(
        module_id=provider_config["module"],
        config=provider_config.get("config"),
        coordinator=session.coordinator
    )
    await loader.initialize(mount_fn, session.coordinator)
```

## The Rust Kernel

amplifier-core is implemented in Rust with Python bindings via PyO3:

- **Same API**: Python code requires zero changes
- **Same imports**: `from amplifier_core import AmplifierSession`
- **Backward compatible**: Existing applications work without modification

The Rust kernel provides:
- Type-safe session management
- Fast event dispatch
- Efficient hook processing
- Cancellation primitives

## Example: Minimal Application

```python
import asyncio
from amplifier_core import AmplifierSession

async def main():
    config = {
        "session": {
            "orchestrator": "loop-basic",
            "context": "context-simple"
        },
        "providers": [{"module": "provider-anthropic"}],
        "tools": [{"module": "tool-filesystem"}]
    }
    
    async with AmplifierSession(config) as session:
        response = await session.execute("List files in current directory")
        print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## See Also

- [Session Lifecycle](../../user_guide/sessions.md) - Session management guide
- [Module Contracts](../contracts/index.md) - Module interfaces
- [Mount Plan Specification](../specs/mount-plan.md) - Configuration format
- [Hooks API](../hooks-api.md) - Event system reference
