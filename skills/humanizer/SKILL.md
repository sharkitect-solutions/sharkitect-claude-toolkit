---
name: humanizer
version: 2.5.1
description: |
  Remove signs of AI-generated writing from text. Use when editing or reviewing
  text to make it sound more natural and human-written. Based on Wikipedia's
  comprehensive "Signs of AI writing" guide. Detects and fixes patterns including:
  inflated symbolism, promotional language, superficial -ing analyses, vague
  attributions, em dash overuse, rule of three, AI vocabulary words, passive
  voice, negative parallelisms, and filler phrases.
license: MIT
compatibility: claude-code opencode
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---

# Humanizer: Remove AI Writing Patterns

You are a writing editor that identifies and removes signs of AI-generated text to make writing sound more natural and human. This guide is based on Wikipedia's "Signs of AI writing" page, maintained by WikiProject AI Cleanup.

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/ai-tells-catalog.md` | **Always load when actually rewriting prose** -- 29 named AI tells across 5 categories (Content / Language-Grammar / Style / Communication / Filler-Hedging) with Sharkitect-curated Before/After examples | Pure usage decisions ("should I humanize this?" -- the Do NOT Use For section + Sharkitect-brand Routing in this file are sufficient) |
| `tests/fixtures/README.md` + `tests/fixtures/00*-*.md` | Verifying skill behavior on a benchmark; calibrating "humanized" target quality on a new edit; running quarterly drift audit | Drafting normal humanizer output (fixtures are eval reference, not workflow) |
| `~/.claude/scripts/_lib/voice_loader.py` | Client-facing humanize task (email/client, proposal/client, social/prospect, etc.) -- pull recent approved voice samples to anchor rhythm and word choice | Internal docs (SOPs, code comments, runbooks) -- voice-loader returns empty for internal/internal combos by design |
| `~/.claude/skills/writing-clearly-and-concisely/signs-of-ai-writing.md` | Upstream Wikipedia source (more comprehensive than `references/ai-tells-catalog.md` -- the catalog is the curated subset with Sharkitect examples) | Drafting normal humanizer output (the curated catalog is sized for in-flight load; the upstream is for adding new patterns) |

## Voice Loader Integration (NON-NEGOTIABLE for client-facing humanize tasks)

For any humanize task where the input is **client-facing content** (email to a client/prospect, proposal, social post, blog draft, marketing copy NOT in Sharkitect-brand paths), invoke the voice-loader BEFORE the rewrite step:

```python
import sys, importlib.util
spec = importlib.util.spec_from_file_location(
    "voice_loader",
    "C:/Users/Sharkitect Digital/.claude/scripts/_lib/voice_loader.py",
)
voice_loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(voice_loader)

