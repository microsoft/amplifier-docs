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

## Composition with includes:

Bundles can inherit from other bundles:

```yaml
includes:
  - bundle: foundation                    # Well-known bundle name
  - bundle: git+https://github.com/...    # Git URL
  - bundle: ./bundles/variant.yaml        # Local file
  - bundle: my-bundle:behaviors/foo       # Behavior within same bundle
```

**Merge rules**:
- Later bundles override earlier ones
- `session`: deep-merged (nested dicts merged recursively, later wins for scalars)
- `spawn`: deep-merged (later overrides earlier)
- `providers`, `tools`, `hooks`: merged by module ID (configs for same module are deep-merged)
- `agents`: merged by agent name (later wins)
- `context`: accumulates with namespace prefix (each bundle contributes without collision)
- Markdown instructions: replace entirely (later wins)

## Bundle Preparation

The `prepare()` method activates all modules for execution:

```python
bundle = await load_bundle("git+https://github.com/org/my-bundle@main")
prepared = await bundle.prepare(
    install_deps=True,
    source_resolver=None,
    progress_callback=None
)

# Use the prepared bundle
async with prepared.create_session() as session:
    response = await session.execute("Hello!")
```

### Parameters

- `install_deps` (bool): Whether to install Python dependencies for modules (default: True)
- `source_resolver` (callable): Optional callback for app-layer source override policy
- `progress_callback` (callable): Optional callback for progress reporting

### What prepare() does

1. Installs bundle packages (if bundle has pyproject.toml)
2. Installs packages from all included bundles
3. Activates all modules (downloads and makes them importable)
4. Pre-activates agent-specific modules for child sessions
5. Creates a module resolver for the session
6. Saves install state for fast subsequent startups

### PreparedBundle

Returns a `PreparedBundle` with:
- `mount_plan`: Configuration dict for AmplifierSession
- `resolver`: Module resolver for finding module paths
- `bundle`: The original Bundle object
- `bundle_package_paths`: Paths to bundle src/ directories

## Session Creation

The `PreparedBundle.create_session()` method creates a fully initialized session:

```python
session = await prepared.create_session(
    session_id=None,           # Optional: for resuming
    parent_id=None,            # Optional: parent session ID
    approval_system=None,      # Optional: approval system
    display_system=None,       # Optional: display system
    session_cwd=None,          # Optional: working directory
    is_resumed=False           # Whether resuming existing session
)
```

### Session Working Directory

The `session_cwd` parameter controls where local @-mentions resolve:
- If provided: Local @-mentions like `@AGENTS.md` resolve relative to `session_cwd`
- If omitted: Falls back to `bundle.base_path`

Apps should pass their project/workspace directory to ensure @-mentions resolve correctly.

### Dynamic System Prompts

Sessions support dynamic system prompt reloading:
- @mentioned files are re-read on every LLM call
- Changes to AGENTS.md or bundle instructions take effect immediately
- No session restart needed for context updates

## Spawning Sub-Sessions

The `PreparedBundle.spawn()` method creates child sessions:

```python
result = await prepared.spawn(
    child_bundle,
    "Task instruction",
    compose=True,              # Compose child with parent bundle
    parent_session=session,    # Parent for lineage tracking
    orchestrator_config=None,  # Override orchestrator settings
    parent_messages=None,      # Inject parent conversation
    provider_preferences=None, # Ordered provider/model fallback
    self_delegation_depth=0    # Depth limiting counter
)
```

### Parameters

- `child_bundle` (Bundle): Pre-resolved bundle to spawn
- `instruction` (str): Task instruction for the sub-session
- `compose` (bool): Whether to compose child with parent (default: True)
- `parent_session`: Parent session for UX inheritance
- `orchestrator_config` (dict): Override orchestrator settings
- `parent_messages` (list): Messages to inject into child context
- `provider_preferences` (list[ProviderPreference]): Ordered provider/model fallback chain
- `self_delegation_depth` (int): Current delegation depth for limiting

### Provider Preferences

Provider preferences enable fallback chains with glob pattern support:

```python
from amplifier_foundation import ProviderPreference

result = await prepared.spawn(
    child_bundle,
    "Analyze this code",
    provider_preferences=[
        ProviderPreference(provider="anthropic", model="claude-haiku-*"),
        ProviderPreference(provider="openai", model="gpt-5-mini"),
    ]
)
```

The system tries each preference in order until finding an available provider.

### Result Structure

Returns a dict with:
- `output` (str): Response from the sub-session
- `session_id` (str): Sub-session ID (for resuming)
- `status` (str): Completion status (from orchestrator:complete event)
- `turn_count` (int): Number of turns taken
- `metadata` (dict): Additional metadata from orchestrator

## Bundle Registry

The `BundleRegistry` manages bundle loading, caching, and updates:

```python
from amplifier_foundation import BundleRegistry

registry = BundleRegistry(
    home=None,                  # Base directory (default: ~/.amplifier)
    strict=False,               # Raise on include failures vs warn
    include_source_resolver=None  # Custom include resolution
)

# Register bundles
registry.register({
    "foundation": "git+https://github.com/microsoft/amplifier-foundation@main",
    "my-bundle": "./local/bundle.md"
})

# Load a bundle
bundle = await registry.load("foundation")

# Load all registered bundles
bundles = await registry.load()  # Returns dict[str, Bundle]
```

### Registry State

