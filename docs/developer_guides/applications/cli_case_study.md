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
- **Profile system** - Pre-configured capability sets
- **Provider switching** - Easy model/provider changes

All built on amplifier-core using the libraries and following best practices.

## Architecture

```
amplifier-app-cli/
├── CLI Layer (Typer/Click)
│   ├── Command parsing
│   ├── Argument handling
│   └── Help text
│
├── Application Layer
│   ├── Configuration resolution
│   │   └── Uses: amplifier-foundation
│   ├── Profile loading
│   │   └── Uses: amplifier-foundation
│   ├── Module resolution
│   │   └── Uses: amplifier-foundation
│   └── Mount Plan creation
│
├── Display Layer
│   ├── Rich console formatting
│   ├── Markdown rendering
│   ├── Progress indicators
│   └── Error presentation
│
└── Session Layer
    └── Uses: amplifier-core
        ├── Session lifecycle
        ├── Prompt execution
        └── Event handling
```

## Key Components

### 1. Configuration Resolution

**Challenge:** Users can configure Amplifier at three levels:
- User scope: `~/.amplifier/settings.yaml`
- Project scope: `.amplifier/settings.yaml`
- Local scope: `.amplifier/settings.local.yaml`

**Solution:** Use amplifier-foundation for three-scope configuration.

```python
from amplifier_foundation import ConfigManager

config = ConfigManager()

# Automatically merges all three scopes
provider = config.get("provider")  # User can override at any level
api_key = config.get("anthropic.api_key")
```

**Why this works:** amplifier-foundation implements the deep merge semantics, so the CLI doesn't have to.

### 2. Profile System

**Challenge:** Users want pre-configured capability sets (foundation, base, dev) without manually specifying every module.

**Solution:** Use amplifier-foundation for profile loading and compilation.

```python
from amplifier_foundation import load_profile, compile_profile_to_mount_plan

# Load profile (handles inheritance, overlays, @mentions)
profile = load_profile("dev")

# Compile to Mount Plan (what amplifier-core needs)
mount_plan = compile_profile_to_mount_plan(profile)

# Use with amplifier-core
session = AmplifierSession(mount_plan)
```

**Why this works:** Separates user-facing configuration (profiles) from kernel input (mount plans).

### 3. Interactive REPL

**Challenge:** Provide a chat-style interface with command support.

**Solution:** Simple read-eval-print loop with command detection.

```python
async def interactive_mode(session):
    """Interactive chat mode."""
    
    while True:
        try:
            # Get user input
            prompt = prompt_toolkit.prompt("amplifier> ")
            
            # Handle commands
            if prompt.startswith("/"):
                handle_command(prompt)
                continue
            
            # Handle agent mentions
            if prompt.startswith("@"):
                # Delegate to agent (via task tool)
                response = await session.execute(prompt)
            else:
                # Normal execution
                response = await session.execute(prompt)
            
            # Display response
            console.print(Markdown(response.text))
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
```

**Why this works:** Simple loop, delegates all AI logic to amplifier-core.

### 4. Session Persistence

**Challenge:** Users want to resume previous conversations.

**Solution:** Save session state and restore it.

```python
# Save session
session_data = {
    "id": session.id,
    "mount_plan": mount_plan,
    "messages": await session.context.get_messages(),
    "timestamp": datetime.now().isoformat()
}

with open(f"~/.amplifier/sessions/{session.id}.json", "w") as f:
    json.dump(session_data, f)

# Resume session
with open(session_file) as f:
    session_data = json.load(f)

# Create new session with saved mount plan
session = AmplifierSession(session_data["mount_plan"])
await session.initialize()

# Restore messages
for msg in session_data["messages"]:
    await session.context.add_message(msg)
```

**Why this works:** The kernel provides access to context, the CLI decides what to persist.

### 5. Display Formatting

**Challenge:** Make output beautiful and readable.

**Solution:** Use Rich library for formatting, but keep it in the application layer.

