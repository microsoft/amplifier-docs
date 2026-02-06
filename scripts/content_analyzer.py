#!/usr/bin/env python3
"""
Content Analyzer for Documentation Freshness (v2)

Uses structured fact extraction instead of raw term comparison.
Focuses on meaningful content: config keys, models, behavior sections.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ExtractedFacts:
    """Structured facts extracted from a document."""

    config_keys: set[str] = field(default_factory=set)
    models: set[str] = field(default_factory=set)
    sections: set[str] = field(default_factory=set)
    features: set[str] = field(default_factory=set)
    env_vars: set[str] = field(default_factory=set)


def strip_code_blocks(content: str) -> str:
    """Remove fenced code blocks from content."""
    return re.sub(r"```[\w]*\n.*?```", "", content, flags=re.DOTALL)


def extract_config_keys(content: str) -> set[str]:
    """Extract configuration keys from content."""
    keys = set()

    # Strip code blocks to avoid extracting noise from examples
    clean_content = strip_code_blocks(content)

    # From table rows: | `key` | type | default | - this is the most reliable
    table_pattern = r"\|\s*`([a-z][a-z0-9_]*)`\s*\|"
    for match in re.finditer(table_pattern, clean_content, re.IGNORECASE):
        key = match.group(1).lower()
        if len(key) > 2:
            keys.add(key)

    # From definition lists or config descriptions: **key** or `key` -
    defn_pattern = r"(?:\*\*|`)([a-z][a-z0-9_]*)(?:\*\*|`)\s*[-:]"
    for match in re.finditer(defn_pattern, clean_content, re.IGNORECASE):
        key = match.group(1).lower()
        if len(key) > 2:
            keys.add(key)

    # Filter out common noise
    noise = {
        "true",
        "false",
        "null",
        "none",
        "type",
        "value",
        "default",
        "string",
        "int",
        "bool",
        "float",
        "description",
        "example",
        "title",
        "name",
        "config",
        "module",
        "source",
        "providers",
    }
    keys = {k for k in keys if k not in noise}

    return keys


def extract_models(content: str) -> set[str]:
    """Extract model names from content."""
    models = set()

    # Claude models
    claude_pattern = r"claude[-_]?([a-z]+)[-_]?(\d+[-_]?\d*)"
    for match in re.finditer(claude_pattern, content, re.IGNORECASE):
        model = f"claude-{match.group(1)}-{match.group(2)}".lower().replace("_", "-")
        models.add(model)

    # GPT models
    gpt_pattern = r"gpt[-_]?(\d+(?:[-_]?turbo)?(?:[-_]?preview)?)"
    for match in re.finditer(gpt_pattern, content, re.IGNORECASE):
        model = f"gpt-{match.group(1)}".lower().replace("_", "-")
        models.add(model)

    # Generic model patterns in backticks
    backtick_pattern = r"`([a-z]+-[a-z0-9-]+)`"
    for match in re.finditer(backtick_pattern, content):
        candidate = match.group(1).lower()
        if any(x in candidate for x in ["claude", "gpt", "llama", "mistral"]):
            models.add(candidate)

    return models


def extract_sections(content: str) -> set[str]:
    """Extract section headings (H2 and H3)."""
    sections = set()

    # Match ## and ### headings
    heading_pattern = r"^#{2,3}\s+(.+)$"
    for match in re.finditer(heading_pattern, content, re.MULTILINE):
        heading = match.group(1).strip().lower()
        # Normalize
        heading = re.sub(r"[^\w\s]", "", heading)
        if len(heading) > 2:
            sections.add(heading)

    return sections


def extract_features(content: str) -> set[str]:
    """Extract feature keywords from content."""
    features = set()

    # Important feature keywords to look for
    feature_keywords = [
        "streaming",
        "tool use",
        "function calling",
        "vision",
        "rate limit",
        "retry",
        "debug",
        "beta",
        "context window",
        "token",
        "error recovery",
        "validation",
        "graceful",
    ]

    content_lower = content.lower()
    for keyword in feature_keywords:
        if keyword in content_lower:
            features.add(keyword.replace(" ", "_"))

    return features


def extract_env_vars(content: str) -> set[str]:
    """Extract environment variable names."""
    env_vars = set()

    # Pattern: $VAR or ${VAR} or UPPER_CASE_VAR
    patterns = [
        r"\$([A-Z][A-Z0-9_]+)",
        r"\$\{([A-Z][A-Z0-9_]+)\}",
        r"export\s+([A-Z][A-Z0-9_]+)",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, content):
            env_vars.add(match.group(1))

    return env_vars


def extract_facts(content: str) -> ExtractedFacts:
    """Extract all structured facts from content."""
    return ExtractedFacts(
        config_keys=extract_config_keys(content),
        models=extract_models(content),
        sections=extract_sections(content),
        features=extract_features(content),
        env_vars=extract_env_vars(content),
    )


def compare_facts(source_facts: ExtractedFacts, doc_facts: ExtractedFacts) -> dict:
    """Compare facts between source and doc."""
    # Config key comparison (critical)
    missing_config = source_facts.config_keys - doc_facts.config_keys
    extra_config = doc_facts.config_keys - source_facts.config_keys

    # Model comparison (critical)
    missing_models = source_facts.models - doc_facts.models
    extra_models = doc_facts.models - source_facts.models

    # Section comparison (important)
    missing_sections = source_facts.sections - doc_facts.sections

    # Feature comparison (important)
    missing_features = source_facts.features - doc_facts.features

    # Calculate staleness score
    # 3 points per missing config key or model mismatch
    # 2 points per missing important section
    # 1 point per missing feature
    score = (
        3 * len(missing_config)
        + 3 * len(missing_models)
        + 3 * len(extra_models)  # Model version changes
        + 2 * len(missing_sections)
        + 1 * len(missing_features)
    )

    # Determine staleness
    is_stale = (
        len(missing_config) >= 1
        or len(missing_models) >= 1
        or len(extra_models) >= 1
        or score >= 5
    )

    return {
        "staleness_score": score,
        "is_stale": is_stale,
        "missing_config_keys": sorted(missing_config),
        "extra_config_keys": sorted(extra_config),
        "missing_models": sorted(missing_models),
        "extra_models": sorted(extra_models),
        "missing_sections": sorted(list(missing_sections)[:10]),
        "missing_features": sorted(missing_features),
        "source_facts": {
            "config_keys": len(source_facts.config_keys),
            "models": len(source_facts.models),
            "sections": len(source_facts.sections),
            "features": len(source_facts.features),
        },
        "doc_facts": {
            "config_keys": len(doc_facts.config_keys),
            "models": len(doc_facts.models),
            "sections": len(doc_facts.sections),
            "features": len(doc_facts.features),
        },
    }


def analyze_mapping(
    outline_path: str, repos_dir_str: str, docs_dir_str: str = "docs"
) -> dict:
    """Analyze all mappings in the outline."""
    repos_dir = Path(repos_dir_str).expanduser()
    docs_dir = Path(docs_dir_str)

    with open(outline_path) as f:
        outline = json.load(f)

    results = {
        "summary": {
            "total_sections": 0,
            "analyzed": 0,
            "stale": 0,
            "healthy": 0,
            "missing_doc": 0,
            "missing_source": 0,
        },
        "stale_docs": [],
        "healthy_docs": [],
        "missing_docs": [],
    }

    for section in outline.get("content_sections", []):
        section_id = section.get("id", "unknown")
        doc_path = section.get("doc_path", "")
        sources = section.get("sources", [])
        relationship = section.get("relationship_type", "DERIVED")
        priority = section.get("metadata", {}).get("priority", "medium")

        results["summary"]["total_sections"] += 1

        # Skip N/A relationships
        if relationship == "N/A" or not sources:
            continue

        # Check if doc exists
        if doc_path.startswith("docs/"):
            full_doc_path = docs_dir / doc_path[5:]
        else:
            full_doc_path = docs_dir / doc_path

        if not full_doc_path.exists():
            results["summary"]["missing_doc"] += 1
            results["missing_docs"].append(
                {
                    "section_id": section_id,
                    "doc_path": doc_path,
                    "priority": priority,
                }
            )
            continue

        # Read doc content
        doc_content = full_doc_path.read_text()

        # Aggregate source content
        source_content = ""
        sources_found = 0
        sources_missing = []

        for source in sources:
            repo = source.get("repo", "")
            path = source.get("path", "")

            # Handle wildcards
            if "*" in path:
                import glob

                pattern = str(repos_dir / repo / path)
                matches = glob.glob(pattern)
                if matches:
                    for match_path in matches[:5]:  # Limit to 5 files
                        source_content += Path(match_path).read_text() + "\n\n"
                    sources_found += 1
                else:
                    sources_missing.append(f"{repo}/{path}")
            else:
                source_path = repos_dir / repo / path
                if source_path.exists():
                    source_content += source_path.read_text() + "\n\n"
                    sources_found += 1
                else:
                    sources_missing.append(f"{repo}/{path}")

        if not source_content:
            results["summary"]["missing_source"] += 1
            continue

        results["summary"]["analyzed"] += 1

        # Extract facts from both
        source_facts = extract_facts(source_content)
        doc_facts = extract_facts(doc_content)

        # Compare facts
        comparison = compare_facts(source_facts, doc_facts)

        entry = {
            "section_id": section_id,
            "doc_path": doc_path,
            "relationship": relationship,
            "priority": priority,
            "sources_found": sources_found,
            "sources_missing": sources_missing,
            "comparison": comparison,
            "is_stale": comparison["is_stale"],
            "staleness_reasons": [],
        }

        # Build staleness reasons
        if comparison["missing_config_keys"]:
            entry["staleness_reasons"].append(
                f"Missing config: {', '.join(comparison['missing_config_keys'][:5])}"
            )
        if comparison["missing_models"]:
            entry["staleness_reasons"].append(
                f"Missing models: {', '.join(comparison['missing_models'])}"
            )
        if comparison["extra_models"]:
            entry["staleness_reasons"].append(
                f"Outdated models: {', '.join(comparison['extra_models'])}"
            )
        if comparison["missing_features"]:
            entry["staleness_reasons"].append(
                f"Missing features: {', '.join(comparison['missing_features'][:3])}"
            )

        if comparison["is_stale"]:
            results["summary"]["stale"] += 1
            results["stale_docs"].append(entry)
        else:
            results["summary"]["healthy"] += 1
            results["healthy_docs"].append(entry)

    # Sort stale docs by priority and score
    priority_order = {"high": 0, "medium": 1, "low": 2}
    results["stale_docs"].sort(
        key=lambda x: (
            priority_order.get(x["priority"], 1),
            -x["comparison"]["staleness_score"],
        )
    )

    return results


def generate_report(results: dict, output_path: str) -> str:
    """Generate markdown report from analysis results."""
    s = results["summary"]

    if s["analyzed"] > 0:
        health_pct = (s["healthy"] / s["analyzed"]) * 100
    else:
        health_pct = 0

    if health_pct >= 90:
        status = "🟢 HEALTHY"
    elif health_pct >= 70:
        status = "🟡 WARNING"
    else:
        status = "🔴 CRITICAL"

    report = f"""# Documentation Freshness Report (Structured Analysis v2)

