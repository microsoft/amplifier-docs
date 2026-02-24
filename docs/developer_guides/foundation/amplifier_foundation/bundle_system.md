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
  exclude_tools: [tool-task]  # Agents inherit all EXCEPT these
  # OR
  # tools: [tool-a, tool-b]   # Agents get ONLY these

agents:
  include:
    - my-bundle:agent-name    # Loads from agents/ directory
---

# System Instructions

You are an AI assistant with the following capabilities...

[Markdown body becomes system instruction]
```

## The Thin Bundle Pattern (Recommended)

**Most bundles should be thin** - inheriting from foundation and adding only their unique capabilities.

### The Problem

When creating bundles that include foundation, a common mistake is to **redeclare things foundation already provides**:

```yaml
# ❌ BAD: Fat bundle that duplicates foundation
includes:
  - bundle: foundation

session:              # ❌ Foundation already defines this!
  orchestrator:
    module: loop-streaming
    source: git+https://github.com/...
  context:
    module: context-simple

tools:                # ❌ Foundation already has these!
  - module: tool-filesystem
    source: git+https://github.com/...
  - module: tool-bash
    source: git+https://github.com/...
```

This duplication:
- Creates maintenance burden (update in two places)
- Can cause version conflicts
- Misses foundation updates automatically

### The Solution: Thin Bundles

A **thin bundle** only declares what it uniquely provides:

```yaml
# ✅ GOOD: Thin bundle inherits from foundation
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

**That's it.** All tools, session config, and hooks come from foundation.

### Exemplar: amplifier-bundle-recipes

