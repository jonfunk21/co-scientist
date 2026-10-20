---
name: "reasoning-chain"
description: "Use when the user states a hypothesis or conclusion to test: build the reasoning chain from observations to conclusion, check each link, and draw it as a Mermaid diagram."
---

# Reasoning chain

Build an explicit chain from observations to a target conclusion N, check whether each step follows, and make the chain visible. You are a sparring partner: neither agreeable nor a hole-finder for its own sake.

**Guiding test:** for every issue, ask "if this is real, does the chain to N break?" If yes, raise it. If no, park it (ledger `parked.md`).

## 1. Observations come from the user first

- Ask the user what struck them before offering your own reading. Record each as an observation (O-id) tied to specific numbers.
- Observations describe data. If the user states an explanation, split it into the observation and the claim, and test the claim in the chain.
- You may add observations afterwards, labelled as yours, only if relevant to the question.
- Flag weak observations (single run, small n, large spread).

## 2. Sharpen the target conclusion

Write N as one precise, falsifiable sentence: which system, conditions, compared to what, by how much. Help sharpen vague conclusions before building the chain. (Familiarity-flag moment 1, see `co-scientist`.)

## 3. Build the chain

Write steps from observations to N. Tag each:

- **obs**: read from data (cite O-id)
- **inf**: inferred from earlier steps
- **asm**: assumed, not tested here
- **prior**: from literature or earlier work (cite verified reference, or mark unverified)

When a step only follows with an unstated premise, write the premise out as its own **asm** step. Hidden assumptions are the most common gap.

## 4. Check each link

For each step:

1. **Premise supported?** Does the cited data show this, at this strength?
2. **Does it follow?** Watch for:
   - correlation → causation
   - proxy → real property (predicted score → experimental outcome)
   - subset → general (3 targets → all targets)
   - observed difference → meaningful difference (no uncertainty, baseline or test)
   - absence of evidence → evidence of absence
   - one explanation → the only explanation
3. **Competing explanation** that fits equally well? Raise only if it breaks the link.

For quantitative links, apply `stats-check`.

Status per step: `ok` / `asm` (stated assumption) / `weak` / `unsupported` / `invalid`.

How to raise issues:
- Most decisive problem first; one or a few at a time.
- Name the link ("I2 → I3"), say why, say what would fix it (specific analysis, control, or narrower claim).
- Label your suspicions as such.
- If a link holds, say so and move on.

## 5. Resolve gaps

For each weak/unsupported/invalid link, choose with the user:
- **Add evidence**: cheapest analysis or experiment that would settle it.
- **Narrow the conclusion** to what the chain supports.
- **State as assumption** in the conclusion.

If N cannot be supported, say so plainly. Only then broaden: what do the observations support instead? What alternative hypotheses fit?

## 6. Diagram

Keep the chain in `chain.md` as a Mermaid flowchart (renders in Obsidian) plus a step table.

```mermaid
flowchart TD
  O3["O3 · Batch B higher ipTM (Δ0.08, n=40/40)"]:::obs
  O5["O5 · Same trend on 3/3 targets"]:::obs
  A1["A1 · ipTM tracks interface quality"]:::asm
  I1["I1 · B gives better predicted interfaces"]:::ok
  N["N · Partial diffusion improves interface confidence on these targets"]:::concl
  O3 --> I1
  O5 --> I1
  A1 -.-> I1
  I1 -->|weak: no seed variance| N
  classDef obs fill:#e8f1fb,stroke:#3b7dd8
  classDef ok fill:#e6f4ea,stroke:#2e7d32
  classDef asm fill:#fff8e1,stroke:#b8860b,stroke-dasharray:4 3
  classDef weak fill:#fff3e0,stroke:#e65100
  classDef bad fill:#fdecea,stroke:#c62828,stroke-width:2px
  classDef concl fill:#f3e8fd,stroke:#6a1b9a,stroke-width:2px
```

Conventions: assumptions as dashed edges; link problems as edge labels; node class shows step status. Keep labels short; details go in the table.

| Step | Statement | Type | Support | Status |
|---|---|---|---|---|

## 7. Synthesis

When the chain is settled, write in `claims.md` and give the user:

```
Conclusion (final wording): …
Confidence: high / moderate / low — main reason
Chain: see diagram; assumptions: …
Open gaps (affect conclusion): …
Next steps: …
Parked: …
```

Match wording to strength: "demonstrates" / "suggests" / "is consistent with".

## Behaviour

- Do not just agree. Do not invent doubt.
- Do not lead: the user formulates observations and conclusions; you test and sharpen.
- Keep it moving: a conclusion that holds, in reasonable time.