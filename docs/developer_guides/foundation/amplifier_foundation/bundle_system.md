---
title: Bundle System Deep Dive
description: Loading, composition, validation, and preparation
---

# Bundle System Deep Dive

Detailed guide to the bundle system: loading, composition, validation, and preparation. For the mental model, see [Core Concepts](concepts.md).

## Loading Bundles

Bundles can be loaded from multiple source types using `load_bundle()`:

```python
from amplifier_foundation import load_bundle

# From git URL
bundle = await load_bundle("git+https://github.com/org/my-bundle@main")

# From local file
bundle = await load_bundle("./bundle.md")

# From git URL with subdirectory
bundle = await load_bundle(
    "git+https://github.com/org/repo@main#subdirectory=providers/anthropic-opus.yaml"
)
```

### Source URI Formats

| Format | Example | Use Case |
|--------|---------|----------|
| Local path | `./modules/my-module` | Modules within the bundle |
| Relative path | `../shared-module` | Sibling directories |
| Git URL | `git+https://github.com/org/repo@main` | External modules |
| Git with subpath | `git+https://github.com/org/repo@main#subdirectory=modules/foo` | Module within larger repo |

**Local paths are resolved relative to the bundle's location.**

### Bundle File Formats

Bundles support two file formats:

- **Markdown** (`.md`) — YAML frontmatter + markdown body for system instruction
- **YAML** (`.yaml`, `.yml`) — Pure YAML configuration (no instruction body)

When loading a directory, the registry looks for `bundle.md` first, then `bundle.yaml`.

### Bundle File Structure

A bundle is a markdown file with YAML frontmatter:

```markdown
---
bundle:
  name: my-bundle
  version: 1.0.0
  description: What this bundle provides

includes:
  - bundle: foundation              # Inherit from other bundles
  - bundle: my-bundle:behaviors/x   # Include behaviors

# Only declare tools NOT inherited from includes
tools:
  - module: tool-name
    source: ./modules/tool-name     # Local path
    config:
      setting: value

# Control what tools spawned agents inherit
spawn:
  exclude_tools: [tool-task]        # Agents inherit all EXCEPT these
  # OR use explicit list:
  # tools: [tool-a, tool-b]         # Agents get ONLY these tools

agents:
  include:
    - my-bundle:agent-name          # Reference agents in this bundle

# Only declare hooks NOT inherited from includes
hooks:
  - module: hooks-custom
    source: git+https://github.com/...
---

# System Instructions

Your markdown instructions here. This becomes the system prompt.

Reference documentation with @mentions:
@my-bundle:docs/GUIDE.md
```

## Composition

Bundles compose via `includes:` or programmatically via `.compose()`:

```python
# Programmatic composition
base = await load_bundle("foundation")
overlay = await load_bundle("./my-config.md")
composed = base.compose(overlay)  # Later overrides earlier

# Declarative composition (in YAML)
includes:
  - bundle: foundation
  - bundle: my-bundle:behaviors/my-capability
```

### Composition Order

Bundles compose left-to-right (earlier to later):

```yaml
includes:
  - bundle: foundation     # Base layer
  - bundle: custom-tools   # Adds tools
  - bundle: dev-config     # Dev overrides
```

Result: `foundation.compose(custom_tools).compose(dev_config)`

### Merge Rules

| Section | Rule |
|---------|------|
| `session` | Deep merge (nested dicts merged recursively, later wins for scalars) |
| `spawn` | Deep merge (later overrides earlier) |
| `providers` | Merge by module ID (configs for same module are deep-merged) |
| `tools` | Merge by module ID |
| `hooks` | Merge by module ID |
| `agents` | Merge by agent name (later wins) |
| `context` | Accumulates with namespace prefix (each bundle contributes without collision) |
| `instruction` | Replace entirely (later wins) |

**Module ID merge**: Same ID = update config, new ID = add to list.

### Example: Config Override

```python
# Base bundle
base = Bundle(
    name="base",
    providers=[{
        "module": "provider-anthropic",
        "config": {"default_model": "claude-sonnet-4-5"}
    }]
)

# Override
overlay = Bundle(
    name="overlay",
    providers=[{
        "module": "provider-anthropic",
        "config": {"temperature": 0.3}
    }]
)

# Result: merged config for provider-anthropic
result = base.compose(overlay)
# result.providers[0].config = {
#     "default_model": "claude-sonnet-4-5",  # From base
#     "temperature": 0.3                      # From overlay
# }
```

## Validation

Validate bundle structure before use:

```python
from amplifier_foundation import validate_bundle, validate_bundle_or_raise

# Get validation result
result = await validate_bundle(bundle)
if not result.is_valid:
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")

# Or raise on error
await validate_bundle_or_raise(bundle)
```

### Validation Checks

- Required fields (`bundle.name`)
- Module ID uniqueness
- Source URI format
- Agent references
- Context file existence
- Circular includes

## Preparation

Prepare a bundle for execution:

```python
bundle = await load_bundle("./bundle.md")
prepared = await bundle.prepare()  # Downloads and activates modules

# Use prepared bundle
async with prepared.create_session() as session:
    response = await session.execute("Hello!")
```

