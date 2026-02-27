# MTAT — Modular Training Architecture Template

A Python CLI system for AI-assisted adaptation of training course modules. One person maintains base content; Claude adapts it for unlimited audiences and locales.

## Project Overview

- **`generate-variant.py`** — Core CLI: reads a module (`base.md` + `metadata.yaml`), calls Claude API, writes an audience-adapted variant to `variants/`
- **`upload-to-moodle.py`** — Uploads generated variants to a local Moodle LMS via Docker for preview
- **`prompts/adapt.md`** — Version-controlled system prompt governing Claude's adaptation behavior
- **`RUBRIC.md`** — Quality scoring rubric (1–5 per dimension) for evaluating base modules and variants
- **`example-course/`** — Working example: Prompt Engineering Fundamentals (4 modules: concept, demo, exercise, assessment)
- **`variants/`** — Generated output (gitignored except `manifest.yaml`)

## Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here   # or add to .env
```

## Key Commands

```bash
# Generate a variant
python3 generate-variant.py --module example-course/01-concept --audience developer
python3 generate-variant.py --module example-course/02-demo --audience executive --locale es-MX

# Start local Moodle (Docker)
docker compose up -d

# Upload variants to Moodle (first time)
python upload-to-moodle.py --setup-moodle
# Subsequent runs
python upload-to-moodle.py
```

## Audience Presets

| Preset | Who they are |
|---|---|
| `developer` | Engineers building with LLMs/APIs — technical, mechanism-first |
| `executive` | Senior leaders — ROI framing, business outcomes |
| `champion` | Internal trainers — facilitation notes, timing, debrief prompts |
| `technical-writer` | Doc professionals — structured authoring analogies |

Custom audiences are supported: `--audience "healthcare compliance officers with no prior AI experience"`

## Module Structure

Each module is a directory with exactly two files:

```
01-concept/
├── base.md          # Content — plain Markdown, audience-agnostic
└── metadata.yaml    # Structured data: ID, type, objectives, version, tags
```

Module types: `concept` | `demo` | `exercise` | `assessment`

## Adding a New Course

1. Create a subdirectory (e.g., `my-course/`)
2. Add numbered module subdirectories with `base.md` + `metadata.yaml`
3. Score each module against `RUBRIC.md` — must score ≥3 on all dimensions before publishing
4. Generate variants: `python3 generate-variant.py --module my-course/01-concept --audience developer`

## Variant Manifest

Every generation appends to `variants/manifest.yaml` — the audit trail tracking module ID, audience, locale, output file, timestamp, model, and token counts (for cost visibility).

## Architecture Notes

- `base.md` has no front matter — the script prepends YAML front matter to each generated variant
- `prompts/adapt.md` is version-controlled — changes affect all future variants; commit with a clear rationale message
- Generated variant files are gitignored; only `manifest.yaml` is committed
- Add audience presets by extending `AUDIENCE_PROFILES` dict in `generate-variant.py`
- Module IDs (e.g., `pe-fundamentals-01`) are stable across versions and used as manifest keys

## Dependencies

- `anthropic>=0.40.0` — Claude API client
- `pyyaml>=6.0` — metadata parsing and manifest writes
- `python-dotenv>=1.0` — `.env` file support for API key
- `requests>=2.31.0` — Moodle REST API calls
- `markdown>=3.5.0` — Markdown-to-HTML conversion for Moodle upload
