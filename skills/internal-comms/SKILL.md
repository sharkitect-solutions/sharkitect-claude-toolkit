---
name: internal-comms
description: "Use when asked to write any internal communication: status reports, leadership updates, 3P updates, company newsletters, FAQ responses, incident reports, project updates, or any message intended for an internal audience. NEVER for external communications (press releases, customer emails, marketing copy, proposals, or public-facing content)."
license: Complete terms in LICENSE.txt
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

## File Index

Load the appropriate guideline file before writing any internal communication. These files define the exact format, tone, and structure requirements.

| File | Communication Type | Load When |
|------|--------------------|-----------|
| `examples/3p-updates.md` | Progress / Plans / Problems updates | Team or project update with a recurring cadence; sender wants structured three-part format |
| `examples/company-newsletter.md` | Company-wide newsletters | Audience is the whole company or a large cross-functional group; multiple topics or sections |
| `examples/faq-answers.md` | FAQ responses | User asks Claude to answer a set of questions or draft FAQ-style content for internal audiences |
| `examples/general-comms.md` | Everything else | Communication type does not clearly match any of the above; use as the fallback |

**Decision rule for ambiguous cases:** When the communication type is unclear, ask one clarifying question: "Who is the intended audience and what action (if any) do they need to take?" The answer usually resolves ambiguity. If still unclear, default to `general-comms.md`.

---

## How to Use This Skill

1. **Identify the communication type** from the request.
2. **Load the matching guideline file** from the table above.
3. **Follow the specific instructions** in that file for formatting, tone, content gathering, and structure.
4. **Do not write from memory.** The guideline files are the authoritative source. Reading them is not optional.

This sequence is non-negotiable. Skipping Step 2 is the most common failure mode.

---

## Rationalization Table

These are the excuses Claude makes to skip loading the proper template. Recognize them and reject them.

| Rationalization | Why It Is Wrong |
|-----------------|-----------------|
| "This is a simple status update, I can write it from memory." | Memory-based writing drifts from the company's preferred format. Load the template regardless of perceived simplicity. |
| "I know how to write a newsletter, I don't need the file." | Generic newsletter structure is not the same as the format this company uses. The file exists for a reason. |
| "The user just wants something quick, the template is overkill." | Speed is not a reason to produce non-standard output. Templates are fast to follow once loaded. |
| "Internal comms don't need formal structure." | Internal audiences are often senior stakeholders who expect consistent, structured communications. Informal does not mean structureless. |
| "This is basically a 3P update but the user didn't say so, so I'll wing it." | Pattern-match on the content, not just the label. If it has Progress, Plans, and Problems, use the 3P template. |
| "The guideline file probably just says the same thing I would write anyway." | The point of loading the file is to confirm that assumption, not skip on the assumption. |
| "There's no perfect template for this, so I'll skip all of them." | Imperfect fit is exactly when `general-comms.md` exists. Fall back to it rather than writing freeform. |
| "The user gave me so much context that I already know what to write." | User-provided context fills in the content; the template provides the structure. Both are needed. |

---

## Red Flags Checklist

These are observable signs that the skill is being violated or that the communication will fail its purpose. Check for each before delivering output.

- [ ] The communication was written without loading any guideline file from `examples/`.
- [ ] The communication type was assumed rather than identified from the request or a clarifying question.
- [ ] The lede is buried: the most important information appears after the second paragraph.
- [ ] The audience level is wrong: technical jargon in a leadership update, or oversimplified language in a team-level technical update.
- [ ] Missing action items: the communication requires a decision or response but contains no explicit ask.
- [ ] Wall of text: no headers, bullets, or visual separation in a communication longer than 150 words.
- [ ] Passive voice dominates: "it was decided," "the issue was resolved," "the plan was updated" without naming who owns what.
- [ ] The tone is inconsistent: starts formal, ends casual, or vice versa.
- [ ] No clear ownership: the communication describes a problem or plan without naming a responsible person or team.
- [ ] The subject line or opening line does not state the purpose of the communication.
- [ ] Status is ambiguous: "things are going well" instead of "on track," "at risk," or "blocked."
- [ ] The communication length does not match the audience: a one-sentence request was turned into a five-paragraph essay, or a complex incident was summarized in two lines.

---

## NEVER List

| Prohibition | Why |
|-------------|-----|
| NEVER write an internal communication without first loading the relevant guideline file. | Freeform writing produces output that does not match the company's expected format, forcing revision. |
| NEVER default to external communication conventions (press release tone, marketing language, customer-facing framing). | Internal audiences expect directness and operational detail, not polish and narrative. |
| NEVER omit the status indicator in status reports or project updates. | Readers scan for red/yellow/green before reading body text. Missing it forces follow-up questions. |
| NEVER bury the action item. | If a response, decision, or action is needed, it goes in the first paragraph or as a standalone callout, not at the end. |
| NEVER use jargon calibrated for one audience when writing for another. | A leadership update and a technical team sync have different vocabulary requirements. Confirm audience before writing. |
| NEVER write a 3P update without all three sections. | Progress, Plans, and Problems are a complete unit. Omitting Problems sanitizes the picture and erodes trust. |
| NEVER ignore a stated format preference from the user. | If the user specifies length, structure, or tone, that overrides guideline defaults. |

