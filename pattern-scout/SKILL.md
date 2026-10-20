---
name: "pattern-scout"
description: "Use only when the user explicitly asks to scout, scan or explore data for patterns: systematic, multiple-testing-aware search returning ranked candidate patterns, not conclusions."
---

# Pattern scout

Scan data systematically and return **candidate** patterns the user may find striking. The user judges interest; you report evidence strength. Run only when asked.

## 1. Protect the user's own view

Before showing candidates, check whether the user has recorded their own observations for this data (ledger `observations.md`). If not, ask whether they want to note them first, so the scout list does not anchor them. Respect a "just run it".

## 2. Define the scan before running it

Write down, and log in the ledger (`analyses.md`):
- the question or context (from the ledger index)
- variables and relationships to scan (e.g. all metric pairs, metric vs condition, per-group differences)
- the number of comparisons this implies
- thresholds and methods

Defining the space first is what makes the multiple-testing correction honest.

## 3. Scan

For each candidate:
- effect size with CI (bootstrap where appropriate)
- effective n
- robustness: rank-based version, leave-one-group-out (target, batch, family), outlier removal
- multiple-testing correction across the whole scan (e.g. Benjamini–Hochberg q-value), or explicit "exploratory, uncorrected"
- artefact flags: driven by one group or outlier; confounded with batch, length, date; ceiling/floor; trivially explained by construction (e.g. a composite score correlating with its own component)

## 4. Report candidates

- Rank by evidence strength (effect size, robustness, corrected significance), **not** by how interesting you think it is.
- Show the top 5–10 in a table with caption per `reporting-numbers`; write the full list to a file and point to it.
- IDs: S1, S2, … (scout candidates). They are not observations until the user adopts them.

| ID | Pattern | Effect [95% CI] | n | q-value | Robust to | Artefact flags |
|---|---|---|---|---|---|---|

Then one line: total comparisons made, how many survive correction, and what fraction would be expected by chance.

Familiarity flag (see `co-scientist`) only if a candidate is likely to be called novel and the concept is specifically familiar.

## 5. Hand over

- The user picks which candidates are interesting. Adopted ones become observations (O-ids) in the ledger, marked `recorded by: scout`.
- Never phrase candidates as conclusions or mechanisms. "X and Y co-vary (ρ = 0.6)", not "X drives Y".
- Log the scan, including null results and the comparison count, in `analyses.md`.