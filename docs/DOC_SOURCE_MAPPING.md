# Documentation Source Mapping

This file maps each documentation page to the source files required to regenerate it. This mapping is designed to be machine-readable and can be used by automation tools, AI assistants, or documentation generation pipelines.

## Format

## Relationship Type Legend

- **DIRECT**: Content directly copied or auto-generated from source
- **DERIVED**: Manually written but closely follows source structure/content
- **REFERENCE**: Source informs doc but doc is substantially custom
- **MANUAL**: No meaningful derivation from listed sources


Each entry contains:
- **Documentation Page**: The path to the documentation file relative to the `docs/` directory
- **Source Files**: One or more source files that contain the information for this documentation
  - Multiple files are separated by `|` 
  - Paths are relative to `~/repo/amplifier-dev/`
- **Notes**: Additional context about the documentation page, dependencies, or generation strategy

## Legend

- `N/A` - No direct source file; manually maintained
- `*` - Wildcard indicating multiple matching files
- `|` - Separator for multiple source files

---

## Getting Started

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `index.md` | N/A | **MANUAL** | Landing page - manually maintained |
| `getting_started/index.md` | `amplifier-app-cli/README.md` | **REFERENCE** | Quick start guide for CLI application |
| `getting_started/installation.md` | `amplifier-app-cli/README.md`<br>`amplifier-app-cli/pyproject.toml` | **REFERENCE** | Installation methods and requirements |
| `getting_started/providers.md` | `amplifier-app-cli/amplifier_app_cli/provider_manager.py`<br>`amplifier-module-provider-*/README.md` | **REFERENCE** | Provider setup and configuration |

## User Guide (CLI Application)

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `user_guide/index.md` | `amplifier-app-cli/README.md` | **REFERENCE** | CLI user guide overview |
| `user_guide/cli.md` | `amplifier-app-cli/amplifier_app_cli/cli.py`<br>`amplifier-app-cli/amplifier_app_cli/commands/*.py` | **DERIVED** | Complete CLI command reference |
| `user_guide/profiles.md` | `amplifier-profiles/src/amplifier_profiles/*.py`<br>`amplifier-profiles/README.md` | **DERIVED** | Profile system documentation |
| `user_guide/agents.md` | `amplifier-collection-toolkit/agents/*`<br>`amplifier-app-cli/docs/AGENT_DELEGATION_IMPLEMENTATION.md` | **DERIVED** | Agent delegation and usage |
| `user_guide/sessions.md` | `amplifier-core/amplifier_core/session.py`<br>`amplifier-app-cli/amplifier_app_cli/session_spawner.py` | **DERIVED** | Session management and persistence |
| `user_guide/collections.md` | `amplifier-collections/src/amplifier_collections/*.py`<br>`amplifier-collections/README.md` | **DERIVED** | Collections system documentation |

## Developer Guides

### Foundation

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `developer_guides/foundation/index.md` | `amplifier-core/README.md`<br>`amplifier-core/docs/DESIGN_PHILOSOPHY.md` | **DERIVED** | Foundation developer guide overview |

### Applications

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `developer_guides/applications/index.md` | `amplifier-core/amplifier_core/session.py`<br>`amplifier-app-cli/amplifier_app_cli/__init__.py` | **REFERENCE** | Building applications on amplifier-core |
| `developer_guides/applications/cli_case_study.md` | `amplifier-app-cli/amplifier_app_cli/*.py`<br>`amplifier-app-cli/docs/*.md` | **REFERENCE** | CLI application architecture case study |

### Modules

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `developer/index.md` | `amplifier-core/docs/contracts/README.md` | **DERIVED** | Module developer guide overview |
| `developer/module_development.md` | `amplifier-core/docs/contracts/*.md`<br>`amplifier-module-*/README.md` | **DERIVED** | Creating custom modules |