---

## Tone Calibration Guide

Internal communication tone is not uniform. Use this guide to calibrate before writing.

### Leadership Updates (Executives, Directors, VPs)
- **Length:** Short. One screen or less. Use bullets, not prose.
- **Tone:** Direct, confident, no hedging. State status clearly.
- **Content emphasis:** Business impact, decisions needed, risks, and timelines. Omit implementation detail unless asked.
- **Common mistake:** Over-explaining context that leadership already has. Start from where they are, not from the beginning.

### Team-Level Updates (Peers, ICs, Technical Colleagues)
- **Length:** As long as needed to be complete. Detail is welcome.
- **Tone:** Collaborative, specific, technically accurate.
- **Content emphasis:** What happened, what is next, what is blocked, what is needed from others.
- **Common mistake:** Omitting blockers or problems because they feel like bad news. Peer-level updates require honesty to function.

### Company-Wide Communications
- **Length:** Moderate. Use clear section headers. Assume low shared context.
- **Tone:** Warm but professional. Avoid internal acronyms and team-specific shorthand.
- **Content emphasis:** Why this matters to the reader, what changes for them, what they need to do (if anything).
- **Common mistake:** Writing for the sender's team rather than the full company audience.

### Incident Reports
- **Length:** Comprehensive. Do not abbreviate.
- **Tone:** Factual, neutral, accountable. No blame language, no defensive framing.
- **Content emphasis:** Timeline, root cause, impact, resolution, and prevention steps. All four sections are required.
- **Common mistake:** Writing a resolution without writing the root cause. Resolution without diagnosis does not prevent recurrence.

### FAQ Responses
- **Length:** Per-answer brevity. Each answer should be complete in 2-4 sentences unless complexity demands more.
- **Tone:** Clear, helpful, scannable.
- **Content emphasis:** Anticipate the next question each answer will generate and address it preemptively.
- **Common mistake:** Writing FAQ answers as mini-essays. If an answer exceeds 100 words, it should be broken into sub-questions or supplemented with a linked reference.

---

## Handling Ambiguous Communication Types

Some requests do not obviously fit a single template. Use these decision criteria.

**"Write an update for the all-hands"**
This is a company-wide communication. Load `examples/company-newsletter.md` even if it is framed as an "update." All-hands content follows newsletter conventions: multiple sections, broad audience, low assumed context.

**"Write a project update for my stakeholders"**
Stakeholders could be peers or leadership. Ask: "Are the primary stakeholders executives or the project team?" Leadership stakeholders get a short, structured leadership update. Project team stakeholders get a detailed team-level update.

**"Write a 3P update but make it casual"**
Casual tone is a style modifier, not a format modifier. Load `examples/3p-updates.md` and apply the tone adjustment on top of the structure. Do not skip the template because the tone request implies informality.

**"Help me write an email to my team about the outage"**
This is an incident communication. Load `examples/general-comms.md` and apply incident report conventions (timeline, root cause, impact, resolution, next steps). If the incident was significant, suggest the user also complete a formal incident report separately.

**"Write something for the company Slack"**
Slack messages are internal communications. Identify what type of update is being posted (team status, announcement, incident notification) and load the corresponding template. Apply length constraints appropriate to Slack (shorter, punchier, clear call-to-action in the first line).

---

## Anti-Patterns to Avoid

These are the most common ways internal communications fail, independent of format.

**Buried lede.** The most important information -- the status, the ask, the decision -- appears in the third paragraph. Readers who skim miss it entirely. Fix: put the key message in the first sentence.

**Missing ownership.** The communication describes work, status, or plans without naming who is responsible. "The issue is being investigated" is useless. "Priya and the platform team are investigating, ETA is Friday" is actionable. Fix: every action item and open question must have a named owner.

**False green.** A project status is reported as on-track when it is actually at risk, because the writer wants to avoid delivering bad news. This destroys trust and delays intervention. Fix: use the traffic-light convention honestly. At-risk is not failure; it is a request for help.

**Audience mismatch.** A leadership update contains three paragraphs of implementation detail that the executive does not need or want. A team update uses business-impact framing without the technical specifics the team needs to act. Fix: confirm the primary audience before writing. Let audience determine what to include and what to omit.

**No clear next step.** The communication ends without a clear statement of what happens next or what the reader needs to do. This generates follow-up questions that the communication was meant to prevent. Fix: every communication should end with either "No action needed, for information only" or a specific, time-bound ask.
