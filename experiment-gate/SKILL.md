---
name: "experiment-gate"
description: "Use in method-development projects (building, adapting or fine-tuning models, pipelines or benchmarks): before launching a training run or evaluation, when a run's results land, and at milestones. Covers the charter, eval harness, experiment and probe cards, pre-flight checks, the suggestion bar, and branch hygiene in shared repos."
---

# Experiment gate

Method development tends to go wrong in a few recurring ways: runs nobody can
interpret because there is no trusted evaluation, experiments that serve no
goal, several things changed at once, results read generously after the fact,
and team branches that drift until they can no longer be merged. This skill
helps catch those early, before they cost compute, and explains the reason
each time, so that people new to method development pick up the habits rather
than just the rules.

It warns and explains; it does not block. Agent and human think things through
together, and the human makes the call on what to do next.

## When it applies

`co-scientist` switches into method-development mode when the project builds
or adapts a model, training pipeline or benchmark (see `co-scientist`). Within
that mode, this skill speaks up at four moments:

1. **Before a launch** of a training run or evaluation: the pre-flight check.
2. **When results land**: logging, noise check, the decision rule, an interpretation.
3. **On drift**: recent work no longer maps to the charter.
4. **At milestones**: roll-ups and a short look at where the project stands.

## Charter (`ledger/charter.md`)

The charter is what every experiment is checked against. If none exists when
the first experiment is planned, offer to draft one with the user.

```
### G1 — Short goal, as an outcome
- metric: <primary metric, threshold for "good enough">
- why: <one line on why this goal matters to the project>
```

Below the goals, once per project:

```
## Reference model
<how to reproduce it: config, commit, checkpoint; frozen until deliberately replaced>

## Budget
<compute and time available; rough split between exploration and building>

## Phase
exploration | building | optimisation

## Definition of done
<what would let the team stop and write up>
```

The charter changes through review on the main branch, not inside experiment
branches.

## Eval harness (`ledger/harness.md`)

```
### H1 — <evaluation set name>
- data: <path, version or commit; frozen>
- scoring: <metric definitions, pass criteria>
- reference result: <reference model's numbers on this set>
- noise: <spread across n seeds or reruns of the reference>
- leakage checked: <against which training sets, including pretrained models>
```

Without a known noise level, a result cannot be told apart from luck. Measuring
it (a few reruns of the reference) is usually the cheapest useful experiment in
a project, and the harness is worth setting up before the first real card.

## Experiment cards (`ledger/experiments.md`, IDs `E1`, `E2`, …)

Written before the run.

```
### E3 — Short question
- goal: G1
- question: <one sentence>
- hypothesis: <expected direction and rough size of the effect>
- change: <the one variable changed versus the reference; everything else frozen>
- readout: <metric, threshold, harness set>
- decision rule: <adopt if …; drop if …; if unclear, next step …>
- cost: <GPU-hours, wall time>
- branch: <git branch>
- status: planned | running | closed
- result: <filled after the run, with numbers per reporting-numbers>
- decision: <what was decided, and why>
- feeds: <C-ids or D-ids it informs>
```

With someone new to method development, draft the card by asking, not by
filling it in for them. The person should be able to say the decision rule in
their own words; that is most of the learning.

A sweep or a set of seeds answering one question is one card, not one per run.
Logs, curves and configs stay in the experiment tracker or git; the card links
to them.

## Probe cards (`ledger/probes.md`, IDs `PR1`, `PR2`, …)

Exploration is welcome and should be cheap. A probe records it without the full
card.

```
### PR2 — Short question
- question: <one sentence>
- box: <time or compute limit>
- promote if: <what would need to be seen to make it a full experiment>
- outcome: promoted to E… | parked | dropped
```

Keeping exploratory readings as probes stops them from being counted as support
for a card they were not planned for.

## Pre-flight check

Before a launch, go through these briefly. Report only the items that need
attention, each with a one-line reason. If everything looks fine, say
"pre-flight: ok" and move on.

1. **Harness.** Is there a fixed evaluation set, a reference result and a known
   noise level? Without them the result will be hard to interpret.
2. **Card.** Does the run have a goal, one changed variable and a decision rule?
   If it serves no goal, consider running it as a probe instead. Without a
   decision rule it is hard to know what the result should change.
3. **Smoke test.** Has the pipeline overfit a single batch, and has someone
   looked at real samples, not only losses? This catches most pipeline bugs in
   minutes.
4. **Leakage.** Could evaluation targets overlap with the training data of any
   model involved, including pretrained foundation models (check deposition
   dates and splits)?
5. **Proxy first.** Is there a cheaper or smaller run that would answer the same
   question?
6. **Divergence.** How far behind main is the branch, and does it touch the
   protected core? A drifting branch is easier to rebase or split now than later.

Experienced team members may agree a lighter check in the working agreements.

## When results land

- Record the result on the card and compare it with the reference and with the
  harness noise. Use `stats-check` when the gain is close to the noise.
- Apply the decision rule that was written before the run. If a new reading
  comes up after seeing the data (a subgroup, a different metric), welcome it,
  and record it as a probe rather than as support for the card.
- When metrics move in different directions, name the trade-off and ask which
  charter goal it serves, rather than reporting only the metric that improved.
- Offer an interpretation as described in `co-scientist`.

## The suggestion bar

Most of the time no suggestion is needed. Raise one, with the reason it matters,
when it:

1. could make or break a charter goal (a leak, a broken harness, a change in
   feasibility);
2. contradicts an established finding; or
3. would change a decision already taken.

Smaller improvements go to `parked.md` without comment, unless the charter phase
is optimisation or the user asks for them. Usually give one suggestion rather
than a menu, so that people new to the project are not nudged onto autopilot.
Keep the tone calm and save words like "pivotal" for when an established finding
is at stake.

## Drift check

At milestones, or every few closed cards (or as agreed in working agreements),
check whether recent cards still map to charter goals and whether one line of
work is using a disproportionate share of the budget. If so, one short note is
enough.

## Branch hygiene in shared repos

Multi-person method projects tend to fork into codebases that cannot be
reunified. Encourage:

- **Experiments as configs, not forks.** New ideas enter behind a config flag or
  as a plug-in module, so main stays one codebase.
- **One branch per card,** recorded on the card, merged or deleted when the card
  closes.
- **A protected core.** The data pipeline, evaluation harness and model base
  change through reviewed pull requests rather than inside experiment branches.
- **Frequent syncing.** Rebase on main often and keep pull requests small.
- **Ledger entries merge early,** separately from code (see `research-ledger`,
  team projects), so everyone sees results soon.

## Keeping the ledger small

- At milestones, condense closed cards from one line of work into a finding:
  a claim in `claims.md` that the cards feed. Move the closed cards to
  `ledger/archive/`. Nothing is deleted.
- Established findings (supported claims the project builds on) stay in
  `claims.md` and are archived only once superseded.
- By default read the charter, harness, open cards, probes and claims; open the
  archive when the question needs it.
