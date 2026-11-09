# Changelog

Versions are of the suite as a whole, not of individual skills: the skills are
used together and a ledger is written by several of them at once, so one
version number is what a ledger can meaningfully record.

A ledger stamps the version it was created under in its `00-index.md`
frontmatter. When you read an old ledger, that stamp tells you which rules were
in force when it was written.

## v0.8.0 — 2026-11-09

The ledger gets a mechanical check, and delegated work is rewritten before it is recorded.

Observed behaviour that prompted this (a long method-development session,
2026-11-09, ledger created under v0.1.0 and migrated to v0.7.0):

- **Ledger entries became unreadable.** Observations used undefined code names
  (`E_des_pr`, `int_ljatr`, κ²), unitless numbers and arrow chains. Most of it
  came from subagent reports pasted in with light editing.
- **The record drifted from the rules without any one edit being wrong.**
  Claims grew extra fields, near-duplicate observations accumulated, and merged
  items were deleted, which left dangling `feeds` references.
- **A stale install went unnoticed.** The session ran a skill copy from
  2026-10-19 (v0.1.0) while the repo was at v0.7.0.

Changes:

- **`research-ledger`: `ledger_lint.py`.** A mechanical check of the ledger
  rules (closed claim fields and budget, ID placement and uniqueness, dangling
  references, undefined code names, near-duplicates, aggregates without n,
  stale page), plus an example Claude Code hook that runs it and regenerates
  `ledger.html` after every ledger edit.
- **`research-ledger`: definitions and run tables** at the top of
  `observations.md` once a project has its own vocabulary.
- **`research-ledger`: merging near-duplicates leaves a pointer item**, never a
  deleted heading.
- **`co-scientist`: delegated work is rewritten before it enters the ledger**,
  and the lint runs before the agent reports the ledger as updated.

Upgrading: nothing breaks. The linter is optional and read-only; on an existing
ledger, expect findings for vocabulary that was never defined.

## v0.7.0 — 2026-11-05

Method development gets its own mode, and the agent becomes a fuller partner in
interpretation.

Observed behaviour that prompted this:

- **The agent stopped interpreting.** "The agent does not lead the
  interpretation" was applied as "the agent never interprets": results were
  reported in tables and then left there.
- **The agent stopped contributing ideas.** The suite was made cautious after
  earlier agents treated small findings as pivotal and pulled the user into
  side paths. It swung too far: next steps were rarely suggested at all.
- **Method-development work drifted.** In model-building projects, runs were
  launched without a trusted evaluation or a clear purpose, and multi-person
  branches drifted until they were hard to merge.

Changes:

- **New skill: `experiment-gate`.** Charter, eval harness, experiment cards
  written before the run, lightweight probe cards for exploration, a pre-flight
  check before launches (harness, card, smoke test, leakage, proxy first, branch
  divergence), a suggestion bar tied to the charter and project phase, a drift
  check, and branch hygiene for shared repos. It warns and explains rather than
  blocks, so newcomers learn the reasons.
- **`co-scientist`: two kinds of project.** Analysis and method development;
  the agent says which mode it is in and switches on request. New-member
  briefing at session start.
- **`co-scientist`: interpretation is joint.** After the user's first
  impressions, the agent offers a labelled reading at three scales (per result,
  when a line of work closes, at milestones).
- **`co-scientist`: speaking up.** Most of the time no suggestion is needed;
  raise one when it could change a conclusion, a goal or a decision, usually one
  rather than a menu, in a calm tone. Smaller ideas go to `parked.md`.
- **`research-ledger`:** optional method-development files (`charter.md`,
  `harness.md`, `experiments.md`, `probes.md`, `archive/`), a `Mode` line in
  `00-index.md`, rules for team ledgers shared through git, and guidance on
  keeping the ledger small.
- **`stats-check`:** leakage checks include pretrained foundation models; gains
  are compared with measured harness noise.

Upgrading: nothing breaks. The new ledger files are optional and render with
`ledger_html.py` like any other file; `archive/` is not rendered. Existing
ledgers can add a `Mode` line to `00-index.md` when convenient.

## v0.6.0 — 2026-10-21

New skill: **`data-bundle`**, for the point where a project's data has to
become something other people can use.

Written from doing it once. A project had its data in four unrelated places
plus symlinks into a differently-named tree holding 46 GB of raw prediction
output. The rules that turned out to matter:

- Decide how much raw output to include by asking what each artefact is *for*,
  and **state the exclusions and the reason** — a reader meeting absence cannot
  tell a scope decision from an oversight.
- A manifest with a SHA-256 and a provenance path per file, and a verification
  snippet in the README so checking is one paste.
- Resolve inputs from the bundle when present, falling back to the original
  location when not. The builder must read the originals explicitly, or once
  the bundle exists it copies the bundle onto itself and records it as its own
  provenance — silently, passing every test.
- **Prove sufficiency in a clean room**: point the project root at an empty
  directory and run. On the machine that built it the fallback hides every gap.
- Staging, durable and citable are three different copies. Say which exist.

Nothing else changes; no existing skill is affected.

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
