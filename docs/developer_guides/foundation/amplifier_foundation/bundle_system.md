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

### Loading from CLI

```bash
# Load from local file
amplifier run --bundle ./bundle.md "prompt"

# Load from git URL
amplifier run --bundle git+https://github.com/org/amplifier-bundle-foo@main "prompt"
```

## Composition

Bundles can be **composed** to layer configuration. Later bundles override earlier ones.

### includes Directive

```yaml
includes:
  - bundle: foundation                    # Well-known bundle name
  - bundle: git+https://github.com/...    # Git URL
  - bundle: ./bundles/variant.yaml        # Local file
  - bundle: my-bundle:behaviors/foo       # Behavior within same bundle
```

### Merge Rules

| Section | Rule |
|---------|------|
| `session` | Deep-merged (nested dicts merged recursively, later wins for scalars) |
| `spawn` | Deep-merged (later overrides earlier) |
| `providers` | Merged by module ID (configs for same module are deep-merged) |
| `tools` | Merged by module ID (configs for same module are deep-merged) |
| `hooks` | Merged by module ID (configs for same module are deep-merged) |
| `agents` | Merged by agent name (later wins) |
| `context` | Accumulates with namespace prefix (each bundle contributes without collision) |
| Markdown instructions | Replace entirely (later wins) |

**Module ID merge**: Same ID = deep-merge config, new ID = add to list.

### The Thin Bundle Pattern

**Most bundles should be thin** — inheriting from foundation and adding only their unique capabilities:

```yaml
# GOOD: Thin bundle inherits from foundation
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

Don't redeclare tools, session config, or hooks that foundation already provides. This duplication creates maintenance burden, can cause version conflicts, and misses foundation updates automatically.

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
    source: git+https://github.com/microsoft/amplifier-bundle-my-capability@main#subdirectory=modules/tool-my-capability

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

Include a behavior in your bundle:

```yaml
includes:
  - bundle: foundation
  - bundle: my-capability:behaviors/my-capability   # From same bundle
  - bundle: git+https://github.com/org/bundle@main#subdirectory=behaviors/foo.yaml  # External
```

### Agent Definition Patterns

Both **include** and **inline** patterns are supported:

```yaml
# Pattern 1: Include (recommended for most cases)
agents:
  include:
    - my-bundle:my-agent      # Loads agents/my-agent.md

# Pattern 2: Inline (valid for tool-scoped agents)
agents:
  my-agent:
    description: "Agent with bundle-specific tool access"
    instructions: my-bundle:agents/my-agent.md
    tools:
      - module: tool-special    # This agent gets specific tools
        source: ./modules/tool-special
```

| Scenario | Pattern | Why |
|----------|---------|-----|
| Standard agent with own instructions | Include | Cleaner separation, context sink pattern |
| Agent needs specific tools | Inline | Can specify `tools:` for just this agent |
| Agent reused across bundles | Include | Separate file is more portable |
| Agent tightly coupled to bundle | Inline | Keep definition with bundle config |

### context.include vs @mentions

These two patterns have **different composition behavior** and are **NOT interchangeable**:

| Pattern | Composition Behavior | Use When |
|---------|---------------------|----------|
| `context.include` | **ACCUMULATES** — content propagates to including bundles | Behaviors that inject context into parents |
| `@mentions` | **REPLACES** — stays with this instruction only | Direct references in your own instruction |

**Use `context.include` in behaviors** (`.yaml` files) — context propagates to including bundles.
**Use `@mentions` in root bundles** (`.md` files) — stays with this instruction.

If you use `context.include` in a root bundle.md, that context will propagate to any bundle that includes yours. If you use `@mentions` in a behavior, the instruction (containing the @mention) **replaces** during composition and your @mention may get overwritten.

### App-Level Runtime Injection

Bundles define **what** capabilities exist. Apps inject **how** they run at runtime:

| Injection | Source | Example |
|-----------|--------|---------|
| Provider configs | `settings.yaml` providers | API keys, model selection |
| Tool configs | `settings.yaml` modules.tools | `allowed_write_paths` for filesystem |
| Session overrides | Session-scoped settings | Temporary path permissions |

Tool configs are **deep-merged by module ID** — your settings extend the bundle's config, not replace it.

**Don't declare in bundles:** provider API keys or model preferences, environment-specific paths, or user preferences. These are app-layer concerns.

The full composition chain:

```
Foundation → Your bundle → App settings → Session overrides
    ↓            ↓              ↓               ↓
 (tools)     (agents)     (providers,      (temporary
                          tool configs)     permissions)
```

## Validation

Bundles are validated for structure and completeness.

### Programmatic Validation

```python
from amplifier_foundation import validate_bundle, validate_bundle_or_raise

