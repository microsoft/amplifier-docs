---
title: Custom Configuration Example
description: Tailoring agents via composition
---

# Custom Configuration Example

Learn how to customize your agent by composing different capabilities - adding tools, enabling streaming, and swapping orchestrators.

## What This Example Demonstrates

- **Adding Tools**: Compose tools into your agent for filesystem and bash access
- **Streaming**: Swap orchestrators to enable real-time response streaming
- **Composition Patterns**: Build customized agents by layering bundles
- **Module Sources**: Specify where to download modules from

**Time to Complete**: 5 minutes  
**Complexity**: ⭐ Beginner

## Running the Example

```bash
# Clone the repository
git clone https://github.com/microsoft/amplifier-foundation
cd amplifier-foundation

# Set your API key
export ANTHROPIC_API_KEY='your-key-here'

# Run the example (shows 3 different configurations)
uv run python examples/02_custom_configuration.py
```

[:material-github: View Full Source Code](https://github.com/microsoft/amplifier-foundation/blob/main/examples/02_custom_configuration.py){ .md-button }

## How It Works

This example shows **three progressive configurations**:

### 1. Basic Agent (No Tools)

```python
composed = foundation.compose(provider)
```

Just foundation + provider = minimal agent with no tools.

**Result**: Agent can answer questions but cannot execute tools.

### 2. Agent with Tools

```python
tools_config = Bundle(
    name="tools-config",
    tools=[
        {"module": "tool-filesystem", "source": "git+https://..."},
        {"module": "tool-bash", "source": "git+https://..."}
    ]
)

composed = foundation.compose(provider).compose(tools_config)
```

**Composition chain**: foundation → provider → tools

**Result**: Agent can now read/write files and execute bash commands.

Learn more: [Tool modules](/modules/tools/)

### 3. Streaming Agent

```python
streaming_config = Bundle(
    name="streaming-config",
    session={
        "orchestrator": {
            "module": "loop-streaming",  # Streaming orchestrator!
            "source": "git+https://..."
        }
    },
    hooks=[
        {
            "module": "hooks-streaming-ui",  # Hook to display streaming output
            "source": "git+https://..."
        }
    ]
)

composed = foundation.compose(provider).compose(streaming_config)
```

**Composition chain**: foundation → provider → streaming

**Result**: Responses stream in real-time as the model generates them.

Learn more: [Orchestrator modules](/modules/orchestrators/)

## Key Concepts

### Composition Over Configuration

```python
# Want different behavior? Compose different modules!
basic = foundation.compose(provider)
with_tools = foundation.compose(provider).compose(tools_config)
streaming = foundation.compose(provider).compose(streaming_config)
```

**No flags to toggle, no YAML configuration files** - just compose the capabilities you need.

### Module Sources

Modules can come from:

- **Git URLs**: `git+https://github.com/org/repo@main`
- **Local paths**: `./modules/my-module`
- **Git subdirectories**: `git+https://github.com/org/repo@main#subdirectory=modules/foo`

### Session Configuration

The `session` section controls:

- **Orchestrator**: How the agent loop runs (`loop-basic`, `loop-streaming`)
- **Context**: How conversation history is managed

### Adding Capabilities

Each capability type has its own section:

- `providers`: LLM backends
- `tools`: Agent capabilities
- `hooks`: Lifecycle hooks for UI, logging, etc.

## Example Output

When you run the example, you'll see:

```
🎨 Amplifier Configuration Showcase
============================================================

KEY CONCEPT: Composition over Configuration
- Want different behavior? Swap modules, don't toggle flags
- Each module is independently testable and upgradeable
- Compose your perfect agent from building blocks

============================================================
EXAMPLE 1: Basic Agent (No Tools)
============================================================
⏳ Preparing...
📝 Asking: What tools do you have available?

✓ Response: I don't have any tools available...

============================================================
EXAMPLE 2: Agent with Tools (Filesystem + Bash)
============================================================
⏳ Preparing (downloading tool modules, may take 30s first time)...
📝 Asking: List files in current directory

✓ Response: I can see several files in the current directory...

============================================================
EXAMPLE 3: Streaming Agent (Real-time Responses)
============================================================
Key: Swap orchestrator from 'loop-basic' to 'loop-streaming'
⏳ Preparing...

📝 Watch the response stream in real-time:

[Response streams word-by-word here...]

✓ Final response captured: 450 chars
```

## Next Steps

- **Custom Tools**: Create your own tool modules - [Tool Contract](/developer/contracts/tool.md)
- **Multi-Agent Systems**: Coordinate specialized agents - [Multi-Agent Example](multi_agent_system.md)
- **Production Apps**: Build complete applications - [Application Guide](/developer_guides/applications/index.md)

## Learn More

- [Bundle System Deep Dive](../bundle_system.md) - How composition works
- [Common Patterns](../patterns.md) - More composition patterns
- [Module Types](/modules/) - All available module types