**Generated:** {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M")}
**Analysis Type:** Structured fact comparison (config keys, models, features)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Sections** | {s["total_sections"]} |
| **Analyzed** | {s["analyzed"]} |
| **Healthy** | {s["healthy"]} |
| **Stale** | {s["stale"]} |
| **Missing Docs** | {s["missing_doc"]} |
| **Health Score** | {health_pct:.0f}% |
| **Status** | {status} |

---

## Stale Documentation ({s["stale"]} found)

"""

    if results["stale_docs"]:
        for doc in results["stale_docs"]:
            comp = doc["comparison"]
            reasons = (
                ", ".join(doc["staleness_reasons"])
                if doc["staleness_reasons"]
                else "Score threshold"
            )

            report += f"""### {doc["doc_path"]}

| Attribute | Value |
|-----------|-------|
| **Priority** | {doc["priority"].upper()} |
| **Staleness Score** | {comp["staleness_score"]} |
| **Reasons** | {reasons} |

"""
            if comp["missing_config_keys"]:
                report += "**Missing Config Keys:**\n"
                for key in comp["missing_config_keys"][:10]:
                    report += f"- `{key}`\n"
                report += "\n"

            if comp["missing_models"] or comp["extra_models"]:
                report += "**Model Mismatches:**\n"
                for model in comp["missing_models"]:
                    report += f"- Missing: `{model}`\n"
                for model in comp["extra_models"]:
                    report += f"- Outdated: `{model}` (in doc but not source)\n"
                report += "\n"

            if comp["missing_features"]:
                report += "**Missing Features:**\n"
                for feat in comp["missing_features"]:
                    report += f"- {feat.replace('_', ' ')}\n"
                report += "\n"

            report += "---\n\n"
    else:
        report += "*No stale documentation found.*\n\n---\n\n"

    # Healthy docs summary
    report += f"""## Healthy Documentation ({s["healthy"]} found)

"""
    if results["healthy_docs"]:
        for doc in results["healthy_docs"][:10]:
            report += f"- ✅ {doc['doc_path']}\n"
        if len(results["healthy_docs"]) > 10:
            report += f"- ... and {len(results['healthy_docs']) - 10} more\n"
    else:
        report += "*No healthy documentation found.*\n"

    report += """
---

## Recommendations

"""

    high_stale = [d for d in results["stale_docs"] if d["priority"] == "high"]
    if high_stale:
        report += "### 🔴 High Priority (Update Immediately)\n\n"
        for doc in high_stale[:5]:
            report += f"1. **{doc['doc_path']}**\n"
            for reason in doc["staleness_reasons"][:2]:
                report += f"   - {reason}\n"
        report += "\n"

    medium_stale = [d for d in results["stale_docs"] if d["priority"] == "medium"]
    if medium_stale:
        report += "### 🟡 Medium Priority\n\n"
        for doc in medium_stale[:5]:
            report += f"1. **{doc['doc_path']}** - Score: {doc['comparison']['staleness_score']}\n"
        report += "\n"

    if not results["stale_docs"]:
        report += "✅ **All documentation is up-to-date!**\n"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(report)

    return report


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Analyze documentation freshness")
    parser.add_argument("--outline", default="outlines/amplifier-docs-outline.json")
    parser.add_argument("--repos-dir", default="~/repo/amplifier-sources")
    parser.add_argument(
        "--output", default="sync-output/reports/content-analysis-report.md"
    )
    parser.add_argument(
        "--json-output", default="sync-output/cache/content-analysis.json"
    )
    args = parser.parse_args()

    print("Analyzing documentation content (v2 - structured facts)...")
    print(f"  Outline: {args.outline}")
    print(f"  Repos: {args.repos_dir}")

    results = analyze_mapping(args.outline, args.repos_dir)

    # Save JSON results
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_output, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  JSON saved: {args.json_output}")

    # Generate and save report
    generate_report(results, args.output)
    print(f"  Report saved: {args.output}")

    # Print summary
    s = results["summary"]
    print("\n=== SUMMARY ===")
    print(f"  Analyzed: {s['analyzed']} sections")
    print(f"  Healthy: {s['healthy']}")
    print(f"  Stale: {s['stale']}")
    print(f"  Missing docs: {s['missing_doc']}")

    if s["stale"] > 0:
        print("\n=== TOP STALE DOCS ===")
        for doc in results["stale_docs"][:5]:
            reasons = ", ".join(doc["staleness_reasons"][:2]) or "Score threshold"
            print(f"  - {doc['doc_path']}: {reasons}")


if __name__ == "__main__":
    main()
