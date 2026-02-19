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

**Challenge:** Users can configure Amplifier at three levels:
- User scope: `~/.amplifier/settings.yaml`
- Project scope: `.amplifier/settings.yaml`
- Local scope: `.amplifier/settings.local.yaml`

**Solution:** Use amplifier-foundation for three-scope configuration. amplifier-foundation implements the deep merge semantics internally, so the CLI doesn't have to manually merge scopes.

**Why this works:** amplifier-foundation implements the deep merge semantics, so the CLI doesn't have to.

### 2. Bundle System

**Challenge:** Users want pre-configured capability sets (foundation, base, dev) without manually specifying every module.

**Solution:** Use amplifier-foundation for bundle loading and session creation.

```python
from amplifier_foundation.bundle import PreparedBundle

# Load and prepare bundle (handles inheritance, @mentions, module resolution)
prepared_bundle = await PreparedBundle.prepare("dev")

# Create session (foundation handles all setup internally)
session = await prepared_bundle.create_session(
    session_id=session_id,
    approval_system=approval_system,
    display_system=display_system,
)
```

**Why this works:** Separates user-facing configuration (bundles) from kernel input (mount plans).

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

**Solution:** Save session state atomically and restore it.

```python
from amplifier_app_cli.session_store import SessionStore

# Save session (atomic write with backup)
# Saves to: ~/.amplifier/projects/{project-slug}/sessions/{session-id}/
#   - transcript.jsonl  (conversation history, one JSON object per line)
#   - metadata.json     (session config, bundle, model, turn count)
store = SessionStore()
messages = await context.get_messages()
metadata = {
    "session_id": actual_session_id,
    "bundle": bundle_name,
    "model": model_name,
    "turn_count": len([m for m in messages if m.get("role") == "user"]),
    "working_dir": str(Path.cwd().resolve()),
}
store.save(actual_session_id, messages, metadata)

# Resume session
store = SessionStore()
transcript, metadata = store.load(session_id)

# Create new session with saved bundle name
prepared_bundle = await PreparedBundle.prepare(metadata["bundle"])
session = await prepared_bundle.create_session(session_id=session_id, ...)

# Restore transcript to context
context = session.coordinator.get("context")
await context.set_messages(transcript)
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

**Solution:** Use priority-based provider configuration via `ProviderManager`.

```python
from amplifier_app_cli.provider_manager import ProviderManager

# Configure provider at a scope (local/project/global)
# Priority 1 ensures this provider wins over bundle defaults (priority 100)
manager = ProviderManager(config)
manager.use_provider(
    "provider-openai",
    scope="global",
    config={"default_model": "gpt-4o", "priority": 1},
)

# Or override provider for a specific sub-session spawn
# In session_spawner.py: promotes provider to priority 0
merged_config = _apply_provider_override(
    config, provider_id="openai", model="gpt-4o"
)
```

**Why this works:** Mount plans use a priority system — lower numbers mean higher precedence. Applications control priority to override bundle defaults.

### 7. Command Handling

**Challenge:** Provide helpful commands like `/help`, `/tools`, `/status`.

**Solution:** Simple command routing in the application layer via `CommandProcessor`.

```python
class CommandProcessor:
    """Process slash commands and special directives."""

    COMMANDS = {
        "/mode":         "Set or toggle a mode (e.g., /mode plan)",
        "/modes":        "List available modes",
        "/save":         "Save conversation transcript",
        "/status":       "Show session status",
        "/clear":        "Clear conversation context",
        "/help":         "Show available commands",
        "/config":       "Show current configuration",
        "/tools":        "List available tools",
        "/agents":       "List available agents",
        "/allowed-dirs": "Manage allowed write directories",
        "/denied-dirs":  "Manage denied write directories",
        "/rename":       "Rename current session",
        "/fork":         "Fork session at turn N: /fork [turn]",
    }

    def process_input(self, user_input: str) -> tuple[str, dict]:
        """Process user input and extract commands."""
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            if command in self.COMMANDS:
                return self.COMMANDS[command]["action"], {"args": args}
            return "unknown_command", {"command": command}
        return "prompt", {"text": user_input}
