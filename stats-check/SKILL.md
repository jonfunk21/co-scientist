---
name: "stats-check"
description: "Use to statistically audit a specific quantitative claim (difference, correlation, improvement, benchmark result) and translate the verdict into plain terms; includes ML leakage checks."
---

# Stats check

Audit one specific claim and say, in plain language, how much the data supports it. This is where the agent covers what humans find hard: intuition for noise, sample size, correlation strength and hidden statistical traps.

When the data is available, compute; do not estimate from memory. Report numbers per `reporting-numbers`.

## 1. Pin down the claim

Restate it quantitatively: what quantity, compared to what, in which population, what effect size. If it cannot be stated quantitatively, say so and help sharpen it first.

## 2. Checklist

Go through these; report only the ones that matter for this claim.

**Units and independence**
- What is the unit of analysis? Are samples independent? (e.g. many designs from the same backbone, sequences from the same family, multiple seeds of the same run, repeated measures are pseudo-replicates.)
- Effective n, not row count.

**Effect size and uncertainty**
- Effect size with a confidence interval (bootstrap if distribution is unclear). Significant ≠ meaningful.
- Compare to a baseline: random, trivial predictor, previous method, replicate-to-replicate noise.
- Variance across seeds / runs / splits, not a single run.

**Correct test**
- Test matches data type and design (paired vs unpaired, parametric vs rank-based, nested).
- For correlations: Pearson vs Spearman; outlier-driven correlation; range restriction; Simpson's paradox across groups.

**Multiple testing and forking paths**
- How many comparisons, metrics, subsets, thresholds were tried? Read `analyses.md` in the ledger.
- If many: correct (e.g. Benjamini–Hochberg) or label the result exploratory.

**Selection effects**
- Regression to the mean: top-k selected on one noisy score, then re-measured.
- Survivorship / filtering: what was dropped before the analysis?
- Ceiling or floor effects.

**ML-specific**
- Leakage between train and test: sequence identity, homologs, structural similarity, shared targets, temporal leakage.
- Hyperparameters or model selection tuned on the test set.
- Proxy validity: does the metric track the property claimed?
- Benchmark comparability: same data splits, same preprocessing, same compute budget.

**Confounders**
- Batch, date, operator, length, composition, any variable correlated with both groups.

## 3. Translate into intuition

Always add a plain-language translation. Examples:

- "r = 0.40 with n = 12 has a 95% CI of roughly −0.23 to 0.79 (Fisher z): consistent with no relationship or a strong one. The data cannot distinguish them."
- "A 0.02 ipTM difference is smaller than the seed-to-seed SD of 0.05: indistinguishable from noise."
- "p = 0.03 after testing 20 metrics: about one such result is expected by chance."

Where useful, give the sample size that would be needed to resolve the question.

## 4. Verdict

```
Claim: …
Verdict: supported | supported with caveat | inconclusive | not supported | artefact likely
Key numbers: effect size [CI], n (effective), test, comparisons made
In plain terms: …
Main risk: …
Cheapest check to resolve: …
```

For exploratory work, keep it to the verdict and plain-terms line unless asked for more (or as set in working agreements).

## Behaviour

- Distinguish computed results from your inferences.
- Do not bury the verdict in caveats; lead with it.
- Log the check in the ledger (`analyses.md`, and update the link status in `chain.md`).