See [amplifier-bundle-recipes](https://github.com/microsoft/amplifier-bundle-recipes) for the canonical example - only 14 lines of YAML!

**Key observations**:
- No `tools:`, `session:`, or `hooks:` declarations (inherited from foundation)
- Uses behavior pattern for its unique capabilities
- References consolidated instructions file
- Minimal markdown body

## The Behavior Pattern

A **behavior** is a reusable capability add-on that bundles agents + context (and optionally tools/hooks). Behaviors live in `behaviors/` and can be included by any bundle.

### Why Behaviors?

Behaviors enable:
- **Reusability** - Add capability to any bundle
- **Modularity** - Separate concerns cleanly
- **Composition** - Mix and match behaviors

### Behavior File Structure

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

### Using Behaviors

Include a behavior in your bundle:

```yaml
includes:
  - bundle: foundation
  - bundle: my-capability:behaviors/my-capability   # From same bundle
  - bundle: git+https://github.com/org/bundle@main#subdirectory=behaviors/foo.yaml  # External
```

### Agent Definition Patterns: Include vs Inline

**Both patterns are fully supported** by the code. Choose based on your needs:

#### Pattern 1: Include (Recommended for most cases)

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

#### When to Use Each

| Scenario | Pattern | Why |
|----------|---------|-----|
| Standard agent with own instructions | Include | Cleaner separation, context sink pattern |
| Agent needs specific tools | Inline | Can specify `tools:` for just this agent |
| Agent reused across bundles | Include | Separate file is more portable |
| Agent tightly coupled to bundle | Inline | Keep definition with bundle config |

**Key insight**: The code in `bundle.py:_parse_agents()` explicitly handles both patterns. Neither pattern is deprecated. Both are intentional design choices for different use cases.

## Context De-duplication

**Consolidate instructions into a single file** rather than inline in bundle.md.

### The Problem

Inline instructions in bundle.md cause:
- Duplication if behavior also needs to reference them
- Large bundle.md files that are hard to maintain
- Harder to reuse context across bundles

### The Solution: Consolidated Context Files

Create `context/instructions.md` with all the instructions:

```markdown
# My Capability Instructions

You have access to the my-capability tool...

## Usage

[Detailed instructions]

## Agents Available

[Agent descriptions]
```

Reference it from your behavior:

```yaml
# behaviors/my-capability.yaml
context:
  include:
    - my-capability:context/instructions.md
```

And from your bundle.md:

```markdown
---
bundle:
  name: my-capability
includes:
  - bundle: foundation
  - bundle: my-capability:behaviors/my-capability
---

# My Capability

@my-capability:context/instructions.md

---

@foundation:context/shared/common-system-base.md
```

## Directory Conventions

Bundle repos follow **conventions** that enable maximum reusability and composition. These are patterns, not code-enforced rules.

> **Structural vs Conventional**: Bundles have two independent classification systems. For **structural** concepts (root bundles, nested bundles, namespace registration), see [Core Concepts](concepts.md). This section covers **conventional** organization patterns.

### Standard Directory Layout

| Directory | Convention Name | Purpose |
|-----------|-----------------|---------|
| `/bundle.md` | **Root bundle** | Repo's primary entry point, establishes namespace |
| `/bundles/*.yaml` | **Standalone bundles** | Pre-composed, ready-to-use variants (e.g., "with-anthropic") |
| `/behaviors/*.yaml` | **Behavior bundles** | "The value this repo provides" - compose onto YOUR bundle |
| `/providers/*.yaml` | **Provider bundles** | Provider configurations to compose |
| `/agents/*.md` | **Agent files** | Specialized agent definitions |
| `/context/*.md` | **Context files** | Shared instructions, knowledge |
| `/modules/` | **Local modules** | Tool implementations specific to this bundle |
| `/docs/` | **Documentation** | Guides, references, examples |

### Directory Purposes

**Root bundle** (`/bundle.md`): The primary entry point for your bundle. Establishes the namespace (from `bundle.name`) and typically includes its own behavior for DRY. This is both structurally a "root bundle" and conventionally the main entry point.

**Standalone bundles** (`/bundles/*.yaml`): Pre-composed variants ready to use as-is. Typically combine the root bundle with a provider choice. Examples: `with-anthropic.yaml`, `minimal.yaml`. These are structurally "nested bundles" (loaded via `namespace:bundles/foo`) but conventionally "standalone" because they're complete and ready to use.

**Behavior bundles** (`/behaviors/*.yaml`): The reusable capability this repo provides. When someone wants to add your capability to THEIR bundle, they include your behavior. Contains agents, context, and optionally tools. The root bundle should include its own behavior (DRY pattern).

**Provider bundles** (`/providers/*.yaml`): Provider configurations that can be composed onto other bundles. Allows users to choose which provider to use without the bundle author making that decision.

### The Recommended Pattern

1. **Put your main value in `/behaviors/`** - this is what others compose onto their bundles
2. **Root bundle includes its own behavior** - DRY, root bundle stays thin
3. **`/bundles/` offers pre-composed variants** - convenience for users who want ready-to-run combinations

```yaml
# bundle.md (root) - thin, includes own behavior
bundle:
  name: my-capability
  version: 1.0.0

includes:
  - bundle: foundation
  - bundle: my-capability:behaviors/my-capability  # DRY: include own behavior
```

```yaml
# bundles/with-anthropic.yaml - standalone variant
bundle:
  name: my-capability-anthropic
  version: 1.0.0

includes:
  - bundle: my-capability                           # Root already has behavior
  - bundle: foundation:providers/anthropic-opus     # Add provider choice
```

### Structural vs Conventional Classification

A bundle can be classified in BOTH systems independently:

| Bundle | Structural | Conventional |
|--------|------------|--------------|
| `/bundle.md` | Root (`is_root=True`) | Root bundle |
| `/bundles/with-anthropic.yaml` | Nested (`is_root=False`) | Standalone bundle |
| `/behaviors/my-capability.yaml` | Nested (`is_root=False`) | Behavior bundle |
| `/providers/anthropic-opus.yaml` | Nested (`is_root=False`) | Provider bundle |

**Key insight:** A "standalone bundle" (conventional) is still a "nested bundle" (structural) when loaded via `namespace:bundles/foo.yaml`. These aren't contradictions—they describe different aspects.

## Bundle Directory Structure

### Thin Bundle (Recommended)

```
my-bundle/
├── bundle.md                 # Thin: includes + context refs only
├── behaviors/
│   └── my-capability.yaml    # Reusable behavior
├── agents/                   # Agent definitions
│   ├── agent-one.md
│   └── agent-two.md
├── context/
│   └── instructions.md       # Consolidated instructions
├── docs/                     # Additional documentation
├── README.md
├── LICENSE
├── SECURITY.md
└── CODE_OF_CONDUCT.md
```

### Bundle with Local Modules

```
my-bundle/
├── bundle.md
├── behaviors/
│   └── my-capability.yaml
├── agents/
├── context/
├── modules/                  # Local modules (when needed)
│   └── tool-my-capability/
│       ├── pyproject.toml    # Module's package config
│       └── my_module/
├── docs/
├── README.md
└── ...
```

**Note**: No `pyproject.toml` at the root. Only modules inside `modules/` need their own `pyproject.toml`.

## Composition

Bundles compose via the `includes:` field:

```python
# Programmatic composition
base = Bundle(name="base", ...)
overlay = Bundle(name="overlay", ...)
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

## Validation

Validate bundles before loading:

```python
from amplifier_foundation import validate_bundle

result = validate_bundle("./bundle.md")

if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error}")
    for warning in result.warnings:
        print(f"Warning: {warning}")
