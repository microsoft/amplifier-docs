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

# Strict mode: include failures raise exceptions instead of logging warnings (useful for CI)
bundle = await load_bundle("git+https://github.com/org/my-bundle@main", strict=True)
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

`bundle.prepare()` downloads and installs all modules specified in the mount plan, making them importable. Returns a `PreparedBundle` containing `mount_plan` and a `BundleModuleResolver` for use with `AmplifierSession`.

```python
# Standard preparation
prepared = await bundle.prepare()

# Skip package installation (use pre-installed modules)
prepared = await bundle.prepare(install_deps=False)

# With source override policy (app-layer module routing)
def resolve_with_overrides(module_id: str, source: str) -> str:
    return overrides.get(module_id) or source

prepared = await bundle.prepare(source_resolver=resolve_with_overrides)
```

**Parameters:**

- `install_deps` (`bool`, default `True`) — Whether to install Python dependencies for modules.
- `source_resolver` (`Callable[[str, str], str] | None`) — Optional callback `(module_id, original_source) -> resolved_source`. Allows app-layer source override policy to be applied before activation.
- `progress_callback` (`Callable[[str, str], None] | None`) — Optional callback `(action, detail)` for progress reporting. Actions include `"installing_package"`, `"activating"`, `"installing"`.

Use `prepared.create_session()` to create an `AmplifierSession`:

```python
prepared = await bundle.prepare()
async with prepared.create_session() as session:
    response = await session.execute("Hello!")
```

Use `prepared.spawn()` to spawn a sub-session with a child bundle:

```python
from amplifier_foundation.bundle import Bundle

# Resolve child bundle
child_bundle = await load_bundle("./agents/bug-hunter.md")

# Spawn sub-session (composed with parent by default)
result = await prepared.spawn(
    child_bundle,
    "Find the bug in auth.py",
)
# Returns: {"output": str, "session_id": str, "status": str, "turn_count": int, "metadata": dict}

# Resume existing sub-session
result = await prepared.spawn(
    child_bundle,
    "Continue investigating",
    session_id=result["session_id"],
)

# Spawn without composition (standalone bundle, no parent merge)
result = await prepared.spawn(
    child_bundle,
    "Do something",
    compose=False,
)

# With provider preferences (fallback chain)
from amplifier_foundation.spawn_utils import ProviderPreference

result = await prepared.spawn(
    child_bundle,
    "Analyze this code",
    provider_preferences=[
        ProviderPreference(provider="anthropic", model="claude-haiku-*"),
        ProviderPreference(provider="openai", model="gpt-5-mini"),
    ],
)
```

**`PreparedBundle.spawn()` parameters:**

- `child_bundle` (`Bundle`) — Bundle to spawn (already resolved by app layer).
- `instruction` (`str`) — Task instruction for the sub-session.
- `compose` (`bool`, default `True`) — Whether to compose child with parent bundle.
- `parent_session` (`Any`, default `None`) — Parent session for lineage tracking and UX inheritance.
- `session_id` (`str | None`) — Optional session ID for resuming an existing session.
- `orchestrator_config` (`dict | None`) — Optional orchestrator config to override/merge (e.g., `min_delay_between_calls_ms`).
- `parent_messages` (`list | None`) — Optional parent messages to inject into child context.
- `session_cwd` (`Path | None`) — Optional working directory override for the child session.
- `provider_preferences` (`list[ProviderPreference] | None`) — Ordered provider/model fallback chain.
- `self_delegation_depth` (`int`, default `0`) — Current delegation depth for depth limiting.

> **Note:** The app layer (CLI, API server) typically wraps `PreparedBundle.spawn()` in a "spawn capability" function that handles additional concerns such as agent name resolution, tool/hook inheritance filtering, and state persistence. See `amplifier-app-cli/session_spawner.py` for the reference production implementation.

## Registry Management

The `BundleRegistry` manages named bundles:

```python
from amplifier_foundation import BundleRegistry

registry = BundleRegistry()
registry.register({"foundation": "git+https://github.com/microsoft/amplifier-foundation@main"})
bundle = await registry.load("foundation")

# Strict mode: include failures raise exceptions instead of logging warnings
registry = BundleRegistry(strict=True)
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
