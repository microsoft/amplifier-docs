---
title: Core Concepts
description: Mental model for amplifier-foundation's design
---

# Core Concepts

Mental model for Amplifier Foundation. For code examples, see [Common Patterns](patterns.md).

## What is a Bundle?

A **Bundle** is a composable configuration unit that produces a **mount plan** for AmplifierSession.

```
Bundle → to_mount_plan() → Mount Plan → AmplifierSession
```

### Bundle Contents

| Section | Purpose |
|---------|---------|
| `bundle` | Metadata (name, version) |
| `session` | Orchestrator and context manager |
| `providers` | LLM backends |
| `tools` | Agent capabilities |
| `hooks` | Observability and control |
| `agents` | Named agent configurations |
| `context` | Context files to include |
| `instruction` | System instruction (markdown body) |
| `spawn` | Tool inheritance policy for spawned agents |

Bundles are markdown files with YAML frontmatter. See [Common Patterns](patterns.md) for format examples.

## Composition

Bundles can be **composed** to layer configuration:

```python
result = base.compose(overlay)  # Later overrides earlier
```

### Merge Rules

| Section | Rule |
|---------|------|
| `session` | Deep merge (nested dicts merged) |
| `providers` | Merge by module ID |
| `tools` | Merge by module ID |
| `hooks` | Merge by module ID |
| `spawn` | Deep merge (later overrides) |
| `instruction` | Replace (later wins) |

**Module ID merge**: Same ID = update config, new ID = add to list.

## Mount Plan

A **mount plan** is the final configuration dict consumed by AmplifierSession.

Contains: `session`, `providers`, `tools`, `hooks`, `agents`

**Not included**: `includes` (resolved), `context` (processed separately), `instruction` (injected into context).

## Prepared Bundle

A **PreparedBundle** is a bundle ready for execution with all modules activated.

```python
bundle = await load_bundle("/path/to/bundle.md")
prepared = await bundle.prepare()  # Downloads modules
async with prepared.create_session() as session:
    response = await session.execute("your prompt")
```

**Preparation** fetches external modules, validates configuration, and creates a ready-to-run session factory.

## Bundle Registry

The **BundleRegistry** manages named bundles with caching and update tracking.

```python
from amplifier_foundation import BundleRegistry

registry = BundleRegistry()
registry.register({"foundation": "git+https://github.com/microsoft/amplifier-foundation@main"})
bundle = await registry.load("foundation")
```

### Registry Features

- **Named bundles**: Register URIs with friendly names
- **Caching**: Downloaded bundles cached in `~/.amplifier/cache`
- **Update tracking**: Detect when bundles have new versions
- **State persistence**: Saved to `~/.amplifier/registry.json`

### Bundle State Tracking

The registry tracks metadata for each bundle:

```python
state = registry.get_state("foundation")
# Returns BundleState with:
# - uri: Source URI
# - name: Bundle name
# - version: Current version
# - loaded_at: Last load timestamp
# - local_path: Cache location
# - is_root: True for root bundles, False for nested
# - root_name: For nested bundles, the containing root's name
# - includes: Bundles this bundle includes
# - included_by: Bundles that include this bundle
```

### Root vs Nested Bundles

**Root bundle**: A bundle at `/bundle.md` or `/bundle.yaml` at the root of a repo or directory tree. Establishes the namespace and root directory for path resolution.

**Nested bundle**: A bundle loaded via `#subdirectory=` URIs or `@namespace:path` references. Shares the namespace with its root bundle and resolves paths relative to its own location.

Examples:
- `git+https://github.com/org/repo@main` → root bundle
- `git+https://github.com/org/repo@main#subdirectory=behaviors/streaming` → nested bundle
- `foundation:behaviors/streaming-ui` → nested bundle (namespace:path syntax)

The namespace comes from `bundle.name`, not the repo URL or directory name.

## Includes

Bundles compose via `includes`:

```yaml
includes:
  - bundle: foundation
  - bundle: my-custom-tools
```

**Include resolution**:
1. Registered names (via registry)
2. URIs (git+, file://, http://)
3. `namespace:path` syntax (e.g., `foundation:behaviors/streaming-ui`)

**Circular dependencies**: The registry detects and prevents circular includes.

## @Mentions

Reference context files using `@mentions`:

```markdown
---
context:
  - "@foundation:context/IMPLEMENTATION_PHILOSOPHY.md"
  - "@mybundle:docs/guidelines.md"
---
```

**Syntax**: `@namespace:path/to/file.md`

The mention resolver:
1. Looks up namespace in registry
2. Resolves path relative to bundle's location
3. Loads file content
4. Injects into session context

## Source Resolution

Bundles can reference external modules and other bundles by URI:

```yaml
tools:
  - module: my-tool
    source: git+https://github.com/org/my-tool@main
```

**Supported URI formats**:
- `git+https://github.com/org/repo@branch`
- `git+https://github.com/org/repo@tag`
- `git+https://github.com/org/repo@commit-hash`
- `git+https://github.com/org/repo@main#subdirectory=path/to/module`
- `file:///absolute/path`
- Relative paths (resolved relative to bundle location)

## Design Philosophy

### Mechanism, Not Policy

Foundation provides **mechanisms** (loading, composition, resolution) but doesn't dictate **policy** (which bundles, what configuration).

Applications like `amplifier-app-cli` define policy:
- Which bundles to load
- How to compose them
- What defaults to apply

### Composability First

Everything composes:
- Bundles compose via `includes`
- Configuration sections merge predictably
- No global state or singletons

### Pure Data Flow

Bundles are pure data transformations:
```
Sources → Load → Compose → Mount Plan → Session
```

No side effects during composition. Side effects (module loading, session creation) happen explicitly via `prepare()` and `create_session()`.

## Common Patterns

### Base + Override Pattern

```python
base = await registry.load("foundation")
override = await load_bundle("./local-overrides.md")
composed = base.compose(override)
```

Use for: Local customization of shared bundles.

### Multi-Layer Composition

```python
result = base.compose(team).compose(project).compose(personal)
```

Layers merge left-to-right. Later layers override earlier.

### Agent-Specific Overlays

```python
agent_bundle = await load_bundle("./agents/zen-architect.md")
agent_config = agent_bundle.to_mount_plan()

# Merge with parent config
merged = parent_config.copy()
deep_merge(merged, agent_config)
```

Use for: Agent delegation with config overlays.

## Related Documentation

- [Bundle System Deep Dive](bundle_system.md) - Loading, validation, preparation
- [Common Patterns](patterns.md) - Code examples and recipes
- [API Reference](api_reference.md) - Complete API documentation