```python
from rich.console import Console
from rich.markdown import Markdown

console = Console()

# Kernel returns plain response
response = await session.execute(prompt)

# CLI formats it beautifully
console.print(Markdown(response.text))

# CLI can also show metadata
if verbose:
    console.print(f"[dim]Model: {response.model}[/dim]")
    console.print(f"[dim]Tokens: {response.usage.total_tokens}[/dim]")
```

**Why this works:** Kernel doesn't know about display, CLI owns the presentation.

### 6. Provider Switching

**Challenge:** Users want to easily switch providers/models.

**Solution:** Modify mount plan based on user preferences.

```python
def create_mount_plan(profile_name, provider_override=None):
    """Create mount plan with optional provider override."""
    
    # Load base profile
    profile = load_profile(profile_name)
    mount_plan = compile_profile_to_mount_plan(profile)
    
    # Override provider if specified
    if provider_override:
        mount_plan["providers"] = [
            {
                "module": f"provider-{provider_override}",
                "source": f"git+https://github.com/microsoft/amplifier-module-provider-{provider_override}@main"
            }
        ]
    
    return mount_plan

# Usage
mount_plan = create_mount_plan("dev", provider_override="openai")
```

**Why this works:** Mount plans are just data structures. Applications can modify them.

### 7. Command Handling

**Challenge:** Provide helpful commands like `/help`, `/tools`, `/status`.

**Solution:** Simple command routing in the application layer.

```python
def handle_command(command: str, session: AmplifierSession):
    """Handle REPL commands."""
    
    cmd = command[1:].lower()  # Remove leading /
    
    if cmd == "help":
        show_help()
    elif cmd == "tools":
        tools = session.coordinator.get_mounted("tools")
        for name, tool in tools.items():
            console.print(f"[cyan]{name}[/cyan]: {tool.description}")
    elif cmd == "status":
        console.print(f"Session ID: {session.id}")
        console.print(f"Profile: {current_profile}")
        console.print(f"Provider: {current_provider}")
    elif cmd == "clear":
        await session.context.clear()
        console.print("[green]Context cleared[/green]")
    elif cmd in ["quit", "exit"]:
        return True  # Exit REPL
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
    
    return False
```

**Why this works:** Commands are UI concerns, not kernel concerns.

### 8. Error Handling

**Challenge:** Present errors helpfully to users.

**Solution:** Catch and format errors in the application.

```python
try:
    response = await session.execute(prompt)
    console.print(Markdown(response.text))
    
except ModuleNotFoundError as e:
    console.print(f"[red]Module not found: {e}[/red]")
    console.print("[yellow]Try: amplifier module refresh[/yellow]")
    
except ProviderAuthError as e:
    console.print(f"[red]Authentication failed: {e}[/red]")
    console.print("[yellow]Check your API key: amplifier provider setup[/yellow]")
    
except Exception as e:
    console.print(f"[red]Error: {e}[/red]")
    if debug:
        console.print_exception()
```

**Why this works:** User-friendly error messages are application responsibility.

## Lessons Learned

### 1. Libraries Simplify Application Development

Without amplifier-foundation, amplifier-app-cli would need to implement:
- Profile loading and inheritance
- Three-scope configuration merging
- Module resolution strategies

With amplifier-foundation, this is ~20 lines of code.

### 2. Kernel is Just Session Management

The CLI doesn't talk to LLMs, execute tools, or manage context directly. It just:
1. Creates a mount plan
2. Creates a session
3. Calls `session.execute()`
4. Displays results

Everything else is in modules.

### 3. Mount Plans are Data

Mount plans are just dictionaries. Applications can:
- Load them from profiles
- Modify them dynamically
- Generate them programmatically
- Validate them before use

This flexibility is powerful.

### 4. Events Provide Observability

The CLI subscribes to events for:
- Progress indicators
- Logging
- Approval prompts
- Debug output

Without writing event handlers, it's just a silent execution.

