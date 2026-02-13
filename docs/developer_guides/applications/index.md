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
│         │                │                 │       │
│         └────────────────┼─────────────────┘       │
│                          │                         │
│                          ▼                         │
│                   ┌─────────────┐                  │
│                   │ Mount Plan  │                  │
│                   │  Creation   │                  │
│                   └──────┬──────┘                  │
└──────────────────────────┼──────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  amplifier-foundation  │ (Optional)
              └────────────┬───────────┘
                           │
                           ▼
                 ┌──────────────────┐
                 │ amplifier-core   │
                 │                  │
                 │  • Session       │
                 │  • Coordinator   │
                 │  • Module Loader │
                 │  • Events        │
                 └──────────────────┘
```

## Core Responsibilities

As an application developer, you are responsible for:

### 1. Creating Mount Plans

The kernel doesn't know what to load - you tell it via the Mount Plan.

```python
mount_plan = {
    "session": {
        "orchestrator": "loop-streaming",  # You choose
        "context": "context-persistent"     # You choose
    },
    "providers": [
        {
            "module": "provider-anthropic",
            "source": "git+https://github.com/...",
            "config": {
                "default_model": "claude-sonnet-4-5"
            }
        }
    ],
    "tools": [
        {"module": "tool-filesystem"},
        {"module": "tool-bash"}
    ],
    "hooks": [
        {"module": "hook-logging", "config": {...}}
    ]
}
```

### 2. Managing Session Lifecycle

You control when sessions start, execute, and clean up.

```python
from amplifier_core import AmplifierSession

# Create session
session = AmplifierSession(mount_plan)

# Initialize (loads modules)
await session.initialize()

# Execute prompts
response = await session.execute("Your prompt here")

# Clean up
await session.cleanup()
```

Or use async context manager:

```python
async with AmplifierSession(mount_plan) as session:
    response = await session.execute("Your prompt")
    # Auto cleanup when context exits
```

### 3. Handling User Interaction

The kernel doesn't know about CLI, web, or GUI. You decide.

```python
# CLI example
while True:
    prompt = input("> ")
    if prompt == "/quit":
        break
    response = await session.execute(prompt)
    print(response)

# Web API example
@app.post("/chat")
async def chat(request: ChatRequest):
    response = await session.execute(request.message)
    return {"response": response}

# GUI example
def on_submit(prompt):
    response = await session.execute(prompt)
    text_area.insert(response)
```

### 4. Using Libraries (Optional but Recommended)

Libraries are **application concerns**, not kernel concerns. Use them to simplify your application.

```python
# Use amplifier-foundation for profile management
from amplifier_foundation import load_profile, compile_profile_to_mount_plan

profile = load_profile("dev")
mount_plan = compile_profile_to_mount_plan(profile)

# Use amplifier-foundation for configuration
from amplifier_foundation import ConfigManager

config = ConfigManager()
api_key = config.get("anthropic.api_key")
```

**Important:** Runtime modules (providers, tools, etc.) never use libraries. Only applications do.

## Step-by-Step: Building Your First Application

Let's build a minimal AI chat application.

### Step 1: Set Up Your Project

```bash
mkdir my-amplifier-app
cd my-amplifier-app

# Create virtual environment
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
uv pip install amplifier-core
```

### Step 2: Create a Mount Plan

```python
# app.py
import asyncio
from amplifier_core import AmplifierSession

mount_plan = {
    "session": {
        "orchestrator": "loop-basic",
        "context": "context-simple"
    },
    "providers": [
        {
            "module": "provider-anthropic",
            "source": "git+https://github.com/microsoft/amplifier-module-provider-anthropic@main",
            "config": {
                "api_key": "your-api-key-here"  # Or use env var
            }
        }
    ],
    "tools": []  # No tools for now
}
```

### Step 3: Create a Simple REPL

```python
async def main():
    async with AmplifierSession(mount_plan) as session:
        print("Welcome to My AI App!")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                prompt = input("> ")
                
                if prompt.lower() in ["quit", "exit"]:
                    break
                
                if not prompt.strip():
                    continue
                
                response = await session.execute(prompt)
                print(f"\n{response}\n")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 4: Run It

