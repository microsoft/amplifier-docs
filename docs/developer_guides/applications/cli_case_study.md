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

**Challenge:** Users need flexible configuration (global defaults, project-specific, runtime overrides).

**Solution:** Multi-scope configuration via amplifier-foundation's Bundle system:

```python
# runtime/config.py
def resolve_config(bundle_name: str, app_settings: AppSettings, console) -> tuple:
    """Resolve configuration from bundle."""
    # Load bundle
    bundle = await load_bundle(bundle_uri)
    
    # Apply settings overrides (provider, tools, etc.)
    # from local/project/global scopes
    
    # Prepare bundle (download modules)
    prepared = await bundle.prepare()
    
    return config_data, prepared
```

**Key insight**: Configuration flows from bundles, not hardcoded settings. Settings override specific bundle sections.

### 2. Provider Management

**Challenge:** Users want to switch providers without editing configuration files.

**Solution:** ProviderManager with three-scope configuration:

```python
# provider_manager.py
class ProviderManager:
    def use_provider(self, provider_id: str, scope: ScopeType, config: dict):
        """Configure provider at specified scope (local/project/global)."""
        # Build provider entry with high priority
        config_with_priority = {**config, "priority": 1}
        provider_entry = {"module": provider_id, "config": config_with_priority}
        
        # Update settings at scope
        self._settings.set_provider_override(provider_entry, scope)
```

**Commands**:
```bash
amplifier provider use anthropic --model claude-sonnet-4-5 --local
amplifier provider use openai --global
amplifier provider current
```

### 3. Session Storage

**Challenge:** Persist conversations across runs, support resume.

**Solution:** SessionStore with project-scoped storage:

```python
# session_store.py
class SessionStore:
    """Project-scoped session persistence."""
    
    def save(self, session_id: str, transcript: list, metadata: dict):
        """Save session to ~/.amplifier/projects/{project}/sessions/{id}/"""
        
    def load(self, session_id: str) -> tuple[list, dict]:
        """Load transcript and metadata."""
        
    def find_session(self, partial_id: str) -> str:
        """Find session by partial ID match."""
```

**Storage structure**:
```
~/.amplifier/projects/my-project/sessions/
├── abc123-def456/
│   ├── events.jsonl       # Full event log
│   ├── transcript.json    # Messages only
│   └── metadata.json      # Bundle, provider, timestamp
└── xyz789-uvw012/
    └── ...
```

### 4. Interactive Mode

**Challenge:** REPL with slash commands for control.

**Solution:** Slash command processor integrated into chat loop:

```python
# Interactive loop with slash commands
while True:
    user_input = prompt("> ")
    
    # Handle slash commands
    if user_input.startswith("/"):
        if user_input == "/think":
            enable_plan_mode()  # Read-only
        elif user_input == "/do":
            disable_plan_mode()  # Re-enable writes
        elif user_input.startswith("/save"):
            save_transcript(user_input)
        # ... more commands
        continue
    
    # Execute normal prompt
    response = await session.execute(user_input)
    display(response)
```

**Available commands**: `/think`, `/do`, `/save`, `/clear`, `/status`, `/tools`, `/config`, `/help`, `/stop`

### 5. Bundle System Integration

**Challenge:** Users want pre-configured capability sets.

**Solution:** Bundle-based configuration with registry:

```python
# Bundle usage
async def run(bundle: str, prompt: str):
    # Default to foundation
    if not bundle:
        bundle = "foundation"
    
    # Resolve and prepare bundle
    config_data, prepared_bundle = resolve_config(
        bundle_name=bundle,
        app_settings=app_settings,
        console=console,
    )
    
    # Create session from prepared bundle
    session = await prepared_bundle.create_session()
```

**Commands**:
```bash
amplifier bundle use my-bundle --local
amplifier bundle current
amplifier run --bundle dev "prompt"
```

### 6. Runtime Overrides

**Challenge:** Override provider/model without changing configuration.

**Solution:** CLI flags with priority system:

```python
# commands/run.py
@click.option("--provider", "-p", help="LLM provider to use")
@click.option("--model", "-m", help="Model to use")
@click.option("--max-tokens", type=int, help="Maximum output tokens")
def run(provider: str, model: str, max_tokens: int, ...):
    # Apply runtime overrides to config_data
    if provider:
        # Set priority=0 (highest) for specified provider
        for entry in config_data["providers"]:
            if entry["module"] == provider_module:
                entry["config"]["priority"] = 0
                if model:
                    entry["config"]["default_model"] = model
```

**Usage**:
```bash
amplifier run -p anthropic "prompt"
amplifier run -m claude-sonnet-4-5 "prompt"
amplifier run -p openai -m gpt-5.2 --max-tokens 1000 "prompt"
```