```

## Preparation

Prepare bundles for execution:

```python
from amplifier_foundation import load_bundle

# Load bundle
bundle = await load_bundle("./bundle.md")

# Prepare (downloads modules, resolves dependencies)
prepared = await bundle.prepare()

# Create session
async with prepared.create_session() as session:
    response = await session.execute("Hello!")
```

## Creating a Bundle Step-by-Step

### Step 1: Decide Your Pattern

**Ask yourself**:
- Does my bundle add capability to foundation? → **Use thin bundle + behavior pattern**
- Is my bundle standalone (no foundation dependency)? → Declare everything you need
- Do I want my capability reusable by other bundles? → **Create a behavior**

### Step 2: Create Behavior (if adding to foundation)

Create `behaviors/my-capability.yaml`:

```yaml
bundle:
  name: my-capability-behavior
  version: 1.0.0
  description: Adds X capability

agents:
  include:
    - my-capability:my-agent

context:
  include:
    - my-capability:context/instructions.md
```

### Step 3: Create Consolidated Instructions

Create `context/instructions.md`:

```markdown
# My Capability Instructions

You have access to the my-capability tool for [purpose].

## Available Agents

- **my-agent** - Does X, useful for Y

## Usage Guidelines

[Instructions for the AI on how to use this capability]
```

### Step 4: Create Agent Definitions

Place agent files in `agents/` with proper frontmatter:

```markdown
---
meta:
  name: my-agent
  description: "Description shown when listing agents. Include usage examples..."
---

# My Agent

You are a specialized agent for [specific purpose].

## Your Capabilities

[Agent-specific instructions]
```

### Step 5: Create Thin bundle.md

```markdown
---
bundle:
  name: my-capability
  version: 1.0.0
  description: Provides X capability

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: my-capability:behaviors/my-capability
---

# My Capability

@my-capability:context/instructions.md

---

@foundation:context/shared/common-system-base.md
```

### Step 6: Add README and Standard Files

Create README.md documenting:
- What the bundle provides
- The architecture (thin bundle + behavior pattern)
- How to load/use it

## Anti-Patterns to Avoid

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

**Why it's bad**: Creates maintenance burden, version conflicts, misses foundation updates.

**Fix**: Remove duplicated declarations. Foundation provides them.

### ❌ Inline Instructions in bundle.md

```yaml
---
bundle:
  name: my-bundle
---

# Instructions

[500 lines of instructions here]

## Usage

[More instructions]
```

**Why it's bad**: Can't be reused by behavior, hard to maintain, can't be referenced separately.

**Fix**: Move to `context/instructions.md` and reference with `@my-bundle:context/instructions.md`.

### ❌ Skipping the Behavior Pattern

```yaml
# DON'T DO THIS for capability bundles
---
bundle:
  name: my-capability

includes:
  - bundle: foundation

agents:
  include:
    - my-capability:agent-one
    - my-capability:agent-two
---

[All instructions inline]
```

**Why it's bad**: Your capability can't be added to other bundles without including your whole bundle.

**Fix**: Create `behaviors/my-capability.yaml` with agents + context, then include it.

### ❌ Using @ Prefix in YAML

```yaml
# DON'T DO THIS - @ prefix is for markdown only
context:
  include:
    - "@my-bundle:context/instructions.md"   # ❌ @ doesn't belong here

agents:
  include:
    - "@my-bundle:my-agent"                  # ❌ @ doesn't belong here
```

```yaml
# DO THIS - bare namespace:path in YAML
context:
  include:
    - my-bundle:context/instructions.md   # ✅ No @ prefix

agents:
  include:
    - my-bundle:my-agent                  # ✅ No @ prefix
```

**Why it's bad**: `@` is markdown syntax for mention resolution. In YAML, use bare `namespace:path`.

## Next Steps

- [Core Concepts](concepts.md) - Mental model for bundles
- [Common Patterns](patterns.md) - Practical usage patterns
- [API Reference](api_reference.md) - Complete API documentation
- [Examples](examples/index.md) - Progressive examples from hello world to production
