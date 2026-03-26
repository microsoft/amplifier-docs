---
title: Foundation Developer Guide
description: Building with amplifier-core and contributing to the foundation
---

# Foundation Developer Guide

This guide is for developers who want to **work with the Amplifier foundation** - the core kernel, libraries, and architectural components that power all Amplifier applications.

!!! note "Audience"
    Building an application on top of Amplifier? You're in the right place. For building a pluggable module (Provider, Tool, Hook), see [Module Development](../../developer/index.md).

## Who This Guide Is For

This guide is for you if you want to:

- ✅ **Build applications** using amplifier-core (like building your own CLI, web UI, or automation tool)
- ✅ **Contribute** to amplifier-core or other foundation libraries
- ✅ **Understand** the kernel internals and how the foundation works
- ✅ **Use amplifier-foundation** in your applications

## Not What You're Looking For?

- **Using the Amplifier CLI?** → See the [CLI User Guide](../../user_guide/)
- **Creating custom modules (tools/providers)?** → See the [Module Developer Guide](../../developer/index.md)
- **Building applications on Amplifier?** → Start here, then see [Application Developer Guide](../applications/)

## Understanding the Architecture

Amplifier is built in layers, inspired by the Linux kernel model:

```
┌─────────────────────────────────────────────────┐
│        Applications Layer                       │
│  (amplifier-app-cli, your-app, etc.)            │
│                                                  │
│  • User interaction                             │
│  • Configuration resolution                     │
│  • Mount Plan creation                          │
│  • Uses libraries                               │
├─────────────────────────────────────────────────┤
│        Libraries Layer                          │
│  (amplifier-foundation, amplifier-*-lib)        │
│                                                  │
│  • Bundle system (composition & loading)        │
│  • @Mention resolution                          │
│  • Utilities (I/O, merging, caching)            │
│  • Reference content (agents, behaviors)        │
├─────────────────────────────────────────────────┤
│        Kernel Layer (amplifier-core)            │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │  Rust Kernel (crates/amplifier-core/)    │  │
│  │  • Session lifecycle                      │  │
│  │  • Coordinator                            │  │
│  │  • Event system                           │  │
│  │  • Hook registry                          │  │
│  │  • Type-safe contracts                    │  │
│  └───────────────┬───────────────────────────┘  │
│                  │ PyO3 bridge                   │
│                  ↓                               │
│  ┌───────────────────────────────────────────┐  │
│  │  Python Bindings                          │  │
│  │  • Pydantic models                        │  │
│  │  • Module loader                          │  │
│  │  • Backward-compatible API                │  │
│  └───────────────────────────────────────────┘  │
├─────────────────────────────────────────────────┤
│        Modules Layer (Userspace)                │
│  (Providers, Tools, Hooks, Orchestrators)       │
│                                                  │
│  • Providers: LLM backends                      │
│  • Tools: Agent capabilities                    │
│  • Orchestrators: Execution loops               │
│  • Contexts: Memory management                  │
│  • Hooks: Observability                         │
└─────────────────────────────────────────────────┘
```

### Layer Responsibilities

**Applications Layer** (amplifier-app-cli, your-app):
- User interaction (CLI, web, API)
- Configuration management
- Bundle composition
- Session initialization

**Libraries Layer** (amplifier-foundation):
- Bundle loading and composition
- @Mention resolution (@namespace:path)
- Reference content (agents, providers, behaviors)
- Utilities (YAML I/O, dict merging, caching)

**Kernel Layer** (amplifier-core):
- **Rust kernel**: Session lifecycle, event system, coordinator
- **Python bindings**: Pydantic models, module loader, API surface
- Module discovery and loading
- Hook dispatch
- Stable contracts

**Modules Layer** (Userspace):
- Providers: LLM backend implementations
- Tools: Agent capabilities (filesystem, bash, web)
- Orchestrators: Execution strategies
- Contexts: Memory management
- Hooks: Observability and control

## The Rust Kernel

amplifier-core is **implemented in Rust** for performance and type safety, with Python bindings via PyO3:

### Why Rust?

- **Performance**: Native speed for session lifecycle and event dispatch
- **Type safety**: Compile-time guarantees for kernel contracts
- **Memory safety**: No runtime errors from memory issues
- **Zero-cost abstractions**: High-level code, low-level performance

### Transparent to Consumers

**Existing Python code requires zero changes**:

```python
# Same imports work identically
from amplifier_core import AmplifierSession

# Same API, same behavior
session = AmplifierSession(config=mount_plan)
response = await session.execute("Hello!")
```

The Python API is unchanged. The Rust implementation is transparent - you get better performance with the same interface.

### Architecture

```
Rust Kernel (crates/amplifier-core/)
  ├── Session lifecycle
  ├── Coordinator
  ├── Event system
  ├── Hook registry
  └── Cancellation tokens
           ↓ PyO3 bridge
Python Bindings (python/amplifier_core/)
  ├── Pydantic models (unchanged)
  ├── Module loader (Python)
  └── Backward-compatible imports
           ↓ Protocols
Modules (Tool, Provider, Hook, etc.)
  └── Implemented in Python (unchanged)
```

