---
name: "literature-scan"
description: "Use only when the user asks for a literature search on a question, claim or method: verified references only, documented search coverage, results mapped onto the reasoning chain."
---

# Literature scan

Find out whether a question has been addressed, what supports or contradicts a claim, and which methods could be borrowed. Run only when asked (often after a familiarity flag).

## Hard rules

- **Every reference is verified**: fetched from its source, with title, authors, year, venue and DOI/URL taken from that source, not from memory. If you cannot verify it, it is not a reference; at most it is an unverified lead, labelled as such.
- **Never claim exhaustiveness.** Say what was searched. "Not found in <sources> with <queries>" is different from "does not exist".
- Distinguish peer-reviewed from preprint.
- Do not overstate what a paper shows; report its actual claim and setting.

## 1. Scope

State the target precisely, ideally tied to the ledger:
- which claim or chain link (e.g. "link I2 → N", "C2")
- what would count as: directly answers / supports / contradicts / method to borrow

Translate the recalled concept from the familiarity flag into search terms, including synonyms used in neighbouring fields (ML, structural biology, biophysics, statistics).

## 2. Search

- Use available tools: web search, and any connected literature sources (e.g. PubMed, bioRxiv, arXiv, Semantic Scholar) if present.
- Run several query formulations; follow citations from the most relevant hits (backward and forward) where possible.
- For fast-moving ML topics, explicitly include recent preprints.

## 3. Report

```
Target: <claim / link>
Searched: <sources>, <queries>, <date>; ~<n> results screened

Directly addresses: L1, …
Supports: …
Contradicts: …
Methods to borrow: …
Not found: <what was looked for and not found>

Implication for the chain: <does any link change status? does N need narrowing? is the result less novel than thought?>
```

Per reference: one or two sentences on what it actually shows and how it bears on the claim.

## 4. Ledger

- Add verified references to `literature.md` (verified section) with L-ids.
- Update the familiarity flag that triggered the scan to `scanned`.
- If a chain link changes status, update `chain.md` and tell the user.