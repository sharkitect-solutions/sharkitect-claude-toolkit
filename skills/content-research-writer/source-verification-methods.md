# Source Verification Methods

Load when evaluating source quality beyond the basic credibility tier, fact-checking specific claims, assessing study methodology, verifying statistics, or determining whether a source actually supports the claim being made.

## Study Methodology Assessment

Not all "research" is equal. Before citing a study, assess its methodology.

| Study Type | Strength | What to Check | Writer's Shortcut |
|---|---|---|---|
| Meta-analysis of RCTs | Highest | Heterogeneity (I-squared), publication bias assessment, funnel plot | Safe to cite as "strong evidence." Check if the meta-analysis is recent enough to include latest studies. |
| Randomized Controlled Trial | High | Sample size, blinding, attrition rate, pre-registration | n>100 per group for behavioral claims. If unregistered, check for outcome switching. |
| Cohort / Longitudinal | Moderate | Confounders controlled, follow-up duration, dropout rate | Good for trends. Always note "association, not causation" in your writing. |
| Cross-sectional survey | Low-moderate | Sample representativeness, response rate, question framing | >50% response rate for survey data. Below that, non-response bias likely. |
| Case study / Anecdote | Low | Replicability, selection bias, cherry-picking | Never extrapolate from case studies. Use for illustration only, not evidence. |
| Expert opinion | Context-dependent | Track record, conflicts of interest, consensus vs outlier | Attribute clearly. "Dr. X argues..." not "Research shows..." |

### Pre-Registration Check

Studies registered before data collection (ClinicalTrials.gov, AsPredicted, OSF) are more trustworthy. If a study claims surprising results and wasn't pre-registered, the risk of p-hacking or HARKing (Hypothesizing After Results are Known) is elevated.

**Quick check**: Search the study DOI on OSF Registries or ClinicalTrials.gov. If a behavioral/psychology study published after 2018 has no pre-registration, note this as a credibility concern.

### Retraction and Correction Check

Before citing any study, especially older ones:

| Check | How | Why It Matters |
|---|---|---|
| Retraction Watch database | Search author name or paper title at retractionwatch.com | 10,000+ papers retracted since 2010. Psychology and biomedical fields have highest retraction rates. |
| Publisher correction notices | Check the paper's DOI page for "correction" or "erratum" links | Corrections may invalidate the specific data point you're citing even if the paper stands. |
| Citation context | Check who cites this paper -- do citing papers confirm or challenge? | A highly-cited paper that's mostly cited as "X found this, but subsequent work shows..." is not supporting evidence. |

## Statistical Literacy for Writers

You don't need to run statistics. You need to recognize when statistics are being misused.

### Red Flags in Statistical Claims

| Red Flag | What It Looks Like | What to Do |
|---|---|---|
| Relative vs absolute risk | "50% increase in risk!" (from 0.002% to 0.003%) | Always report absolute numbers alongside percentages. A 50% increase from a tiny base is tiny. |
| Correlation presented as causation | "Countries that eat more chocolate win more Nobel prizes" | Rewrite as association. If the source claims causation from correlational data, downgrade credibility. |
| Cherry-picked timeframes | "Sales grew 400% in Q3" (from $100 to $400, after declining from $10,000) | Request the full time series. Any claim about growth needs a baseline and duration. |
| Survivorship bias | "Successful companies all do X" (ignoring failed companies that also did X) | Ask: "What about the companies that did X and failed?" If the source doesn't address this, flag it. |
| Base rate neglect | "This test is 95% accurate!" (but the condition affects 0.1% of people, so most positives are false) | Check prevalence. High accuracy + rare condition = mostly false positives. |
| Composite metrics | "Our proprietary index shows improvement" | Ask what's in the index and how it's weighted. Unauditable metrics are not evidence. |
| N=small, claim=large | "In our study of 12 participants..." | For behavioral claims, n<30 per group is almost meaningless. For medical claims, check power analysis. |

### How to Describe Uncertainty

| Confidence Level | Language | Use When |
|---|---|---|
| Strong evidence (multiple RCTs, meta-analyses) | "Research consistently shows..." or "Evidence strongly suggests..." | 3+ high-quality studies converge |
| Moderate evidence (1-2 good studies) | "Studies indicate..." or "Early research suggests..." | Limited but methodologically sound research |
| Preliminary/emerging | "Initial findings suggest..." or "One study found..." | Single study, preprint, or small sample |
| Contested | "The evidence is mixed..." or "Researchers disagree on..." | Studies show contradictory results |
| No evidence | "While commonly claimed, no published research supports..." | Popular belief without empirical backing |

## Press Release vs Research Paper

Press releases systematically distort findings. 40% of health press releases contain exaggerated claims (Sumner et al., 2014 BMJ).

| Distortion Pattern | How It Works | Writer's Defense |
|---|---|---|
| Causation upgrade | Study found correlation; press release says "X causes Y" | Always read the abstract and results section. Check if the study design supports causal claims. |
| Human extrapolation | Study was in mice/cells; press release implies human relevance | Check the Methods section for "in vitro," "murine," or "cell line." Note the gap explicitly. |
| Magnitude inflation | Effect size was small; press release highlights relative change | Read the actual effect size. Cohen's d < 0.2 is trivial even if statistically significant. |
| Context removal | Study had significant limitations; press release omits them | Read the Discussion section's limitations paragraph. Every honest paper has one. |
| Novelty exaggeration | Findings replicate existing knowledge; press release says "groundbreaking" | Check if the paper cites prior work finding the same thing. "Confirms previous findings" is more accurate. |

## Fact-Checking Procedure

### Three-Layer Verification

| Layer | What to Verify | When Required |
|---|---|---|
| 1. Claim exists | The source actually says what you're attributing to it | Every citation, every time. Misattribution is the most common and most damaging error. |
| 2. Claim is current | The information hasn't been superseded or retracted | Claims older than 3 years in fast-moving fields (tech, medicine, social media). Always for statistics. |
| 3. Claim is representative | The source isn't an outlier -- the broader evidence agrees | Bold or surprising claims, anything that will be a key argument in the piece |

### Verification Shortcuts by Claim Type

| Claim Type | Quick Verification Method |
|---|---|
| Statistics / Data points | Trace to primary source. If "X% of companies..." -- find the original survey, check sample and methodology. |
| Historical facts | Cross-reference with 2+ independent sources. Wikipedia footnotes are good starting points, never endpoints. |
| Quotes | Find the original context. Quotes are frequently truncated to reverse their meaning. |
| "Studies show..." | Identify which study. If the article doesn't cite one, the claim is unverifiable -- don't repeat it. |
| Product/company claims | Verify on the company's own current materials. Press coverage of companies often uses outdated numbers. |
| Legal/regulatory | Check the actual regulation text, not summaries. Summaries frequently omit exceptions and conditions. |

### Disappeared Source Recovery

Sources go offline. When a cited URL returns 404:

1. **Wayback Machine** (web.archive.org): Paste the URL. Usually has cached copies.
2. **Google Cache**: Search `cache:URL` in Google.
3. **DOI resolver**: For academic papers, the DOI (10.xxxx/xxxx) should resolve even if the journal's site changes.
4. **If unrecoverable**: Replace with an alternative source or note "[source no longer available, archived at web.archive.org/...]"
