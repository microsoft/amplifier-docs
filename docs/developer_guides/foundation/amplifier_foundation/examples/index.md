---
title: amplifier-foundation Examples
description: Progressive examples from hello world to production applications
---

# amplifier-foundation Examples

Progressive examples demonstrating how to use amplifier-foundation, from basic concepts to production applications.

## Learning Paths

<div class="grid cards" markdown>

-   :material-school: __For Beginners__

    ---

    1. [Hello World](hello_world.md) - See it work (2 min)
    2. [Custom Configuration](custom_configuration.md) - Composition (5 min)
    3. [Custom Tool](custom_tool.md) - Build capabilities (10 min)

-   :material-wrench: __For Builders__

    ---

    1. [CLI Application](cli_application.md) - Best practices (15 min)
    2. [Multi-Agent System](multi_agent_system.md) - Complex systems (30 min)

</div>

## Examples Catalog

| Example | Time | Complexity | Key Concepts |
|---------|------|------------|--------------|
| [Hello World](hello_world.md) | 2 min | ⭐ Beginner | Bundle loading, composition, execution |
| [Custom Configuration](custom_configuration.md) | 5 min | ⭐ Beginner | Composition patterns, adding tools |
| [Custom Tool](custom_tool.md) | 10 min | ⭐⭐ Intermediate | Tool protocol, registration |
| [CLI Application](cli_application.md) | 15 min | ⭐⭐ Intermediate | App architecture, error handling |
| [Multi-Agent System](multi_agent_system.md) | 30 min | ⭐⭐⭐ Advanced | Agent workflows, orchestration |

## Running Examples