```

**Why this works:** Commands are UI concerns, not kernel concerns. Mode shortcuts (e.g., `/plan` as an alias for `/mode plan`) are populated dynamically from bundle mode definitions.

### 8. Output Formats

**Challenge:** Automation tools, CI/CD pipelines, and evaluation platforms need structured output.

**Solution:** Support three output formats via `--output-format` flag on `amplifier run`.

```python
async def execute_single(prompt, config, ..., output_format="text"):
    """Execute a single prompt with configurable output format."""

    # In JSON modes, redirect Rich console output to stderr
    # so stdout carries only clean JSON
    if output_format in ["json", "json-trace"]:
        sys.stdout = sys.stderr
        console.file = sys.stderr

    response = await session.execute(prompt)

    if output_format == "json":
        # Response + session metadata
        output = {
            "status": "success",
            "response": response,
            "session_id": actual_session_id,
            "bundle": bundle_name,
            "model": model_name,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    elif output_format == "json-trace":
        # Adds execution_trace: all tool calls with timing and arguments
        # Adds metadata: total_tool_calls, total_agents_invoked, duration_ms
        output = {**base_output, "execution_trace": trace_collector.get_trace()}
    else:
        # Default text: render markdown to console
        console.print(Markdown(response))
```

**Usage:**
```bash
amplifier run "analyze this code"                        # text (human)
amplifier run --output-format json "analyze this code"   # JSON for scripts
amplifier run --output-format json-trace "..."           # full trace for evals
```

**Why this works:** stdout carries only the structured data; all diagnostics, hook output, and progress indicators go to stderr. Downstream tools can pipe cleanly.

### 9. Error Handling

**Challenge:** Present errors helpfully to users.

**Solution:** Catch and format errors in the application.

```python
try:
    response = await session.execute(prompt)
    console.print(Markdown(response.text))
    
except ModuleValidationError as e:
    display_validation_error(console, e, verbose=verbose)
    
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
- Bundle loading and inheritance
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
- Load them from bundles
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
# main.py - Entry point
import click
from amplifier_app_cli.utils.help_formatter import AmplifierGroup

@click.group(cls=AmplifierGroup, invoke_without_command=True)
@click.version_option(version=get_version(), prog_name="amplifier")
@click.pass_context
def cli(ctx, install_completion):
    """Amplifier - AI-powered modular development platform."""
    # Default: launch interactive chat
    if ctx.invoked_subcommand is None:
        ctx.invoke(_run_command, prompt=None, bundle=None, mode="chat")

# Commands registered as groups and standalone commands
cli.add_command(bundle_group)    # amplifier bundle ...
cli.add_command(provider_group)  # amplifier provider ...
cli.add_command(agents_group)    # amplifier agent list/show
cli.add_command(session_group)   # amplifier session list/resume
cli.add_command(tool_group)      # amplifier tool ...
cli.add_command(module_group)    # amplifier module ...
# (also: init, update, version, reset, notify, source, allowed_dirs, denied_dirs)

# session_runner.py - Unified session initialization
from amplifier_core import AmplifierSession
from amplifier_foundation.bundle import PreparedBundle

async def create_initialized_session(config: SessionConfig, console) -> InitializedSession:
    """Single entry point for all session creation.
    Handles: provider auto-install, bundle loading, resume, capability registration.
    """
    session = await _create_bundle_session(config, ...)
    register_mention_handling(session)
    register_session_spawning(session)
    return InitializedSession(session=session, session_id=session_id, ...)

# session_spawner.py - Agent delegation
async def spawn_sub_session(agent_name, instruction, parent_session, ...) -> dict:
    """Create child session with agent config overlay.
    Returns: {"output": str, "session_id": str, "status": str, "turn_count": int}
    """
    merged_config = merge_configs(parent_session.config, agent_config)
    child_session = AmplifierSession(config=merged_config, parent_id=parent_session.session_id)
    await child_session.initialize()
    response = await child_session.execute(instruction)
    return {"output": response, "session_id": sub_session_id, ...}

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
