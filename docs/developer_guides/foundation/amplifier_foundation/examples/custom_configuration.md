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
            "source": "git+https://github.com/microsoft/amplifier-module-loop-streaming@main",
        }
    },
    hooks=[
        {
            "module": "hooks-streaming-ui",  # Hook to display streaming output
            "source": "git+https://github.com/microsoft/amplifier-module-hooks-streaming-ui@main",
        }
    ],
)

composed = foundation.compose(provider).compose(streaming_config)
```

**What changed**:
- Swapped orchestrator from `loop-basic` to `loop-streaming`
- Added `hooks-streaming-ui` to display streaming output

**Result**: See responses appear word-by-word in real-time!

Learn more: [Orchestrator modules](/modules/orchestrators/)

## Key Concepts

### Composition is Additive

Each `.compose()` call adds or overrides configuration:

```python
foundation           # Has orchestrator, context manager
  .compose(provider) # Adds LLM provider
  .compose(tools)    # Adds tool capabilities
  .compose(streaming) # Swaps orchestrator to streaming
```

Later bundles override earlier ones when they define the same keys.

### Module Sources

Every module needs a `source` - where to download it from:

```python
{
    "module": "tool-filesystem",
    "source": "git+https://github.com/microsoft/amplifier-module-tool-filesystem@main"
}
```

Foundation bundle includes sources for common modules, so you often don't need to specify them.

### Configuration via Bundles

Instead of flags and settings, Amplifier uses **composition**:

❌ **Don't**: `session.enable_streaming = True`  
✅ **Do**: Compose a bundle that specifies the streaming orchestrator

This makes configurations:
- Shareable (bundle files)
- Testable (swap in test bundles)
- Composable (mix and match capabilities)

## Complete Example Code

```python
import asyncio
import os
from pathlib import Path

from amplifier_foundation import Bundle, load_bundle

async def basic_agent():
    """A minimal agent with no tools."""
    foundation_path = Path(__file__).parent.parent
    foundation = await load_bundle(str(foundation_path))
    provider = await load_bundle(str(foundation_path / "providers" / "anthropic-sonnet.yaml"))

    composed = foundation.compose(provider)
    prepared = await composed.prepare()
    session = await prepared.create_session()

    async with session:
        response = await session.execute("What tools do you have available?")
        print(f"Response: {response[:200]}...")

async def agent_with_tools():
    """An agent with filesystem and bash capabilities."""
    foundation_path = Path(__file__).parent.parent
    foundation = await load_bundle(str(foundation_path))
    provider = await load_bundle(str(foundation_path / "providers" / "anthropic-sonnet.yaml"))

    # Add tools via composition
    tools_config = Bundle(
        name="tools-config",
        version="1.0.0",
        tools=[
            {
                "module": "tool-filesystem",
                "source": "git+https://github.com/microsoft/amplifier-module-tool-filesystem@main",
            },
            {"module": "tool-bash", "source": "git+https://github.com/microsoft/amplifier-module-tool-bash@main"},
        ],
    )

    composed = foundation.compose(provider).compose(tools_config)
    prepared = await composed.prepare()
    session = await prepared.create_session()

    async with session:
        response = await session.execute("List the files in the current directory and tell me what you find.")
        print(f"Response: {response[:300]}...")

async def streaming_agent():
    """An agent with streaming for real-time responses."""
    foundation_path = Path(__file__).parent.parent
    foundation = await load_bundle(str(foundation_path))
    provider = await load_bundle(str(foundation_path / "providers" / "anthropic-sonnet.yaml"))

    # Configure streaming via session config
    streaming_config = Bundle(
        name="streaming-config",
        version="1.0.0",
        session={
            "orchestrator": {
                "module": "loop-streaming",
                "source": "git+https://github.com/microsoft/amplifier-module-loop-streaming@main",
            }
        },
        hooks=[
            {
                "module": "hooks-streaming-ui",
                "source": "git+https://github.com/microsoft/amplifier-module-hooks-streaming-ui@main",
            }
        ],
    )

    composed = foundation.compose(provider).compose(streaming_config)
    prepared = await composed.prepare()
    session = await prepared.create_session()

    async with session:
        response = await session.execute("Write a short poem about software modularity.")
        print(f"Final response captured: {len(response)} chars")

async def main():
    """Run all examples to showcase configuration patterns."""
    await basic_agent()
    await agent_with_tools()
    await streaming_agent()

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("✖ ERROR: Set ANTHROPIC_API_KEY environment variable")
        exit(1)

    asyncio.run(main())
```

## Expected Output

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

✓ Response: [Lists files using tool-filesystem]...

============================================================
EXAMPLE 3: Streaming Agent (Real-time Responses)
============================================================
⏳ Preparing...

📝 Watch the response stream in real-time:

[Words appear one by one as the poem is generated]

✓ Final response captured: 234 chars

============================================================
📚 WHAT YOU LEARNED:
============================================================
1. Orchestrators: loop-basic (simple) vs loop-streaming (real-time)
2. Tools: Add capabilities by composing tool modules with 'source' field
3. Composition: foundation.compose(provider).compose(tools)

✅ All configuration through composition - no flags, no YAML hell!

💡 Next: Try 03_custom_tool.py to build your own custom tool
```

## Key Takeaways

**Composition over Configuration**:
- No flags to toggle
- No complex YAML configuration
- Just compose bundles with the capabilities you need

**Modules are Swappable**:
- Want streaming? Swap orchestrator
- Want different tools? Compose different tool bundles
- Want different provider? Compose different provider bundle

**First-class Tools**:
- Tools are modules with source URLs
- Downloaded automatically on first use
- Cached for subsequent runs

## Next Steps

- **[Multi-Agent System](multi_agent_system.md)** - Coordinate specialized agents
- **[Common Patterns](../patterns.md)** - More composition patterns
- **[Bundle Guide](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md)** - Create your own bundles