### 7. Context Loading (@Mentions)

**Challenge:** Load context files referenced in prompts.

**Solution:** @mention system integrated at application layer:

```python
# Detect @mentions in user input
mentions = parse_mentions(user_input)

# Load mentioned files
for mention in mentions:
    content = await load_file(mention)
    # Add as context message BEFORE user message
    context.add_message("user", f"<context_file paths=\"{mention}\">\n{content}\n</context_file>")

# Then add user message with @mention preserved
context.add_message("user", user_input)
```

**Supported syntax**:
- `@AGENTS.md` - Current directory
- `@foundation:context/file.md` - Bundle resource
- `@~/path/to/file.md` - User home directory
- `./relative/path.md` - Relative to source

## Design Patterns

### 1. Protocol Boundary Pattern

**Keep kernel simple, add features at app layer:**

```python
# ✓ App layer handles @mentions
user_input = "Analyze @AGENTS.md"
mentions = parse_mentions(user_input)  # App-layer parsing
for file in mentions:
    context.add_message("user", load_file(file))  # Use kernel API

# ✗ Don't add @mention handling to kernel
# Kernel provides add_message() API, app decides when/how to use it
```

### 2. Thin Configuration Pattern

**Bundles provide configuration, not business logic:**

```yaml
# ✓ Bundle specifies modules and config
bundle:
  name: my-app
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5

# ✗ Don't put app logic in bundles
# App layer handles provider selection, runtime overrides, etc.
```

### 3. Three-Scope Configuration

**Local > Project > Global priority:**

```python
# Settings merge with precedence
settings = merge_settings([
    local_settings,      # Highest priority (.amplifier/settings.yaml)
    project_settings,    # (.amplifier/settings.yaml in repo root)
    global_settings,     # (~/.amplifier/settings.yaml)
])
```

### 4. Session Persistence Pattern

**Project-scoped sessions:**

```python
# Sessions stored under project directory
session_dir = Path.cwd() / ".amplifier" / "sessions" / session_id

# Enables:
# - Resume by project context
# - Multiple developers don't conflict
# - Git can ignore session data
```

## Anti-Patterns to Avoid

### ❌ Don't Put Business Logic in Bundles

Bundles are configuration, not code:

```python
# ✗ Wrong: Business logic in bundle
bundle.validate_user_input = lambda x: x.strip()

# ✓ Right: App layer handles logic
user_input = user_input.strip()
session.execute(user_input)
```

### ❌ Don't Modify Kernel for App Features

Use kernel APIs, don't extend kernel:

```python
# ✗ Wrong: Add custom kernel method
session.execute_with_context_files(prompt, files)

# ✓ Right: Use existing kernel APIs
for file in files:
    session.context.add_message("user", load_file(file))
session.execute(prompt)
```

### ❌ Don't Hardcode Module Sources

Use bundle composition:

```python
# ✗ Wrong: Hardcoded in app
mount_plan = {
    "providers": [{"module": "provider-anthropic", "source": "git+https://..."}]
}

# ✓ Right: From bundle
bundle = await load_bundle("foundation")
mount_plan = bundle.to_mount_plan()
```

## Key Takeaways

**Separation of Concerns**:
- Kernel: Session lifecycle, module loading, coordination
- Foundation: Bundle composition, utilities
- App: Configuration resolution, UX, persistence

**Configuration Flows Through Bundles**:
- Default from foundation bundle
- Override via settings (local/project/global)
- Override via CLI flags (highest priority)

**App Layer is Policy**:
- When to process @mentions
- How to store sessions
- Which provider to use by default
- Interactive vs single-shot mode

**Kernel Provides Mechanism**:
- `session.execute()` - Execute prompts
- `context.add_message()` - Add messages
- Module loading and lifecycle
- Provider abstraction

## Further Reading

**CLI-Specific Documentation**:
- [Interactive Mode](https://github.com/microsoft/amplifier-app-cli/blob/main/docs/INTERACTIVE_MODE.md) - Slash commands and REPL
- [Context Loading](https://github.com/microsoft/amplifier-app-cli/blob/main/docs/CONTEXT_LOADING.md) - @mention system
- [Agent Delegation](https://github.com/microsoft/amplifier-app-cli/blob/main/docs/AGENT_DELEGATION_IMPLEMENTATION.md) - Sub-session spawning

**Foundation Documentation**:
- [Bundle Guide](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md) - Creating bundles
- [Concepts](../foundation/amplifier_foundation/concepts.md) - Mental models
- [Patterns](../foundation/amplifier_foundation/patterns.md) - Common patterns

**Core Documentation**:
- [Architecture](/architecture/) - Kernel design
- [Modules](/modules/) - Available modules