### What `prepare()` Does

1. **Downloads modules** from git URLs to cache
2. **Installs dependencies** for each module
3. **Activates modules** (makes them importable)
4. **Creates resolver** for module lookup
5. **Returns PreparedBundle** with mount plan and resolver

### PreparedBundle

A `PreparedBundle` contains:

- `mount_plan` - Configuration dict for AmplifierSession
- `resolver` - Module source resolver
- `bundle` - Original Bundle instance
- `bundle_package_paths` - List of bundle package paths for `sys.path`

### Creating Sessions from Prepared Bundles

```python
# Context manager (recommended)
async with prepared.create_session() as session:
    response = await session.execute("prompt")
    # Automatic cleanup

# Manual creation
session = AmplifierSession(config=prepared.mount_plan)
await session.coordinator.mount("module-source-resolver", prepared.resolver)
await session.initialize()
# ... use session ...
await session.cleanup()
```

## Agent Loading

Agents are loaded and compiled into the mount plan:

### Agent Definition Patterns

**Pattern 1: Include (Recommended)**

```yaml
agents:
  include:
    - my-bundle:my-agent      # Loads agents/my-agent.md
```

**Use when**: Agent is self-contained with its own instructions in a separate `.md` file.

**Pattern 2: Inline (Valid for tool-scoped agents)**

```yaml
agents:
  my-agent:
    description: "Agent with bundle-specific tool access"
    instructions: my-bundle:agents/my-agent.md
    tools:
      - module: tool-special    # This agent gets specific tools
        source: ./modules/tool-special
```

**Use when**: Agent needs bundle-specific tool configurations that differ from the parent bundle.

### When to Use Each

| Scenario | Pattern | Why |
|----------|---------|-----|
| Standard agent with own instructions | Include | Cleaner separation, context sink pattern |
| Agent needs specific tools | Inline | Can specify `tools:` for just this agent |
| Agent reused across bundles | Include | Separate file is more portable |
| Agent tightly coupled to bundle | Inline | Keep definition with bundle config |

Both patterns are fully supported and intentional design choices for different use cases.

### Agent Metadata Loading

After composition, call `load_agent_metadata()` to enrich agent configs:

```python
bundle = await load_bundle("./bundle.md")
bundle.load_agent_metadata()  # Loads description from .md files
```

This loads `meta.description` and other fields from agent `.md` files.

## @Mention Resolution

Instructions can reference files using `@namespace:path` syntax:

```markdown
See @foundation:context/guidelines.md for guidelines.
```

### Resolution Process

1. During composition, each bundle's `base_path` is tracked by namespace (from `bundle.name`)
2. PreparedBundle resolves `@namespace:path` references against the original bundle's path
3. Content is loaded and included inline in the system prompt

### Syntax Quick Reference