# Get validation result
result = validate_bundle(bundle)
if not result.valid:
    for error in result.errors:
        print(f"Error: {error}")
    for warning in result.warnings:
        print(f"Warning: {warning}")

# Or raise on error
validate_bundle_or_raise(bundle)  # Raises BundleValidationError
```

| Export | Source | Purpose |
|--------|--------|---------|
| `BundleValidator` | `validator.py` | Bundle structure validation |
| `ValidationResult` | `validator.py` | Validation result with errors/warnings |
| `validate_bundle` | `validator.py` | Validate bundle, return result |
| `validate_bundle_or_raise` | `validator.py` | Validate bundle, raise on error |

### Module List Validation

Module lists (`providers`, `tools`, `hooks`) are validated during `Bundle.from_dict()` parsing:

- Must be a list (not a dict or string)
- Each item must be a dict with `module` and `source` keys
- Relative source paths (starting with `./` or `../`) are resolved at parse time against the bundle's `base_path`

Invalid module lists raise `BundleValidationError` with descriptive messages showing the correct format.

## Preparation

A **PreparedBundle** is a bundle ready for execution with all modules activated.

### Bundle.prepare()

```python
bundle = await load_bundle("/path/to/bundle.md")
prepared = await bundle.prepare()  # Downloads and activates modules
async with prepared.create_session() as session:
    response = await session.execute("Hello!")
```

`prepare()` performs:

1. **Compiles mount plan** from bundle configuration via `to_mount_plan()`
2. **Installs bundle packages** — bundles with `pyproject.toml` are installed first so modules can import from them
3. **Activates all modules** — downloads from git URLs, installs dependencies, makes importable
4. **Creates module resolver** — maps module IDs to their local paths for the kernel

### Source Resolution Override

Apps can inject source-resolution policy without foundation knowing about settings:

```python
def resolve_with_overrides(module_id: str, source: str) -> str:
    return overrides.get(module_id) or source

prepared = await bundle.prepare(source_resolver=resolve_with_overrides)
```

### PreparedBundle

The `PreparedBundle` provides:

| Attribute | Purpose |
|-----------|---------|
| `mount_plan` | Configuration dict for `AmplifierSession` |
| `resolver` | Module resolver mapping IDs to local paths |
| `bundle` | Original Bundle for spawning support |
| `bundle_package_paths` | Paths to bundle `src/` directories on `sys.path` |

Key methods:

- `create_session()` — Creates an initialized `AmplifierSession` with resolver mounted, working directory capability registered, and system prompt factory configured
- `spawn()` — Spawns a sub-session with a child bundle, handling composition, module mounting, provider preferences, context inheritance, and working directory propagation

### Spawning Sub-Sessions

```python
from amplifier_foundation.spawn_utils import ProviderPreference

result = await prepared.spawn(
    child_bundle,
    "Find the bug in auth.py",
    provider_preferences=[
        ProviderPreference(provider="anthropic", model="claude-haiku-*"),
        ProviderPreference(provider="openai", model="gpt-4o-mini"),
    ],
)
# result: {"output": "...", "session_id": "...", "status": "success", "turn_count": 1}
```

The `spawn()` method supports:

- `compose` — Whether to compose child with parent bundle (default `True`)
- `parent_session` — Parent session for lineage tracking and UX inheritance
- `session_id` — Resume existing sub-session
- `orchestrator_config` — Override orchestrator settings for this spawn
- `parent_messages` — Inject parent's conversation history into child context
- `session_cwd` — Override working directory for the spawned session
- `provider_preferences` — Ordered list of provider/model preferences with glob pattern support

## BundleRegistry

The `BundleRegistry` is the central bundle management system for the Amplifier ecosystem. Handles registration, loading, caching, and update checking.

### Initialization

```python
from amplifier_foundation import BundleRegistry

registry = BundleRegistry()  # Uses ~/.amplifier by default
registry = BundleRegistry(home=Path("/custom/home"))
registry = BundleRegistry(strict=True)  # Raise on include failures
```

Home directory resolves in order:

1. Explicit `home` parameter
2. `AMPLIFIER_HOME` env var
3. `~/.amplifier` (default)

Structure under home:

```
home/
├── registry.json   # Persisted state
└── cache/          # Cached remote bundles
```

### Registration and Discovery

```python
# Register bundles
registry.register({"foundation": "git+https://github.com/microsoft/amplifier-foundation@main"})

# Look up URI
uri = registry.find("foundation")

# List all registered
names = registry.list_registered()

# Remove
registry.unregister("my-bundle")
```

### Loading

```python
# Load single bundle by name
bundle = await registry.load("foundation")

# Load by URI (auto-registers by extracted name)
bundle = await registry.load("git+https://github.com/org/bundle@main")

