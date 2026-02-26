#!/usr/bin/env python3
"""
MTAT — Modular Training Architecture Template
generate-variant.py

Generates audience-adapted variants of training modules using Claude.
Reads a module's base.md + metadata.yaml, sends both to Claude with a
structured adaptation prompt, and writes the result to the variants/ directory.
A manifest.yaml file tracks all generated variants with provenance metadata.

Usage:
    python generate-variant.py --module <path> --audience <preset> [options]

Examples:
    python generate-variant.py --module example-course/01-concept --audience developer
    python generate-variant.py --module example-course/02-demo --audience executive --locale es-MX
    python generate-variant.py --module example-course/01-concept --audience champion --output my-output/
"""

import argparse
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional; ANTHROPIC_API_KEY can be set in environment

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Audience presets
# Each value is injected into the adaptation prompt so Claude knows exactly
# who it is writing for. Extend this dict to add new audience types without
# changing the core script logic.
# ---------------------------------------------------------------------------
AUDIENCE_PROFILES = {
    "developer": (
        "Software engineers and technical practitioners who build with LLMs and APIs. "
        "They want precision, code examples, edge cases, and integration details. "
        "They distrust hand-waving — show them the mechanism. Assume comfort with "
        "technical vocabulary; do not over-explain standard concepts. Favor concrete "
        "examples over metaphors."
    ),
    "executive": (
        "Senior business leaders who own budget and strategy decisions. They need "
        "ROI framing, business outcomes, and risk context. Skip implementation details; "
        "translate every feature into business impact. Lead with 'why it matters' before "
        "'what it is.' Use industry benchmarks and peer-company examples where relevant."
    ),
    "champion": (
        "Internal enablement champions who will train their own teams. They need "
        "facilitator notes, discussion prompts, timing guidance, and common participant "
        "questions. Preserve all learner-facing content but add [FACILITATOR NOTE] "
        "callouts throughout. Frame content from the perspective of someone who will teach it, "
        "not just learn it."
    ),
    "technical-writer": (
        "Documentation and content professionals learning to work with LLMs. "
        "They appreciate analogies to content workflows, structured authoring, and "
        "information architecture. Connect AI concepts to their existing mental models "
        "(DITA, structured content, single-sourcing, topic-based authoring, CMS workflows)."
    ),
}

MODEL = "claude-opus-4-6"


def load_module(module_path: Path) -> tuple[str, dict]:
    """Load base.md content and metadata.yaml from a module directory."""
    base_path = module_path / "base.md"
    meta_path = module_path / "metadata.yaml"

    missing = [p for p in (base_path, meta_path) if not p.exists()]
    if missing:
        for p in missing:
            print(f"Error: required file not found: {p}")
        sys.exit(1)

    content = base_path.read_text(encoding="utf-8")
    with open(meta_path, encoding="utf-8") as f:
        metadata = yaml.safe_load(f)

    return content, metadata


def load_system_prompt() -> str:
    """Load the versioned adaptation system prompt from prompts/adapt.md."""
    prompt_path = Path(__file__).parent / "prompts" / "adapt.md"
    if not prompt_path.exists():
        print("Warning: prompts/adapt.md not found. Using minimal fallback prompt.")
        return (
            "You are a training content adaptation specialist. "
            "Adapt the provided module for the specified audience. "
            "Preserve structure, learning objectives, and module ID. "
            "Return only the adapted Markdown content."
        )
    return prompt_path.read_text(encoding="utf-8")


def build_user_message(content: str, metadata: dict, audience: str, locale: str) -> str:
    """Construct the user-turn message sent to Claude."""
    audience_description = AUDIENCE_PROFILES.get(
        audience,
        f"Custom audience: '{audience}'. Adapt the content to be most relevant and accessible for this group."
    )

    locale_instruction = ""
    if locale != "en-US":
        locale_instruction = (
            f"\n\n**Locale:** {locale}  \n"
            "Translate the output into the target language. Preserve all Markdown "
            "formatting and code blocks exactly — translate comments and string values "
            "inside code blocks but never alter code syntax or variable names."
        )

    metadata_block = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)

    return f"""## Source Module

**Metadata:**
```yaml
{metadata_block}
```

**Base Content:**

{content}

---

## Adaptation Target

**Audience:** `{audience}`
{audience_description}{locale_instruction}

Generate the adapted module now.
"""


