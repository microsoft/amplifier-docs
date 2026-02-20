---
title: Module Resolution
---

# Module Resolution Library

The `amplifier-module-resolution` library resolves module IDs to installation sources using pluggable strategies. It implements a priority chain so that workspace and user overrides take precedence over profile-specified sources.

## Resolution Priority

```
1. Workspace override (AMPLIFIER_MODULE_SOURCE_* env vars)
   ↓
2. Workspace configuration (.amplifier/settings.local.yaml)
   ↓
3. User/Project settings (settings.yaml)
   ↓
4. Profile specification (mount plan source field)
   ↓
5. Installed packages (entry points)
```

## Key APIs

### StandardModuleSourceResolver

```python
from amplifier_module_resolution import StandardModuleSourceResolver

resolver = StandardModuleSourceResolver(
    workspace_sources=workspace_sources,
    settings_sources=settings_sources,
)

# Resolve module to source
source = await resolver.resolve(
    module_id="provider-anthropic",
    profile_source="git+https://github.com/microsoft/amplifier-module-provider-anthropic@main"
)

# Install module
await resolver.install(source)
```

### Source Types

#### GitSource

```python
from amplifier_module_resolution import GitSource

source = GitSource(
    url="https://github.com/microsoft/amplifier-module-provider-anthropic",
    ref="main",
    subdirectory=None
)

# Install using uv
await source.install(cache_dir=Path("~/.amplifier/modules"))
```

#### FileSource

```python
from amplifier_module_resolution import FileSource

source = FileSource(
    path=Path("/home/user/dev/my-module")
)

# Symlinks for development
await source.install(cache_dir=cache_dir)
```

#### PackageSource

```python
from amplifier_module_resolution import PackageSource

source = PackageSource(
    package_name="amplifier-module-provider-anthropic"
)

# Uses installed package (no installation needed)
```

## Source URL Formats

```python
# Git repository
"git+https://github.com/org/module@main"

# Git with specific tag
"git+https://github.com/org/module@v1.0.0"

# Git with commit SHA
"git+https://github.com/org/module@abc123"

# Git subdirectory (monorepo)
"git+https://github.com/org/monorepo@main#subdirectory=modules/my-module"

# Local path
"file:///home/user/modules/my-module"

# Package (installed)
"package:amplifier-module-provider-anthropic"
```

## Environment Override

Override module sources via environment:

```bash
export AMPLIFIER_MODULE_SOURCE_PROVIDER_ANTHROPIC="file:///home/user/dev/provider-anthropic"
```

Variable format: `AMPLIFIER_MODULE_SOURCE_<MODULE_ID>` (uppercase, hyphens to underscores)

## Caching

Git sources are cached to avoid repeated clones:

```
~/.amplifier/modules/
├── provider-anthropic/
│   ├── abc123/          # Commit SHA
│   └── current -> abc123
├── tool-filesystem/
│   └── ...
```

The resolver tracks commit SHAs for cache invalidation.

## Integration with Kernel

The resolver integrates with the kernel via the `ModuleSourceResolver` protocol:

```python
# Mount in session setup
coordinator.mount(
    "module-source-resolver",
    resolver,
    name="standard"
)

# Kernel uses for dynamic module loading
source = await resolver.resolve(module_id, profile_source)
await resolver.install(source)
```

## Custom Resolvers

Implement custom resolution strategies:

```python
from amplifier_module_resolution import ModuleSourceResolverProtocol

class EnterpriseResolver(ModuleSourceResolverProtocol):
    async def resolve(
        self,
        module_id: str,
        profile_source: str | None
    ) -> ModuleSource:
        # Check internal registry
        if module_id in self.internal_registry:
            return self.internal_registry[module_id]
        # Fall back to standard resolution
        return await self.standard_resolver.resolve(module_id, profile_source)
```

## References

- **→ [amplifier-module-resolution Repository](https://github.com/microsoft/amplifier-module-resolution)** - Full documentation
