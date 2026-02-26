# Content Quality Rubric

Use this rubric to evaluate a module before adding it to the library and after generating AI-adapted variants. Score each dimension 1–5. A module scoring below 3 on any dimension should not be published without revision.

The rubric serves two purposes:
1. **Human review gate:** Run it manually on new base modules before they enter the library.
2. **Automated spot-check:** Pipe base.md content and this rubric to an LLM to generate a structured quality report at scale.

---

## Scoring Scale

| Score | Meaning |
|---|---|
| 5 | Exemplary — exceeds standard; usable as a reference |
| 4 | Meets standard — minor gaps that do not affect usability |
| 3 | Acceptable — present but needs improvement before next version |
| 2 | Below standard — significant gaps; revise before publishing |
| 1 | Absent or incoherent — do not publish |

---

## Dimension 1: Learning Objective Alignment

**What to look for:** Every learning objective stated in metadata.yaml is addressed somewhere in the content. The module does not teach things that are not in the objectives. Objectives are written as observable learner outcomes (starts with a measurable verb: identify, write, explain, compare, apply — not "understand" or "know").

| Score | Evidence |
|---|---|
| 5 | All objectives are covered; each maps to a specific section; objectives are measurable verbs |
| 4 | All objectives covered; one objective could be more specifically addressed |
| 3 | All objectives mentioned but one is thin or non-measurable |
| 2 | One or more objectives are missing from the content |
| 1 | Objectives and content are misaligned or objectives are absent |

**Score: _____ / 5**

**Notes:** _______________________________________________

---

## Dimension 2: Technical Accuracy

**What to look for:** Facts, examples, code, product names, and procedure steps are correct and current. No deprecated methods, outdated screenshots, or incorrect claims. If the module covers a specific product or API, version references are explicit.

| Score | Evidence |
|---|---|
| 5 | All content verifiable; code runs; product references are versioned |
| 4 | Content accurate; minor gaps in version specificity |
| 3 | Mostly accurate; one claim is ambiguous or unverified |
| 2 | One or more factual errors or significantly outdated examples |
| 1 | Multiple errors; content should not be used as written |

**Score: _____ / 5**

**Notes:** _______________________________________________

---

## Dimension 3: Audience Appropriateness

**What to look for:** Vocabulary, examples, tone, and depth match the stated audience in metadata.yaml. The module does not assume knowledge the audience lacks or over-explain things the audience already knows well. Jargon is either avoided or defined on first use.

| Score | Evidence |
|---|---|
| 5 | Pitch-perfect for the stated audience throughout |
| 4 | Appropriate; one section drifts slightly in vocabulary or depth |
| 3 | Audience is generally served but noticeable gaps in vocabulary calibration |
| 2 | Significant mismatch — too technical, too basic, or wrong tone |
| 1 | Content is clearly written for a different audience |

**Score: _____ / 5**

**Notes:** _______________________________________________

---

## Dimension 4: Example Quality

**What to look for:** Examples are specific, realistic, and directly illustrate the concept being taught. Generic, abstract, or toy examples score lower. Examples reference real systems, realistic data, or recognizable scenarios — not placeholder data like "foo/bar" or "Lorem ipsum."

| Score | Evidence |
|---|---|
| 5 | Examples are specific, realistic, and illuminate the concept better than any explanation could |
| 4 | Good examples; one could be more specific or realistic |
| 3 | Examples are present but generic or not directly tied to the learning objective |
| 2 | Examples are vague, abstract, or tangential to the concept |
| 1 | No examples, or examples actively confuse rather than clarify |

**Score: _____ / 5**

**Notes:** _______________________________________________

---

## Dimension 5: Structural Completeness

**What to look for:** The module follows the expected structure for its type:
- **concept**: overview → explanation → example(s) → check for understanding
- **demo**: scenario → initial attempt → diagnosis → revision → key takeaways
- **exercise**: goal → prerequisites → step-by-step instructions → reflection
- **assessment**: clear instructions → questions → answer key or rubric

Every section expected for the module type is present. Headings are used consistently.

| Score | Evidence |
|---|---|
| 5 | Complete structure; all expected sections present; logical flow throughout |
| 4 | Complete; one section is thinner than ideal |
| 3 | Mostly complete; one expected section is missing or significantly underdeveloped |
| 2 | Two or more sections missing; flow is disrupted |
| 1 | No discernible structure; content is not organized by type conventions |

**Score: _____ / 5**

**Notes:** _______________________________________________

---

## Dimension 6: AI Adaptability

**What to look for:** Content is structured for AI-assisted adaptation. This means: no embedded images or diagrams that carry essential meaning (describe them in text instead), no audience-specific content locked into the base module (save it for variants), examples are generic enough to be replaced by the adaptation tool, and no hard-coded product names that would be wrong for all variants.

| Score | Evidence |
|---|---|
| 5 | Fully adaptable; no audience lock-in; examples are replaceable; no image-only content |
| 4 | Adaptable; one small piece of audience-specific language could be abstracted |
| 3 | Mostly adaptable; one element will require manual review after adaptation |
| 2 | Significant adaptation friction; content is audience-specific in ways that will confuse variants |
| 1 | Not adaptable without major rewrite |

**Score: _____ / 5**

**Notes:** _______________________________________________

---

## Summary Scorecard

| Dimension | Score | Status |
|---|---|---|
| 1. Learning Objective Alignment | /5 | |
| 2. Technical Accuracy | /5 | |
| 3. Audience Appropriateness | /5 | |
| 4. Example Quality | /5 | |
| 5. Structural Completeness | /5 | |
| 6. AI Adaptability | /5 | |
| **Total** | **/30** | |

**Publication decision:**
- 27–30: Publish as-is
- 22–26: Publish with minor revisions noted above
- 15–21: Revise before publishing; address all dimensions scoring below 3
- Below 15: Do not publish; return for significant revision

---

## Using This Rubric for Automated Spot-Checks

To generate a scored quality report using Claude:

1. Use this file as the system prompt.
2. Pass the module's `base.md` content as the user message.
3. Instruct Claude to return a JSON object with keys for each dimension (`learning_objectives`, `technical_accuracy`, `audience_appropriateness`, `example_quality`, `structural_completeness`, `ai_adaptability`), each containing `score` (int 1–5) and `rationale` (string) and `suggested_improvement` (string or null).

This automates first-pass quality triage. Human review is still required for technical accuracy (Dimension 2), which requires domain knowledge the model may not have.