### Contracts

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `developer/contracts/index.md` | `amplifier-core/docs/contracts/README.md` | **DERIVED** | Module contracts overview |
| `developer/contracts/provider.md` | `amplifier-core/docs/contracts/PROVIDER_CONTRACT.md`<br>`amplifier-core/amplifier_core/interfaces.py` | **DERIVED** | Provider contract specification |
| `developer/contracts/tool.md` | `amplifier-core/docs/contracts/TOOL_CONTRACT.md`<br>`amplifier-core/amplifier_core/interfaces.py` | **DERIVED** | Tool contract specification |
| `developer/contracts/hook.md` | `amplifier-core/docs/contracts/HOOK_CONTRACT.md`<br>`amplifier-core/amplifier_core/hooks.py` | **DERIVED** | Hook contract specification |
| `developer/contracts/orchestrator.md` | `amplifier-core/docs/contracts/ORCHESTRATOR_CONTRACT.md`<br>`amplifier-core/amplifier_core/interfaces.py` | **DERIVED** | Orchestrator contract specification |
| `developer/contracts/context.md` | `amplifier-core/docs/contracts/CONTEXT_CONTRACT.md`<br>`amplifier-core/amplifier_core/interfaces.py` | **DERIVED** | Context contract specification |

## Architecture

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `architecture/index.md` | `amplifier-core/docs/DESIGN_PHILOSOPHY.md` | **DERIVED** | Architecture documentation overview |
| `architecture/overview.md` | `amplifier-core/docs/DESIGN_PHILOSOPHY.md`<br>`amplifier-core/README.md` | **DERIVED** | High-level architecture overview |
| `architecture/kernel.md` | `amplifier-core/docs/DESIGN_PHILOSOPHY.md`<br>`amplifier-core/amplifier_core/*.py` | **DERIVED** | Kernel philosophy and design |
| `architecture/modules.md` | `amplifier-core/docs/contracts/README.md`<br>`amplifier-core/amplifier_core/loader.py` | **DERIVED** | Module system architecture |
| `architecture/mount_plans.md` | `amplifier-core/docs/specs/MOUNT_PLAN_SPECIFICATION.md`<br>`amplifier-core/amplifier_core/models.py` | **DERIVED** | Mount plan specification |
| `architecture/events.md` | `amplifier-core/docs/specs/CONTRIBUTION_CHANNELS.md`<br>`amplifier-core/amplifier_core/events.py` | **DERIVED** | Event system architecture |

## API Reference

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `api/index.md` | N/A | **MANUAL** | API reference overview |
| `api/core/index.md` | `amplifier-core/amplifier_core/__init__.py` | **MANUAL** | Core API overview |
| `api/core/session.md` | `amplifier-core/amplifier_core/session.py` | **REFERENCE** | Session API reference |
| `api/core/coordinator.md` | `amplifier-core/amplifier_core/coordinator.py` | **REFERENCE** | Coordinator API reference |
| `api/core/hooks.md` | `amplifier-core/amplifier_core/hooks.py`<br>`amplifier-core/docs/HOOKS_API.md` | **DERIVED** | Hooks API reference |
| `api/core/models.md` | `amplifier-core/amplifier_core/models.py`<br>`amplifier-core/amplifier_core/message_models.py` | **REFERENCE** | Data models reference |
| `api/core/events.md` | `amplifier-core/amplifier_core/events.py` | **REFERENCE** | Events API reference |
| `api/cli/index.md` | `amplifier-app-cli/amplifier_app_cli/cli.py` | **REFERENCE** | CLI API reference |

## Libraries

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `libraries/index.md` | `amplifier-profiles/README.md`<br>`amplifier-collections/README.md`<br>`amplifier-config/README.md`<br>`amplifier-module-resolution/README.md` | **DERIVED** | Libraries overview |
| `libraries/profiles.md` | `amplifier-profiles/src/amplifier_profiles/*.py`<br>`amplifier-profiles/README.md` | **DERIVED** | Profiles library documentation |
| `libraries/collections.md` | `amplifier-collections/src/amplifier_collections/*.py`<br>`amplifier-collections/README.md` | **DERIVED** | Collections library documentation |
| `libraries/config.md` | `amplifier-config/src/amplifier_config/*.py`<br>`amplifier-config/README.md` | **DERIVED** | Config library documentation |
| `libraries/module_resolution.md` | `amplifier-module-resolution/src/amplifier_module_resolution/*.py`<br>`amplifier-module-resolution/README.md` | **DERIVED** | Module resolution library documentation |