**For developers**: 
- Modules remain in Python (no change required)
- Python bindings handle the bridge
- Rust kernel provides the engine

## Core Concepts

### Session

Execution context with mounted modules and conversation state. Lifecycle: `initialize()` → `execute()` → `cleanup()`.

### Mount Plan

Configuration dictionary specifying which modules to load and their configuration. Applications and bundles compile to mount plans.

### Coordinator

Infrastructure context providing:
- `session_id` and `request_id`
- Config access
- Hook dispatch
- Module registry

Injected into all modules during initialization.

### Module Types

All modules use Python `Protocol` (structural typing, no inheritance required):

| Module Type | Purpose | Key Methods |
|-------------|---------|-------------|
| **Provider** | LLM backends | `complete()`, `parse_tool_calls()`, `get_info()`, `list_models()` |
| **Tool** | Agent capabilities | `execute()` |
| **Orchestrator** | Execution loops | `execute()` |
| **ContextManager** | Memory | `add_message()`, `get_messages()`, `compact()` |
| **Hook** | Observability | `__call__(event, data)` |

See [Module Development](../../developer/) for protocol details.

## Design Philosophy

### Mechanism, Not Policy

The kernel provides **capabilities** without **decisions**:

| Kernel Provides (Mechanism) | Modules Decide (Policy) |
| --------------------------- | ----------------------- |
| Module loading              | Which modules to load   |
| Event emission              | What to log, where      |
| Session lifecycle           | Orchestration strategy  |
| Hook registration           | Security policies       |

**Litmus test**: "Could two teams want different behavior?" → If yes, it's policy → Module, not kernel.

### Ruthless Simplicity

- **KISS taken seriously**: As simple as possible, but no simpler
- **Minimize abstractions**: Every layer must justify existence
- **Start minimal**: Grow as needed, avoid future-proofing
- **Code you don't write has no bugs**

### Small, Stable, Boring Kernel

- **Changes rarely**: Maintains backward compatibility always
- **Single maintainer scope**: Easy to reason about
- **Favor deletion over accretion**: Keep kernel minimal
- **Innovation at edges**: Modules compete, kernel stays stable

### Modular Design (Bricks & Studs)

Think LEGO blocks:

- **Brick** = Self-contained module with clear responsibility
- **Stud** = Interface/protocol where bricks connect
- **Blueprint** = Specification (docs define target state)
- **Builder** = AI generates code from spec

**Prefer regeneration over editing**: Rebuild from spec, don't line-edit.

### Event-First Observability

- **If it's important → emit a canonical event**
- **If it's not observable → it didn't happen**
- **One JSONL stream = single source of truth**
- **Hooks observe without blocking**

### Text-First, Inspectable

- **Human-readable, diffable, versionable representations**
- **JSON schemas for validation**
- **No hidden state, no magic globals**
- **Explicit > implicit**

### Polyglot Module Loading

Modules can be written in any language. Four transport types determine how a module integrates with its host:

- **python**: Direct import into Python host. Dependencies managed via `uv pip install` at load time.
- **rust**: Rust host links directly as a native library. Non-Rust host spawns the compiled binary as a gRPC sidecar.
- **wasm**: Loaded in-process via a WASM runtime. Sandboxed execution with no host OS access unless explicitly granted.
- **grpc**: Connects to an external gRPC service at the runtime endpoint declared in `amplifier.toml`.

The `amplifier.toml` manifest declares the module's transport. The host runtime reads this declaration and selects the appropriate loading strategy. A Rust module written for direct linking works transparently as a sidecar in any non-Rust host without modification.

gRPC bridges exist for all six module types (tool, hook, orchestrator, context, provider, and scaffold), so any module type can cross a language boundary without changing its external contract.

## Getting Started

### Building Applications

Start with the [Application Developer Guide](../applications/):

1. Learn how to initialize sessions
2. Build mount plans from bundles
3. Handle user interaction
4. Format and display results

Key example: [CLI Case Study](../applications/cli_case_study.md)

### Using amplifier-foundation

The foundation library provides bundle composition and utilities:

```python
from amplifier_foundation import load_bundle

# Load bundles
foundation = await load_bundle("git+https://github.com/microsoft/amplifier-foundation@main")
provider = await load_bundle("./providers/anthropic.yaml")

# Compose (later overrides earlier)
composed = foundation.compose(provider)

# Prepare: resolve modules, download if needed
prepared = await composed.prepare()

# Create session
async with await prepared.create_session() as session:
    response = await session.execute("Hello!")
```

See [amplifier-foundation documentation](amplifier_foundation/) for complete API.

### Contributing to amplifier-core

**Prerequisites**:
- Rust 1.70+ (for kernel development)
- Python 3.10+
- maturin (for building Python bindings)

**Development setup**:

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Clone repo
git clone https://github.com/microsoft/amplifier-core
cd amplifier-core

# Build and install in development mode
pip install maturin
maturin develop