def build_output_front_matter(metadata: dict, audience: str, locale: str) -> str:
    """Build YAML front matter for the generated variant."""
    variant_meta = {
        "id": metadata.get("id", "unknown"),
        "title": metadata.get("title", ""),
        "module_type": metadata.get("module_type", ""),
        "course_id": metadata.get("course_id", ""),
        "version": metadata.get("version", "1.0"),
        "audience": audience,
        "locale": locale,
        "learning_objectives": metadata.get("learning_objectives", []),
        "tags": metadata.get("tags", []),
        "generated_from": "base",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return "---\n" + yaml.dump(variant_meta, default_flow_style=False, allow_unicode=True) + "---\n\n"


def update_manifest(manifest_path: Path, entry: dict) -> None:
    """Append a variant entry to the variants/manifest.yaml tracking file."""
    existing = []
    if manifest_path.exists():
        with open(manifest_path, encoding="utf-8") as f:
            existing = yaml.safe_load(f) or []
    existing.append(entry)
    with open(manifest_path, "w", encoding="utf-8") as f:
        yaml.dump(existing, f, default_flow_style=False, allow_unicode=True)


def generate_variant(
    module_path: Path,
    audience: str,
    locale: str,
    output_dir: Path,
) -> Path:
    """Core generation function. Returns the path of the written variant file."""
    content, metadata = load_module(module_path)
    system_prompt = load_system_prompt()
    user_message = build_user_message(content, metadata, audience, locale)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "Error: ANTHROPIC_API_KEY is not set.\n"
            "Set it in your environment or add it to a .env file in this directory."
        )
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"  Model : {MODEL}")
    print(f"  Module: {module_path}")
    print(f"  Audience: {audience}  |  Locale: {locale}")
    print("  Calling Claude API...")

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    adapted_content = response.content[0].text

    # Prepend structured front matter to the adapted content
    front_matter = build_output_front_matter(metadata, audience, locale)
    full_output = front_matter + adapted_content

    # Write to variants/<module-name>/<audience>-<locale>.md
    variant_dir = output_dir / module_path.name
    variant_dir.mkdir(parents=True, exist_ok=True)
    output_file = variant_dir / f"{audience}-{locale}.md"
    output_file.write_text(full_output, encoding="utf-8")

    # Update manifest
    manifest_path = output_dir / "manifest.yaml"
    update_manifest(manifest_path, {
        "module_id": metadata.get("id", "unknown"),
        "module_path": str(module_path),
        "audience": audience,
        "locale": locale,
        "output_file": str(output_file),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": MODEL,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    })

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Generate audience-adapted training module variants using Claude.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Audience presets:
  developer         Software engineers building with LLMs and APIs
  executive         Senior leaders focused on business outcomes
  champion          Internal trainers who will teach their own teams
  technical-writer  Documentation professionals learning AI workflows

Examples:
  python generate-variant.py --module example-course/01-concept --audience developer
  python generate-variant.py --module example-course/02-demo --audience executive --locale es-MX
  python generate-variant.py --module example-course/01-concept --audience champion --output custom-output/
        """,
    )
    parser.add_argument(
        "--module", required=True,
        help="Path to the module directory (must contain base.md and metadata.yaml)",
    )
    parser.add_argument(
        "--audience", required=True,
        help="Target audience preset (developer | executive | champion | technical-writer) or custom string",
    )
    parser.add_argument(
        "--locale", default="en-US",
        help="Output locale as BCP 47 tag (default: en-US). Examples: es-MX, fr-FR, ja-JP",
    )
    parser.add_argument(
        "--output", default="variants",
        help="Output directory for generated variants (default: variants/)",
    )

    args = parser.parse_args()

    module_path = Path(args.module)
    if not module_path.exists() or not module_path.is_dir():
        print(f"Error: module path does not exist or is not a directory: {module_path}")
        sys.exit(1)

    output_file = generate_variant(
        module_path=module_path,
        audience=args.audience,
        locale=args.locale,
        output_dir=Path(args.output),
    )

    print(f"\nDone.")
    print(f"  Variant : {output_file}")
    print(f"  Manifest: {Path(args.output) / 'manifest.yaml'}")


if __name__ == "__main__":
    main()
