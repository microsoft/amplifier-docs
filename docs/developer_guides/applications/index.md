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
┌─────────────────────────────────────────────────────┐
│  Your Application                                   │
│                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   UI Layer  │  │  Config      │  │  Display  │ │
│  │  (CLI/Web)  │  │  Resolution  │  │  Formatter│ │
│  └──────┬──────┘  └──────┬───────┘  └─────┬─────┘ │
│         │                │                │       │
│         └────────────────┴────────────────┘       │
│                          │                        │
│                  ┌───────▼────────┐               │
│                  │ amplifier-     │               │
│                  │ foundation     │               │
│                  │ (Bundle        │               │
│                  │  composition)  │               │
│                  └───────┬────────┘               │
│                          │                        │
│                  ┌───────▼────────┐               │
│                  │ amplifier-core │               │
│                  │ (Session,      │               │
│                  │  Coordinator,  │               │
│                  │  Module loader)│               │
│                  └───────┬────────┘               │
│                          │                        │
│         ┌────────────────┼────────────────┐       │
│         │                │                │       │
│    ┌────▼─────┐  ┌──────▼──────┐  ┌─────▼────┐  │
│    │ Provider │  │   Tools     │  │  Hooks   │  │
│    │ Modules  │  │   Modules   │  │  Modules │  │
│    └──────────┘  └─────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
```

**Your job as an application developer:**

1. **UI Layer** - Capture user input and display results
2. **Configuration** - Use amplifier-foundation to load and compose bundles
3. **Session Management** - Create and manage amplifier-core sessions
4. **Display** - Format and present AI responses to users

## The Application Pattern

### 1. Load and Compose Bundles

Use amplifier-foundation to manage configuration:

```python
from amplifier_foundation import load_bundle

# Load base bundle
foundation = await load_bundle("git+https://github.com/microsoft/amplifier-foundation-bundle@main")

# Load provider
provider = await load_bundle("./providers/anthropic-sonnet.yaml")

# Compose
bundle = foundation.compose(provider)

# Get mount plan for amplifier-core
mount_plan = bundle.to_mount_plan()
```

### 2. Create Session

Use the mount plan to create an amplifier-core session:

```python
from amplifier_core import AmplifierSession

# Create session
session = AmplifierSession(
    config=mount_plan,
    session_id=session_id,  # Optional: for resuming
    parent_id=parent_id,    # Optional: for child sessions
    approval_system=approval_system,  # Optional: app-layer approval
    display_system=display_system,    # Optional: app-layer display
    is_resumed=is_resumed   # Whether resuming existing session
)

# Initialize (loads and mounts modules)
await session.initialize()
```

### 3. Execute Prompts

```python
# Single execution
response = await session.execute("Your prompt here")

# Interactive loop
async with session:
    while True:
        prompt = get_user_input()
        if not prompt:
            break
        response = await session.execute(prompt)
        display_response(response)
```

### 4. Session Lifecycle

```python
# Context manager handles cleanup
async with session:
    # Session is initialized and ready
    response = await session.execute(prompt)
    # Session cleanup happens automatically

# Or manual cleanup
try:
    await session.initialize()
    response = await session.execute(prompt)
finally:
    await session.cleanup()
```

## Key Application Responsibilities

### Configuration Resolution

**Your app decides:**
- Which bundles to load (foundation, provider, tools)
- How to compose them (order, overrides)
- Where config files are stored
- How users select profiles/providers

**Example: Profile-based config**

```python
async def load_profile(profile_name: str) -> Bundle:
    """Load user's profile bundle."""
    profile_path = Path(f"~/.myapp/profiles/{profile_name}.md").expanduser()
    return await load_bundle(str(profile_path))

# User selects profile
profile = await load_profile("development")
composed = foundation.compose(profile)
```

### Session Management

**Your app manages:**
- Creating new sessions
- Resuming previous sessions
- Session storage location
- Session metadata (working directory, project context)

**Example: Session directory structure**

```python
def get_session_dir(session_id: str) -> Path:
    """Get session storage directory."""
    project_slug = get_project_slug(os.getcwd())
    return Path(f"~/.myapp/projects/{project_slug}/sessions/{session_id}").expanduser()

# Create or resume
if resume_id:
    session_dir = get_session_dir(resume_id)
    # Load metadata, pass to AmplifierSession
else:
    session_id = str(uuid.uuid4())
    session_dir = get_session_dir(session_id)
    session_dir.mkdir(parents=True, exist_ok=True)