```bash
python app.py
```

Congratulations! You've built an application on amplifier-core.

## Advanced Topics

### Using amplifier-foundation

Instead of hardcoding the mount plan, use profiles:

```python
from amplifier_foundation import load_profile, compile_profile_to_mount_plan

# Load a profile
profile = load_profile("dev")  # Looks in standard locations

# Compile to mount plan
mount_plan = compile_profile_to_mount_plan(profile)

# Use with session
async with AmplifierSession(mount_plan) as session:
    ...
```

### Handling Events

Subscribe to events for observability:

```python
async def on_tool_call(event_name, data):
    print(f"Tool called: {data['tool_name']}")

# During session initialization
session = AmplifierSession(mount_plan)
await session.initialize()

# Register event handler
session.coordinator.hooks.register("tool:pre", on_tool_call)

# Now execute
await session.execute("List files")
```

### Custom Display Formatting

The kernel returns raw responses. You format them:

```python
response = await session.execute(prompt)

# Simple text
print(response.text)

# With metadata
print(f"Model: {response.model}")
print(f"Tokens: {response.usage.total_tokens}")
print(f"Content: {response.text}")

# JSON output (for APIs)
return {
    "response": response.text,
    "model": response.model,
    "tokens": response.usage.total_tokens
}
```

### Error Handling

Handle errors gracefully in your application:

```python
try:
    response = await session.execute(prompt)
except ModuleLoadError as e:
    print(f"Failed to load module: {e}")
    # Show helpful message to user
except ProviderError as e:
    print(f"Provider error: {e}")
    # Maybe retry or switch providers
except Exception as e:
    print(f"Unexpected error: {e}")
    # Log and recover
```

## Case Study: How amplifier-app-cli Works

Want to understand a real application? See [CLI Application Case Study](cli_case_study.md) for a walkthrough of how amplifier-app-cli is built on amplifier-core.

## Best Practices

### 1. Validate Mount Plans Early

```python
from amplifier_core import validate_mount_plan

errors = validate_mount_plan(mount_plan)
if errors:
    print(f"Invalid mount plan: {errors}")
    exit(1)
```

### 2. Use Environment Variables for Secrets

```python
import os

mount_plan = {
    "providers": [
        {
            "module": "provider-anthropic",
            "config": {
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            }
        }
    ]
}
```

### 3. Implement Graceful Shutdown

```python
async def main():
    session = AmplifierSession(mount_plan)
    await session.initialize()
    
    try:
        # Your application logic
        ...
    finally:
        # Always cleanup
        await session.cleanup()
```

### 4. Log Events for Debugging

```python
async def log_all_events(event_name, data):
    logger.debug(f"Event: {event_name}", extra=data)

session.coordinator.hooks.register("*", log_all_events)
```

### 5. Separate UI from Business Logic

```python
# Good: Separated
class Application:
    def __init__(self, mount_plan):
        self.session = AmplifierSession(mount_plan)
    
    async def execute(self, prompt):
        return await self.session.execute(prompt)

class CLI:
    def __init__(self, app):
        self.app = app
    
    async def run(self):
        while True:
            prompt = input("> ")
            response = await self.app.execute(prompt)
            print(response)
```

## Resources

- **[Foundation Developer Guide](../foundation/index.md)** - Understanding amplifier-core and libraries
- **[Architecture Overview](../../architecture/overview.md)** - System architecture
- **[Module Developer Guide](../../developer/index.md)** - Creating extensions
- **[CLI Case Study](cli_case_study.md)** - Real-world application example

## Next Steps

<div class="grid">

<div class="card">
<h3><a href="cli_case_study/">CLI App Case Study</a></h3>
<p>Deep dive into how amplifier-app-cli is built. Learn from a production application.</p>
</div>

<div class="card">
<h3><a href="../foundation/">Foundation Guide</a></h3>
<p>Understand the foundation components and how to use them.</p>
</div>

<div class="card">
<h3><a href="../../architecture/">Architecture</a></h3>
<p>Deep dive into the architecture and design philosophy.</p>
</div>

</div>
