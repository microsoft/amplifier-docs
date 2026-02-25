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

### Persistence

Registry state persists to `~/.amplifier/registry.json`:

```json
{
  "foundation": {
    "uri": "git+https://github.com/microsoft/amplifier-foundation@main",
    "name": "foundation",
    "version": "1.0.0",
    "loaded_at": "2024-01-15T10:30:00Z",
    "local_path": "/home/user/.amplifier/cache/github.com/microsoft/amplifier-foundation/main",
    "is_root": true
  }
}
```

## Update Checking

Check for bundle updates:

```python
from amplifier_foundation import check_bundle_status, update_bundle

# Check status
status = await check_bundle_status(registry, "foundation")
if status.update_available:
    print(f"Update available: {status.current_version} -> {status.latest_version}")
    
    # Update
    await update_bundle(registry, "foundation")
```

### BundleStatus

Update status information:

- `name` - Bundle name
- `current_version` - Installed version
- `latest_version` - Available version
- `update_available` - Boolean flag
- `last_checked` - When last checked

## Include Resolution

The registry resolves `includes:` recursively:

```yaml
# my-bundle.md
includes:
  - bundle: foundation
  - bundle: my-bundle:behaviors/my-capability
```

### Resolution Process

1. Load each included bundle
2. Compose in order (earlier to later)
3. Track dependencies in registry
4. Detect circular includes

### Circular Include Detection

The registry prevents circular includes:

```yaml
# bundle-a.md
includes:
  - bundle: bundle-b

# bundle-b.md
includes:
  - bundle: bundle-a  # Error: circular include
```

## Module Activation

`prepare()` activates modules for use:

### Activation Process

1. **Extract module specs** from mount plan
2. **Download sources** (git URLs to cache)
3. **Install dependencies** (via pip/uv)
4. **Register entry points** (make importable)
5. **Save install state** for fast subsequent startups

### Module Paths

Activated modules are tracked by the `BundleModuleResolver`:

```python
prepared = await bundle.prepare()
resolver = prepared.resolver  # BundleModuleResolver

# Resolver provides module paths for ModuleLoader
```

### Bundle Package Paths

Bundles can include Python packages that need to be on `sys.path`:

```python
prepared = await bundle.prepare()
package_paths = prepared.bundle_package_paths

# These paths are registered as session capabilities
# for inheritance by child sessions
```

## Agent Pre-activation

`prepare()` pre-activates modules declared in agent configs:

```python
# Without pre-activation, spawned agent sessions would fail
# when their orchestrator/provider/tool modules aren't found

# prepare() activates:
# - Agent's session orchestrator and context
# - Agent's providers, tools, hooks
```

This ensures child sessions can find all needed modules via the inherited resolver.

## Context File Loading

Context files are loaded during preparation:

### context.include (YAML)

```yaml
context:
  include:
    - my-bundle:context/instructions.md
```

Content is **accumulated** across composition and injected into system prompt with headers.

### @mentions (Markdown)

```markdown
@my-bundle:context/file.md
```

Content is **prepended** as XML during instruction loading:

```xml
<context_file paths="@my-bundle:context/file.md → /abs/path">
[file content]
</context_file>

---

[instruction with @mention still present as semantic reference]
```

## Load-on-Demand Pattern

Use **soft references** (text without `@`) for content that's sometimes needed:

```markdown
**Documentation (load on demand):**
- Schema: recipes:docs/RECIPE_SCHEMA.md
- Examples: recipes:examples/code-review-recipe.yaml
- Guide: foundation:docs/BUNDLE_GUIDE.md
```

The AI can load these via `read_file` when actually needed.

### When to Use Each Pattern

| Pattern | Syntax | Loads | Use When |
|---------|--------|-------|----------|
| **@mention** | `@bundle:path` | Immediately | Content is ALWAYS needed |
| **Soft reference** | `bundle:path` (no @) | On-demand | Content is SOMETIMES needed |
| **Agent delegation** | Delegate to expert agent | When spawned | Content belongs to a specialist |

## Best Practices

### Use the Thin Bundle Pattern

When including foundation, don't redeclare what it provides:

```yaml
# ✅ GOOD: Thin bundle
includes:
  - bundle: foundation

# Only declare what YOU add
agents:
  include:
    - my-bundle:my-agent
```

### Create Behaviors for Reusability

Package agents + context in `behaviors/` so others can include just your capability:

```yaml
# behaviors/my-capability.yaml
bundle:
  name: my-capability-behavior
  
agents:
  include:
    - my-bundle:my-agent
    
context:
  include:
    - my-bundle:context/instructions.md
```

### Consolidate Instructions

Put instructions in `context/instructions.md`, not inline in bundle.md:

```markdown
---
bundle:
  name: my-bundle
includes:
  - bundle: foundation
  - bundle: my-bundle:behaviors/my-capability
---

# My Bundle

@my-bundle:context/instructions.md

---

@foundation:context/shared/common-system-base.md
```

### Use Context Sink Agents

For heavy documentation, create specialized agents that @mention the docs:

```markdown
# agents/my-expert.md - Context sink
---
meta:
  name: my-expert
  description: "Expert with deep domain knowledge..."
---

# My Expert

@my-bundle:docs/COMPREHENSIVE_GUIDE.md
@my-bundle:docs/API_REFERENCE.md
```

The root session stays light; heavy context loads only when the agent is spawned.

## Common Anti-Patterns

### ❌ Duplicating Foundation

```yaml
# DON'T DO THIS when you include foundation
includes:
  - bundle: foundation

tools:
  - module: tool-filesystem     # Foundation has this!
    source: git+https://...
```

**Fix**: Remove duplicated declarations.

### ❌ Using @ Prefix in YAML

```yaml
# DON'T DO THIS - @ prefix is for markdown only
context:
  include:
    - "@my-bundle:context/instructions.md"   # ❌ @ doesn't belong here

# DO THIS
context:
  include:
    - my-bundle:context/instructions.md      # ✅ No @ in YAML
```

### ❌ Using Repository Name as Namespace

```yaml
# If loading: git+https://github.com/microsoft/amplifier-bundle-recipes@main
# And bundle.name in that repo is: "recipes"

# DON'T DO THIS
agents:
  include:
    - amplifier-bundle-recipes:recipe-author   # ❌ Repo name

# DO THIS
agents:
  include:
    - recipes:recipe-author                    # ✅ bundle.name value
```

**Why**: The namespace is ALWAYS `bundle.name`, not the git URL or repository name.

### ❌ Including Subdirectory in Paths

```yaml
# If loading: git+https://...@main#subdirectory=bundles/foo
# And bundle.name is: "foo"

# DON'T DO THIS
context:
  include:
    - foo:bundles/foo/context/instructions.md   # ❌ Redundant path

# DO THIS
context:
  include:
    - foo:context/instructions.md               # ✅ Relative to bundle location
```

**Why**: When loaded via `#subdirectory=X`, the bundle root IS `X/`. Paths are relative to that root.

## Related Documentation

- **[Core Concepts](concepts.md)** - Mental model
- **[Common Patterns](patterns.md)** - Usage examples
- **[API Reference](api_reference.md)** - API overview
- **[Bundle Guide](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md)** - Complete authoring guide
- **[URI Formats](https://github.com/microsoft/amplifier-foundation/blob/main/docs/URI_FORMATS.md)** - Source URI reference