All examples are in the [amplifier-foundation repository](https://github.com/microsoft/amplifier-foundation):

```bash
# Clone the repo
git clone https://github.com/microsoft/amplifier-foundation
cd amplifier-foundation

# Set API key
export ANTHROPIC_API_KEY='your-key-here'

# Run any example
uv run python examples/01_hello_world.py
uv run python examples/02_custom_configuration.py
uv run python examples/03_custom_tool.py
uv run python examples/08_cli_application.py
uv run python examples/09_multi_agent_system.py
```

## Example Summaries

### Hello World

Your first Amplifier agent in ~15 lines of code.

**What you learn:**
- Load and compose bundles
- Prepare modules for execution
- Create and execute sessions

**Key code:**
```python
foundation = await load_bundle(foundation_path)
provider = await load_bundle(provider_path)
composed = foundation.compose(provider)
prepared = await composed.prepare()
session = await prepared.create_session()
response = await session.execute("Your prompt")
```

### Custom Configuration

Tailor agents via composition.

**What you learn:**
- Add tools to your agent
- Use streaming orchestrators
- Customize behavior through composition

**Key concept:** Composition over configuration - swap capabilities, not flags.

### Custom Tool

Build domain-specific capabilities.

**What you learn:**
- Tool protocol (`name`, `description`, `input_schema`, `execute()`)
- Integrating custom capabilities
- Protocol-based design (no inheritance required)

**Key code:**
```python
class WeatherTool:
    @property
    def name(self) -> str:
        return "get_weather"
    
    async def execute(self, input: dict) -> ToolResult:
        return ToolResult(success=True, output="weather data")
```

### CLI Application

Production-quality CLI application architecture.

**What you learn:**
- Configuration management
- Logging and error handling
- Session lifecycle management
- Application patterns

**Key patterns:**
- Load-Prepare-Execute flow
- Graceful error handling
- Configuration resolution
- Reusable application classes

### Multi-Agent System

Coordinate specialized agents for complex workflows.

**What you learn:**
- Define agents with different tools and instructions
- Sequential workflows (design → implement → review)
- Parallel execution patterns
- Context passing between agents

**Key architecture:**
```python
# Agent 1: Architect - designs system
architect = Bundle(name="architect", tools=[...], instruction="...")

# Agent 2: Implementer - writes code
implementer = Bundle(name="implementer", tools=[...], instruction="...")

# Agent 3: Reviewer - checks quality
reviewer = Bundle(name="reviewer", tools=[...], instruction="...")
```

## Additional Examples

### Tier 2: Foundation Concepts (04-07)

**Goal:** Understand how Amplifier works internally

- **04_load_and_inspect.py** - Learn how `load_bundle()` works and what a bundle contains
- **05_composition.py** - Understand how `compose()` merges configuration
- **06_sources_and_registry.py** - Learn source formats and BundleRegistry
- **07_full_workflow.py** - See the complete preparation and execution flow

### Tier 4: Real-World Applications (10-21)

**Goal:** Practical use cases and advanced patterns

- **10_meeting_notes_to_actions.py** - Text processing workflow
- **11_provider_comparison.py** - Compare LLM providers
- **12_approval_gates.py** - Human-in-the-loop patterns
- **13_event_debugging.py** - Session observability
- **14_session_persistence.py** - Save and restore sessions
- **17_multi_model_ensemble.py** - Ensemble patterns
- **18_custom_hooks.py** - Build custom hooks
- **19_github_actions_ci.py** - CI/CD integration
- **20_calendar_assistant.py** - External API integration
- **21_bundle_updates.py** - Bundle update detection

## Troubleshooting

### "Module not found" Error

Modules need `source` fields so `prepare()` can download them:
```python
{"module": "tool-bash", "source": "git+https://..."}
```

### First Run Takes 30+ Seconds

This is normal - modules are downloaded from GitHub and cached in `~/.amplifier/cache/`. Subsequent runs are fast.

### "API key error"

Set your provider's API key:
```bash
export ANTHROPIC_API_KEY='your-key-here'
# or
export OPENAI_API_KEY='your-key-here'
```

### Path Issues

Examples assume you're running from the `amplifier-foundation` directory:
```bash
cd amplifier-foundation
uv run python examples/XX_example.py
```

If path errors occur, check that `Path(__file__).parent.parent` resolves to the amplifier-foundation directory.

## Key Concepts

### Bundles

Composable configuration units that produce mount plans for AmplifierSession. A bundle specifies which modules to load, how to configure them, and what instructions to provide.

```python
bundle = Bundle(
    name="my-agent",
    providers=[...],  # LLM backends
    tools=[...],      # Capabilities
    hooks=[...],      # Observability
    instruction="..." # System prompt
)
```

### Composition

Combine bundles to create customized agents. Later bundles override earlier ones, allowing progressive refinement.

```python
foundation = await load_bundle("foundation")
custom = Bundle(name="custom", tools=[...])
composed = foundation.compose(custom)  # custom overrides foundation
```

### Preparation

Download and activate all modules before execution. The `prepare()` method resolves module sources (git URLs, local paths) and makes them importable.

```python
prepared = await composed.prepare()  # Downloads modules if needed
session = await prepared.create_session()
```

### Module Sources

Specify where to download modules from. Every module needs a `source` field for `prepare()` to resolve it.

```python
tools=[
    {
        "module": "tool-filesystem",
        "source": "git+https://github.com/microsoft/amplifier-module-tool-filesystem@main"
    }
]
```

### Tool Protocol

Custom tools implement a simple protocol - no inheritance required:

```python
class MyTool:
    @property
    def name(self) -> str:
        return "my-tool"
    
    @property
    def description(self) -> str:
        return "What this tool does..."
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            },
            "required": ["param"]
        }
    
    async def execute(self, input: dict) -> ToolResult:
        return ToolResult(success=True, output="result")
```

## Architecture Principles

### Composition Over Configuration

Amplifier favors swapping modules over toggling flags. Want streaming? Use `orchestrator: loop-streaming`. Want different tools? Compose a different tool bundle. No complex configuration matrices.

### Protocol-Based

Tools, providers, hooks, and orchestrators implement protocols (duck typing), not base classes. No framework inheritance required - just implement the interface.

### Explicit Sources

Module sources are explicit in configuration. No implicit discovery or magic imports. If you need a module, specify where it comes from: git repository, local path, or package name.

### Preparation Phase

Modules are resolved and downloaded before execution (`prepare()`), not during runtime. This ensures deterministic behavior and clear error messages.

## Next Steps

- [Core Concepts](../concepts.md) - Mental model for bundles
- [Bundle System Deep Dive](../bundle_system.md) - Complete bundle authoring guide
- [Common Patterns](../patterns.md) - Practical usage patterns
- [API Reference](../api_reference.md) - Complete API documentation
