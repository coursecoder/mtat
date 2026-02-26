# Example Course: Prompt Engineering Fundamentals

This directory contains a complete example course built using the MTAT module structure. It is intended as both a working demonstration and a starting template for new courses.

## Course Overview

**Title:** Prompt Engineering Fundamentals
**ID:** `prompt-engineering-fundamentals`
**Audience:** General (all variants generated from these base modules)
**Total estimated time:** ~75 minutes

## Module Sequence

| # | ID | Type | Title | Time |
|---|---|---|---|---|
| 01 | `pe-fundamentals-01` | concept | What Is Prompt Engineering? | 15 min |
| 02 | `pe-fundamentals-02` | demo | Crafting Effective Prompts: Live Walkthrough | 20 min |
| 03 | `pe-fundamentals-03` | exercise | Prompt Iteration Lab | 30 min |
| 04 | `pe-fundamentals-04` | assessment | Check for Understanding | 10 min |

## Generating Variants

From the repo root:

```bash
# Developer variant of module 01
python generate-variant.py --module example-course/01-concept --audience developer

# Executive variant of module 02
python generate-variant.py --module example-course/02-demo --audience executive

# Spanish champion variant of module 01
python generate-variant.py --module example-course/01-concept --audience champion --locale es-MX
```

All generated variants are written to `variants/` with a `manifest.yaml` tracking file.