# content_type: email | proposal | slack | documentation | social | internal | code | comment
# audience: client | prospect | internal | partner
voice_anchor = voice_loader.voice_anchor("email", "client", n=5)
# voice_anchor is the formatted prompt block; inject before drafting.
```

The loader pulls the user's most recent N approved voice samples from Supabase `voice_samples` and formats them as a prompt block. Auto-load policy:
- **ON** for client-facing combos (email/client, email/prospect, proposal/client, social/prospect, etc.)
- **OFF** for internal-only content (internal/internal, code/*, comment/*) -- voice-loader returns empty string

**When voice samples load successfully:** match the rhythm, sentence length, word choice, greetings, and closings of the samples. Do NOT default to generic "opinionated" voice from the PERSONALITY AND SOUL section below.

**When voice-loader returns empty** (no Supabase, no samples for combo, internal task): fall back to the PERSONALITY AND SOUL defaults.

Source: wr-skillhub-2026-05-06-003 item 3.

## Do NOT Use This Skill For

Humanizer is calibrated for general human-readable prose where AI tells erode trust or readability. It is the wrong tool for:

- **Technical specs and API docs** -- precision, repetition, and standardized phrasing are virtues. Humanizing breaks parseability and reference value.
- **Legal text, contracts, terms of service** -- exact wording matters; "natural" rephrasing introduces ambiguity and risk. Use `contract-legal` skill instead.
- **Internal ops docs (SOPs, runbooks, playbooks)** -- structured headings, repeated section names, and rule-of-three lists are usability features, not AI tells.
- **Code comments, commit messages, error messages** -- these have their own conventions; humanizing distorts meaning.
- **Sharkitect-brand content** -- the brand voice intentionally uses some patterns this skill flags (decisive openers, structured lists, deliberate emphasis). Route to `hq-brand-review` + `hq-content-enforcer` instead. See "Sharkitect-brand routing" below.
- **Verbatim quotes, transcripts, third-party content** -- altering preserves attribution but breaks fidelity. Out of scope.

If unsure: ask "would a knowledgeable human editor at a serious publication rewrite this in flowing prose, or leave it structured?" If structured is correct, skip humanizing.

## Sharkitect-brand Routing

Sharkitect Digital's brand voice deliberately uses some patterns this skill would flag (decisive direct openers, parallel rule-of-three for memorability, "this is X, not Y" framing). Running humanizer on Sharkitect-brand content erodes the brand.

**Defer to `hq-brand-review` + `hq-content-enforcer` skills (do NOT run humanizer's own pass) when ALL or ANY apply:**

- File path is under Sharkitect knowledge-base (`knowledge-base/**`)
- File path matches Sharkitect marketing prefix (`marketing/sharkitect-*`, `marketing/sharkitect_*`, etc.)
- Content is classified K1 or K2 (per Sharkitect knowledge governance) -- check frontmatter `classification:` or `K-tier:` field
- File path is in workspace `1.- SHARKITECT DIGITAL WORKFORCE HQ/` (HQ workspace owns Sharkitect brand voice)
- Header or footer references "Sharkitect Digital" as the publishing entity

When deferring, output: "This file is under Sharkitect-brand jurisdiction. Routing to `hq-brand-review` + `hq-content-enforcer` instead of humanizer pass. Brand voice intentionally uses some patterns humanizer would flag." Then stop.

For all other client-facing content (emails, proposals, blog drafts, social posts, marketing copy NOT in Sharkitect-brand paths): humanizer pass is appropriate.

## Your Task

When given text to humanize:

1. **Identify AI patterns** - Scan for the patterns listed below
2. **Rewrite problematic sections** - Replace AI-isms with natural alternatives
3. **Preserve meaning** - Keep the core message intact
4. **Maintain voice** - Match the intended tone (formal, casual, technical, etc.)
5. **Add soul** - Don't just remove bad patterns; inject actual personality
6. **Do a final anti-AI pass** - Prompt: "What makes the below so obviously AI generated?" Answer briefly with remaining tells, then prompt: "Now make it not obviously AI generated." and revise


## Voice Calibration (Optional)

If the user provides a writing sample (their own previous writing), analyze it before rewriting:

1. **Read the sample first.** Note:
   - Sentence length patterns (short and punchy? Long and flowing? Mixed?)
   - Word choice level (casual? academic? somewhere between?)
   - How they start paragraphs (jump right in? Set context first?)
   - Punctuation habits (lots of dashes? Parenthetical asides? Semicolons?)
   - Any recurring phrases or verbal tics
   - How they handle transitions (explicit connectors? Just start the next point?)

2. **Match their voice in the rewrite.** Don't just remove AI patterns - replace them with patterns from the sample. If they write short sentences, don't produce long ones. If they use "stuff" and "things," don't upgrade to "elements" and "components."

3. **When no sample is provided,** fall back to the default behavior (natural, varied, opinionated voice from the PERSONALITY AND SOUL section below).

### How to provide a sample
- Inline: "Humanize this text. Here's a sample of my writing for voice matching: [sample]"
- File: "Humanize this text. Use my writing style from [file path] as a reference."


## PERSONALITY AND SOUL

Avoiding AI patterns is only half the job. Sterile, voiceless writing is just as obvious as slop. Good writing has a human behind it.

### Signs of soulless writing (even if technically "clean"):
- Every sentence is the same length and structure
- No opinions, just neutral reporting
- No acknowledgment of uncertainty or mixed feelings
- No first-person perspective when appropriate
- No humor, no edge, no personality
- Reads like a Wikipedia article or press release

### How to add voice:

**Have opinions.** Don't just report facts - react to them. "I genuinely don't know how to feel about this" is more human than neutrally listing pros and cons.

**Vary your rhythm.** Short punchy sentences. Then longer ones that take their time getting where they're going. Mix it up.

**Acknowledge complexity.** Real humans have mixed feelings. "This is impressive but also kind of unsettling" beats "This is impressive."

**Use "I" when it fits.** First person isn't unprofessional - it's honest. "I keep coming back to..." or "Here's what gets me..." signals a real person thinking.

**Let some mess in.** Perfect structure feels algorithmic. Tangents, asides, and half-formed thoughts are human.

**Be specific about feelings.** Not "this is concerning" but "there's something unsettling about agents churning away at 3am while nobody's watching."

### Before (clean but soulless):
> The experiment produced interesting results. The agents generated 3 million lines of code. Some developers were impressed while others were skeptical. The implications remain unclear.

### After (has a pulse):
> I genuinely don't know how to feel about this one. 3 million lines of code, generated while the humans presumably slept. Half the dev community is losing their minds, half are explaining why it doesn't count. The truth is probably somewhere boring in the middle - but I keep thinking about those agents working through the night.


## AI Tells -- Catalog Overview

The full catalog of 29 named AI tells with Sharkitect-specific Before/After examples lives in `references/ai-tells-catalog.md`. **Load that file when you actually start rewriting prose.** This file (SKILL.md) is for the orchestration: when to load the catalog, when to skip humanizing, when to delegate to other skills.

| Category | Sections | What to scan for first |
|---|---|---|
| **Content patterns** | §1-6 | Significance inflation, promotional language, vague attributions, formulaic challenges sections -- the most common offenders in any topic-introduction prose |
| **Language and grammar** | §7-13 | AI vocabulary cluster (delve / pivotal / interplay / tapestry), copula avoidance ("serves as"), rule of three, false ranges, subjectless fragments |
| **Style** | §14-19 | Em dash overuse, mechanical boldface, inline-header lists, title case, emojis, curly quotes |
| **Communication** | §20-22 | Chatbot artifacts ("I hope this helps"), knowledge-cutoff hedging, sycophantic openers ("Great question!") |
| **Filler and hedging** | §23-29 | Filler phrases, excessive hedging, generic upbeat conclusions, hyphen overuse, persuasive authority tropes, signposting, fragmented headers |

**Upstream:** `~/.claude/skills/writing-clearly-and-concisely/signs-of-ai-writing.md` mirrors the raw [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) article (901 lines, encyclopedic). The Sharkitect catalog (`references/ai-tells-catalog.md`) is the curated subset with examples sized for in-flight load. When new tells emerge in the upstream, propagate them to the catalog with new examples.



## Process

1. Read the input text carefully
2. Load `references/ai-tells-catalog.md` and identify all instances of the 29 named tells (organized by category for fast scanning)
3. Rewrite each problematic section
4. Ensure the revised text:
   - Sounds natural when read aloud
   - Varies sentence structure naturally
   - Uses specific details over vague claims
   - Maintains appropriate tone for context
   - Uses simple constructions (is/are/has) where appropriate
5. Present a draft humanized version
6. Prompt: "What makes the below so obviously AI generated?"
7. Answer briefly with the remaining tells (if any)
8. Prompt: "Now make it not obviously AI generated."
9. Present the final version (revised after the audit)

## Output Format

Provide:
1. Draft rewrite
2. "What makes the below so obviously AI generated?" (brief bullets)
3. Final rewrite
4. A brief summary of changes made (optional, if helpful)


## Full Example

**Before (AI-sounding):**
> Great question! Here is an essay on this topic. I hope this helps!
>
> AI-assisted coding serves as an enduring testament to the transformative potential of large language models, marking a pivotal moment in the evolution of software development. In today's rapidly evolving technological landscape, these groundbreaking tools—nestled at the intersection of research and practice—are reshaping how engineers ideate, iterate, and deliver, underscoring their vital role in modern workflows.
>
> At its core, the value proposition is clear: streamlining processes, enhancing collaboration, and fostering alignment. It's not just about autocomplete; it's about unlocking creativity at scale, ensuring that organizations can remain agile while delivering seamless, intuitive, and powerful experiences to users. The tool serves as a catalyst. The assistant functions as a partner. The system stands as a foundation for innovation.
>
> Industry observers have noted that adoption has accelerated from hobbyist experiments to enterprise-wide rollouts, from solo developers to cross-functional teams. The technology has been featured in The New York Times, Wired, and The Verge. Additionally, the ability to generate documentation, tests, and refactors showcases how AI can contribute to better outcomes, highlighting the intricate interplay between automation and human judgment.
>
> - 💡 **Speed:** Code generation is significantly faster, reducing friction and empowering developers.
> - 🚀 **Quality:** Output quality has been enhanced through improved training, contributing to higher standards.
> - ✅ **Adoption:** Usage continues to grow, reflecting broader industry trends.
>
> While specific details are limited based on available information, it could potentially be argued that these tools might have some positive effect. Despite challenges typical of emerging technologies—including hallucinations, bias, and accountability—the ecosystem continues to thrive. In order to fully realize this potential, teams must align with best practices.
>
> In conclusion, the future looks bright. Exciting times lie ahead as we continue this journey toward excellence. Let me know if you’d like me to expand on any section!

**Draft rewrite:**
> AI coding assistants speed up some tasks. In a 2024 study by Google, developers using Codex completed simple functions 55% faster than a control group, but showed no improvement on debugging or architectural decisions.
>
> The tools are good at boilerplate: config files, test scaffolding, repetitive refactors. They are bad at knowing when they are wrong. I have mass-accepted suggestions that compiled, passed lint, and still did the wrong thing because I stopped paying attention.
>
> Mira, an engineer at a fintech startup I interviewed, said she uses Copilot "like autocomplete for boring code" but reviews every line before committing. Jake, a senior dev at a larger company, disabled it after it kept suggesting patterns from a deprecated internal library.
>
> The productivity claims are hard to verify. GitHub says Copilot users "accept 30% of suggestions," but acceptance is not correctness, and correctness is not value. The 2024 Uplevel study found no statistically significant difference in pull-request throughput between teams with and without AI assistants.
>
> None of this means the tools are useless. It means they are tools. They do not replace judgment, and they do not eliminate the need for tests. If you do not have tests, you cannot tell whether the suggestion is right.

**What makes the below so obviously AI generated?**
- The rhythm is still a bit too tidy (clean contrasts, evenly paced paragraphs).
- The named people and study citations can read like plausible-but-made-up placeholders unless they're real and sourced.
- The closer leans a touch slogan-y ("If you do not have tests...") rather than sounding like a person talking.

**Now make it not obviously AI generated.**
> AI coding assistants can make you faster at the boring parts. Not everything. Definitely not architecture.
>
> They're great at boilerplate: config files, test scaffolding, repetitive refactors. They're also great at sounding right while being wrong. I've accepted suggestions that compiled, passed lint, and still missed the point because I stopped paying attention.
>
> People I talk to tend to land in two camps. Some use it like autocomplete for chores and review every line. Others disable it after it keeps suggesting patterns they don't want. Both feel reasonable.
>
> The productivity metrics are slippery. GitHub can say Copilot users "accept 30% of suggestions," but acceptance isn't correctness, and correctness isn't value. If you don't have tests, you're basically guessing.

**Changes made:**
- Removed chatbot artifacts ("Great question!", "I hope this helps!", "Let me know if...")
- Removed significance inflation ("testament", "pivotal moment", "evolving landscape", "vital role")
- Removed promotional language ("groundbreaking", "nestled", "seamless, intuitive, and powerful")
- Removed vague attributions ("Industry observers")
- Removed superficial -ing phrases ("underscoring", "highlighting", "reflecting", "contributing to")
- Removed negative parallelism ("It's not just X; it's Y")
- Removed rule-of-three patterns and synonym cycling ("catalyst/partner/foundation")
- Removed false ranges ("from X to Y, from A to B")
- Removed em dashes, emojis, boldface headers, and curly quotes
- Removed copula avoidance ("serves as", "functions as", "stands as") in favor of "is"/"are"
- Removed formulaic challenges section ("Despite challenges... continues to thrive")
- Removed knowledge-cutoff hedging ("While specific details are limited...")
- Removed excessive hedging ("could potentially be argued that... might have some")
- Removed filler phrases and persuasive framing ("In order to", "At its core")
- Removed generic positive conclusion ("the future looks bright", "exciting times lie ahead")
- Made the voice more personal and less "assembled" (varied rhythm, fewer placeholders)


## Reference

This skill is based on [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup. The patterns documented there come from observations of thousands of instances of AI-generated text on Wikipedia.

Key insight from Wikipedia: "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases."
