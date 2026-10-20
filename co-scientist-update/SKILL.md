---
name: "co-scientist-update"
description: "Use to check whether the co-scientist skill suite has updates on GitHub, to report what changed and why it might matter, and to install an update. Also the skill a scheduled daily update check invokes."
---

# co-scientist-update

Checks `jonfunk21/co-scientist` for changes to the skill suite, explains what
changed and **why**, and installs an update only when the user says so.

A skill is a set of standing instructions. Changing one silently changes how
the agent behaves on every later project, so an update is never applied
without the user seeing what it does.

## Configuration

| | default |
|---|---|
| local clone | `~/co-scientist` |
| remote | `https://github.com/jonfunk21/co-scientist.git` (public) |
| installed copy | the user's skills directory, e.g. `~/.claude/skills/` (or wherever they installed the suite) |
| state file | `~/.claude/co-scientist-update-state.json` |

The repository is public, so a check needs network access but no credentials.
Never report "no updates" when what actually happened was a failed fetch —
say the check failed and why.

## Checking

```bash
cd ~/co-scientist && git fetch --tags --quiet origin
git -C ~/co-scientist log --oneline HEAD..origin/main
git -C ~/co-scientist tag --sort=-v:refname | head -3
cat ~/co-scientist/VERSION
```

Three outcomes:

- **Up to date** — `HEAD..origin/main` is empty. In a scheduled check, say
  nothing at all (see *Scheduled checks*). When the user asked directly, one
  line: `co-scientist is up to date (v<version>).`
- **Updates available** — report them (below).
- **Check failed** — no clone, no network, repo moved.
  Say which, in one line, and do not retry in a loop.

## Reporting an update

The useful content is in the commit bodies, not the subjects: this repo's
convention is that every commit explains the behaviour that prompted the
change. Read them with `git log HEAD..origin/main` and report, per change:

1. **What behaviour changes** — concretely, what the agent will do differently.
2. **Why it was changed** — the observation behind it, from the commit body.
3. **Whether it affects this user's existing ledgers** — the question they
   actually have. A rule about how new claims are written does not invalidate
   old ones; a change to the ledger file layout does.

Then one recommendation, not a menu: take it, or skip it and why. Keep the
whole report under about 15 lines. If an update is large, summarise by theme
and offer the full log.

Do not report a diff of the markdown. The user cares about behaviour, and a
diff of instructions is not a description of behaviour.

## Installing

Only after the user agrees.

```bash
cd ~/co-scientist && git pull --ff-only origin main
```

Then copy the changed skill directories into the installed location and tell
the user which files moved. If the skills are managed by the Claude Code skill
sync (a `manifest.json` with `source: plugin` entries), the synced copy is
**downstream of claude.ai and will be overwritten on the next sync** — in that
case say so plainly and tell the user the change has to be re-uploaded there to
take effect. Do not write into a sync-managed directory and report success.

After installing, update the state file and tell the user the new version.

Do not touch `created_with` in any existing ledger. It records the version a
ledger was created under and is meant to go stale. If the update changes a
convention that affects an existing ledger, append one line to that ledger's
`retro.md` naming both versions.

## Scheduled checks

The daily check exists to catch updates the user would otherwise not notice,
so it must be quiet enough to stay switched on.

- **Silence is the default.** No update, nothing to say. Do not report having
  checked, do not report that everything is fine.
- **Speak only for a new version** that is not the one last reported. The state
  file holds `last_reported_sha`; compare against it so the same update is
  never announced twice.
- **A failed check is silent the first two times.** Transient network
  failures are common and are not worth a daily interruption.
  Report on the third consecutive failure, once, with the reason.
- Keep a scheduled report to **three lines**: version, the one-sentence reason
  for the change, and an offer to show the detail.

State file:

```json
{"last_checked": "2026-10-20", "last_reported_sha": "<sha>",
 "installed_version": "<version>", "consecutive_failures": 0}
```

To set the schedule up, create a daily cron that invokes this skill. Propose it
once; if the user declines, do not propose it again.

## When NOT to check

- Mid-analysis. An update is never urgent enough to interrupt reasoning. If a
  scheduled check fires during substantive work, hold the report until the
  current thread of work is finished.
- More than once a day on a schedule. If the user asks directly, check
  regardless of when the last check ran.
