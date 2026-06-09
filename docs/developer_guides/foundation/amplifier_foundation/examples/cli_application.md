---
title: CLI Application Example
description: Building a real CLI tool with Amplifier Foundation — architecture patterns, lifecycle management, and error handling
---

# CLI Application Example

> **Source**: [`examples/08_cli_application.py`](https://github.com/microsoft/amplifier-foundation/blob/main/examples/08_cli_application.py)

Demonstrates building a production-quality CLI application with Amplifier. Covers application architecture patterns, session lifecycle, error handling, logging, and configuration management.

**Time to value**: 15 minutes

## What You'll Learn

- Application architecture patterns with Amplifier
- Proper session lifecycle management
- Error handling and recovery
- Logging and observability
- Configuration management
- Building reusable application classes

## Real-World Use Cases

- Internal developer tools
- Data analysis assistants
- Code review helpers
- Automation scripts

## Architecture Overview

The example structures an Amplifier app in four sections:

1. **Configuration management** — Load from environment/config files, validate
2. **Application class** — Encapsulate bundle/session lifecycle
3. **CLI interface** — Interactive and single-prompt modes
4. **Entry point** — Argument handling and startup

## Section 1: Configuration Management

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AppConfig:
    """Application configuration loaded from environment."""

    # LLM Provider
    provider_bundle: str = "anthropic-sonnet.yaml"
    api_key: str | None = None

    # Application Settings
    log_level: str = "INFO"
    storage_path: Path = Path.home() / ".amplifier" / "app_sessions"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            provider_bundle=os.getenv("PROVIDER", "anthropic-sonnet.yaml"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def validate(self) -> None:
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        if not self.storage_path.exists():
            self.storage_path.mkdir(parents=True, exist_ok=True)
```

In production, extend `from_env()` to load from `.amplifier/settings.yaml`, AWS Secrets Manager, or CLI arguments.

## Section 2: Application Class

```python
class AmplifierApp:
    """Encapsulates bundle management, session lifecycle, and error handling."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.session = None
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
        return logging.getLogger("amplifier_app")

    async def initialize(self) -> None:
        """Initialize the application and create session."""
        # Load foundation bundle
        foundation_path = Path(__file__).parent.parent
        foundation = await load_bundle(str(foundation_path))

        # Load provider
        provider_path = foundation_path / "providers" / self.config.provider_bundle
        provider = await load_bundle(str(provider_path))

        # Build tools config
        tools_config = Bundle(
            name="app-tools",
            version="1.0.0",
            tools=[
                {
                    "module": "tool-filesystem",
                    "source": "git+https://github.com/microsoft/amplifier-module-tool-filesystem@main",
                },
                {
                    "module": "tool-bash",
                    "source": "git+https://github.com/microsoft/amplifier-module-tool-bash@main",
                },
            ],
        )

        # Compose and prepare
        composed = foundation.compose(provider).compose(tools_config)
        prepared = await composed.prepare()

        # Create session (note: not using context manager here for lifecycle control)
        self.session = await prepared.create_session()

    async def execute(self, prompt: str) -> str:
        """Execute a prompt. Raises RuntimeError if not initialized."""
        if not self.session:
            raise RuntimeError("Session not initialized. Call initialize() first.")
        return await self.session.execute(prompt)

    async def shutdown(self) -> None:
        """Gracefully release session resources."""
        if self.session:
            await self.session.cleanup()

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()
```

### Key Patterns

**Lifecycle control without context manager**: `create_session()` is called without `async with` when the session needs to outlive a single block. `shutdown()` must explicitly call `session.cleanup()`.

**Context manager support**: `__aenter__`/`__aexit__` enables `async with AmplifierApp(config) as app:` for clean lifecycle in the entry point.

## Section 3: CLI Interface

```python
async def run_interactive_cli(app: AmplifierApp):
    """Multi-turn interactive REPL."""
    print("Amplifier CLI App - Interactive Mode")
    print("Type your prompts, or 'quit' to exit.\n")

    while True:
        try:
            prompt = input("\nYou: ")
            if prompt.lower() in ("quit", "exit", "q"):
                break
            if not prompt.strip():
                continue
            response = await app.execute(prompt)
            print(f"\nAgent: {response}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("The session is still active. You can continue.")


async def run_single_prompt(app: AmplifierApp, prompt: str):
    """Non-interactive single-prompt mode."""
    response = await app.execute(prompt)
    print(response)
```

**Error resilience**: Errors in `execute()` are caught in the REPL loop so the session survives individual failures. The session is still usable after a tool error or provider timeout.

## Section 4: Entry Point

```python
async def main():
    # Load and validate configuration
    try:
        config = AppConfig.from_env()
        config.validate()
    except Exception as e:
        print(f"Configuration error: {e}")
        return 1

    # Initialize and run
    async with AmplifierApp(config) as app:
        if len(sys.argv) > 1:
            prompt = " ".join(sys.argv[1:])
            await run_single_prompt(app, prompt)
        else:
            await run_interactive_cli(app)

    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
```

**Dual mode via `sys.argv`**: No argument parsing library needed — `sys.argv[1:]` provides single-prompt mode; no args defaults to interactive.

## Running the Example

```bash
# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Interactive mode
python examples/08_cli_application.py

# Single-prompt mode
python examples/08_cli_application.py "Summarize this directory"

# Custom log level
LOG_LEVEL=DEBUG python examples/08_cli_application.py
```

## Adapting for Production

Replace the hard-coded `foundation_path` with your bundle's actual location:

```python
# Point to your bundle
foundation = await load_bundle("git+https://github.com/your-org/your-bundle@main")
```

Add persistent context for sessions that survive process restarts:

```python
# Use context-persistent instead of context-simple
from amplifier_foundation import Bundle

persistence_overlay = Bundle(
    name="persistence",
    version="1.0.0",
    session={
        "context": {
            "module": "context-persistent",
            "source": "git+https://github.com/microsoft/amplifier-module-context-persistent@main",
            "config": {"persist_dir": str(config.storage_path)},
        }
    },
)

composed = foundation.compose(provider).compose(tools_config).compose(persistence_overlay)
```

## See Also

- [Common Patterns](../patterns.md) — Bundle composition patterns
- [Sessions](../../../../user_guide/sessions.md) — Session lifecycle reference
- [AmplifierSession API](../../../../api/core/session.md) — Constructor and methods
