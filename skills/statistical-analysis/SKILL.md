---
name: statistical-analysis
description: "Use when conducting statistical hypothesis tests (t-test, ANOVA, chi-square, non-parametric), regression, correlation, or Bayesian analyses on research data. Also use when selecting appropriate statistical tests, checking and recovering from assumption violations, calculating effect sizes, conducting power analyses, or formatting results in APA style. NEVER use for machine learning model evaluation or hyperparameter tuning, A/B test design for product experiments (use ab-test-setup), data visualization without statistical inference, or exploratory data analysis without hypothesis testing."
version: "2.0"
optimized: true
optimized_date: "2026-03-12"
---

# Statistical Analysis

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Test selection, assumption violation recovery, common mistakes, effect size reference, power analysis, reporting essentials, anti-patterns | Always (auto-loaded) |
| references/test_selection_guide.md | Comprehensive decision tree for choosing tests by research design, variable types, sample size, and distribution shape | When the Test Selection Decision Matrix in SKILL.md doesn't cover the specific research design, or when dealing with unusual variable combinations (ordinal DV with continuous IV, repeated measures with missing cells) |
| references/assumptions_and_diagnostics.md | Detailed assumption checking procedures, diagnostic visualization interpretation, remedial action protocols for each violation type | When assumption checks fail and SKILL.md's Assumption Violation Recovery table needs more detailed guidance on transformation choices, robust alternatives, or diagnostic plot interpretation |
| references/effect_sizes_and_power.md | Effect size calculation formulas, conversion between effect size families, power analysis for complex designs (factorial ANOVA, mixed models, mediation), sensitivity analysis procedures | When conducting power analysis for non-standard designs, converting between effect size metrics (d to r to eta-squared), or planning multi-study research programs |
| references/bayesian_statistics.md | Prior specification guidance, Bayes Factor interpretation, MCMC diagnostics, posterior predictive checks, Bayesian model comparison, hierarchical model setup | When conducting Bayesian analyses beyond basic Bayesian t-tests, specifying informative priors, diagnosing convergence issues, or comparing Bayesian and frequentist results |
| references/reporting_standards.md | APA 7th edition statistical reporting templates for every test type, table/figure formatting, results section structure, common reporting errors | When writing up results for publication, formatting statistical tables, or ensuring APA compliance for specific test types not covered in SKILL.md's quick templates |
| scripts/assumption_checks.py | Automated assumption checking: normality (Shapiro-Wilk + Q-Q), homogeneity (Levene's), outliers (IQR + z-score), linearity checks with visualization | When running assumption checks programmatically. Provides comprehensive_assumption_check() for full workflow or individual functions for targeted checks |

Do NOT load companion files for basic test selection using the decision matrix, standard APA reporting of t-tests/ANOVA/regression, or simple effect size interpretation -- SKILL.md covers these fully.

## Scope Boundary

| Area | This Skill | Other Skill |
|---|---|---|
| Hypothesis testing (t-test, ANOVA, chi-square, non-parametric) | YES | -- |
| Regression analysis (linear, multiple, logistic) with diagnostics | YES | -- |
| Bayesian hypothesis testing and model comparison | YES | -- |
| Power analysis and sample size planning | YES | -- |
| Effect size calculation and interpretation | YES | -- |
| APA-style statistical reporting | YES | -- |
| Assumption checking and violation recovery | YES | -- |
| A/B test design for product experiments | NO | ab-test-setup |
| Machine learning model training and evaluation | NO | data science tooling |
| Survey design and questionnaire validation | NO | research methodology |
| Data cleaning and preprocessing | NO | data engineering |
| Exploratory data visualization without inference | NO | analytics-tracking |

## Analysis Planning Framework

Before choosing ANY test, answer these five questions. They determine everything downstream.

| Question | Why It Matters | If You Skip It |
|---|---|---|
| 1. Is this analysis confirmatory or exploratory? | Confirmatory requires pre-registration and strict multiple comparison control. Exploratory allows flexibility but results must be labeled as hypothesis-generating, not hypothesis-confirming | You'll present exploratory findings as confirmatory (HARKing), inflating false-positive rate |
| 2. What is the smallest effect size of practical importance? | This determines your target power and required sample size. A "statistically significant" d = 0.05 with n = 10,000 is meaningless if d = 0.30 is the minimum meaningful effect | You'll either miss real effects (underpowered) or detect trivially small effects (overpowered) |
| 3. What assumptions does your intended test require? | Check BEFORE collecting data if possible. Severe violations require different tests, larger samples, or different study designs | You'll discover violations after data collection and face painful choices (transform data, switch tests, lose interpretability) |
| 4. How many tests will you run in total? | This determines your multiple comparison strategy (none, Holm-Bonferroni, FDR, or pre-registered contrasts) | You'll inflate your family-wise error rate without realizing it |
| 5. How will you handle missing data? | Missing mechanism (MCAR, MAR, MNAR) determines appropriate treatment. Listwise deletion is rarely the best option -- it wastes data and can introduce bias | You'll lose statistical power (listwise deletion can discard 30-60% of rows if multiple variables have missingness) or introduce bias (MAR/MNAR treated as MCAR) |

## Test Selection Decision Matrix

| Research Question | Variables | Assumptions Met? | Test | Non-Parametric Alternative |
|---|---|---|---|---|
| Two independent groups differ? | 1 continuous DV, 1 binary IV | Normal + equal variance | Independent t-test | Mann-Whitney U |
| Two related measurements differ? | 1 continuous DV, 2 time points | Normal differences | Paired t-test | Wilcoxon signed-rank |
| 3+ independent groups differ? | 1 continuous DV, 1 categorical IV (3+ levels) | Normal + equal variance | One-way ANOVA | Kruskal-Wallis |
| 3+ related measurements differ? | 1 continuous DV, 3+ repeated measures | Normal + sphericity | Repeated measures ANOVA | Friedman |
| Two categorical variables associated? | 2 categorical variables | Expected freq >= 5 | Chi-square test | Fisher's exact (small n) |
| Predict continuous outcome? | 1+ continuous/categorical IVs, 1 continuous DV | Linearity, normality of residuals, homoscedasticity | Linear regression | -- |
| Predict binary outcome? | 1+ continuous/categorical IVs, 1 binary DV | Linearity of logit, no multicollinearity | Logistic regression | -- |
| Two continuous variables related? | 2 continuous variables | Bivariate normality | Pearson r | Spearman rho |
| Multiple factors and their interaction? | 1 continuous DV, 2+ categorical IVs | Normal + equal variance + no interaction if unbalanced | Factorial ANOVA | Aligned rank transform |

**Critical decision point**: When n > 30 per group AND distributions are only mildly non-normal (skewness < |2|, kurtosis < |7|), parametric tests are robust enough to use. The Central Limit Theorem makes the t-test and ANOVA more robust than textbooks suggest. Switch to non-parametric only for severe violations, small samples, or ordinal data.

## Assumption Violation Recovery

| Assumption | Test to Check | Threshold | Mild Violation | Severe Violation |
|---|---|---|---|---|
| Normality | Shapiro-Wilk (n < 50), K-S with Lilliefors (n >= 50) | p < .05 | Proceed if n > 30 per group (CLT). Report violation | Transform (log, sqrt, Box-Cox) or switch to non-parametric |
| Homogeneity of variance | Levene's test (median-based, more robust than mean-based) | p < .05 | Use Welch's t-test or Welch's ANOVA (default in many packages) | Use Welch's + report. For regression: robust standard errors (HC3) or WLS |
| Sphericity (repeated measures) | Mauchly's test | p < .05 | Greenhouse-Geisser correction if epsilon < .75 | Huynh-Feldt if epsilon >= .75, or switch to mixed-effects model |
| Linearity (regression) | Residuals vs fitted plot | Pattern in residuals | Add polynomial term (quadratic) | Transform DV, use GAM, or model non-linearity explicitly |
| No multicollinearity | VIF (Variance Inflation Factor) | VIF > 5 (conservative: > 10) | Center predictors if VIF is from interaction terms | Remove redundant predictor, combine via PCA, or use ridge regression |
| Independence | Study design (not testable post-hoc) | Durbin-Watson < 1.5 or > 2.5 (time series) | Use clustered standard errors | Use mixed-effects model with random effects for the clustering variable |
| No influential outliers | Cook's distance | Cook's D > 4/n | Report with and without outlier, compare results | Winsorize, use robust regression (M-estimation), or report both analyses |

**Welch's by default**: Always use Welch's t-test and Welch's ANOVA unless you have a specific reason not to. They perform identically to Student's when variances are equal, and protect you when they aren't. There is no downside.

## Named Statistical Mistakes

| Name | Mistake | Impact | Fix |
|---|---|---|---|
| The p-Hack | Testing multiple DVs/subgroups until p < .05, then reporting only the significant result | Simmons et al. (2011): researcher degrees of freedom can push false-positive rate from 5% to >60% | Pre-register analyses. Report ALL planned tests. Apply Holm-Bonferroni correction for multiple comparisons |
| The HARKer | Hypothesizing After Results are Known -- presenting exploratory findings as confirmatory | Destroys the confirmatory-exploratory distinction. Published "predictions" that were actually post-hoc have inflated Type I error rates | Label exploratory analyses explicitly. Pre-register hypotheses. Separate confirmatory and exploratory sections in paper |
| The Power Handwave | Skipping a priori power analysis, then running study with n = 15 per group | With n = 15 and d = 0.5, power = 0.34. You have a 66% chance of missing a real medium effect. Non-significant results are uninterpretable | Run G*Power or statsmodels power analysis BEFORE data collection. Target power >= .80 (ideally .90) for the smallest effect of interest |
| The Post-Hoc Power Fallacy | Computing "observed power" after a non-significant result to explain why | Post-hoc power is a direct mathematical transformation of the p-value (Hoenig & Heisey 2001). It adds zero new information. If p = .40, observed power will always be low | Use sensitivity analysis instead: "With our n, we could detect d >= X at 80% power." This tells you about detectable effects, not about the null result |
| The Significance Worship | Treating p = .049 as fundamentally different from p = .051 | The .05 threshold is arbitrary (Fisher suggested it as a "convenient" guideline). A p-value of .051 is not "no effect" and .049 is not "definitely real" | Report exact p-values. Emphasize effect sizes and confidence intervals. Consider Bayesian analysis for evidence quantification |
| The Assumption Ignorer | Running parametric tests without checking assumptions | Violated homogeneity of variance inflates Type I error for t-tests (can double false-positive rate with 4:1 variance ratio). Non-normality affects small-sample CI coverage | Check assumptions systematically using scripts/assumption_checks.py. Report which checks were done and what was found |
| The Multiple Comparison Dodge | Running 10 post-hoc t-tests after ANOVA without correction | Family-wise error rate: 1 - (1-.05)^10 = 40% chance of at least one false positive | Use Tukey's HSD (all pairwise), Holm-Bonferroni (ordered), or FDR (Benjamini-Hochberg) for exploratory. Match correction to research question |
| The Correlation Causalist | Interpreting r = .65 as evidence that X causes Y | Correlation cannot establish causation (third variables, reverse causation, shared method variance). Even r = .90 may be entirely spurious | Use experimental designs for causal claims. For observational data, discuss alternative explanations. Use mediation/moderation analysis for mechanism testing |
| The Garden of Forking Paths | Making data-contingent analysis decisions (transform this variable, exclude that outlier, use this subgroup) without acknowledging that each choice inflated degrees of freedom | Gelman & Loken (2013): even without conscious p-hacking, the "garden of forking paths" of analytic choices inflates false positives. Each decision point doubles the implicit comparison space | Document ALL analysis decisions and their alternatives. Run multiverse analysis (Steegen et al. 2016) for key decisions: run all reasonable analysis variants and report the distribution of results |

## Multiple Comparison Correction Decision

| Situation | Correction | Why |
|---|---|---|
| Small number of planned comparisons (2-3) | Bonferroni or Holm-Bonferroni | Conservative, easy to justify. Holm is uniformly more powerful than Bonferroni with no downside |
| All pairwise comparisons after ANOVA | Tukey's HSD | Designed specifically for this. Controls family-wise error while maximizing power for pairwise |
| Many tests, exploratory analysis | FDR (Benjamini-Hochberg) | Controls false discovery rate (proportion of false positives among rejections) instead of family-wise error. More powerful when many tests are truly significant |
| Only one pre-planned comparison | No correction needed | If you pre-registered one specific comparison, it stands alone. The issue is only when you test many and report selectively |
| Testing against control only (Dunnett's) | Dunnett's test | More powerful than Tukey when you only care about comparisons to one reference group |

**Never use Bonferroni for >10 comparisons** -- it becomes so conservative that you can't detect real effects. Switch to FDR (Benjamini-Hochberg) which adapts to the number of true effects.

## Effect Size Quick Reference

| Test | Effect Size | Small | Medium | Large | Interpretation Caveat |
|---|---|---|---|---|---|
| t-test | Cohen's d | 0.20 | 0.50 | 0.80 | Cohen's benchmarks are for behavioral science. In clinical trials, d = 0.20 may be huge. Context-dependent |
| ANOVA | Partial eta-squared | 0.01 | 0.06 | 0.14 | Inflated in designs with many factors. Omega-squared or generalized eta-squared preferred for between-subjects |
| Correlation | r | 0.10 | 0.30 | 0.50 | r = .10 explains 1% of variance. r = .30 explains 9%. The "small" threshold is barely distinguishable from noise in most contexts |
| Regression | R-squared | 0.02 | 0.13 | 0.26 | Adjusted R-squared for multiple predictors. In social science, R-squared = .20 is often considered good. In physics, R-squared < .99 is often bad |
| Chi-square | Cramer's V | 0.10 | 0.30 | 0.50 | Depends on df. For 2x2: V = phi. For larger tables, V is deflated. Use odds ratio for 2x2 tables instead |
| Non-parametric | r = Z / sqrt(N) | 0.10 | 0.30 | 0.50 | For Mann-Whitney U and Wilcoxon. Less intuitive than d -- convert if audience expects Cohen's d |

**Always report effect sizes with confidence intervals.** A point estimate of d = 0.50 with CI [0.05, 0.95] tells a very different story than d = 0.50 with CI [0.35, 0.65].

## APA Reporting Quick Templates

**t-test**: t(df) = X.XX, p = .XXX, d = X.XX, 95% CI [X.XX, X.XX]
**ANOVA**: F(df_between, df_within) = X.XX, p = .XXX, eta-p-squared = .XX
**Correlation**: r(df) = .XX, p = .XXX, 95% CI [.XX, .XX]
**Regression**: F(df_model, df_residual) = X.XX, p = .XXX, R-squared = .XX, adj. R-squared = .XX
**Chi-square**: chi-squared(df, N = XX) = X.XX, p = .XXX, V = .XX
**Bayesian**: BF10 = X.XX, posterior median = X.XX, 95% CrI [X.XX, X.XX]

**Reporting rules**:
- Exact p-values to 3 decimal places (p = .032, not p < .05). Exception: p < .001 when p is very small
- Always include df, test statistic, p-value, effect size, and CI
- Report assumption checks: which tests were run, results, any remedial actions taken
- Non-significant results: report them fully (no "n.s." without numbers)
- Bayesian: report BF with Jeffreys (1961) scale interpretation (BF > 3 = moderate, > 10 = strong, > 30 = very strong, > 100 = extreme)

## Software Implementation Gotchas

Library-specific behaviors that produce different results from the same data. These trip up even experienced analysts.

| Library Behavior | What Happens | Impact |
|---|---|---|
| scipy `ttest_ind` defaults to Student's t-test; pingouin `ttest` defaults to Welch's | Same data, same function name, different p-values when variances are unequal | Student's has inflated Type I error with unequal variances. Always specify `equal_var=False` in scipy or use pingouin which defaults correctly |
| scipy `chi2_contingency` applies Yates' continuity correction by default | Results differ from R's `chisq.test` (which also applies Yates by default) vs Python `statsmodels` (which does NOT) | For 2x2 tables, Yates correction is conservative. With n > 40 and no expected cell < 5, disable it: `correction=False` |
| statsmodels `OLS` does NOT include intercept by default | Must call `sm.add_constant(X)`. Forgetting this fits regression through the origin, producing inflated R-squared and biased coefficients | pingouin `linear_regression` and R's `lm()` include intercept by default. This is the #1 statsmodels beginner error |
| Shapiro-Wilk becomes oversensitive at n > 200 | Almost always rejects normality for large samples, even when the departure is trivially small and irrelevant to the test | For n > 200, use Anderson-Darling test or rely on Q-Q plot visual inspection + skewness/kurtosis thresholds (|skew| < 2, |kurt| < 7) instead of hypothesis-testing normality |
| SPSS uses Type III sums of squares by default; R `aov()` uses Type I | Type I SS results depend on the ORDER variables enter the model. Type III does not. Same data, same model, different F-values and p-values | For unbalanced designs, always use Type III (statsmodels: `sm.stats.anova_lm(model, typ=3)`). For balanced designs, all three types give identical results |
| pingouin reports partial eta-squared for ANOVA; SPSS can report either; R `effectsize` package reports generalized eta-squared by default | Three different effect size metrics for the same analysis, all called "eta-squared" in casual discussion | Specify which eta-squared you're reporting. Partial eta-squared is inflated with many factors. Omega-squared is less biased for small samples. Generalized eta-squared is most comparable across designs |
| Levene's test: scipy uses mean by default; the robust version uses median | Mean-based Levene's is sensitive to non-normality. Median-based (Brown-Forsythe test) is more robust | Always use `center='median'` in scipy.stats.levene() unless you have a specific reason not to |

## Bayesian vs Frequentist Decision

| Situation | Recommended Approach | Why |
|---|---|---|
| Standard group comparison, large n, no prior info | Frequentist | Simpler, reviewers expect it, results will align with Bayesian anyway |
| Need to quantify evidence FOR null hypothesis | Bayesian (Bayes Factor) | Frequentist can't distinguish "no evidence of effect" from "evidence of no effect." BF01 > 3 = moderate support for null |
| Small sample, strong prior information | Bayesian with informative priors | Priors regularize estimates in small samples. But you must justify prior choice |
| Sequential data collection (interim analyses) | Bayesian | No alpha-spending required. Posterior updates continuously. Stop when evidence is sufficient |
| Hierarchical/multilevel data with complex structure | Bayesian (via PyMC, Stan) | Flexible specification of random effects, crossed random factors, non-standard distributions |
| Publication in traditional journal | Both (frequentist primary, Bayesian supplementary) | Reviewers expect p-values. Bayesian results add interpretive depth. Report both for maximum impact |

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "p < .05 means the effect is real" | p < .05 means "data this extreme would occur <5% of the time if H0 is true." It does NOT mean H1 is 95% likely. With low prior probability, most p < .05 results are false positives (Ioannidis 2005) |
| "The effect was non-significant so there's no effect" | Absence of evidence is not evidence of absence. With low power, you'd miss real effects most of the time. Report effect size + CI to show what you can and can't rule out |
| "We don't need power analysis, we'll just collect as much data as we can" | Without knowing required n, you risk two failures: underpowered study (wastes participants' time) or overpowered study (wastes resources detecting trivially small effects) |
| "Our sample is too small for Bayesian analysis" | Bayesian methods work BETTER with small samples than frequentist (priors regularize). The opposite of the intuition. Small n is when Bayesian shines |
| "We'll just Bonferroni-correct everything" | Bonferroni with 20+ tests is so conservative that true effects become undetectable. Use FDR (Benjamini-Hochberg) for large test families |
| "Normality doesn't matter because of the Central Limit Theorem" | CLT makes the SAMPLING DISTRIBUTION of the mean approximately normal. It does not fix outlier influence, variance heterogeneity, or non-linear relationships. It's a robustness argument for moderate non-normality only |

## Red Flags

- Running parametric tests without any assumption checks -- homogeneity violations can double the false-positive rate
- Reporting p < .05 or "n.s." without exact p-values, test statistics, or effect sizes -- impossible to meta-analyze or interpret
- Power analysis conducted AFTER data collection ("observed power") -- it's a mathematical transformation of p, adds nothing
- Multiple comparisons without correction -- 10 uncorrected tests give 40% family-wise error rate
- Effect size reported without confidence interval -- a point estimate without precision is incomplete
- Interpreting correlation as causation without discussing confounds, reverse causation, or shared method variance
- Using one-tailed test without pre-registered directional hypothesis -- post-hoc one-tailing is p-hacking
- Removing outliers without transparent criteria or reporting both with-and-without analyses

## NEVER

- Report "observed power" or "post-hoc power" -- it's a discredited practice that adds no information beyond the p-value itself (Hoenig & Heisey 2001)
- Use one-tailed tests without a pre-registered directional hypothesis -- switching from two-tailed to one-tailed after seeing the direction halves your p-value, which is p-hacking
- Discard outliers without documenting the criteria, the number removed, and the impact on results -- unreported outlier removal is a form of data manipulation
- Apply Bonferroni correction to more than 10 tests -- use FDR (Benjamini-Hochberg) instead, which controls false discovery rate without sacrificing power to detect real effects
- Interpret a non-significant Bayesian result as "supporting the null" without checking BF01 -- a BF01 of 1.2 is inconclusive, not evidence for the null. Requires BF01 > 3 for moderate support
