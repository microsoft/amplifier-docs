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
  exclude_tools:
    - tool-task                     # Don't pass to child sessions
---

# System Instruction

This is the markdown body that becomes the system instruction.

## Sections

You can use markdown formatting, headers, lists, etc.
```

### Root Bundles vs Nested Bundles

Bundles are classified structurally:

- **Root bundle**: At `/bundle.md` or `/bundle.yaml` at the root of a repo/directory. Establishes the namespace via `bundle.name`. Tracked with `is_root=True`.

- **Nested bundle**: Loaded via `#subdirectory=` URIs or `@namespace:path` references. Shares namespace with root bundle. Resolves paths relative to its own location. Tracked with `is_root=False`.

**Key insight**: The namespace comes from `bundle.name`, not the repo URL or directory name.

### Registry and Caching

The `BundleRegistry` manages bundle discovery, loading, and caching:

```python
from amplifier_foundation import BundleRegistry

registry = BundleRegistry()

# Register bundles
registry.register({
    "foundation": "git+https://github.com/microsoft/amplifier-foundation@main"
})

# Load by name
bundle = await registry.load("foundation")

# Load by URI (auto-registers if auto_register=True)
bundle = await registry.load("git+https://github.com/org/bundle@main")

# Load all registered bundles
bundles = await registry.load()  # Returns dict[str, Bundle]
```

**Caching**: The registry caches loaded bundles in `~/.amplifier/cache/` to avoid re-downloading. Cached bundles are reused across sessions.

**Deduplication**: If the same bundle is requested multiple times (diamond dependencies), the registry returns the same instance.

## Bundle Composition

Bundles compose via the `compose()` method or `includes:` declarations:

```python
# Programmatic composition
base = Bundle(name="base", tools=[...])
overlay = Bundle(name="overlay", providers=[...])
composed = base.compose(overlay)

# Declarative composition via includes
---
bundle:
  name: my-bundle
includes:
  - bundle: foundation
  - bundle: my-bundle:behaviors/my-capability
---
```

### Composition Rules

For each section during composition:

- **session/spawn**: Deep merge (nested dicts merged, later wins for scalars)
- **providers/tools/hooks**: Merge by module ID (later config overrides earlier)
- **agents**: Later overrides earlier (by agent name)
- **context**: Accumulates with namespace prefix (each bundle contributes)
- **instruction**: Later replaces earlier

### The Thin Bundle Pattern (Recommended)

Most bundles should be **thin** - inheriting from foundation and adding only their unique capabilities:

```yaml
---
bundle:
  name: my-capability
  version: 1.0.0
  description: Adds X capability

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: my-capability:behaviors/my-capability    # Behavior pattern
---

# My Capability

@my-capability:context/instructions.md

---

@foundation:context/shared/common-system-base.md
```

**Why thin bundles?**
- No duplication of foundation's tools, session config, hooks
- Automatic foundation updates
- Cleaner separation of concerns
- Easier maintenance

### The Behavior Pattern

A **behavior** is a reusable capability add-on that bundles agents + context (and optionally tools/hooks). Behaviors live in `behaviors/` and can be included by any bundle.

```yaml
# behaviors/my-capability.yaml
bundle:
  name: my-capability-behavior
  version: 1.0.0
  description: Adds X capability with agents and context

# Optional: Add tools specific to this capability
tools:
  - module: tool-my-capability
    source: git+https://github.com/org/bundle@main#subdirectory=modules/tool-my-capability

# Declare agents this behavior provides
agents:
  include:
    - my-capability:agent-one
    - my-capability:agent-two

# Declare context files this behavior includes
context:
  include:
    - my-capability:context/instructions.md
```

**Using behaviors:**

```yaml
includes:
  - bundle: foundation
  - bundle: my-capability:behaviors/my-capability   # From same bundle
  - bundle: git+https://github.com/org/bundle@main#subdirectory=behaviors/foo.yaml  # External
```

### Agent Definition Patterns

Both patterns are fully supported:

#### Pattern 1: Include (Recommended)

```yaml
agents:
  include:
    - my-bundle:my-agent      # Loads agents/my-agent.md
```

**Use when**: Agent is self-contained with its own instructions in a separate `.md` file.

#### Pattern 2: Inline (Valid for tool-scoped agents)

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

## Bundle Validation

Bundles are validated during loading:

```python
from amplifier_foundation import validate_bundle, validate_bundle_or_raise

# Validate and get result
result = validate_bundle(bundle)
if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error}")

# Validate and raise on error
validate_bundle_or_raise(bundle)  # Raises BundleValidationError if invalid
```

**Validation checks:**
- Required fields: `bundle.name`, `session.orchestrator`, `session.context` (if session present)
- Module lists: `providers`, `tools`, `hooks` must be lists of dicts with `module` key
- Tool inheritance: `spawn.exclude_tools` and `spawn.inherit_tools` are mutually exclusive

## Bundle Preparation

The `prepare()` method activates all modules, making them importable:

```python
bundle = await load_bundle("git+https://github.com/org/my-bundle@main")

# Prepare bundle (downloads and installs modules)
prepared = await bundle.prepare(install_deps=True)

# Create session from prepared bundle
async with prepared.create_session() as session:
    response = await session.execute("Hello!")

# Or manually:
from amplifier_core import AmplifierSession

session = AmplifierSession(config=prepared.mount_plan)
await session.coordinator.mount("module-source-resolver", prepared.resolver)
await session.initialize()
```

**What prepare() does:**

1. **Install bundle packages**: If the bundle has a `pyproject.toml`, installs it as a Python package
2. **Install included bundle packages**: Installs packages from all bundles in `source_base_paths`
3. **Activate modules**: Downloads and installs all modules (orchestrator, context, providers, tools, hooks)
4. **Create resolver**: Returns a `BundleModuleResolver` for AmplifierSession to use

**Source resolver callback:**

```python
def resolve_with_overrides(module_id: str, source: str) -> str:
    # App-layer policy: override module sources from settings
    return overrides.get(module_id) or source

prepared = await bundle.prepare(source_resolver=resolve_with_overrides)
```

**Progress callback:**

```python
def on_progress(action: str, detail: str):
    print(f"{action}: {detail}")

prepared = await bundle.prepare(progress_callback=on_progress)
```

## Context and Agent Resolution

Bundles track paths for context files and agents:

```python
# Resolve context file
path = bundle.resolve_context_path("my-bundle:context/instructions.md")

# Resolve agent file
path = bundle.resolve_agent_path("my-bundle:my-agent")
# Looks in: source_base_paths["my-bundle"]/agents/my-agent.md

# Resolve pending context (after composition)
bundle.resolve_pending_context()

# Load agent metadata (after composition)
bundle.load_agent_metadata()
```

**Pending context**: Context references with namespace prefixes (e.g., `foundation:context/file.md`) are stored as pending during parsing. After composition, `resolve_pending_context()` resolves them using `source_base_paths`.

**Agent metadata**: `load_agent_metadata()` loads descriptions and other metadata from agent `.md` files. Call after composition when `source_base_paths` is fully populated.

## Mount Plan Generation

Convert a bundle to a mount plan for `AmplifierSession`:

```python
mount_plan = bundle.to_mount_plan()

# Mount plan structure:
{
    "session": {"orchestrator": {...}, "context": {...}},
    "providers": [{...}],
    "tools": [{...}],
    "hooks": [{...}],
    "agents": {...},
    "spawn": {...}
}

# Use with AmplifierSession
session = AmplifierSession(config=mount_plan)
```

## Directory Conventions

Bundle repos follow conventions for maximum reusability:

| Directory | Purpose |
|-----------|---------|
| `/bundle.md` | Root bundle - repo's primary entry point, establishes namespace |
| `/bundles/*.yaml` | Standalone bundles - pre-composed, ready-to-use variants |
| `/behaviors/*.yaml` | Behavior bundles - reusable capabilities to compose onto other bundles |
| `/providers/*.yaml` | Provider bundles - provider configurations |
| `/agents/*.md` | Agent files - specialized agent definitions |
| `/context/*.md` | Context files - shared instructions, knowledge |
| `/modules/` | Local modules - tool implementations specific to this bundle |

**Recommended pattern:**

1. Put your main value in `/behaviors/` (what others compose onto their bundles)
2. Root bundle includes its own behavior (DRY pattern)
3. `/bundles/` offers pre-composed variants (convenience for users)

## Structural vs Conventional Classification

Bundles have two independent classification systems:

| Bundle | Structural | Conventional |
|--------|------------|--------------|
| `/bundle.md` | Root (`is_root=True`) | Root bundle |
| `/bundles/with-anthropic.yaml` | Nested (`is_root=False`) | Standalone bundle |
| `/behaviors/my-capability.yaml` | Nested (`is_root=False`) | Behavior bundle |
| `/providers/anthropic-opus.yaml` | Nested (`is_root=False`) | Provider bundle |

**Structural**: How the bundle is loaded and tracked by the registry
**Conventional**: What role it plays in your bundle architecture

## Common Anti-Patterns

### ❌ Duplicating Foundation

```yaml
# DON'T DO THIS when you include foundation
includes:
  - bundle: foundation

tools:
  - module: tool-filesystem     # Foundation has this!
    source: git+https://...

session:
  orchestrator:                 # Foundation has this!
    module: loop-streaming
```

**Fix**: Remove duplicated declarations. Foundation provides them.

### ❌ Using @ Prefix in YAML

```yaml
# DON'T DO THIS - @ prefix is for markdown only
context:
  include:
    - "@my-bundle:context/instructions.md"   # ❌ @ doesn't belong here

# DO THIS - bare namespace:path in YAML
context:
  include:
    - my-bundle:context/instructions.md      # ✅ No @ in YAML
```

**Why it's wrong**: The `@` prefix is markdown syntax for eager file loading. YAML sections use bare `namespace:path` references. Using `@` in YAML causes **silent failure**.

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

**Why it's wrong**: The namespace is ALWAYS `bundle.name` from the YAML frontmatter, regardless of the git URL or repository name.

## Next Steps

- [Common Patterns](patterns.md) - Practical patterns for using Amplifier Foundation
- [API Reference](api_reference.md) - Complete API documentation
- [Bundle Guide](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md) - Comprehensive guide to creating bundles
