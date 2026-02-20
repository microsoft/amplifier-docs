---
title: Profiles
description: Pre-configured capability sets for Amplifier
---

# Profiles

Profiles are pre-configured capability sets that define which modules (providers, tools, hooks) are available during a session.

## Profile Concepts

Profiles are defined in Markdown files with YAML frontmatter. They support inheritance via `extends`, overlay merging across search paths, and compilation to Mount Plans for `AmplifierSession`.

## Using Profiles

Profiles are loaded by the application via bundles. In the Amplifier CLI, bundles compose profiles and other configuration:

```bash
# List available bundles (which load profiles)
amplifier bundle list

# Use a specific bundle
amplifier bundle use my-bundle

# Show current bundle
amplifier bundle current

# Show bundle details
amplifier bundle show my-bundle
```

## Profile Contents

### `foundation`

The minimal profile - just LLM access:

- **Provider**: Your configured provider
- **Tools**: None
- **Hooks**: Basic logging

### `base`

Adds essential development tools:

- Everything in `foundation`
- **Tools**: filesystem, bash
- Use for: Basic file operations, running commands

### `dev`

Full development capabilities:

- Everything in `base`
- **Tools**: web, search, task
- **Agents**: explorer, bug-hunter, zen-architect, researcher
- **Hooks**: approval, streaming-ui
- Use for: Day-to-day development work

### `full`

All available features:

- Everything in `dev`
- Additional experimental tools
- All available hooks
- Use for: Testing new features, maximum capability

## Creating Custom Profiles

Profiles are YAML files with markdown frontmatter.

### Profile Location

Profiles are loaded from (in order):

1. `.amplifier/profiles/` (project)
2. `~/.amplifier/profiles/` (user)
3. Bundled profiles (fallback)

### Profile Format

Create `.amplifier/profiles/my-profile.md`:

```yaml
---
name: my-profile
extends: base
description: My custom development profile
---

# My Profile

Custom instructions that will be included in the system prompt.

## Guidelines

- Follow our coding standards
- Write tests for all new code
```

### Profile Schema

```yaml
---
# Required - profile metadata
profile:
  name: profile-name
  version: 1.0.0
  description: What this profile is for
  extends: base  # Optional - inherit from another profile

# Optional - override session settings
session:
  orchestrator: loop-streaming
  context: context-persistent

# Optional - configure providers
providers:
  - module: provider-anthropic
    source: git+https://github.com/microsoft/amplifier-module-provider-anthropic@main
    config:
      model: claude-sonnet-4-5

# Optional - add/configure tools
tools:
  - module: tool-filesystem
  - module: tool-bash

# Optional - configure hooks
hooks:
  - module: hooks-logging

# Optional - agent availability
#   agents: all              # All discovered agents
#   agents: none             # No agents
#   agents: [explorer, bug-hunter]  # Specific agents only

# Optional - exclude inherited modules
exclude:
  hooks:
    - hooks-logging
---
```

## Profile Inheritance

Profiles can extend other profiles:

```yaml
---
name: my-dev
extends: dev
---

Additional system instructions on top of dev profile.
```

The child profile:

- Inherits all parent settings
- Can override specific configurations
- Adds its own system instructions

### Inheritance Chain

```
foundation → base → dev → your-profile
```

Each level adds capabilities without removing parent features.

## Profile-Specific Tools

Enable or disable tools per profile:

```yaml
---
name: safe-profile
extends: base
tools:
  - module: tool-filesystem
    config:
      read_only: true
  # tool-bash intentionally omitted
---
```

## Profile System Instructions

The markdown content after the frontmatter becomes the system instruction:

```yaml
---
name: code-reviewer
extends: base
---

# Code Review Assistant

You are an expert code reviewer. When reviewing code:

1. Check for bugs and edge cases
2. Suggest performance improvements
3. Ensure code follows best practices
4. Look for security vulnerabilities

Be constructive and explain your reasoning.
```

## Mentions in Profiles

Reference context files using @mentions:

```yaml
---
name: team-profile
extends: dev
---

Follow our team standards:

@project:context/coding-standards.md
@project:context/architecture.md
```

## Sharing Profiles

### Via Git Repository

Commit profiles to your project's `.amplifier/profiles/` directory.

### Via Collections

Package profiles in a collection for broader sharing:

```
my-collection/
├── profiles/
│   ├── my-profile.md
│   └── another-profile.md
├── agents/
└── context/
```

See [Collections](collections.md) for more details.

## Troubleshooting

### Profile Not Found

```bash
# Check profile locations
ls ~/.amplifier/profiles/
ls .amplifier/profiles/
```

### Profile Not Loading

Verify YAML frontmatter syntax in the profile `.md` file. Ensure the `profile:` section contains a valid `name` field.

### Inheritance Issues

Check the inheritance chain by examining the `extends` field in each profile's frontmatter and ensuring parent profiles exist in the search paths.

## Best Practices

1. **Start minimal**: Extend `foundation` or `base`, add only what you need
2. **Use inheritance**: Don't duplicate - extend parent profiles
3. **Document purpose**: Include clear descriptions
4. **Project-specific**: Put team profiles in `.amplifier/profiles/`
5. **Test profiles**: Run `amplifier profile show` to verify

## See Also

- [CLI Reference](cli.md) - Profile commands
- [Collections](collections.md) - Sharing profiles
- [Agents](agents.md) - Agent configuration in profiles
- **→ [Profile Authoring Guide](https://github.com/microsoft/amplifier-profiles/blob/main/docs/PROFILE_AUTHORING.md)** - Complete reference
