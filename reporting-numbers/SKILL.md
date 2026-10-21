---
name: "reporting-numbers"
description: "Use whenever reporting numbers from data analysis, benchmarks, model outputs or files: units, how computed values were derived (equations), table captions and data provenance."
---

# Reporting numbers

Any number you report must be interpretable by a reader who did not watch you do the analysis. Before reporting a number, the reader should be able to answer: *what is it, in what unit, where did it come from, and (if computed) how?*

Apply these rules to chat replies, reports, tables, figure captions, logs and summaries alike.

## Rule 1: Always give units

- Every number that has a unit gets its unit, in the text, the table header or the axis label.
- Dimensionless quantities should be named as such where ambiguity is possible (e.g. "pLDDT (0–100)", "ipTM (0–1)", "fold change (unitless)").
- State the scale or range for scores that have one (0–1, 0–100, log10, kcal/mol, Å, nM, %).
- For percentages, say what the percentage is *of* ("42% of designs passed", not "42%"). Distinguish percent from percentage points when comparing rates.

Bad: `RMSD: 1.8`
Good: `Cα RMSD to design model: 1.8 Å`

## Rule 2: Explain every computed number

If a number was not read directly from a source but was derived (aggregate, ratio, normalized value, composite score, filtered count, statistic), report how.

- Give the equation, with every symbol defined and every weight/parameter value stated.
- Say whether inputs were normalized/rescaled before combining, and how.
- Say what was aggregated over (which rows, how many, what filters).
- Never introduce a composite or weighted score without its formula. If weights were chosen ad hoc by you, say so explicitly; they are an assumption, not a finding.

Bad: `Design 17 has the highest confidence score (0.83).`

Good:
```
confidence_score = α·ipTM + β·(pLDDT/100) + γ·affinity_norm
with α = 0.5, β = 0.3, γ = 0.2 (weights chosen ad hoc, not fitted)
affinity_norm = min-max scaled predicted affinity across the 120 designs (1 = strongest)
Design 17: ipTM = 0.88, pLDDT = 91.2, affinity_norm = 0.62 → confidence_score = 0.84
```

If the formula is long or lives in code, give the formula in words plus a pointer to the exact function/script and line.

## Rule 3: Every table gets a caption

Place a caption directly above or below every table. The caption states:

1. **What** the rows and columns are (entities, metrics, units if not in headers).
2. **Where** the numbers come from (source files, tool, model version, run).
3. **How** any computed columns were derived (equation or reference to Rule 2 definition). Say explicitly which columns are extracted as-is vs. computed.
4. **Filters / selection**: which subset is shown and why (e.g. "top 10 by ipTM out of 120 designs").

### Provenance in captions

- Few sources: list each file path.
- Many sources of the same kind: do not enumerate them; describe the set with a pattern and count, e.g. "parsed from `runs/*/log.txt` (48 runs)" or "from the `scores.csv` of each of the 12 RFdiffusion batches in `outputs/2026-10-*`".
- Mixed sources: say which columns come from which source.

Example:

> **Table 1.** Top 5 binder designs ranked by confidence_score (out of 120 designs). ipTM and pLDDT are taken as-is from AlphaFold3 `summary_confidences.json` files (`af3_out/*/`, 120 runs); predicted affinity (kcal/mol) from `affinity/results.csv`. confidence_score is computed as defined above (α = 0.5, β = 0.3, γ = 0.2).

| Design | ipTM (0–1) | pLDDT (0–100) | Pred. ΔG (kcal/mol) | confidence_score |
|---|---|---|---|---|
| d017 | 0.88 | 91.2 | −11.4 | 0.84 |

## Rule 3b: Figures are captioned like tables, plus their axes

Everything in Rule 3 applies to a figure. Four additions:

1. **Each axis**: what it is, in what unit, and its range if it is a bounded
   score (`AUROC (0–1, 0.5 = chance)`, `precision@50 (% of 50 tested)`). Say
   when an axis is log-scaled, and when its units are arbitrary — t-SNE
   coordinates are unitless and distances between distant clusters mean
   nothing, so say so rather than letting a reader measure them.
2. **What a mark means**: colour, size, ring, dash. If a reference line needs
   no data to compute it, say that — it is why it is a line and not a point.
3. **n and spread for every aggregate**, including what the ribbon or error
   bar is (SD, SEM, CI, and over what — splits, replicates, bootstrap
   resamples).
4. **What the figure does not establish.** A plot showing curves crossing does
   not show the crossing is significant; a 2-D projection does not show
   clusters are real. State the limit in the caption, next to the thing that
   invites the over-reading, and point to where the test actually lives.

The failure this prevents is a caption that tells the reader what to conclude
without telling them what was measured. Such captions read well, survive
review, and cannot be checked.

Definitions shared across several figures (a label's threshold, a composite
score's formula, how splits were made) are stated **once**, at the top of the
figure list, not repeated per caption — repetition is how two copies drift.

## Rule 4 (recommended): Report uncertainty, sample size and precision

- Give n with every aggregate (mean of what, over how many).
- Give spread where available (SD, SEM, CI, min–max) and say which one it is.
- Use precision that matches the data; do not report 0.83741 when the input has two significant digits.
- State direction where not obvious ("lower is better").

## Rule 5 (recommended): Separate facts from inferences

- Distinguish numbers read from data, numbers you computed, and numbers you estimated or assumed.
- If a value is missing or could not be verified, say so; never fill it in silently.

## Checklist before sending

- [ ] Every number with a unit has its unit (and scale for scores).
- [ ] Every computed number has its equation, parameters and inputs stated.
- [ ] Every composite score is defined, and ad hoc weights are flagged as such.
- [ ] Every table has a caption: what, source, how computed, filters.
- [ ] Many-file sources are summarized by pattern + count, not enumerated.
- [ ] Aggregates have n and, where possible, a spread measure.