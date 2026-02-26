# Check for Understanding

## Instructions

This assessment covers the core concepts from the Prompt Engineering Fundamentals course. Answer each question before reviewing the answer key. The goal is to surface gaps in understanding, not to score points.

Estimated time: 10 minutes.

---

## Section 1: Definitions

**1.** In one or two sentences, define prompt engineering in your own words. Do not quote the course materials — use language you would use to explain it to a colleague who missed the training.

> Your answer: _______________________________________________

**2.** Why does treating a prompt as a repeatable artifact (rather than a one-off message) matter for teams deploying AI at scale?

> Your answer: _______________________________________________

---

## Section 2: Identify the Elements

**3.** Read the following prompt and identify which of the three elements — context, task specification, or constraints — is present, partial, or missing.

```
Write a summary of last quarter's sales performance for the board meeting.
```

| Element | Present / Partial / Missing | Evidence from the prompt |
|---|---|---|
| Context | | |
| Task specification | | |
| Constraints | | |

**4.** Rewrite the prompt from Question 3 to include all three elements. Use realistic details.

> Your rewrite: _______________________________________________

---

## Section 3: Evaluate an Output

**5.** A team member submits this prompt and is unhappy with the output:

**Prompt:**
```
Explain machine learning to our customers.
```

**Output they received:**
> Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves. The process begins with observations or data, such as examples, direct experience, or instruction, so that computers can look for patterns in data and make better decisions in the future...

What is the primary reason the output is not working for this team member? Which element is most responsible for the poor fit?

> Your answer: _______________________________________________

---

## Section 4: Applied Scenario

**6.** You are building a shared prompt library for your team. A colleague asks you to write a reusable prompt for drafting weekly project status updates. The updates go to a VP-level audience, should be 3–5 bullet points, and must flag any blockers. Write the prompt template. Use `[PLACEHOLDER]` notation for any fields that will vary by project or week.

> Your prompt template: _______________________________________________

---

## Answer Key

**1.** Look for: the idea that prompt engineering is about designing structured inputs to produce reliable, useful outputs — not about tricks or memorization. Strong answers include something about repeatability or intentionality.

**2.** Look for: when prompts are treated as artifacts, they can be shared, improved, and audited. Individuals do not have to rediscover effective prompts. Outputs become more consistent across users and use cases.

**3.**
- Context: Missing (no audience, no purpose, no platform)
- Task specification: Partial ("summary" is specified; format, length, and focus are not)
- Constraints: Missing (no length, no level of detail, no what to include/exclude)

**4.** A strong rewrite includes: who the audience is (board), what data is included, how long the summary should be, and what to focus on (highlights, risks, or comparison to prior quarter).

**5.** The primary issue is missing context. The model does not know who "our customers" are, what industry they are in, what their technical background is, or what the communication goal is. "Explain machine learning" is also underspecified — explain at what depth, for what purpose, in what format? All three elements are weak, but context is doing the most damage.

**6.** Look for a prompt that specifies: the audience (VP level), the format (3–5 bullets), the requirement to surface blockers, and placeholders for project name, time period, and actual status. Strong answers also constrain length or tone.
