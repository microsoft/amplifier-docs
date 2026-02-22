---
title: Hello World Example
description: Your first Amplifier agent in ~15 lines of code
---

# Hello World Example

The simplest possible amplifier-foundation application - load bundles, compose them, and execute a prompt.

## What This Example Demonstrates

- **Bundle Loading**: Load foundation and provider bundles from sources
- **Composition**: Layer bundles to build your configuration
- **Preparation**: Automatic module downloading and caching
- **Session Creation**: Creating a ready-to-use agent session
- **Execution**: Running prompts through the configured agent

**Time to Complete**: 2 minutes  
**Complexity**: ⭐ Beginner

## Running the Example

```bash
# Clone the repository
git clone https://github.com/microsoft/amplifier-foundation
cd amplifier-foundation

# Set your API key
export ANTHROPIC_API_KEY='your-key-here'

# Run the example
uv run python examples/01_hello_world.py
```

[:material-github: View Full Source Code](https://github.com/microsoft/amplifier-foundation/blob/main/examples/01_hello_world.py){ .md-button }

## How It Works

### 1. Load the Foundation Bundle

```python
foundation = await load_bundle(str(foundation_path))
```

The **foundation bundle** provides the base configuration:
- Orchestrator (controls execution flow)
- Context manager (handles conversation memory)
- Hooks (observability points)
- Base system instruction

Learn more: [What is a Bundle?](../concepts.md)

### 2. Load a Provider Bundle

```python
provider = await load_bundle(str(provider_path / "anthropic-sonnet.yaml"))
```

The **provider bundle** adds the LLM backend:
- Which model to use (Claude Sonnet 4.5)
- API configuration
- Module source (where to download the provider module)

Learn more: [Provider modules](/modules/providers/)

### 3. Compose Bundles

```python
composed = foundation.compose(provider)
```

**Composition** merges the configurations - later bundles override earlier ones. This gives you:
- Orchestrator from foundation
- Context manager from foundation
- Provider from provider bundle
- Complete configuration ready for execution

Learn more: [Composition](../concepts.md#composition)

### 4. Prepare for Execution

```python
prepared = await composed.prepare()
```

**Preparation** does the heavy lifting:
- Resolves module sources (git URLs)
- Downloads modules if not cached (~30s first time)
- Validates module structure
- Returns a PreparedBundle ready for session creation

Subsequent runs use the cache and are much faster.

Learn more: [Prepared Bundle](../concepts.md#prepared-bundle)

### 5. Create Session

```python
session = await prepared.create_session(session_cwd=Path.cwd())
```

**Session** is your interface to the AI agent:
- Pass `session_cwd` to set working directory for file operations
- Critical for server deployments where `Path.cwd()` isn't the user's project

### 6. Execute a Prompt

```python
async with session:
    response = await session.execute("Your prompt here")
    print(response)
```

The session manages:
- Conversation context
- Tool execution
- Provider routing
- Response streaming (if configured)

## Complete Code

```python
import asyncio
import os
from pathlib import Path

from amplifier_foundation import load_bundle

async def main():
    """The simplest possible Amplifier agent."""

    # Step 1: Load the foundation bundle
    foundation_path = Path(__file__).parent.parent
    foundation = await load_bundle(str(foundation_path))
    print(f"✓ Loaded foundation: {foundation.name} v{foundation.version}")

    # Step 2: Load a provider bundle
    provider_path = foundation_path / "providers" / "anthropic-sonnet.yaml"
    provider = await load_bundle(str(provider_path))
    print(f"✓ Loaded provider: {provider.name}")

    # Step 3: Compose foundation + provider
    composed = foundation.compose(provider)
    print("✓ Composed bundles")

    # Step 4: Prepare (resolves and downloads modules if needed)
    print("⏳ Preparing (downloading modules if needed, this may take 30s first time)...")
    prepared = await composed.prepare()
    print("✓ Modules prepared")

    # Step 5: Create session
    print("⏳ Creating session...")
    session = await prepared.create_session(session_cwd=Path.cwd())
    print("✓ Session ready")

    # Step 6: Execute a prompt
    async with session:
        response = await session.execute(
            "Write a Python function to check if a number is prime. Include docstring and type hints."
        )
        print(f"\nResponse:\n{response}")

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("✖ ERROR: Set ANTHROPIC_API_KEY environment variable")
        exit(1)

    asyncio.run(main())
```

## Expected Output

```
🚀 Amplifier Hello World

✓ Loaded foundation: foundation v1.0.0
✓ Loaded provider: anthropic-sonnet
✓ Composed bundles
⏳ Preparing (downloading modules if needed, this may take 30s first time)...
✓ Modules prepared
⏳ Creating session...
✓ Session ready

Response:
[AI-generated prime checking function with docstring and type hints]

✅ That's it! You just ran your first AI agent.

💡 Next: Try 02_custom_configuration.py to see different configurations
```

## Key Takeaways

**Bundle composition is powerful**:
- Foundation provides base functionality
- Provider adds the LLM
- You can add tools, hooks, agents through more composition

**First run takes time**:
- Module downloads happen once
- Cached for subsequent runs
- Uses `uv` for dependency management

**Session is the interface**:
- Create from PreparedBundle
- Execute prompts via `session.execute()`
- Context maintained across turns

## Next Steps

Try these examples to learn more:

- **[Custom Configuration](custom_configuration.md)** - Add tools and enable streaming
- **[Multi-Agent System](multi_agent_system.md)** - Coordinate specialized agents

Or explore concepts:

- [What is a Bundle?](../concepts.md#what-is-a-bundle)
- [Composition Rules](../concepts.md#composition)
- [Common Patterns](../patterns.md)