## Modules Catalog

### Overview

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `modules/index.md` | `amplifier-core/docs/contracts/README.md` | **DERIVED** | Modules catalog overview |

### Providers

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `modules/providers/index.md` | `amplifier-module-provider-*/README.md` | **DERIVED** | Providers catalog |
| `modules/providers/anthropic.md` | `amplifier-module-provider-anthropic/amplifier_module_provider_anthropic/__init__.py`<br>`amplifier-module-provider-anthropic/README.md` | **DERIVED** | Anthropic provider documentation |
| `modules/providers/openai.md` | `amplifier-module-provider-openai/amplifier_module_provider_openai/__init__.py`<br>`amplifier-module-provider-openai/README.md` | **DERIVED** | OpenAI provider documentation |
| `modules/providers/azure.md` | `amplifier-module-provider-azure-openai/amplifier_module_provider_azure_openai/__init__.py`<br>`amplifier-module-provider-azure-openai/README.md` | **DERIVED** | Azure OpenAI provider documentation |
| `modules/providers/ollama.md` | `amplifier-module-provider-ollama/amplifier_module_provider_ollama/__init__.py`<br>`amplifier-module-provider-ollama/README.md` | **DERIVED** | Ollama provider documentation |
| `modules/providers/vllm.md` | `amplifier-module-provider-vllm/amplifier_module_provider_vllm/__init__.py`<br>`amplifier-module-provider-vllm/README.md` | **DERIVED** | vLLM provider documentation |

### Tools

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `modules/tools/index.md` | `amplifier-module-tool-*/README.md` | **DERIVED** | Tools catalog |
| `modules/tools/filesystem.md` | `amplifier-module-tool-filesystem/amplifier_module_tool_filesystem/*.py`<br>`amplifier-module-tool-filesystem/README.md` | **DERIVED** | Filesystem tool documentation |
| `modules/tools/bash.md` | `amplifier-module-tool-bash/amplifier_module_tool_bash/__init__.py`<br>`amplifier-module-tool-bash/README.md` | **DERIVED** | Bash tool documentation |
| `modules/tools/web.md` | `amplifier-module-tool-web/amplifier_module_tool_web/__init__.py`<br>`amplifier-module-tool-web/README.md` | **DERIVED** | Web tool documentation |
| `modules/tools/search.md` | `amplifier-module-tool-search/amplifier_module_tool_search/__init__.py`<br>`amplifier-module-tool-search/README.md` | **DERIVED** | Search tool documentation |
| `modules/tools/task.md` | `amplifier-module-tool-task/amplifier_module_tool_task/__init__.py`<br>`amplifier-module-tool-task/README.md` | **DERIVED** | Task tool documentation |
| `modules/tools/todo.md` | `amplifier-module-tool-todo/amplifier_module_tool_todo/__init__.py`<br>`amplifier-module-tool-todo/README.md` | **DERIVED** | Todo tool documentation |

### Orchestrators

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `modules/orchestrators/index.md` | `amplifier-module-loop-*/README.md` | **DERIVED** | Orchestrators catalog |
| `modules/orchestrators/loop_basic.md` | `amplifier-module-loop-basic/amplifier_module_loop_basic/__init__.py`<br>`amplifier-module-loop-basic/README.md` | **DERIVED** | Basic orchestrator documentation |
| `modules/orchestrators/loop_streaming.md` | `amplifier-module-loop-streaming/amplifier_module_loop_streaming/__init__.py`<br>`amplifier-module-loop-streaming/README.md` | **DERIVED** | Streaming orchestrator documentation |
| `modules/orchestrators/loop_events.md` | `amplifier-module-loop-events/amplifier_module_loop_events/__init__.py`<br>`amplifier-module-loop-events/README.md` | **DERIVED** | Events orchestrator documentation |

