---
name: "research-ledger"
description: "Use to create, read or update a co-scientist project ledger: Obsidian-compatible markdown tracking observations, claims, reasoning chain, analyses, literature and working agreements."
---

# Research ledger

The ledger is the shared memory of a research project. It keeps findings, the reasoning chain and every analysis in one place so neither the user nor the agent has to hold it in their head. It is plain markdown, readable and editable in Obsidian, and versionable in git.

## Location

- Default: `ledger/` folder at the project repo root. The user may keep it in (or symlink it into) an Obsidian vault.
- If the user has stated a different location in a working agreement or project instructions, use that.
- Never keep two diverging copies. If you cannot write to the user's location, say so and tell them which files changed.

## Files

```
ledger/
  00-index.md        question, working agreements, current status, links
  observations.md    O1, O2, …  descriptions of data
  claims.md          H1/C1, …   hypotheses and conclusions with status
  chain.md           reasoning chain(s): Mermaid diagram + step table
  analyses.md        A1, A2, …  every analysis run, including null results
  literature.md      familiarity flags (unverified) and verified references
  parked.md          P1, P2, …  questions that do not affect the current conclusion
  decisions.md       D1, D2, …  choices made and why
  figures.md         F1, F2, …  figures accepted into the record (optional)
  retro.md           friction log for improving the skills
```

Small projects may use only `00-index.md`, `observations.md`, `chain.md`, `analyses.md`. Create other files when first needed.

## Format conventions

- Every file starts with YAML frontmatter: `project`, `updated` (ISO date), `tags`.
- `00-index.md` additionally carries a **provenance stamp** recording which
  version of this skill suite the ledger was created under (see below). A
  reader opening a ledger a year later needs to know which rules were in force
  when it was written; the conventions in this file have changed before and
  will change again.
- Every item is a heading with a stable ID: `### O3 — Short title`. IDs are never reused or renumbered.
- Cross-link with Obsidian wikilinks to headings: `[[observations#O3 — Short title]]`, or shorter by ID in text ("supported by O3").
- Numbers follow `reporting-numbers` (units, equations, provenance). In
  `claims.md` specifically, **at most one headline number per claim** — the one
  the claim stands or falls on. Every other number stays in `observations.md`
  and is reached through `depends on`. Numbers migrate upward if you let them:
  each is quoted into the claim for a good local reason, and the file ends up
  restating the observations file in a worse format.
- Dates as ISO (`2026-10-19`).
- **Append-only applies to the record, not to the conclusions.**
  `observations.md`, `analyses.md`, `decisions.md` and `literature.md` are an
  audit trail: append and update, never delete, and mark a wrong item
  `status: retracted` with a reason. `claims.md`, `chain.md` and `00-index.md`
  are a present-tense statement of where the project stands: **rewrite them in
  place**. When a claim's wording is sharpened or a sub-claim falls, edit the
  claim to say what is now believed and leave the history to git and to the
  analysis that caused the change. A claim that accumulates the record of its
  own revisions has turned into an audit trail and stopped being a claim.

## Item templates

**Observation**
```
### O3 — Batch B designs have higher ipTM
- data: mean ipTM 0.71 (B, n = 40) vs 0.63 (A, n = 40); Table 2 in [[analyses#A5 — …]]
- source: af3_out/batch_*/summary_confidences.json (80 runs)
- recorded by: user | agent
- strength: replicated | single run | small n | large spread
```

**Claim / hypothesis**

The field set is **closed**. These five fields, in this order, and no others:
```
### C2 — Partial diffusion improves interface confidence
- type: hypothesis | target conclusion | supporting claim
- status: open | supported | supported with assumptions | weak | refuted | retracted
- chain: [[chain#Chain for C2]]
- depends on: O3, O5, assumption X
- one line: <the claim as you would say it out loud, with its scope>
```

A claim entry has a budget of **about eight lines**. If what you want to add
does not fit one of the five fields, it is not a property of the claim — it is
an observation, an analysis, a decision or a caveat, and it belongs in the file
for those. Put it there and reference it from `depends on`.

Do not invent fields. `controls run`, `scope caveats`, `word to avoid`, `why it
is steeper`, `not supported`, `retracted sub-claim` and their like are all real
content, but each one is a new field that no later reader expects, and a reader
scanning `claims.md` to see where the project stands now has to read a
paragraph per claim instead of a line. Scope belongs in `one line`; controls and
caveats belong in `analyses.md` and are reached through `depends on`.

**Analysis**
```
### A5 — ipTM by batch
- date, script/notebook path, input files
- what was tested; number of comparisons made
- result (incl. "no effect found")
- feeds: O3
```

