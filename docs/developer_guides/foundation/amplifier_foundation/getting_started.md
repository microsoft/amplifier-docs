---
title: Getting Started with amplifier-foundation
description: Installation and your first bundle-based application
---

# Getting Started with amplifier-foundation

Get your first bundle-based Amplifier application running in minutes.

## Installation

```bash
pip install git+https://github.com/microsoft/amplifier-foundation
```

## Hello World

The simplest possible amplifier-foundation application:

```python
import asyncio
import os
from pathlib import Path

from amplifier_foundation import load_bundle

async def main():
    # Step 1: Load the foundation bundle
    foundation_path = Path(__file__).parent.parent  # -> amplifier-foundation/
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
        print("✖ Set ANTHROPIC_API_KEY environment variable")
        exit(1)

    asyncio.run(main())
```

!!! note
    This example assumes you have the amplifier-foundation repo cloned locally. For production use, load bundles from git URLs or your application's bundle directory.

## What This Does

### 1. Load the Foundation Bundle

```python
foundation = await load_bundle(str(foundation_path))
```

The **foundation bundle** contains:
- Orchestrator configuration (controls execution flow)
- Context manager (handles conversation memory)
- Hooks (observability and control points)
- Base system instruction

Learn more: [What is a Bundle?](concepts.md#what-is-a-bundle)

### 2. Load a Provider Bundle

```python
provider = await load_bundle(str(provider_path / "anthropic-sonnet.yaml"))
```

The **provider bundle** specifies:
- Which LLM to use (Claude Sonnet 4.5)
- API configuration
- Module source (where to download the provider module)

Learn more: [Providers](/modules/providers/)

### 3. Compose Bundles

```python
composed = foundation.compose(provider)
```

**Composition** merges configurations - later bundles override earlier ones:
- Foundation provides orchestrator, context manager, hooks
- Provider adds the LLM backend
- Result: Complete configuration ready for execution

Learn more: [Composition](concepts.md#composition)

### 4. Prepare for Execution

```python
prepared = await composed.prepare()
```

**Preparation** resolves module sources and downloads them:
- Looks up module sources (git URLs)
- Downloads modules if not cached
- Validates module structure
- Returns PreparedBundle ready for session creation

First run takes ~30 seconds to download modules. Subsequent runs use cache.

Learn more: [Prepared Bundle](concepts.md#prepared-bundle)

### 5. Create and Use Session

```python
session = await prepared.create_session(session_cwd=Path.cwd())
async with session:
    response = await session.execute("Your prompt here")
```

**Session** is your interface to the AI:
- Manages conversation history
- Routes to appropriate provider
- Handles tool execution
- Maintains context across turns

The `session_cwd` parameter sets the working directory for file operations - critical for server deployments.

## Next Steps

**Try more examples:**
- [Custom Configuration](examples/custom_configuration.md) - Add tools and enable streaming
- [Multi-Agent Systems](examples/multi_agent_system.md) - Coordinate specialized agents

**Learn core concepts:**
- [What is a Bundle?](concepts.md#what-is-a-bundle)
- [Composition Rules](concepts.md#composition)
- [Mount Plans](concepts.md#mount-plan)

**Explore patterns:**
- [Bundle Organization](patterns.md#bundle-organization)
- [Provider Patterns](patterns.md#provider-patterns)
- [Session Patterns](patterns.md#session-patterns)

## Troubleshooting

### Module Download Fails

If `prepare()` fails to download modules:

1. Check internet connection
2. Verify git URLs are accessible
3. Check disk space for cache directory

### API Key Issues

Set the appropriate environment variable for your provider:

```bash
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
export AZURE_OPENAI_API_KEY="your-key-here"
```

### Import Errors

If you get import errors:

```bash
pip install --upgrade git+https://github.com/microsoft/amplifier-foundation
```

Ensure you're using Python 3.11+.