### Contexts

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `modules/contexts/index.md` | `amplifier-module-context-*/README.md` | **DERIVED** | Contexts catalog |
| `modules/contexts/simple.md` | `amplifier-module-context-simple/amplifier_module_context_simple/__init__.py`<br>`amplifier-module-context-simple/README.md` | **DERIVED** | Simple context documentation |
| `modules/contexts/persistent.md` | `amplifier-module-context-persistent/amplifier_module_context_persistent/__init__.py`<br>`amplifier-module-context-persistent/README.md` | **DERIVED** | Persistent context documentation |

### Hooks

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `modules/hooks/index.md` | `amplifier-module-hooks-*/README.md` | **DERIVED** | Hooks catalog |
| `modules/hooks/logging.md` | `amplifier-module-hooks-logging/amplifier_module_hooks_logging/__init__.py`<br>`amplifier-module-hooks-logging/README.md` | **DERIVED** | Logging hook documentation |
| `modules/hooks/approval.md` | `amplifier-module-hooks-approval/amplifier_module_hooks_approval/__init__.py`<br>`amplifier-module-hooks-approval/README.md` | **DERIVED** | Approval hook documentation |
| `modules/hooks/redaction.md` | `amplifier-module-hooks-redaction/amplifier_module_hooks_redaction/__init__.py`<br>`amplifier-module-hooks-redaction/README.md` | **DERIVED** | Redaction hook documentation |

## Ecosystem & Community

| Documentation Page | Source Files | Type | Notes |
|-------------------|--------------|------|-------|
| `ecosystem/index.md` | `amplifier-core/docs/contracts/README.md`<br>`amplifier-profiles/README.md` | **DERIVED** | Ecosystem overview |
| `showcase/index.md` | N/A | **DERIVED** | Showcase page - manually curated |
| `community/index.md` | N/A | **MANUAL** | Community page - manually maintained |
| `community/contributing.md` | `amplifier-core/README.md`<br>`CONTRIBUTING.md` | **DERIVED** | Contributing guidelines |
| `community/roadmap.md` | `ROADMAP.md` | **DIRECT** | Project roadmap |

---

## Usage Guidelines

### For Documentation Authors

1. **Check mapping before editing**: Before modifying a documentation page, check this mapping to understand which source files inform it
2. **Update source files first**: When possible, update the source files (code, contracts, READMEs) and regenerate documentation
3. **Keep mapping current**: When adding new documentation pages, add them to this mapping

### For Automation Tools

1. **Parse format**: Both CSV and Markdown versions are provided
   - CSV: `DOC_SOURCE_MAPPING.csv` - Machine-readable
   - Markdown: `DOC_SOURCE_MAPPING.md` - Human-readable
2. **Handle wildcards**: Files with `*` indicate patterns (e.g., `amplifier-module-provider-*/README.md`)
3. **Multi-source files**: Files separated by `|` or line breaks should all be considered
4. **N/A handling**: Pages marked N/A are manually maintained and not auto-generated

### For AI Assistants

When asked to update documentation:

1. **Identify source files**: Look up the documentation page in this mapping
2. **Read source files**: Read all listed source files to understand current state
3. **Determine strategy**:
   - If source files exist: Extract/transform information from source
   - If N/A: Work directly with the documentation file
   - If hybrid: Combine source information with manual content
4. **Preserve structure**: Maintain the documentation format and style
5. **Update mapping**: If you add new documentation, update this mapping file

### Path Resolution

All source file paths are relative to `~/repo/amplifier-dev/`. To resolve:

```bash
# Example: Reading source for api/core/session.md
SOURCE_ROOT=~/repo/amplifier-dev
SOURCE_FILE=amplifier-core/amplifier_core/session.py
FULL_PATH="$SOURCE_ROOT/$SOURCE_FILE"
```

---

## Maintenance

This mapping should be updated when:

- New documentation pages are added
- Source file locations change
- Module structure changes
- New modules are added to the ecosystem

**Last Updated**: 2025-12-08

**Maintainer**: Documentation team

**Version**: 1.0.0
