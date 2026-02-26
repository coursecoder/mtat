# Crafting Effective Prompts: Live Walkthrough

## Overview

This module walks through a realistic prompt engineering scenario from start to finish. You will see an initial prompt, the output it produces, a diagnosis of what is missing, a revised prompt, and the improved output. The goal is to make the iteration process concrete and repeatable — not to produce a perfect prompt on the first try.

Prompt engineering is an iterative discipline. Skilled practitioners do not write great prompts immediately; they write prompts, evaluate outputs, identify gaps, and refine. This module demonstrates that loop.

## The Scenario

A content manager at a software company needs to create a knowledge base article explaining how to reset a password in the company's internal HR portal. The intended audience is non-technical employees.

## Round 1: The Initial Prompt

```
Write a help article about resetting passwords.
```

**Output from this prompt (abbreviated):**

> **How to Reset Your Password**
>
> Forgotten your password? Don't worry — resetting it is simple. Follow these steps:
>
> 1. Click "Forgot Password" on the login page.
> 2. Enter your email address.
> 3. Check your email for a reset link.
> 4. Click the link and create a new password.
> 5. Log in with your new password.
>
> If you continue to have issues, contact your system administrator.

**What the prompt produced:** A generic, reasonable help article for a hypothetical system. It is not wrong — but it is also not useful. It does not reference the actual system (the HR portal), the actual audience (non-technical employees), the actual steps (which may differ), or the tone expected for internal communications.

## Diagnosing the Gap

Using the three-element framework:

| Element | Status | What Is Missing |
|---|---|---|
| Context | Absent | No mention of the HR portal, the company, or the audience |
| Task specification | Partial | "Help article" is specified, but format, length, and structure are not |
| Constraints | Absent | No tone guidance, no audience reading level, no length limit |

## Round 2: The Revised Prompt

```
Context: You are writing internal documentation for Meridian Corp's HR portal,
used by 800 non-technical employees. The portal is called "PeopleHub."
Employees access it at people.meridiancorp.internal.

Task: Write a help article explaining how to reset a PeopleHub password.
Structure the article with: a one-sentence intro, numbered steps, and a
"Still stuck?" section at the end pointing to IT support at ext. 4400.

Constraints:
- Audience: non-technical employees; assume no IT background
- Tone: friendly and direct, matching internal communication style
- Length: 150–200 words
- Do not include generic troubleshooting steps not specific to PeopleHub
```

**Output from the revised prompt (abbreviated):**

> **Reset Your PeopleHub Password**
>
> If you've forgotten your PeopleHub password, you can reset it in a few quick steps.
>
> 1. Go to people.meridiancorp.internal and click **Forgot password?** below the sign-in button.
> 2. Enter your Meridian Corp email address and click **Send reset link**.
> 3. Open the email from noreply@meridiancorp.com (check your spam folder if you don't see it).
> 4. Click **Reset my password** in the email. The link expires in 30 minutes.
> 5. Create a new password and click **Save**. You'll be signed in automatically.
>
> **Still stuck?** Contact IT support at ext. 4400 or ithelp@meridiancorp.com.

**What changed:** The article is now specific, appropriately scoped, and ready to publish with only minor customization. The model did not become smarter — the instructions became clearer.

## What Made the Difference

Three concrete changes drove the improvement:

1. **Named the system and the audience.** "PeopleHub" and "non-technical employees" anchored every word choice the model made.
2. **Specified the structure explicitly.** Instead of "help article," the prompt described the exact sections: intro, numbered steps, still-stuck section.
3. **Set a word count.** A length constraint forces the model to prioritize. Without it, the model pads; with it, the model edits.

## The Iteration Mindset

A first-draft prompt is a hypothesis. The output is data. Evaluate the output against your intent:

- Does it reference the right system/context?
- Is the format correct?
- Is the tone appropriate for the audience?
- Is anything missing that you expected to see?
- Is anything present that you did not ask for?

Each gap maps back to a missing or underspecified element. Add or tighten the relevant element, regenerate, and evaluate again. Most prompts converge in 2–3 iterations.

## Key Takeaways

- A prompt is a hypothesis; an output is data. Treat iteration as the method, not the failure.
- Specificity in context produces specificity in output — the model cannot infer what you did not say.
- Diagnosing a weak output is a skill: map every gap back to a missing element (context, task, or constraint) before rewriting.
