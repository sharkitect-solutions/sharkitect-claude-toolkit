---
name: prompt-engineering-guidance
description: "Use when building constrained LLM generation with Microsoft Guidance library. Use when outputs MUST match a specific format (JSON, dates, enums, code). Use when choosing between Guidance, Instructor, Outlines, or native JSON mode for structured output. Use when debugging constrained generation failures (slow grammar compilation, quality degradation from overly strict constraints). NEVER for general prompt engineering or prompt writing — this is specifically for the Guidance library and constrained generation patterns."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Constrained LLM Generation with Guidance

Think like an engineer who has shipped constrained generation in production and learned where it shines and where it silently destroys output quality.

Core insight: Constraints are a double-edged sword. They guarantee format validity but can murder content quality. A regex-constrained email field will always produce valid syntax — but the model may generate nonsense to satisfy the pattern. The art is constraining just enough.

## When to Use Constrained Generation (vs. Not)

Before reaching for Guidance or any constrained generation tool, ask:

```
Does the output NEED to be machine-parseable?
│
├─ YES → Use constrained generation
│  │
│  ├─ Simple structure (JSON, enum, date)?
│  │  └─ Try native JSON mode first (OpenAI, Anthropic both support it)
│  │     If native mode can't handle it → Guidance or Instructor
│  │
│  └─ Complex structure (nested, conditional, multi-step)?
│     └─ Guidance (grammar-based) or Outlines (schema-based)
│
└─ NO → Do NOT use constrained generation
   Constraints on free-text tasks (creative writing, analysis,
   explanations) actively hurt quality. The model fights the
   constraint instead of thinking about the content.
```

## Tool Selection Decision Tree

| Need | Best Tool | Why Not Others |
|------|-----------|---------------|
| JSON from API models with retries | **Instructor** | Pydantic validation + automatic retry on parse failure. Guidance has no retry. |
| Regex-constrained fields (emails, dates, IDs) | **Guidance** | Token-level regex enforcement. Instructor validates after generation (too late for streaming). |
| Complex grammar (nested structures, code syntax) | **Guidance** | CFG support at token level. Outlines also works but Guidance has better API model support. |
| JSON Schema validation with local models | **Outlines** | JSON Schema → grammar compilation. More automatic than Guidance's manual grammar. |
| Simple enum/classification | **Any** (or native) | All tools handle this well. Native JSON mode is simplest. |
| Multi-step agent workflows | **Guidance** | Stateful functions with `@guidance(stateless=False)` enable agentic loops with constrained actions. |

### The "Just Use Native JSON Mode" Test

Before writing any Guidance code, check if your provider's native structured output works:
- **OpenAI**: `response_format={"type": "json_object"}` or `response_format={"type": "json_schema", ...}`
- **Anthropic**: Tool use with JSON schema for structured responses

Native mode is simpler, requires no library, and works with the provider's latest optimizations. Only reach for Guidance when native mode can't express your constraints (regex patterns, CFG grammars, multi-step workflows).

## Guidance-Specific Expert Knowledge

### Token Healing — The Hidden Feature That Matters

Guidance's most underappreciated feature. When you concatenate prompt + generation, tokenization creates unnatural boundaries:

```
Without healing: "The answer is " + gen() → "The answer is  42" (double space)
With healing:    Guidance backs up one token, regenerates → "The answer is 42"
```