### 5. Separation of Concerns Works

```
User types → CLI parses → App creates mount plan → Kernel executes → App formats → CLI displays
```

Each layer has clear responsibility. No layer reaches across boundaries.

## Code Structure

```python
# cli.py - Entry point
import typer
from amplifier_app_cli.app import Application

app = typer.Typer()

@app.command()
def run(prompt: str, profile: str = "dev"):
    """Execute a single prompt."""
    application = Application(profile)
    asyncio.run(application.run_once(prompt))

@app.command()
def interactive(profile: str = "dev"):
    """Start interactive mode."""
    application = Application(profile)
    asyncio.run(application.run_interactive())

# app.py - Application logic
from amplifier_core import AmplifierSession
from amplifier_foundation import load_profile, compile_profile_to_mount_plan
from amplifier_foundation import ConfigManager

class Application:
    def __init__(self, profile_name: str):
        self.config = ConfigManager()
        self.profile = load_profile(profile_name)
        self.mount_plan = compile_profile_to_mount_plan(self.profile)
        self.session = None
    
    async def initialize(self):
        """Initialize the session."""
        self.session = AmplifierSession(self.mount_plan)
        await self.session.initialize()
    
    async def execute(self, prompt: str) -> str:
        """Execute a prompt."""
        return await self.session.execute(prompt)
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.cleanup()

# display.py - Display logic
from rich.console import Console
from rich.markdown import Markdown

class Display:
    def __init__(self):
        self.console = Console()
    
    def print_response(self, response):
        """Display a response."""
        self.console.print(Markdown(response.text))
    
    def print_error(self, error):
        """Display an error."""
        self.console.print(f"[red]Error: {error}[/red]")
```

## Testing

The CLI is testable because each layer is independent:

```python
# Test application layer
def test_application_initialization():
    app = Application("dev")
    assert app.profile.name == "dev"
    assert "providers" in app.mount_plan

# Test with mock session
async def test_execution():
    app = Application("dev")
    app.session = MockSession()
    
    response = await app.execute("test")
    assert response == "mock response"

# Integration test
async def test_end_to_end():
    app = Application("dev")
    await app.initialize()
    
    response = await app.execute("What is 2+2?")
    assert "4" in response
    
    await app.cleanup()
```

## Comparison: Application vs Module

| Aspect | Application (amplifier-app-cli) | Module (e.g., tool-bash) |
|--------|--------------------------------|-------------------------|
| **Depends on** | amplifier-core + amplifier-foundation | Only amplifier-core |
| **Uses libraries?** | ✅ Yes (amplifier-foundation) | ❌ No |
| **Creates mount plans?** | ✅ Yes | ❌ No |
| **User interaction?** | ✅ Yes (CLI) | ❌ No |
| **Display formatting?** | ✅ Yes (Rich) | ❌ No |
| **Loaded by** | User directly | Kernel at runtime |
| **Versioning** | Can change freely | Must maintain contracts |

## Key Takeaways

1. **Applications use libraries, modules don't** - Clean architectural boundary
2. **Mount plans are configuration** - Applications create them, kernel consumes them
3. **Kernel handles execution, app handles interaction** - Clear separation
4. **Events provide observability** - Subscribe to what you care about
5. **Testing is modular** - Each layer tests independently

## Resources

- **[amplifier-app-cli Repository](https://github.com/microsoft/amplifier-app-cli)** - Full source code
- **[Application Developer Guide](index.md)** - Building your own application
- **[Foundation Guide](../foundation/index.md)** - Understanding the foundation
- **[Architecture Overview](../../architecture/overview.md)** - System architecture

## Next Steps

Now that you understand how a real application is built:

1. **Build your own** - Start with the [Application Guide](index.md)
2. **Extend the CLI** - Fork amplifier-app-cli and customize
3. **Create a web app** - Use the same patterns with a web framework
4. **Build an API** - Expose Amplifier capabilities as a REST API