| Location | Syntax | Example |
|----------|--------|---------|
| **Markdown body** (bundle.md, agents/*.md) | `@namespace:path` | `@my-bundle:context/guide.md` |
| **YAML sections** (context.include, agents.include) | `namespace:path` (NO @) | `my-bundle:context/guide.md` |

The `@` prefix is **only** for markdown text. YAML sections use bare `namespace:path` references.

### context.include vs @mentions

These two patterns have **different composition behavior**:

| Pattern | Composition Behavior | Use When |
|---------|---------------------|----------|
| `context.include` | **ACCUMULATES** - content propagates to including bundles | Behaviors that inject context into parents |
| `@mentions` | **REPLACES** - stays with this instruction only | Direct references in your own instruction |

**Use `context.include` in behaviors (`.yaml` files):**
```yaml
# behaviors/my-behavior.yaml
# This context will propagate to ANY bundle that includes this behavior
context:
  include:
    - my-bundle:context/behavior-instructions.md
```

**Use `@mentions` in root bundles (`.md` files):**
```markdown
---
bundle:
  name: my-bundle
---

# Instructions

@my-bundle:context/my-instructions.md    # Stays with THIS instruction
```

## Namespace Registration

When a bundle loads, its `bundle.name` becomes a namespace:

```
Load foundation → Registers "foundation" namespace
               → @foundation:docs/GUIDE.md resolves to /path/to/foundation/docs/GUIDE.md
```

### Root vs Nested Bundles

| Term | Definition | Registry State |
|------|------------|----------------|
| **Root bundle** | `/bundle.md` or `/bundle.yaml` at repo root. Establishes namespace. | `is_root = True` |
| **Nested bundle** | Loaded via `#subdirectory=` or `@namespace:path`. Shares root's namespace. | `is_root = False` |

**Key insight:** The namespace comes from `bundle.name`, not the repo URL or directory name.

## Source Resolution

The `BundleRegistry` resolves sources to local paths:

```python
registry = BundleRegistry()

# Register named bundles
registry.register({
    "foundation": "git+https://github.com/microsoft/amplifier-foundation@main",
    "my-bundle": "./bundles/my-bundle.md"
})

# Load by name
bundle = await registry.load("foundation")
```

### Resolution Priority

1. **Registry entries** - Named bundles registered with `register()`
2. **Direct URIs** - Git URLs or file paths
3. **Local discovery** - Search in `.amplifier/bundles/` and `~/.amplifier/bundles/`

## Caching

Remote bundles are cached in `~/.amplifier/cache/`:

```
~/.amplifier/
├── cache/
│   └── github.com/
│       └── microsoft/
│           └── amplifier-foundation/
│               └── main/
│                   ├── bundle.md
│                   └── agents/
└── registry.json
```

### Cache Management

- **Automatic**: Remote bundles cached on first load
- **Updates**: Use `registry.update(name)` to refresh
- **Clearing**: Delete `~/.amplifier/cache/` directory

## Spawn Policy

Control which tools spawned agents inherit:

```yaml
# In bundle.md
spawn:
  exclude_tools: [tool-task]  # Agents inherit all EXCEPT these
  # OR
  tools: [tool-a, tool-b]     # Agents get ONLY these tools
```

### How It Works

Before merging parent and agent configs, the spawn policy filters parent tools:

- **exclude_tools**: Blocklist - inherit all except specified
- **tools** (or **inherit_tools**): Allowlist - inherit only specified

**Default**: No spawn section means agents inherit all parent tools.

### Common Pattern

Prevent delegation recursion by excluding `tool-task`:

```yaml
tools:
  - module: tool-task      # Parent can delegate
  - module: tool-filesystem
  - module: tool-bash

spawn:
  exclude_tools: [tool-task]  # But agents can't delegate further
```

## Provider Preferences

Control provider/model selection when spawning agents:

```python
from amplifier_foundation import ProviderPreference

result = await prepared.spawn(
    child_bundle=agent_bundle,
    instruction="Quick analysis",
    provider_preferences=[
        ProviderPreference(provider="anthropic", model="claude-haiku-*"),
        ProviderPreference(provider="openai", model="gpt-4o-mini"),
    ]
)
```

Features:
- **Ordered fallback chain** - Tries each preference until finding available provider
- **Glob pattern support** - `claude-haiku-*` resolves to latest matching model
- **Flexible matching** - Works with provider names or module IDs

## Bundle Registry

The `BundleRegistry` manages bundle lifecycle:

### Registration

```python
registry = BundleRegistry()

# Register bundles
registry.register({
    "foundation": "git+https://github.com/microsoft/amplifier-foundation@main",
    "my-bundle": "./bundles/my-bundle.md"
})

# Query registry
state = registry.get_state("foundation")
print(f"Loaded at: {state.loaded_at}")
print(f"Version: {state.version}")
```

### BundleState

Tracked state for each bundle:

- `uri` - Source URI
- `name` - Bundle name
- `version` - Bundle version
- `loaded_at` - When bundle was loaded
- `checked_at` - When last checked for updates
- `local_path` - Path to cached bundle
- `includes` - Bundles this bundle includes
- `included_by` - Bundles that include this bundle
- `is_root` - True for root bundles, False for nested
- `explicitly_requested` - True if user explicitly requested
- `app_bundle` - True if registered as app bundle

### Update Tracking

Check for bundle updates:

```python
# Check if update available
update_info = await registry.check_for_update("foundation")
if update_info.has_update:
    print(f"Update available: {update_info.current_version} → {update_info.latest_version}")
    
# Update bundle
await registry.update("foundation")
```

## Complete Example

```python
from amplifier_foundation import BundleRegistry, load_bundle

# Create registry
registry = BundleRegistry()

# Register bundles
registry.register({
    "foundation": "git+https://github.com/microsoft/amplifier-foundation@main",
    "custom-tools": "./bundles/custom-tools.md"
})

# Load and compose
base = await registry.load("foundation")
custom = await registry.load("custom-tools")
composed = base.compose(custom)

# Prepare for execution
prepared = await composed.prepare()

# Create session
async with prepared.create_session() as session:
    response = await session.execute("Hello, world!")
    print(response)
```

## Best Practices

### Bundle Organization

```
my-bundle/
├── bundle.md              # Root bundle
├── agents/
│   ├── expert.md         # Agent definitions
│   └── reviewer.md
├── behaviors/
│   ├── streaming.yaml    # Behavior configs
│   └── debug-mode.yaml
├── context/
│   ├── guidelines.md     # Context files
│   └── examples.md
└── modules/
    └── my-tool/          # Local modules
```

### Composition Patterns

**Base + Override**:
```python
base = await registry.load("foundation")
override = await load_bundle("./local-overrides.md")
composed = base.compose(override)
```

**Multi-Layer**:
```python
result = base.compose(team).compose(project).compose(personal)
```

**Conditional Inclusion**:
```yaml
includes:
  - bundle: foundation
  - bundle: debug-tools    # Only in dev
```

### Namespace Management

- Use descriptive bundle names: `my-org-bundle` not `bundle`
- Keep namespaces flat: Avoid deeply nested references
- Document `@mentions`: Comment complex reference chains

## Related Documentation

- [Core Concepts](concepts.md) - Mental model and terminology
- [Common Patterns](patterns.md) - Code examples and recipes
- [API Reference](api_reference.md) - Complete API documentation