The registry tracks loaded bundles with `BundleState`:

```python
state = registry.get_state("foundation")

# BundleState fields:
# - uri: Original source URI
# - name: Bundle name
# - version: Bundle version
# - loaded_at: Last load timestamp
# - checked_at: Last update check timestamp
# - local_path: Cached local path
# - is_root: True for root bundles, False for nested
# - root_name: For nested bundles, the root bundle name
# - explicitly_requested: True if user explicitly loaded
# - includes: List of bundles this bundle includes
# - included_by: List of bundles that include this bundle
```

### Include Source Resolution

Custom include resolution enables app-layer policies:

```python
def resolve_includes(source: str) -> str | None:
    # Override specific includes
    if source == "private:internal":
        return "git+https://github.com/myorg/internal@main"
    return None  # Use default resolution

registry = BundleRegistry(include_source_resolver=resolve_includes)
```

### Update Checking

Check for bundle updates:

```python
# Check single bundle
update_info = await registry.check_update("foundation")
if update_info:
    print(f"Update available: {update_info.current_version} -> {update_info.available_version}")

# Check all bundles
updates = await registry.check_update()  # Returns list[UpdateInfo]
```

### Persistence

Registry state is automatically persisted to `home/registry.json`:

```python
# Save current state
registry.save()

# State is automatically loaded on init from disk
```

## Validation

Validate bundle structure before loading:

```python
from amplifier_foundation import validate_bundle_or_raise

# Raises BundleValidationError if invalid
validate_bundle_or_raise(bundle)

# Or get validation result
from amplifier_foundation import validate_bundle

result = validate_bundle(bundle)
if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error}")
```

## Module Resolution

Modules are resolved through multiple mechanisms:

1. **Python entry points**: `amplifier.modules` group in pyproject.toml
2. **Source URIs**: Git URLs, file paths, or package names
3. **Module resolver**: BundleModuleResolver for activated modules

### Lazy Activation

The `BundleModuleResolver` supports lazy activation:

```python
# Modules not in initial activation set can be activated on-demand
# This is used for agent-specific modules
path = await resolver.async_resolve(
    module_id="tool-custom",
    source_hint="git+https://github.com/org/tool-custom@main"
)
```

## Best Practices

### Use Thin Bundles

When including foundation, don't redeclare what it provides:

```yaml
# ✓ GOOD: Thin bundle
includes:
  - bundle: foundation
  - bundle: my-bundle:behaviors/my-capability

# ✗ BAD: Fat bundle duplicating foundation
includes:
  - bundle: foundation
session:              # Foundation already defines this!
  orchestrator: ...
tools:                # Foundation already has these!
  - module: tool-bash
```

### Consolidate Instructions

Put instructions in `context/instructions.md`, not inline in bundle.md:

```yaml
# behaviors/my-capability.yaml
context:
  include:
    - my-capability:context/instructions.md
```

### Use Behaviors for Reusability

Package agents + context in `behaviors/` so others can include just your capability:

```yaml
# behaviors/my-capability.yaml
bundle:
  name: my-capability-behavior

tools:
  - module: tool-my-capability
    source: ./modules/tool-my-capability

agents:
  include:
    - my-capability:agent-one

context:
  include:
    - my-capability:context/instructions.md
```

### No @ Prefix in YAML

The `@` prefix is markdown syntax only. In YAML sections, use bare `namespace:path`:

```yaml
# ✓ GOOD
context:
  include:
    - my-bundle:context/instructions.md

# ✗ BAD
context:
  include:
    - "@my-bundle:context/instructions.md"  # @ doesn't belong in YAML
```

### Use bundle.name as Namespace

The namespace is always `bundle.name`, not the repository name:

```yaml
# If bundle.name is "recipes"
agents:
  include:
    - recipes:recipe-author  # ✓ Use bundle.name
    - amplifier-bundle-recipes:recipe-author  # ✗ Don't use repo name
```

## Advanced Patterns

### Context Deduplication

The system uses SHA-256 content deduplication to avoid loading the same file multiple times:

```python
# If multiple @mentions reference the same file content,
# it's loaded once and reused
deduplicator = ContentDeduplicator()
```

### Mention Resolution

@mentions are resolved using the `MentionResolver`:

```python
from amplifier_foundation import BaseMentionResolver

resolver = BaseMentionResolver(
    bundles={"foundation": foundation_bundle},
    base_path=Path("/project")
)

results = await load_mentions("See @foundation:docs/GUIDE.md", resolver)
```

### Load-on-Demand (Soft References)

Reference files without `@` to defer loading:

```markdown
**Documentation (load on demand):**
- Schema: recipes:docs/RECIPE_SCHEMA.md
- Guide: foundation:docs/BUNDLE_GUIDE.md
```

The AI can load these on-demand via `read_file` when actually needed.

## Troubleshooting

### Module not found

- Verify `source:` path is correct relative to bundle location
- Check module has `pyproject.toml` with entry point
- Ensure `mount()` function exists in module

### Agent not loading

- Verify `meta:` frontmatter exists with `name` and `description`
- Check agent file is in `agents/` directory
- Verify `agents: include:` uses correct namespace prefix

### @mentions not resolving

- Verify file exists at the referenced path
- Check namespace matches bundle name
- Ensure path is relative to bundle root

### Circular dependencies

The registry detects and skips circular includes automatically. Check logs for warnings about circular dependencies.
