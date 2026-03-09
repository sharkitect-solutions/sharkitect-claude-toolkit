# Skill Versioning & Update Workflow

## Why This Matters

Skills are living artifacts. User feedback, new failure modes, and evolving requirements
mean skills need updates. Without a versioning workflow, updates introduce regressions —
a fix for one test case breaks another, or a description change kills trigger precision.

## When to Update a Skill

| Signal | Action |
|---|---|
| Skill doesn't trigger on a relevant query | Add trigger condition to description, re-run evals |
| Skill triggers on irrelevant queries | Narrow description, add domain qualifiers |
| Claude ignores the skill under new pressure type | Add rationalization to table, add red flag |
| User reports bad output despite skill being loaded | Strengthen rules, add code examples |
| New provider/technology enters the skill's domain | Update references, add trigger keywords |
| Body exceeds 2,500 words | Refactor detail into references |

## The Update Process

### Step 1: Diagnose Before Changing

Never change a skill based on a single report. Run the existing evals first:

```
python run_evals.py report <skill-path>
```

If existing tests still pass, the issue is likely a gap — not a regression. If existing
tests are failing, the skill may have already degraded.

### Step 2: Add a Failing Test First

Before making any change, add a test case to `evals.json` that captures the exact failure.
This is RED phase — the test should fail against the current skill.

```json
{
  "id": 21,
  "query": "[the exact scenario that exposed the problem]",
  "category": "should_trigger",
  "expected": {
    "must_contain": ["[correct behavior]"],
    "must_not_contain": ["[incorrect behavior observed]"],
    "behavior": "[what should happen]"
  },
  "last_result": "fail",
  "last_score": 1
}
```

### Step 3: Make the Minimal Change

Fix the specific issue. Common changes:

**Description change** (trigger problem):
- Add missing trigger phrases
- Add missing keywords
- Remove overly broad terms

**Body change** (behavior problem):
- Add rationalization table row for the new pressure type
- Add red flag for the bad pattern
- Tighten rule language

**Reference change** (detail problem):
- Add provider-specific guidance
- Add edge case documentation
- Update outdated patterns

### Step 4: Re-Run All Evals

After making the change, run ALL test cases — not just the new one:

```
python run_evals.py grade <skill-path>
python run_evals.py report <skill-path>
```

If any previously passing test now fails, the change introduced a regression. Fix before
proceeding.

### Step 5: Bump the Version

Update the `version` field in `evals.json`:

| Change Type | Version Bump | Example |
|---|---|---|
| Description tweak (trigger fix) | Patch: x.y.Z | 1.0.0 → 1.0.1 |
| New rationalization or red flag | Minor: x.Y.0 | 1.0.1 → 1.1.0 |
| Rule rewrite or structural change | Major: X.0.0 | 1.1.0 → 2.0.0 |
| New reference file added | Minor: x.Y.0 | 1.1.0 → 1.2.0 |

## Deprecating a Skill

When a skill is superseded by a better one:

1. **Don't delete immediately.** Both skills may trigger on different queries.
2. **Add negative trigger conditions** to the old skill's description:
   `Use when [condition] but NOT when [condition that the new skill handles better].`
3. **Run evals on both skills** to verify the new skill covers the old one's test cases.
4. **Only then delete** the old skill — after confirming zero regression.

## Changelog Practice

For significant skills (ones you share or rely on heavily), maintain a changelog comment
at the bottom of SKILL.md:

```markdown
<!-- Changelog
v2.0 - Rewrote description for CSO compliance, added 6 rationalization rows
v1.1 - Added pressure test for "keep it simple" scenario
v1.0 - Initial release with 3 rules and 10 test cases
-->
```

This is invisible to Claude but useful for human maintainers reviewing the skill's history.