**Figure**
```
### F1 — Short title, as a finding not a filename
- file: figures/fig_data_regime.png
- supports: C1
- script: scripts/16_fig_data_regime.py
- caption: <see below>
```

`figures.md` is a manifest of figures that have been **reviewed and accepted**,
not an inventory of the `figures/` folder. Only what is listed here is rendered
into the HTML page, so a draft plot never appears by accident. Add an entry when
a figure is one you would put in front of someone.

Figure captions follow `reporting-numbers`, which for a figure means: what each
axis is and in what unit or range; the equation for any computed or composite
quantity, with its parameters, and whether they were fitted or chosen; what was
filtered or selected; n and a spread measure for every aggregate; and what the
figure does **not** establish. Definitions shared by several figures are stated
once at the top of `figures.md` rather than repeated in each caption.

A caption that says what the reader should conclude, without saying what was
measured, has failed. That is the common failure and it looks fine until someone
asks how a number was computed.

The analyses log must include analyses that found nothing and the number of comparisons in exploratory scans. `stats-check` uses this to account for multiple testing and forking paths.

**Literature**
```
## Familiarity flags (unverified)
- 2026-10-19 — concept: calibration of predicted confidence vs experimental success — raised at: C2 — status: not checked | scanned (see below)

## Verified references
### L1 — <title>
- authors, year, venue, DOI/URL; peer-reviewed | preprint
- relevance: supports / contradicts / method for <claim or link>
- verified: <date>, fetched from <source>
```

## 00-index.md

```
---
project: <name>
updated: <date>
created_with: jonfunk21/co-scientist v<VERSION>
repository: https://github.com/jonfunk21/co-scientist
---
# <Project name>

## Question
<one or two sentences>

## Current target conclusion
<C-id and one sentence> — status

## Status
- weakest open link: …
- next step: …

## Working agreements
Project-specific preferences. These override co-scientist skill defaults.
- e.g. familiarity flags only at moment 3
- e.g. always report Spearman alongside Pearson
```

## retro.md

One line per friction event, appended as it happens:
```
- 2026-10-19 — stats-check — too many caveats on an exploratory plot — user wanted a one-line verdict for exploratory work
```

## Provenance stamp

When you create a ledger, read `VERSION` at the root of the skills repo and
write it into `00-index.md` frontmatter as `created_with`. If the repo is not
available locally, use the version the skill was installed at and say in the
stamp that it was not verified.

Do **not** update `created_with` when the suite is upgraded. It records the
version the ledger was *created* under, which is what explains the shape of
the older entries. If a suite upgrade changes conventions in a way that
affects an existing ledger, note the migration in `retro.md` with both version
numbers — that line, not the stamp, is the upgrade record.

## Reading the ledger as a page

`ledger_html.py`, in this skill's folder, renders the whole ledger to a single
self-contained HTML file:

```bash
python <skill>/ledger_html.py --ledger ledger/ --out ledger/ledger.html
```

No network, no sibling files, figures embedded: it can be emailed, opened
offline and archived with the project. One tab per category, every ID is a
link, and each item carries a **"Referenced by"** list computed from the
cross-reference graph. That backlink is the reason to generate the page at all
— the markdown lets you follow `depends on` forwards, never backwards, so from
a file alone you cannot see which claims an observation holds up.

It is read-only and derives everything from the markdown. Nothing is ever
written back to the ledger, so regenerating is always safe.

`--no-embed` links figures instead of embedding them, for viewers that refuse
`data:` URIs; the result is no longer self-contained.

## Updating

- Update the ledger at the end of each session and after any analysis, new observation, or change in claim status.
- **After updating the ledger, regenerate the HTML page if the project has one**
  (`ledger/ledger.html` exists, or the user has asked for it). A stale page is
  worse than no page: it looks current and is the artefact most likely to be
  shared with someone who will not check the markdown behind it. Regenerating
  costs a second and cannot damage the ledger.
- After updating, tell the user in one or two lines what changed (files and IDs).
- Keep `00-index.md` status current; it is what the user reads first.
- **Before editing `claims.md` or `00-index.md`, read the whole file, not just
  the entry you came to change.** Judge the edit by what the file looks like
  afterwards. These two files are read end to end, so their quality is a
  property of the whole, and a sequence of individually reasonable edits can
  degrade it without any one of them being wrong — the failure mode has no
  local symptom and will not be caught by looking at the diff.
- If a claim has outgrown its budget, the fix is to rewrite the claim, not to
  accept the overflow. Move the detail into `observations.md` or `analyses.md`
  and point at it.
