# Documentation Source Mapping

This file maps each documentation page to the source files required to regenerate it. This mapping is designed to be machine-readable and can be used by automation tools, AI assistants, or documentation generation pipelines.

## Format

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

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `index.md` | N/A | Landing page - manually maintained |
| `getting_started/index.md` | `amplifier-app-cli/README.md` | Quick start guide for CLI application |
| `getting_started/installation.md` | `amplifier-app-cli/README.md`<br>`amplifier-app-cli/pyproject.toml` | Installation methods and requirements |
| `getting_started/providers.md` | `amplifier-app-cli/amplifier_app_cli/provider_manager.py`<br>`amplifier-module-provider-*/README.md` | Provider setup and configuration |

## User Guide (CLI Application)

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `user_guide/index.md` | `amplifier-app-cli/README.md` | CLI user guide overview |
| `user_guide/cli.md` | `amplifier-app-cli/amplifier_app_cli/cli.py`<br>`amplifier-app-cli/amplifier_app_cli/commands/*.py` | Complete CLI command reference |
| `user_guide/profiles.md` | `amplifier-profiles/src/amplifier_profiles/*.py`<br>`amplifier-profiles/README.md` | Profile system documentation |
| `user_guide/agents.md` | `amplifier-collection-toolkit/agents/*`<br>`amplifier-app-cli/docs/AGENT_DELEGATION_IMPLEMENTATION.md` | Agent delegation and usage |
| `user_guide/sessions.md` | `amplifier-core/amplifier_core/session.py`<br>`amplifier-app-cli/amplifier_app_cli/session_spawner.py` | Session management and persistence |
| `user_guide/collections.md` | `amplifier-collections/src/amplifier_collections/*.py`<br>`amplifier-collections/README.md` | Collections system documentation |

## Developer Guides

### Foundation

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `developer_guides/foundation/index.md` | `amplifier-core/README.md`<br>`amplifier-core/docs/DESIGN_PHILOSOPHY.md` | Foundation developer guide overview |

### Applications

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `developer_guides/applications/index.md` | `amplifier-core/amplifier_core/session.py`<br>`amplifier-app-cli/amplifier_app_cli/__init__.py` | Building applications on amplifier-core |
| `developer_guides/applications/cli_case_study.md` | `amplifier-app-cli/amplifier_app_cli/*.py`<br>`amplifier-app-cli/docs/*.md` | CLI application architecture case study |

### Modules

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `developer/index.md` | `amplifier-core/docs/contracts/README.md` | Module developer guide overview |
| `developer/module_development.md` | `amplifier-core/docs/contracts/*.md`<br>`amplifier-module-*/README.md` | Creating custom modules |

### Contracts

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `developer/contracts/index.md` | `amplifier-core/docs/contracts/README.md` | Module contracts overview |
| `developer/contracts/provider.md` | `amplifier-core/docs/contracts/PROVIDER_CONTRACT.md`<br>`amplifier-core/amplifier_core/interfaces.py` | Provider contract specification |
| `developer/contracts/tool.md` | `amplifier-core/docs/contracts/TOOL_CONTRACT.md`<br>`amplifier-core/amplifier_core/interfaces.py` | Tool contract specification |
| `developer/contracts/hook.md` | `amplifier-core/docs/contracts/HOOK_CONTRACT.md`<br>`amplifier-core/amplifier_core/hooks.py` | Hook contract specification |
| `developer/contracts/orchestrator.md` | `amplifier-core/docs/contracts/ORCHESTRATOR_CONTRACT.md`<br>`amplifier-core/amplifier_core/interfaces.py` | Orchestrator contract specification |
| `developer/contracts/context.md` | `amplifier-core/docs/contracts/CONTEXT_CONTRACT.md`<br>`amplifier-core/amplifier_core/interfaces.py` | Context contract specification |

