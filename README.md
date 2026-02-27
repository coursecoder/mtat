# MTAT — Modular Training Architecture Template

A content architecture for training courses designed to be maintained by one person and adapted by AI.

MTAT separates training content into **atomic, typed modules** — concept, demo, exercise, assessment — so that a single base module can be AI-adapted into unlimited audience-specific variants without manual rework per variant. A CLI tool (`generate-variant.py`) drives the adaptation using Claude. A versioned system prompt (`prompts/adapt.md`) governs how Claude adapts content and what it must never change.

---

## The Problem This Solves

Training content decays. Product capabilities change. Audiences diverge. Teams multiply.

The traditional response is manual: update the deck, rework the exercises, brief the trainers, repeat for every audience and locale. At small scale, this works. At scale, it collapses — the content library drifts, variants become inconsistent, and the single person who owns the material becomes a bottleneck for every adaptation request.

MTAT is built around a different assumption: if content is structured correctly, an LLM can handle audience adaptation reliably and consistently, and one content owner can operate at the output level that previously required a full team.

---

## Architecture Overview

### Atomic Module Types

Every unit of content is one of four types, with a defined pedagogical role:

| Type | Role | Typical Length |
|---|---|---|
| `concept` | Introduces and explains a new idea | 10–20 min |
| `demo` | Shows the concept applied to a real scenario | 15–25 min |
| `exercise` | Learner applies the concept hands-on | 20–40 min |
| `assessment` | Checks comprehension and surfaces gaps | 5–15 min |

Modules are sequenced by course, not embedded in a deck. The separation means any module can be reused across courses, replaced without touching adjacent content, and adapted independently.

### Module Anatomy

Each module is a directory containing exactly two files:

```
01-concept/
├── base.md          # The content — markdown, audience-agnostic
└── metadata.yaml    # Structured data — ID, objectives, type, version, tags
```

`base.md` contains no front matter. It is plain Markdown that can be read by humans, processed by scripts, or fed to an LLM without parsing complexity.

`metadata.yaml` is the source of truth for all structured facts about the module. The adaptation tool reads it and injects a variant-specific front matter block into each generated output.

### Module ID System

Module IDs follow the pattern: `<course-id>-<sequence-number>`

```
pe-fundamentals-01   # Course: prompt-engineering-fundamentals, Module 1
pe-fundamentals-02   # Course: prompt-engineering-fundamentals, Module 2
```

IDs are:
- Stable across versions (the ID never changes even when content does)
- Referenced in `prerequisites` fields to express sequencing
- Used in `manifest.yaml` to trace every generated variant back to its source

### Variant Tracking

Every call to `generate-variant.py` appends a record to `variants/manifest.yaml`:

```yaml
- module_id: pe-fundamentals-01
  module_path: example-course/01-concept
  audience: developer
  locale: en-US
  output_file: variants/01-concept/developer-en-US.md
  generated_at: 2025-01-15T14:32:00Z
  model: claude-opus-4-6
  input_tokens: 1842
  output_tokens: 2103
```

The manifest is the audit trail. It answers: what variants exist, when they were generated, and what model produced them. When source content changes, the manifest tells you exactly which variants are now stale.

---

## Repository Structure

```
mtat/
├── README.md                          # This file
├── RUBRIC.md                          # Content quality rubric (score new modules before adding)
├── requirements.txt                   # Python dependencies
├── .gitignore
│
├── generate-variant.py                # CLI tool: adapts any module for any audience
│
├── prompts/
│   └── adapt.md                       # System prompt governing Claude's adaptation behavior
│                                      # Version-controlled — changes here change all future variants
│
├── example-course/                    # Complete working example: Prompt Engineering Fundamentals
│   ├── README.md
│   ├── 01-concept/
│   │   ├── base.md
│   │   └── metadata.yaml
│   ├── 02-demo/
│   │   ├── base.md
│   │   └── metadata.yaml
│   ├── 03-exercise/
│   │   ├── base.md
│   │   └── metadata.yaml
│   └── 04-assessment/
│       ├── base.md
│       └── metadata.yaml
│
└── variants/                          # Generated output (gitignored except manifest)
    └── manifest.yaml                  # Audit trail of all generated variants
```

---

## Quickstart

### 1. Install dependencies

Create and activate a virtual environment, then install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> On Windows: `.venv\Scripts\activate`
>
> You'll need to run `source .venv/bin/activate` at the start of each new terminal session before using the script.

### 2. Set your API key

```bash
export ANTHROPIC_API_KEY=your_key_here
```

Or add it to a `.env` file in the repo root:

```
ANTHROPIC_API_KEY=your_key_here
```

### 3. Generate a variant

```bash
python3 generate-variant.py --module example-course/01-concept --audience developer
```

Output is written to `variants/01-concept/developer-en-US.md`. The manifest is updated at `variants/manifest.yaml`.

