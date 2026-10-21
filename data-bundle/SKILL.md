---
name: "data-bundle"
description: "Use when a project's data needs to become a deliverable: collecting scattered inputs and outputs into one citable bundle with a manifest and checksums, deciding what raw output to include, and making the code resolve its paths from the bundle. For paper submission, archiving, handover, or a reproducibility request."
---

# Data bundle

A project accumulates data wherever it was convenient: a collaborator's share,
a scratch folder, symlinks into a differently-named tree, derived tables beside
the code. That is fine while you are the only reader. It stops being fine the
moment someone else has to reproduce a number.

A bundle is **one directory holding everything needed to reproduce the work**,
with a manifest, and with the code pointing at it.

Build it before you need it. The moment it is urgent — a reviewer asking, a
student leaving — is the moment the person who knows where things are has the
least time.

## What goes in

Work backwards from one test: *could someone with this directory and the code,
and nothing else, reproduce every number we report?*

- Inputs exactly as received, not as cleaned. Cleaning is a step to reproduce,
  not a thing to ship in place of the original.
- Derived tables the pipeline produces, even though they are regenerable.
  They let a reader check an intermediate without rerunning everything.
- Results and the figures that were accepted into the record.
- From large raw output: **the part the analysis actually used**. See below.

## Deciding how much raw output to include

Prediction and simulation pipelines emit far more than the analysis reads —
every sampled pose, per-atom confidences, caches. Including all of it can be
10-20x the size for no reproducibility gain; including none of it stops a
reader inspecting anything.

Ask what each artefact is for:

| keep | drop |
|---|---|
| what a reported score was computed from | alternative samples no score used |
| the summary a reader would check | the per-atom version of that summary |
| what makes a selection auditable (rankings) | caches and preprocessed inputs, which regenerate |
| | test and smoke runs |

**State the exclusions and the reason in the bundle README.** A reader
encountering absence cannot tell a deliberate scope decision from an oversight,
and will assume the less flattering one. "We kept the top-ranked pose because
every score here is computed from it" is a methods statement; silence is not.

If the decision is close, put it to the user with sizes attached — the
difference between 2 GB and 40 GB changes where the bundle can be hosted.

## The manifest

One CSV at the root, one row per file: `path, bytes, sha256, description,
source`.

- **`sha256`** lets a reader verify a download, and lets you prove years later
  that a file is the one the paper used.
- **`description`** is per file, not per directory. A reader lands on one file.
- **`source`** is where it came from, with machine-specific prefixes replaced
  by a variable. It is the provenance record, and it is what makes the bundle
  rebuildable rather than a snapshot nobody dares touch.

Put the verification snippet in the README so checking is one paste, not a
task. A manifest nobody can easily check is decoration.

## Make the code resolve from the bundle

The bundle is not a deliverable if the code still reads from the old scattered
paths — it is a copy that silently rots.

Resolve each input **from the bundle when it exists, falling back to the
original location when it does not**. That one rule gives three things: the
pipeline keeps working in the original environment, it runs for someone who has
only the bundle, and the bundle can be rebuilt from the originals.

```python
BUNDLE = Path(os.environ.get('PROJECT_BUNDLE', ROOT / 'project-data'))

def _b(rel, fallback):
    p = BUNDLE / rel
    return p if p.exists() else fallback
```

**The builder must read the originals, never the resolved paths.** Once the
bundle exists the resolver prefers it, so a builder that imports the public
names will copy the bundle onto itself and record it as its own provenance —
losing the real source silently, and passing every test. Keep `SOURCE_*` names
that always point at the originals and build from those.

## Prove it in a clean room

Do not claim a bundle is sufficient because the pipeline runs — on the machine
that built it, the old paths still exist and the fallback is hiding every gap.

Point the project root at an **empty directory**, leave only the bundle
reachable, and run the setup check and one real analysis. Anything the bundle
is missing fails there and nowhere else. Report the result of that run, not the
intention.

## One copy is not an archive

A bundle on scratch is organised, not safe. Distinguish three copies and say
which exist:

| copy | where | for |
|---|---|---|
| staging | wherever it was built | working |
| durable | institutional storage, backed up | not losing it |
| citable | Zenodo, Hugging Face, a DOI | the paper |

Say plainly when only the first exists. "The raw output has exactly one copy"
is a sentence worth writing down, because it is usually news.

## Before it is published

- **Third-party licences.** Outputs of a model inherit constraints from the
  model's weights licence, which often differs from its code licence and may
  forbid commercial use. Check each one and record it. Do this before
  publishing, not after.
- **Nothing unpublishable rides along:** internal paths, credentials,
  collaborator material nobody agreed to release, personal data.
- **A key that joins the parts.** One identifier appearing in both the tables
  and the directory names, named in the README, so a reader can get from a
  reported number to the artefact behind it. Without it a structure directory
  is an opaque name.