## Architecture

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `architecture/index.md` | `amplifier-core/docs/DESIGN_PHILOSOPHY.md` | Architecture documentation overview |
| `architecture/overview.md` | `amplifier-core/docs/DESIGN_PHILOSOPHY.md`<br>`amplifier-core/README.md` | High-level architecture overview |
| `architecture/kernel.md` | `amplifier-core/docs/DESIGN_PHILOSOPHY.md`<br>`amplifier-core/amplifier_core/*.py` | Kernel philosophy and design |
| `architecture/modules.md` | `amplifier-core/docs/contracts/README.md`<br>`amplifier-core/amplifier_core/loader.py` | Module system architecture |
| `architecture/mount_plans.md` | `amplifier-core/docs/specs/MOUNT_PLAN_SPECIFICATION.md`<br>`amplifier-core/amplifier_core/models.py` | Mount plan specification |
| `architecture/events.md` | `amplifier-core/docs/specs/CONTRIBUTION_CHANNELS.md`<br>`amplifier-core/amplifier_core/events.py` | Event system architecture |

## API Reference

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `api/index.md` | N/A | API reference overview |
| `api/core/index.md` | `amplifier-core/amplifier_core/__init__.py` | Core API overview |
| `api/core/session.md` | `amplifier-core/amplifier_core/session.py` | Session API reference |
| `api/core/coordinator.md` | `amplifier-core/amplifier_core/coordinator.py` | Coordinator API reference |
| `api/core/hooks.md` | `amplifier-core/amplifier_core/hooks.py`<br>`amplifier-core/docs/HOOKS_API.md` | Hooks API reference |
| `api/core/models.md` | `amplifier-core/amplifier_core/models.py`<br>`amplifier-core/amplifier_core/message_models.py` | Data models reference |
| `api/core/events.md` | `amplifier-core/amplifier_core/events.py` | Events API reference |
| `api/cli/index.md` | `amplifier-app-cli/amplifier_app_cli/cli.py` | CLI API reference |

## Libraries

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `libraries/index.md` | `amplifier-profiles/README.md`<br>`amplifier-collections/README.md`<br>`amplifier-config/README.md`<br>`amplifier-module-resolution/README.md` | Libraries overview |
| `libraries/profiles.md` | `amplifier-profiles/src/amplifier_profiles/*.py`<br>`amplifier-profiles/README.md` | Profiles library documentation |
| `libraries/collections.md` | `amplifier-collections/src/amplifier_collections/*.py`<br>`amplifier-collections/README.md` | Collections library documentation |
| `libraries/config.md` | `amplifier-config/src/amplifier_config/*.py`<br>`amplifier-config/README.md` | Config library documentation |
| `libraries/module_resolution.md` | `amplifier-module-resolution/src/amplifier_module_resolution/*.py`<br>`amplifier-module-resolution/README.md` | Module resolution library documentation |

## Modules Catalog

### Overview

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `modules/index.md` | `amplifier-core/docs/contracts/README.md` | Modules catalog overview |

### Providers

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `modules/providers/index.md` | `amplifier-module-provider-*/README.md` | Providers catalog |
| `modules/providers/anthropic.md` | `amplifier-module-provider-anthropic/amplifier_module_provider_anthropic/__init__.py`<br>`amplifier-module-provider-anthropic/README.md` | Anthropic provider documentation |
| `modules/providers/openai.md` | `amplifier-module-provider-openai/amplifier_module_provider_openai/__init__.py`<br>`amplifier-module-provider-openai/README.md` | OpenAI provider documentation |
| `modules/providers/azure.md` | `amplifier-module-provider-azure-openai/amplifier_module_provider_azure_openai/__init__.py`<br>`amplifier-module-provider-azure-openai/README.md` | Azure OpenAI provider documentation |
| `modules/providers/ollama.md` | `amplifier-module-provider-ollama/amplifier_module_provider_ollama/__init__.py`<br>`amplifier-module-provider-ollama/README.md` | Ollama provider documentation |
| `modules/providers/vllm.md` | `amplifier-module-provider-vllm/amplifier_module_provider_vllm/__init__.py`<br>`amplifier-module-provider-vllm/README.md` | vLLM provider documentation |