# Or with uv
uv run maturin develop

# Run tests
cargo test -p amplifier-core                                   # Rust kernel tests
uv run pytest tests/ bindings/python/tests/ -q --tb=short     # Python tests
uv run pytest tests/ bindings/python/tests/ --cov             # Full coverage
uv run python tests/validate_rust_kernel.py                   # Validate Rust kernel integration
```

See `docs/RUST_CORE_TESTING.md` in amplifier-core for detailed testing guide.

## Repository Structure

### amplifier-core

```
amplifier-core/
├── crates/amplifier-core/     # Rust kernel
│   ├── src/
│   │   ├── session.rs         # Session lifecycle
│   │   ├── coordinator.rs     # Infrastructure context
│   │   ├── hooks.rs           # Hook registry
│   │   └── events.rs          # Event system
│   └── Cargo.toml
├── bindings/python/           # PyO3 bridge
├── python/amplifier_core/     # Python API
│   ├── interfaces.py          # Protocols
│   ├── models.py              # Data models
│   └── message_models.py      # Pydantic models
└── docs/
    ├── DESIGN_PHILOSOPHY.md   # Architecture principles
    ├── contracts/             # Module contracts
    └── RUST_CORE_TESTING.md   # Testing guide
```

### amplifier-foundation

```
amplifier-foundation/
├── amplifier_foundation/      # Library code
│   ├── bundle.py              # Bundle composition
│   ├── registry.py            # Bundle loading
│   ├── validator.py           # Bundle validation
│   ├── mentions/              # @mention resolution
│   ├── io/                    # File I/O utilities
│   ├── dicts/                 # Dict utilities
│   └── paths/                 # Path utilities
├── docs/
│   ├── BUNDLE_GUIDE.md        # Bundle authoring
│   ├── AGENT_AUTHORING.md     # Agent creation
│   ├── CONCEPTS.md            # Mental model
│   ├── PATTERNS.md            # Common patterns
│   ├── URI_FORMATS.md         # Source URI quick reference
│   └── API_REFERENCE.md       # API index
├── agents/                    # Reference agents
├── behaviors/                 # Reference behaviors
├── providers/                 # Provider configs
└── examples/                  # Working examples
```

## Key Resources

### Documentation

**Core (Kernel)**:
- [DESIGN_PHILOSOPHY.md](https://github.com/microsoft/amplifier-core/blob/main/docs/DESIGN_PHILOSOPHY.md) - Architecture principles
- [Module Contracts](../../developer/index.md) - Protocol specifications
- [RUST_CORE_TESTING.md](https://github.com/microsoft/amplifier-core/blob/main/docs/RUST_CORE_TESTING.md) - Testing guide

**Foundation (Libraries)**:
- [BUNDLE_GUIDE.md](amplifier_foundation/bundle_system.md) - Bundle authoring
- [AGENT_AUTHORING.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/AGENT_AUTHORING.md) - Agent creation
- [CONCEPTS.md](amplifier_foundation/concepts.md) - Mental model
- [PATTERNS.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/PATTERNS.md) - Common patterns
- [URI_FORMATS.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/URI_FORMATS.md) - Source URI quick reference

### Examples

**amplifier-core**: API examples in `examples/`
**amplifier-foundation**: 20+ examples in `examples/` directory
**amplifier-app-cli**: Complete application case study

## Development Workflow

### Typical Development Pattern

1. **Understand the layers**: Know which layer your work belongs in
2. **Follow the philosophy**: Mechanism vs policy, ruthless simplicity
3. **Write specifications first**: Define contracts before implementation
4. **Build modules, not kernel**: Most work happens in modules
5. **Test thoroughly**: Unit tests, integration tests, manual verification
6. **Maintain backward compatibility**: Especially in kernel

### When to Modify the Kernel

**Rarely.** The kernel should change infrequently. Only modify when:

- ✅ Multiple modules need the same mechanism
- ✅ Change benefits the entire ecosystem
- ✅ Backward compatibility is maintained
- ❌ NOT for policy decisions (which provider, how to format)
- ❌ NOT for product features (bundle in modules)

### Contributing Guidelines

1. **Read DESIGN_PHILOSOPHY.md first**
2. **Discuss major changes** before implementation
3. **Maintain backward compatibility** in public APIs
4. **Write tests** for all changes
5. **Update documentation** alongside code

## Next Steps

- **Building an application?** → See [Application Developer Guide](../applications/)
- **Working with bundles?** → See [Bundle System](amplifier_foundation/bundle_system.md)
- **Creating modules?** → See [Module Developer Guide](../../developer/)
- **Contributing to core?** → Read [DESIGN_PHILOSOPHY.md](https://github.com/microsoft/amplifier-core/blob/main/docs/DESIGN_PHILOSOPHY.md)

## Community

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Architecture questions and proposals
- **Pull Requests**: Code contributions

The foundation is built on principles of simplicity, stability, and modularity. When in doubt, ask: "Is this mechanism or policy?" and "Which layer does this belong in?"