# Load all registered bundles
all_bundles = await registry.load()  # Returns dict[str, Bundle]
```

Loading handles:

- **Include resolution** — recursively loads and composes included bundles
- **Cycle detection** — detects circular dependencies per loading chain
- **Diamond deduplication** — concurrent loads of the same URI share a single future
- **Nested bundle detection** — walks up directory tree to find root bundles and register namespaces
- **Namespace preloading** — ensures namespace bundles are loaded before resolving `namespace:path` includes

### BundleState

Each registered bundle has tracked state:

```python
state = registry.get_state("foundation")
# state.uri, state.name, state.version
# state.loaded_at, state.checked_at
# state.local_path, state.is_root, state.root_name
# state.includes, state.included_by
# state.explicitly_requested, state.app_bundle
```

| Field | Purpose |
|-------|---------|
| `is_root` | `True` for root bundles, `False` for nested bundles |
| `root_name` | For nested bundles, the containing root bundle's name |
| `includes` | Bundles this bundle includes |
| `included_by` | Bundles that include this bundle |
| `explicitly_requested` | `True` if user explicitly requested (bundle use/add) |
| `app_bundle` | `True` if this is an app bundle (always composed) |

### Persistence

Registry state persists to `{home}/registry.json`:

```python
registry.save()  # Persist current state
```

On startup, the registry loads persisted state and validates cached paths (clearing stale references to paths that no longer exist).

## Directory Conventions

Bundle repos follow **conventions** that enable maximum reusability and composition. These are patterns, not code-enforced rules.

| Directory | Convention Name | Purpose |
|-----------|-----------------|---------| 
| `/bundle.md` | **Root bundle** | Repo's primary entry point, establishes namespace |
| `/bundles/*.yaml` | **Standalone bundles** | Pre-composed, ready-to-use variants (e.g., "with-anthropic") |
| `/behaviors/*.yaml` | **Behavior bundles** | "The value this repo provides" — compose onto YOUR bundle |
| `/providers/*.yaml` | **Provider bundles** | Provider configurations to compose |
| `/agents/*.md` | **Agent files** | Specialized agent definitions |
| `/context/*.md` | **Context files** | Shared instructions, knowledge |
| `/modules/` | **Local modules** | Tool implementations specific to this bundle |
| `/docs/` | **Documentation** | Guides, references, examples |

### Recommended Pattern

1. **Put your main value in `/behaviors/`** — this is what others compose onto their bundles
2. **Root bundle includes its own behavior** — DRY, root bundle stays thin
3. **`/bundles/` offers pre-composed variants** — convenience for users who want ready-to-run combinations

**Key insight**: Bundles are **configuration**, not Python packages. A bundle repo does not need a root `pyproject.toml`. Only modules inside `modules/` need their own `pyproject.toml`.

## Anti-Patterns

### Duplicating Foundation

Don't redeclare tools, session config, or hooks that foundation provides when you include it. Remove duplicated declarations.

### Inline Instructions in bundle.md

Move lengthy instructions to `context/instructions.md` and reference with `@my-bundle:context/instructions.md`.

### Skipping the Behavior Pattern

If your bundle adds agents + context, create a behavior in `behaviors/`. Without a behavior, your capability can't be added to other bundles without including your whole bundle.

### Using @ Prefix in YAML

```yaml
# WRONG — @ prefix is for markdown only
context:
  include:
    - "@my-bundle:context/instructions.md"   # @ doesn't belong here

# CORRECT — bare namespace:path in YAML
context:
  include:
    - my-bundle:context/instructions.md      # No @ in YAML
```

The `@` prefix is **only** for markdown text that gets processed during instruction loading. YAML sections use bare `namespace:path` references. Using `@` in YAML causes **silent failure**.

### Using Repository Name as Namespace

The namespace is ALWAYS `bundle.name` from the YAML frontmatter, regardless of the git URL, repository name, or file path.

```yaml
# If bundle.name in that repo is: "recipes"

# WRONG
agents:
  include:
    - amplifier-bundle-recipes:recipe-author   # Repo name

# CORRECT
agents:
  include:
    - recipes:recipe-author                    # bundle.name value
```

### Declaring amplifier-core as Runtime Dependency

Tool modules run inside the host application's process, which already has `amplifier-core` loaded. Don't declare it as a dependency — it's a **peer dependency** provided by the runtime environment.

## Reference

- [BUNDLE_GUIDE.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/BUNDLE_GUIDE.md) — Complete bundle creation guide
- [Core Concepts](concepts.md) — Mental model and structural concepts
- [URI_FORMATS.md](https://github.com/microsoft/amplifier-foundation/blob/main/docs/URI_FORMATS.md) — Source URI reference
- [Examples](examples/) — Practical usage examples
