---
title: Bundle System Deep Dive
description: Loading, composition, validation, and preparation
---

# Bundle System Deep Dive

Detailed guide to the bundle system: loading, composition, validation, and preparation. For the mental model, see [Core Concepts](concepts.md).

For complete bundle creation guidance, see [BUNDLE_GUIDE.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md) in the amplifier-foundation repository.

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

Bundles compose via the `includes:` directive. Later bundles override earlier ones.

### Merge Rules

- **`session`**: Deep-merged (nested dicts merged recursively, later wins for scalars)
- **`spawn`**: Deep-merged (later overrides earlier)
- **`providers`, `tools`, `hooks`**: Merged by module ID (configs for same module are deep-merged)
- **`agents`**: Merged by agent name (later wins)
- **`context`**: Accumulates with namespace prefix (each bundle contributes without collision)
- **Markdown instructions**: Replace entirely (later wins)

### Composition Example

```python
from amplifier_foundation import load_bundle

base = await load_bundle("foundation")
overlay = await load_bundle("./my-customizations.md")
composed = base.compose(overlay)
```

## Validation

The `BundleValidator` checks bundle structure:

```python
from amplifier_foundation import validate_bundle

result = validate_bundle(bundle)
if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error}")
```

### Validation Rules

- Bundle name must be a valid identifier
- Includes must be valid URIs
- Module sources must be valid URIs
- Agent references must resolve
- Context references must resolve
- No circular includes

## Preparation

Before mounting, bundles are prepared:

1. **Resolve includes** - Load and compose included bundles
2. **Resolve @mentions** - Load referenced files into instruction
3. **Validate structure** - Check all references resolve
4. **Build mount plan** - Create final configuration for session

## Registry Management

The `BundleRegistry` manages named bundles:

```python
from amplifier_foundation import BundleRegistry

registry = BundleRegistry()
registry.register({"foundation": "git+https://github.com/microsoft/amplifier-foundation@main"})
bundle = await registry.load("foundation")
```

### Registry Features

- **Named bundles** - Register bundles by name
- **Caching** - Downloaded bundles cached locally
- **Update checking** - Check for available updates
- **Dependency tracking** - Track includes relationships

## Best Practices

### Use the Thin Bundle Pattern

When including foundation, don't redeclare what it provides. Your bundle.md should be minimal.

```yaml
# ✅ GOOD: Thin bundle inherits from foundation
---
bundle:
  name: my-capability
  version: 1.0.0

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: my-capability:behaviors/my-capability    # Behavior pattern
---

# My Capability

@my-capability:context/instructions.md

---

@foundation:context/shared/common-system-base.md
```

### Create Behaviors for Reusability

Package your agents + context in `behaviors/` so others can include just your capability.

```yaml
# behaviors/my-capability.yaml
bundle:
  name: my-capability-behavior
  version: 1.0.0
  description: Adds X capability with agents and context

agents:
  include:
    - my-capability:agent-one
    - my-capability:agent-two

context:
  include:
    - my-capability:context/instructions.md
```

### Consolidate Instructions

Put instructions in `context/instructions.md`, not inline in bundle.md.

```markdown
# context/instructions.md
# My Capability Instructions

You have access to the my-capability tool...

## Usage

[Detailed instructions]

## Agents Available

[Agent descriptions]
```

Reference from bundle.md:

```markdown
@my-capability:context/instructions.md
```

### Load-on-Demand Pattern

Not all context needs to load at session start. Use **soft references** (text without `@`) to make content available without consuming tokens until needed.

```markdown
**Documentation (load on demand):**
- Schema: recipes:docs/RECIPE_SCHEMA.md
- Examples: recipes:examples/code-review-recipe.yaml
- Guide: foundation:docs/BUNDLE_GUIDE.md
```

The AI can load these via `read_file` when actually needed.

## See Also

- **[BUNDLE_GUIDE.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md)** - Complete bundle creation guide
- **[Core Concepts](concepts.md)** - Bundle mental model
- **[API Reference](api_reference.md)** - Programmatic API
