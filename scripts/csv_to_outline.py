#!/usr/bin/env python3
"""
Transform DOC_SOURCE_MAPPING.csv into amplifier-docs-outline.json

Usage:
    python scripts/csv_to_outline.py

This script reads the CSV mapping and generates a JSON outline suitable for
the documentation synchronization recipe.
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def generate_id(doc_path: str) -> str:
    """Generate a unique ID from the doc path.

    docs/architecture/kernel.md -> architecture-kernel
    docs/modules/providers/anthropic.md -> modules-providers-anthropic
    """
    # Remove 'docs/' prefix and '.md' suffix
    path = doc_path.replace("docs/", "").replace(".md", "")
    # Replace slashes with dashes
    id_str = path.replace("/", "-")
    # Handle index files
    if id_str.endswith("-index"):
        id_str = id_str[:-6]  # Remove '-index'
    return id_str


def extract_category(doc_path: str) -> str:
    """Extract category from doc path."""
    parts = doc_path.replace("docs/", "").split("/")
    if len(parts) >= 1:
        return parts[0]
    return "other"


def extract_title(doc_path: str) -> str:
    """Extract a readable title from doc path."""
    # Get the last part of the path (filename)
    filename = Path(doc_path).stem
    if filename == "index":
        # Use parent directory name for index files
        filename = Path(doc_path).parent.name
    # Convert to title case with spaces
    title = filename.replace("_", " ").replace("-", " ").title()
    return title


def parse_sources(source_str: str, notes: str) -> list[dict]:
    """Parse pipe-delimited source string into array of source objects."""
    if source_str == "N/A" or not source_str:
        return []

    sources = []
    for source in source_str.split("|"):
        source = source.strip()
        if not source:
            continue

        # Parse repo and path
        # Format: repo-name/path/to/file.ext or repo-name/path/*.py
        parts = source.split("/", 1)
        if len(parts) < 2:
            continue

        repo = parts[0]
        path = parts[1]

        # Determine source type
        if path.endswith(".py"):
            source_type = "python"
        elif path.endswith(".md"):
            if "README" in path:
                source_type = "readme"
            else:
                source_type = "markdown"
        elif path.endswith(".yaml") or path.endswith(".yml"):
            source_type = "yaml"
        else:
            source_type = "other"

        sources.append(
            {
                "repo": repo,
                "path": path,
                "type": source_type,
                "required": True,  # Default to required
            }
        )

    return sources


def get_validation_rules(relationship_type: str) -> list[str]:
    """Get validation rules based on relationship type."""
    rules_map = {
        "DIRECT": ["exact_source_match", "format_consistency", "metadata_preserved"],
        "DERIVED": ["factual_accuracy", "source_traceability", "no_hallucination"],
        "REFERENCE": ["sources_exist", "links_valid", "refs_current"],
        "N/A": ["build_passes", "links_valid"],
    }
    return rules_map.get(relationship_type, ["links_valid"])


def get_prompt_template(relationship_type: str, category: str) -> str | None:
    """Get appropriate prompt template based on relationship type and category."""
    if relationship_type == "N/A":
        return None
    if relationship_type == "DIRECT":
        return "direct_copy"
    if relationship_type == "REFERENCE":
        return "module_reference" if category == "modules" else "validate_only"
    # DERIVED
    if category == "architecture":
        return "synthesize_architecture"
    if category == "api":
        return "api_from_docstrings"
    if category == "modules":
        return "module_reference"
    return "synthesize_documentation"


def get_priority(relationship_type: str, category: str) -> str:
    """Determine priority based on type and category."""
    if relationship_type == "DIRECT":
        return "high"
    if category in ["architecture", "getting_started", "developer"]:
        return "high"
    if category in ["api", "modules"]:
        return "medium"
    return "low"


def transform_csv_to_outline(csv_path: Path, output_path: Path):
    """Transform CSV mapping to JSON outline."""

    # Read CSV
    sections = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc_path = row["Documentation Page"].strip()
            source_files = row["Source Files"].strip()
            relationship_type = row["Relationship Type"].strip()
            notes = row.get("Notes", "").strip()

            section_id = generate_id(doc_path)
            category = extract_category(doc_path)
            title = extract_title(doc_path)
            sources = parse_sources(source_files, notes)

            section = {
                "id": section_id,
                "doc_path": doc_path,
                "title": title,
                "category": category,
                "relationship_type": relationship_type,
                "sources": sources,
                "validation": {
                    "rules": get_validation_rules(relationship_type),
                    "custom_rules": [],
                    "acceptance_threshold": 0.95
                    if relationship_type == "DIRECT"
                    else 0.90,
                },
                "generation": {
                    "prompt_template": get_prompt_template(relationship_type, category),
                    "transform_steps": get_transform_steps(relationship_type),
                    "output_format": "markdown",
                    "preserve_sections": ["## See Also"]
                    if relationship_type != "N/A"
                    else ["*"],
                },
                "metadata": {
                    "priority": get_priority(relationship_type, category),
                    "auto_update": relationship_type not in ["N/A", "REFERENCE"],
                    "last_synced": None,
                    "notes": notes if notes else None,
                },
            }
            sections.append(section)

    # Build full outline
    outline = {
        "_meta": {
            "name": "amplifier-docs-content-outline",
            "version": "1.0.0",
            "description": "Content synchronization outline for amplifier-docs",
            "target_site": "https://microsoft.github.io/amplifier-docs/",
            "generated_from": "docs/DOC_SOURCE_MAPPING.csv",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "allowed_repos": {
                "core": [
                    "amplifier",
                    "amplifier-core",
                    "amplifier-foundation",
                    "amplifier-app-cli",
                ],
                "libraries": [
                    "amplifier-profiles",
                    "amplifier-collections",
                    "amplifier-config",
                    "amplifier-module-resolution",
                ],
                "providers": [
                    "amplifier-module-provider-anthropic",
                    "amplifier-module-provider-openai",
                    "amplifier-module-provider-azure-openai",
                    "amplifier-module-provider-ollama",
                    "amplifier-module-provider-vllm",
                    "amplifier-module-provider-mock",
                ],
                "tools": [
                    "amplifier-module-tool-filesystem",
                    "amplifier-module-tool-bash",
                    "amplifier-module-tool-web",
                    "amplifier-module-tool-search",
                    "amplifier-module-tool-task",
                    "amplifier-module-tool-todo",
                ],
                "hooks": [
                    "amplifier-module-hooks-logging",
                    "amplifier-module-hooks-approval",
                    "amplifier-module-hooks-redaction",
                    "amplifier-module-hooks-backup",
                    "amplifier-module-hooks-scheduler-cost-aware",
                    "amplifier-module-hooks-scheduler-heuristic",
                    "amplifier-module-hooks-status-context",
                    "amplifier-module-hooks-streaming-ui",
                    "amplifier-module-hooks-todo-reminder",
                ],
                "orchestrators": [
                    "amplifier-module-loop-basic",
                    "amplifier-module-loop-streaming",
                    "amplifier-module-loop-events",
                ],
                "contexts": [
                    "amplifier-module-context-simple",
                    "amplifier-module-context-persistent",
                ],
            },
            "github_org": "microsoft",
            "github_base_url": "https://github.com/microsoft",
            "relationship_types": {
                "DIRECT": {
                    "description": "Content closely matches source with minimal transformation",
                    "generation_strategy": "copy_transform",
                    "allows_enhancement": False,
                },
                "DERIVED": {
                    "description": "Synthesized from sources, can enhance and adapt",
                    "generation_strategy": "synthesize",
                    "allows_enhancement": True,
                },
                "REFERENCE": {
                    "description": "References sources for validation only, not regenerated",
                    "generation_strategy": "validate_only",
                    "allows_enhancement": True,
                },
                "N/A": {
                    "description": "Manually maintained, skip generation",
                    "generation_strategy": "skip",
                    "allows_enhancement": True,
                },
            },
            "validation_rule_definitions": {
                "exact_source_match": {
                    "description": "Core content matches source verbatim (excluding formatting)",
                    "check": "diff_content_normalized",
                },
                "format_consistency": {
                    "description": "Markdown formatting follows site standards",
                    "check": "lint_markdown",
                },
                "metadata_preserved": {
                    "description": "Source metadata preserved in output",
                    "check": "compare_frontmatter",
                },
                "factual_accuracy": {
                    "description": "All facts trace to source material",
                    "check": "source_citation_check",
                },
                "source_traceability": {
                    "description": "Each claim can be traced to specific source",
                    "check": "traceability_analysis",
                },
                "no_hallucination": {
                    "description": "No invented facts beyond sources",
                    "check": "hallucination_detection",
                },
                "sources_exist": {
                    "description": "All referenced source files exist",
                    "check": "file_existence",
                },
                "links_valid": {
                    "description": "All internal and external links resolve",
                    "check": "link_validation",
                },
                "refs_current": {
                    "description": "Referenced versions match current releases",
                    "check": "version_comparison",
                },
                "build_passes": {
                    "description": "Documentation builds without errors",
                    "check": "mkdocs_build_strict",
                },
            },
            "prompt_templates": {
                "direct_copy": {
                    "description": "Copy with minimal transformation",
                    "template": "Copy the source content. Add navigation header. Update internal links to match site structure. Preserve all technical accuracy.",
                },
                "synthesize_architecture": {
                    "description": "Synthesize architecture documentation",
                    "template": "Create architecture documentation by:\n1. Extract core philosophy from design docs\n2. Analyze implementation patterns from code\n3. Synthesize into clear narrative\n4. Add diagrams where helpful\n5. Include practical examples\n\nMaintain factual accuracy - every claim must trace to sources.",
                },
                "synthesize_documentation": {
                    "description": "Synthesize general documentation",
                    "template": "Create documentation by synthesizing the source materials:\n1. Extract key concepts and information\n2. Organize in a logical structure\n3. Write clear explanations\n4. Add examples where helpful\n5. Ensure all facts trace to sources",
                },
                "module_reference": {
                    "description": "Generate module reference page",
                    "template": "Create module documentation including:\n- Purpose and capabilities\n- Installation instructions\n- Configuration options (from source)\n- Usage examples\n- API reference\n\nVerify all information against README and source code.",
                },
                "api_from_docstrings": {
                    "description": "Generate API docs from Python docstrings",
                    "template": "Extract and format API documentation from Python source:\n- Class/function signatures\n- Parameter documentation\n- Return types\n- Usage examples from docstrings\n- Cross-references to related APIs",
                },
                "validate_only": {
                    "description": "Validate references without regenerating",
                    "template": "Verify that all source references exist and are accessible. Report any broken links or missing files.",
                },
            },
            "categories": [
                "index",
                "getting_started",
                "user_guide",
                "developer_guides",
                "developer",
                "architecture",
                "api",
                "modules",
                "libraries",
                "ecosystem",
                "showcase",
                "community",
            ],
        },
        "content_sections": sections,
        "summary": {
            "total_sections": len(sections),
            "by_relationship_type": {},
            "by_category": {},
            "by_priority": {},
        },
    }

    # Calculate summary statistics
    for section in sections:
        rt = section["relationship_type"]
        outline["summary"]["by_relationship_type"][rt] = (
            outline["summary"]["by_relationship_type"].get(rt, 0) + 1
        )

        cat = section["category"]
        outline["summary"]["by_category"][cat] = (
            outline["summary"]["by_category"].get(cat, 0) + 1
        )

        pri = section["metadata"]["priority"]
        outline["summary"]["by_priority"][pri] = (
            outline["summary"]["by_priority"].get(pri, 0) + 1
        )

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(outline, f, indent=2, ensure_ascii=False)

    print(f"Generated outline with {len(sections)} sections")
    print(f"  By relationship type: {outline['summary']['by_relationship_type']}")
    print(f"  By category: {outline['summary']['by_category']}")
    print(f"  By priority: {outline['summary']['by_priority']}")
    print(f"Output written to: {output_path}")


def get_transform_steps(relationship_type: str) -> list[str]:
    """Get transformation steps based on relationship type."""
    steps_map = {
        "DIRECT": [
            "copy_content",
            "add_navigation_header",
            "update_links",
            "add_cross_references",
        ],
        "DERIVED": [
            "extract_content",
            "synthesize_narrative",
            "add_examples",
            "add_navigation",
        ],
        "REFERENCE": ["verify_sources_exist", "validate_links", "check_version_match"],
        "N/A": [],
    }
    return steps_map.get(relationship_type, [])


if __name__ == "__main__":
    # Paths relative to repo root
    repo_root = Path(__file__).parent.parent
    csv_path = repo_root / "docs" / "DOC_SOURCE_MAPPING.csv"
    output_path = repo_root / "outlines" / "amplifier-docs-outline.json"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    transform_csv_to_outline(csv_path, output_path)
