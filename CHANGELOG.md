# Changelog

Versions are of the suite as a whole, not of individual skills: the skills are
used together and a ledger is written by several of them at once, so one
version number is what a ledger can meaningfully record.

A ledger stamps the version it was created under in its `00-index.md`
frontmatter. When you read an old ledger, that stamp tells you which rules were
in force when it was written.

## v0.5.0 — 2026-10-21

The ledger becomes readable as a page, and figures become part of the record.

- **`research-ledger` ships `ledger_html.py`**: renders a ledger to one
  self-contained HTML file — tabs per category, every ID a link, figures
  embedded, no network. Each item gets a *Referenced by* list computed from the
  cross-reference graph; that backlink does not exist in the markdown and is
  the reason to generate a page rather than read the files.
- **`research-ledger`: `figures.md`**, a manifest of figures that have been
  reviewed and accepted, using the same item grammar as every other ledger
  file. Only listed figures are rendered, so a draft plot cannot leak into a
  shared document.
- **`research-ledger`: regenerate the page whenever the ledger changes.** A
  stale generated page is worse than none — it is the artefact most likely to
  reach someone who will not read the markdown behind it.
- **`reporting-numbers`: Rule 3b**, captions for figures. Axes with units and
  ranges, what each mark means, n and spread, and what the figure does *not*
  establish.

Upgrading: nothing breaks. `figures.md` is optional and a ledger without one
renders fine.

## v0.4.0 — 2026-10-20

The suite goes public, so that it can be shared with the group and iterated on
in the open.

- README rewritten around the purpose: the agent augments the human scientist,
  covering what humans find hard (statistical intuition, tracking many
  findings, broad literature recall) while the human judges what is
  interesting and commits to conclusions. The previous README described the
  repository's mechanics but not why the suite exists, and contained an
  incorrect description of the group.
- `research-ledger` / `co-scientist`: the ledger stamp key `framework:` is now
  `repository:`. Same value (the repo URL). Older ledgers that use
  `framework:` mean the same thing; no migration needed.
- `co-scientist-update`: the repository is public, so checks fetch over HTTPS
  without credentials. The rule that a failed fetch is never reported as
  "no updates" is unchanged.
- `dbl-code-data-practices` removed. It holds lab-internal conventions, is not
  part of the suite, and is kept separately.
- Added an MIT license.

History before v0.4.0 was developed in a private repository; its tags are not
carried over. The entries below are kept for the reasoning behind each rule.
Effect on existing ledgers: none beyond the key name above.

## v0.3.0 — 2026-10-20

The suite becomes shareable: it has an identity, and a way to tell you it
has changed.

- `research-ledger`: new ledgers stamp `created_with` and a repository link into
  `00-index.md`. The stamp is deliberately never updated — it describes the
  conventions the existing entries follow.
- New skill `co-scientist-update`: checks the GitHub repo, reports what
  changed *and why*, says whether it affects existing ledgers, installs only
  on agreement. Designed to be silent when there is nothing to say, so that a
  daily scheduled check stays switched on.
- `co-scientist`: names the suite and version when results go to a
  collaborator. These rules decide when a claim counts as supported, so they
  are part of the method, not of the tooling.

No effect on existing ledgers. The stamp applies to ledgers created from here
on; add it by hand to older ones if you want it.

## v0.2.0 — 2026-10-20

Claims hygiene. All four changes come from one observed failure: on a
collaboration project `claims.md` grew from 59 lines over 5 claims to 170 lines over 7, and
stopped being readable at a glance, which was the thing that made it useful.
Every individual edit that caused this was locally correct, so the fix is in
the rules rather than in any one edit.

- `research-ledger`: the claim field set is closed, with an added `one line`
  field and an ~8-line budget per claim.
- `research-ledger`: append-only now applies only to the record
  (`observations`, `analyses`, `decisions`, `literature`). `claims`, `chain`
  and `00-index` are rewritten in place.
- `research-ledger`: at most one headline number per claim; the rest stay in
  `observations.md`.
- `research-ledger`: read `claims.md` and `00-index.md` whole before editing
  either — the failure mode is a property of the file, not of any diff.

## v0.1.0 — 2026-10-19

Baseline: the skills as they stood when they were first used on a
collaboration project. No changes; the tag exists so later diffs have something to point at.