```

### Display and Formatting

**Your app controls:**
- How responses are formatted
- Streaming vs. batch display
- Error presentation
- Progress indicators

**Example: Display system**

```python
class MyDisplaySystem:
    """Custom display for my app."""
    
    async def show_response(self, response: str):
        """Display AI response."""
        # Format with your app's style
        formatted = format_markdown(response)
        print(formatted)
    
    async def show_error(self, error: Exception):
        """Display error."""
        print(f"Error: {error}", file=sys.stderr)
    
    async def show_progress(self, message: str):
        """Show progress indicator."""
        print(f"⏳ {message}")
```

### Module Resolution

**Your app provides:**
- Module source resolver (maps module IDs to sources)
- Cache location for downloaded modules
- Update policy (when to check for updates)

**Example: Module source resolver**

```python
from amplifier_foundation import SimpleSourceResolver

# Configure module sources
resolver = SimpleSourceResolver(
    cache_dir=Path("~/.myapp/modules").expanduser(),
    sources={
        "tool-filesystem": "git+https://github.com/microsoft/amplifier-module-tool-filesystem@main",
        "tool-bash": "git+https://github.com/microsoft/amplifier-module-tool-bash@main",
        # ... more modules
    }
)

# Mount resolver before session initialization
await session.coordinator.mount("source-resolver", resolver)
```

## Integration Points

### 1. Bundle System (amplifier-foundation)

**What it provides:**
- Bundle loading and composition
- Module configuration merging
- @mention resolution
- Source resolution

**How you use it:**
```python
from amplifier_foundation import load_bundle, BundleRegistry

registry = BundleRegistry()
bundle = await registry.load("foundation")
mount_plan = bundle.to_mount_plan()
```

### 2. Session System (amplifier-core)

**What it provides:**
- Module lifecycle management
- Orchestrator and context managers
- Event system and hooks
- Provider abstraction

**How you use it:**
```python
from amplifier_core import AmplifierSession

session = AmplifierSession(config=mount_plan)
await session.initialize()
response = await session.execute(prompt)
```

### 3. Your App Layer

**What you provide:**
- User interface (CLI, web, API)
- Configuration policy (where configs live, defaults)
- Session storage (where sessions persist)
- Display formatting (how to present results)

## Real-World Example: CLI Application

See [CLI Case Study](cli_case_study.md) for a detailed walkthrough of how amplifier-app-cli is built.

**Key takeaways:**

- **Thin application layer** - Let foundation and core do the heavy lifting
- **Clear separation** - UI, config, session, display are distinct concerns
- **Composition over configuration** - Build bundles, don't write config files
- **Protocol boundary** - Your app speaks mount plans to core

## Common Patterns

### Pattern: Profile Management

```python
class ProfileManager:
    """Manage user profiles."""
    
    def __init__(self, profiles_dir: Path):
        self.profiles_dir = profiles_dir
    
    async def list_profiles(self) -> list[str]:
        """List available profiles."""
        return [p.stem for p in self.profiles_dir.glob("*.md")]
    
    async def load_profile(self, name: str) -> Bundle:
        """Load profile bundle."""
        path = self.profiles_dir / f"{name}.md"
        return await load_bundle(str(path))
    
    async def save_profile(self, name: str, bundle: Bundle):
        """Save profile bundle."""
        path = self.profiles_dir / f"{name}.md"
        # Serialize and save bundle
```

### Pattern: Session Resumption

```python
async def create_or_resume_session(
    mount_plan: dict,
    session_id: str | None = None
) -> AmplifierSession:
    """Create new session or resume existing."""
    
    if session_id:
        # Load session metadata
        metadata = load_session_metadata(session_id)
        
        # Create session with resume flag
        session = AmplifierSession(
            config=mount_plan,
            session_id=session_id,
            is_resumed=True
        )
    else:
        # Create new session
        session = AmplifierSession(
            config=mount_plan,
            session_id=str(uuid.uuid4())
        )
    
    await session.initialize()
    return session
```

### Pattern: Event Handling

```python
class MyEventHandler:
    """Handle session events."""
    
    async def on_tool_call(self, event: dict):
        """Called when tool is executed."""
        tool_name = event.get("tool_name")
        print(f"🔧 Using tool: {tool_name}")
    
    async def on_error(self, event: dict):
        """Called on error."""
        error = event.get("error")
        print(f"❌ Error: {error}")

# Register handler as hook module
await session.coordinator.mount("hooks", handler, name="my-event-handler")
```

## Next Steps

- **[CLI Case Study](cli_case_study.md)** - Deep dive into amplifier-app-cli
- **[Bundle System](../foundation/amplifier_foundation/bundle_system.md)** - Understanding bundles
- **[Module Contracts](/developer/index.md)** - Building custom modules

## Resources

- **amplifier-core** - Session and module system
- **amplifier-foundation** - Bundle composition layer
- **amplifier-app-cli** - Reference implementation