This seems cosmetic but significantly improves generation quality. The model sees natural token sequences instead of artificial breaks. Always leave token healing enabled (it's on by default).

### Grammar Compilation Latency

**First-run trap:** Grammar compilation is cached after first use, but the FIRST call with a new grammar pattern takes 1-5 seconds. In production:
- Pre-warm grammars at service startup
- Don't create new grammar patterns per-request
- Cache compiled grammars across requests

### The Constraint Strictness Spectrum

```
Too loose ◄──────────────────────────────────► Too strict
gen(max_tokens=100)                          gen(regex=r"^(John|Jane)$")
- No format guarantee                        - Format guaranteed
- Model generates freely                     - Model forced into narrow path
- May need post-processing                   - Quality may suffer severely
```

**The sweet spot:** Constrain structure, not content. Let the model fill in the meaning.

```python
# GOOD: Structure constrained, content free
lm += '{"name": "' + gen("name", stop='"') + '", "reason": "' + gen("reason", stop='"') + '"}'

# BAD: Content over-constrained
lm += gen("name", regex=r"^(Alice|Bob|Charlie)$")  # Only 3 possible outputs
```

### When Guidance + API Models Goes Wrong

Guidance's token-level constraints work perfectly with local models (Transformers, llama.cpp) because it intercepts the logit sampling. With API models (OpenAI, Anthropic), constraints are enforced differently — the library post-filters or uses provider-specific features. This means:

1. **Regex constraints with API models** may silently fall back to post-validation (generate → validate → retry)
2. **Grammar constraints may not work at all** with some API backends
3. **Token healing works** but adds one extra API call per generation boundary

Check `references/backends.md` for backend-specific capabilities.

## File Index

| File | Purpose | When to Load |
|------|---------|-------------|
| SKILL.md | Decision frameworks, anti-patterns, when to use | Always (auto-loaded) |
| references/constraints.md | Regex and grammar pattern cookbook | When writing specific constraint patterns |
| references/backends.md | Backend-specific configuration | When setting up Guidance with a specific provider |
| references/examples.md | Production-ready code examples | When implementing specific patterns |

**Do NOT load** reference files for decision-making tasks (choosing between tools, architecture design). Load them only when implementing specific Guidance patterns.

## Rationalization Table

| Rationalization | When It Appears | Why It's Wrong |
|----------------|-----------------|----------------|
| "Let me add Guidance to guarantee the output format" | Starting any LLM task | Check native JSON mode first. 80% of structured output needs are handled without a library. |
| "More constraints = better output" | Writing constraint patterns | Over-constraining kills content quality. The model spends tokens satisfying the pattern, not thinking about the answer. |
| "I'll constrain the entire response with a grammar" | Complex generation tasks | Grammar-constrained generation is significantly slower for large outputs. Constrain only the structured parts. |
| "Guidance handles everything the same across backends" | Choosing Guidance for API models | Token-level constraints work natively only with local models. API models have degraded constraint support. |

## Red Flags

- [ ] Using constrained generation for free-text tasks (analysis, explanations, creative writing) — constraints hurt quality here
- [ ] Grammar compilation happening per-request instead of at startup — adds 1-5s latency
- [ ] Regex pattern is so strict only a few valid outputs exist — model quality degrades when choice space is too narrow
- [ ] No fallback for when constrained generation produces valid-format but nonsense-content output
- [ ] Using Guidance grammar constraints with API models expecting local-model behavior
- [ ] Every field in the JSON individually constrained with tight regex — constrain structure, not every value

## NEVER

- NEVER use constrained generation for creative or analytical free-text output — constraints fight the model's reasoning process, producing format-valid but content-poor results
- NEVER compile grammars per-request in production — compilation takes 1-5s on first run; pre-warm at startup and cache
- NEVER assume Guidance constraints work identically across local and API backends — local models get true token-level enforcement, API models get post-validation fallback
- NEVER constrain content when you should constrain structure — `gen("name", stop='"')` inside a JSON template is better than `gen("name", regex=r"[A-Z][a-z]+ [A-Z][a-z]+")`
- NEVER skip the "do I need a library?" check — native JSON mode handles most structured output needs without adding a dependency
- NEVER test constrained generation only on happy-path inputs — adversarial and edge-case inputs reveal where constraints produce valid-format garbage

## Implementation Quickstart

When you've decided Guidance is the right tool:

1. Install: `pip install guidance` (add `[transformers]` or `[llama_cpp]` for local models)
2. Choose backend — see `references/backends.md` for configuration
3. Start with `select()` for enums and `gen(stop="\n")` for single-line fields — simplest constraints
4. Use regex only when format matters (emails, dates, IDs) — see `references/constraints.md` for patterns
5. For complex structures, use `@guidance` decorator functions — see `references/examples.md`
6. Pre-warm grammars in production, never compile per-request
7. Always test: generate 10 outputs, check both format validity AND content quality