---

## CLI Reference

```
python3 generate-variant.py [OPTIONS]

Options:
  --module PATH       Path to the module directory. Required.
                      Must contain base.md and metadata.yaml.

  --audience TEXT     Target audience. Required.
                      Built-in presets: developer, executive, champion, technical-writer
                      Any other string is passed to Claude as a custom audience description.

  --locale TEXT       Output locale as a BCP 47 tag. Default: en-US
                      Examples: es-MX, fr-FR, ja-JP, pt-BR

  --output DIR        Output directory. Default: variants/
```

### Audience Presets

| Preset | Who they are | Adaptation focus |
|---|---|---|
| `developer` | Engineers building with LLMs and APIs | Technical precision, code examples, mechanism over metaphor |
| `executive` | Senior leaders making investment decisions | ROI framing, business outcomes, strategic context |
| `champion` | Internal trainers running team rollouts | Facilitation notes, timing, discussion prompts, debrief guides |
| `technical-writer` | Doc and content professionals | Analogies to content workflows, structured authoring patterns |

Custom audiences are supported — pass any descriptive string and Claude will adapt accordingly:

```bash
python3 generate-variant.py --module example-course/01-concept \
  --audience "healthcare compliance officers with no prior AI experience"
```

### Locale Support

The `--locale` flag triggers full translation of all text content. Code blocks are preserved exactly; only inline comments and string values within code are translated.

```bash
python3 generate-variant.py --module example-course/02-demo \
  --audience developer --locale es-MX
```

---

## Adding a New Course

1. Create a subdirectory under the repo root (e.g., `my-new-course/`).
2. Create one subdirectory per module, numbered sequentially.
3. In each module directory, create `base.md` and `metadata.yaml`.
4. Score the module against `RUBRIC.md` before treating it as production-ready.
5. Generate your first variants:
   ```bash
   python3 generate-variant.py --module my-new-course/01-concept --audience developer
   ```

### metadata.yaml Template

```yaml
id: <course-id>-<sequence>          # e.g., api-essentials-01
title: "Module Title"
module_type: concept                 # concept | demo | exercise | assessment
course_id: <course-id>              # e.g., api-essentials
version: "1.0"
audience: general
locale: en-US
estimated_minutes: 15
prerequisites: []                    # list of module IDs this module depends on
learning_objectives:
  - Objective phrased as a learner outcome (starts with a verb)
  - Another objective
tags:
  - relevant-tag
last_updated: "YYYY-MM-DD"
```

---

## Architecture Decisions

### Why separate content from metadata?

`base.md` contains prose. `metadata.yaml` contains structured data. They serve different consumers: humans and editors read `base.md`; scripts, LLMs, and quality checks read `metadata.yaml`. Mixing them (e.g., front matter in base.md) creates parsing friction and makes the metadata harder to query programmatically.

### Why version-control the system prompt?

`prompts/adapt.md` governs what Claude does with every module. A change to the system prompt changes all future variants. Keeping it in version control means you can:
- See exactly what changed between prompt versions
- Attribute quality differences to specific prompt changes
- Roll back if a prompt update degrades output quality
- Require review before prompt changes merge

### Why track token counts in the manifest?

Token counts in `manifest.yaml` make cost visible. Over time, the manifest tells you the average cost per variant type, which audiences require the most tokens (and why), and whether cost is trending up as modules grow. Cost-blindness is how content operations quietly become expensive.

### Why gitignore generated variant files?

Generated variants are outputs, not source. Committing them creates merge conflicts with no resolution strategy and inflates repo history with content that can be regenerated at any time. The manifest provides the index; the source modules provide the canonical content; the CLI provides the generation.

### Why atomic module types instead of full course documents?

A monolithic course document (one big deck or document) is difficult to adapt by part, reuse across courses, or update without reviewing the whole. Atomic modules can be updated individually, recombined into different course sequences, adapted independently for different audiences, and quality-checked at the unit level. The overhead of the directory structure pays for itself the first time you need to update one module without touching the others.

---

## Extending the System

### Add a new audience preset

Add a key-value pair to `AUDIENCE_PROFILES` in `generate-variant.py`. The value should describe who the audience is and how to adapt for them in 3–5 sentences.

### Change adaptation behavior

Edit `prompts/adapt.md`. Commit the change with a clear message describing what behavior you are changing and why. Run a test generation and compare before/after outputs before merging.

### Add a quality gate

Pipe `base.md` content to Claude with the rubric from `RUBRIC.md` before accepting a new module. A simple scoring script that calls the API with the rubric as a system prompt and the module content as the user message can automate this check.

### Connect to an LMS

The `variants/manifest.yaml` is designed to be machine-readable. A sync script can read the manifest, find variants newer than the LMS's last-known version, and push updated content to the platform's API. Each module's stable ID provides the mapping key.