### Tools

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `modules/tools/index.md` | `amplifier-module-tool-*/README.md` | Tools catalog |
| `modules/tools/filesystem.md` | `amplifier-module-tool-filesystem/amplifier_module_tool_filesystem/*.py`<br>`amplifier-module-tool-filesystem/README.md` | Filesystem tool documentation |
| `modules/tools/bash.md` | `amplifier-module-tool-bash/amplifier_module_tool_bash/__init__.py`<br>`amplifier-module-tool-bash/README.md` | Bash tool documentation |
| `modules/tools/web.md` | `amplifier-module-tool-web/amplifier_module_tool_web/__init__.py`<br>`amplifier-module-tool-web/README.md` | Web tool documentation |
| `modules/tools/search.md` | `amplifier-module-tool-search/amplifier_module_tool_search/__init__.py`<br>`amplifier-module-tool-search/README.md` | Search tool documentation |
| `modules/tools/task.md` | `amplifier-module-tool-task/amplifier_module_tool_task/__init__.py`<br>`amplifier-module-tool-task/README.md` | Task tool documentation |
| `modules/tools/todo.md` | `amplifier-module-tool-todo/amplifier_module_tool_todo/__init__.py`<br>`amplifier-module-tool-todo/README.md` | Todo tool documentation |

### Orchestrators

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `modules/orchestrators/index.md` | `amplifier-module-loop-*/README.md` | Orchestrators catalog |
| `modules/orchestrators/loop_basic.md` | `amplifier-module-loop-basic/amplifier_module_loop_basic/__init__.py`<br>`amplifier-module-loop-basic/README.md` | Basic orchestrator documentation |
| `modules/orchestrators/loop_streaming.md` | `amplifier-module-loop-streaming/amplifier_module_loop_streaming/__init__.py`<br>`amplifier-module-loop-streaming/README.md` | Streaming orchestrator documentation |
| `modules/orchestrators/loop_events.md` | `amplifier-module-loop-events/amplifier_module_loop_events/__init__.py`<br>`amplifier-module-loop-events/README.md` | Events orchestrator documentation |

### Contexts

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `modules/contexts/index.md` | `amplifier-module-context-*/README.md` | Contexts catalog |
| `modules/contexts/simple.md` | `amplifier-module-context-simple/amplifier_module_context_simple/__init__.py`<br>`amplifier-module-context-simple/README.md` | Simple context documentation |
| `modules/contexts/persistent.md` | `amplifier-module-context-persistent/amplifier_module_context_persistent/__init__.py`<br>`amplifier-module-context-persistent/README.md` | Persistent context documentation |

### Hooks

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `modules/hooks/index.md` | `amplifier-module-hooks-*/README.md` | Hooks catalog |
| `modules/hooks/logging.md` | `amplifier-module-hooks-logging/amplifier_module_hooks_logging/__init__.py`<br>`amplifier-module-hooks-logging/README.md` | Logging hook documentation |
| `modules/hooks/approval.md` | `amplifier-module-hooks-approval/amplifier_module_hooks_approval/__init__.py`<br>`amplifier-module-hooks-approval/README.md` | Approval hook documentation |
| `modules/hooks/redaction.md` | `amplifier-module-hooks-redaction/amplifier_module_hooks_redaction/__init__.py`<br>`amplifier-module-hooks-redaction/README.md` | Redaction hook documentation |

## Ecosystem & Community

| Documentation Page | Source Files | Notes |
|-------------------|--------------|-------|
| `ecosystem/index.md` | `amplifier-core/docs/contracts/README.md`<br>`amplifier-profiles/README.md` | Ecosystem overview |
| `showcase/index.md` | N/A | Showcase page - manually curated |
| `community/index.md` | N/A | Community page - manually maintained |
| `community/contributing.md` | `amplifier-core/README.md`<br>`CONTRIBUTING.md` | Contributing guidelines |
| `community/roadmap.md` | `ROADMAP.md` | Project roadmap |

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
