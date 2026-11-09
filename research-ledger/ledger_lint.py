#!/usr/bin/env python3
"""Lint a co-scientist ledger against the research-ledger / reporting-numbers rules.

    python research-ledger/ledger_lint.py --ledger ledger/ [--strict] [--max N]

Prints one line per finding:  <file>:<line> [<rule>] <message>
Exit 0 (warn) unless --strict and findings exist (exit 1). Read-only.

Why a linter: the rules are clear, but a long session drifts from them one
reasonable edit at a time (claims grow extra fields, code names leak in from
subagent reports, near-duplicates accumulate). None of these has a local
symptom in a diff; a deterministic check after every edit does.

Rules checked
  frontmatter   every file starts with YAML frontmatter (project, updated, tags)
  index         00-index.md has created_with and a ## Mode section
  claim-fields  claims: the closed field set, in order: type, status, chain,
                depends on, one line
  claim-budget  claims: about eight lines; at most one headline number in `one line`
  id-prefix     item IDs match their file (O in observations.md, C in claims.md, ...)
  id-unique     an ID is defined once across the ledger
  dangling      `depends on` / chain IDs and [[wikilinks]] resolve
  undefined     code-like names (snake_case, with an underscore) in claims or
                observations that are neither in backticks nor in a definitions
                table (first column of a table in observations.md)
  near-dup      two item titles in one file that are nearly identical
  n-missing     an observation with a mean/median/% but no sample size
  html-stale    ledger.html older than the newest markdown file
"""
import argparse
import difflib
import re
import sys
from pathlib import Path

ITEM_RE = re.compile(r'^###\s+([A-Z]{1,3})(\d+)\s*[—–-]\s*(.*)$')
HEAD_RE = re.compile(r'^(#{2,3})\s+(.*?)\s*$')
FIELD_RE = re.compile(r'^-\s+\*{0,2}([a-z][a-z0-9 _/-]{0,30}?)\*{0,2}\s*:\s*(.*)$', re.I)
WIKI_RE = re.compile(r'\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|[^\]]+)?\]\]')
ID_RE = re.compile(r'\b([A-Z]{1,3}\d+)\b')
CODE_RE = re.compile(r'(?<![\w/.`-])([a-z][a-z0-9]*(?:_[a-z0-9]+)+)(?![\w/.`-])')
NUM_RE = re.compile(r'(?<![A-Za-z\d.])[−-]?\d+(?:\.\d+)?(?:e[−-]?\d+)?\s*(?:%|Å|REU|SD|σ)?')
N_RE = re.compile(r'\bn\s*=\s*\d|\b\d[\d,]*(?:\s*[–-]\s*\d+)?\s+(?:[\w-]+\s+){0,3}?'
                  r'(?:designs?|runs?|groups?|targets?|samples?|iterations?|examples?|chains?|collapses?)\b', re.I)

CLAIM_FIELDS = ['type', 'status', 'chain', 'depends on', 'one line']
PREFIX_FILE = {'O': 'observations', 'C': 'claims', 'A': 'analyses', 'D': 'decisions',
               'P': 'parked', 'L': 'literature', 'F': 'figures', 'G': 'charter',
               'H': 'harness', 'E': 'experiments', 'PR': 'probes'}


def strip_code(s):
    return re.sub(r'`[^`]*`', '', s)


def parse(path):
    lines = path.read_text(encoding='utf-8').splitlines()
    items, heads = [], set()
    cur = None
    for i, ln in enumerate(lines, 1):
        h = HEAD_RE.match(ln)
        if h:
            heads.add(h.group(2).strip())
        m = ITEM_RE.match(ln)
        if m:
            cur = {'id': m.group(1) + m.group(2), 'prefix': m.group(1), 'title': m.group(3),
                   'line': i, 'body': []}
            items.append(cur)
        elif ln.startswith('## ') or ln.startswith('# '):
            cur = None
        elif cur is not None:
            cur['body'].append((i, ln))
    return lines, items, heads


def lint(ledger: Path, max_out: int):
    out = []

    def warn(f, line, rule, msg):
        out.append(f'{f}:{line} [{rule}] {msg}')

    md = sorted(p for p in ledger.glob('*.md'))
    if not md:
        return [f'{ledger}: no markdown files']
    files = {p.stem: parse(p) for p in md}

    # frontmatter / index
    for p in md:
        lines = files[p.stem][0]
        if not lines or lines[0].strip() != '---':
            warn(p.name, 1, 'frontmatter', 'missing YAML frontmatter')
            continue
        fm = '\n'.join(lines[1:lines.index('---', 1)] if '---' in lines[1:] else lines[1:10])
        for key in ('project', 'updated', 'tags'):
            if not re.search(rf'^{key}:', fm, re.M):
                warn(p.name, 1, 'frontmatter', f'frontmatter lacks `{key}`')
    if '00-index' in files:
        lines, _, heads = files['00-index']
        text = '\n'.join(lines)
        if 'created_with:' not in text:
            warn('00-index.md', 1, 'index', 'no provenance stamp (`created_with:`)')
        if 'Mode' not in heads:
            warn('00-index.md', 1, 'index', 'no `## Mode` section')

    # IDs: prefix-file match, uniqueness
    defined = {}
    for stem, (_, items, _) in files.items():
        for it in items:
            want = PREFIX_FILE.get(it['prefix'])
            if want and want != stem:
                warn(f'{stem}.md', it['line'], 'id-prefix',
                     f"{it['id']} uses prefix {it['prefix']} (reserved for {want}.md)")
            if it['id'] in defined:
                warn(f'{stem}.md', it['line'], 'id-unique',
                     f"{it['id']} also defined in {defined[it['id']]}")
            defined.setdefault(it['id'], f'{stem}.md')

    # claims: closed fields, budget
    if 'claims' in files:
        for it in files['claims'][1]:
            fields = [(i, FIELD_RE.match(l)) for i, l in it['body'] if FIELD_RE.match(l)]
            names = [m.group(1).strip().lower() for _, m in fields]
            if names != CLAIM_FIELDS:
                extra = [n for n in names if n not in CLAIM_FIELDS]
                missing = [n for n in CLAIM_FIELDS if n not in names]
                msg = []
                if missing:
                    msg.append('missing ' + ', '.join(missing))
                if extra:
                    msg.append('extra fields ' + ', '.join(extra) + ' (move to observations/analyses)')
                if not msg:
                    msg.append('fields out of order (type, status, chain, depends on, one line)')
                warn('claims.md', it['line'], 'claim-fields', f"{it['id']}: " + '; '.join(msg))
            body = [l for _, l in it['body'] if l.strip()]
            if len(body) > 8:
                warn('claims.md', it['line'], 'claim-budget',
                     f"{it['id']}: {len(body)} lines (budget ~8); move detail out and point to it")
            for _, m in fields:
                if m.group(1).strip().lower() == 'one line':
                    nums = [n for n in NUM_RE.findall(strip_code(ID_RE.sub('', m.group(2)))) if n.strip()]
                    if len(nums) > 3:
                        warn('claims.md', it['line'], 'claim-budget',
                             f"{it['id']}: one line carries {len(nums)} numbers; keep the one headline number")

    # dangling refs and wikilinks
    for stem, (lines, items, _) in files.items():
        for i, ln in enumerate(lines, 1):
            for m in WIKI_RE.finditer(ln):
                page, anchor = m.group(1).strip(), (m.group(2) or '').strip()
                if page not in files:
                    warn(f'{stem}.md', i, 'dangling', f'[[{page}]] has no file')
                elif anchor and anchor not in files[page][2]:
                    warn(f'{stem}.md', i, 'dangling', f'[[{page}#{anchor}]] has no such heading')
            fm = FIELD_RE.match(ln)
            if fm and fm.group(1).strip().lower() in ('depends on', 'feeds', 'supports'):
                for ref in ID_RE.findall(strip_code(fm.group(2))):
                    if ref not in defined:
                        warn(f'{stem}.md', i, 'dangling', f'{fm.group(1)} -> {ref} is not defined')

    # undefined code-like names
    terms = set()
    if 'observations' in files:
        for ln in files['observations'][0]:
            if ln.startswith('|'):
                cell = ln.strip('|').split('|')[0]
                terms.update(t.lower() for t in re.findall(r'[A-Za-z][\w/ -]*', strip_code(cell)))
                terms.update(CODE_RE.findall(cell))
    for stem in ('claims', 'observations'):
        if stem not in files:
            continue
        seen = set()
        for i, ln in enumerate(files[stem][0], 1):
            if ln.startswith('|') or ln.startswith('---') or ln.lstrip().startswith(('created_with', 'project:', 'tags:')):
                continue
            for tok in CODE_RE.findall(strip_code(re.sub(r'\[\[[^\]]*\]\]', '', ln))):
                if tok not in terms and tok not in seen:
                    seen.add(tok)
                    warn(f'{stem}.md', i, 'undefined',
                         f'`{tok}` is not defined (add it to the definitions table or wrap a path/name in backticks)')

    # near-duplicate titles
    for stem, (_, items, _) in files.items():
        for a_i, a in enumerate(items):
            for b in items[a_i + 1:]:
                r = difflib.SequenceMatcher(None, a['title'].lower(), b['title'].lower()).ratio()
                if r > 0.85:
                    warn(f'{stem}.md', b['line'], 'near-dup',
                         f"{b['id']} title is {r:.0%} similar to {a['id']}; merge?")

    # observations: aggregates without n
    if 'observations' in files:
        for it in files['observations'][1]:
            text = ' '.join(l for _, l in it['body'])
            if re.search(r'\b(mean|median|average)\b|\d\s*%', text, re.I) and not N_RE.search(text):
                warn('observations.md', it['line'], 'n-missing',
                     f"{it['id']}: reports an aggregate but no sample size (n)")

    # stale html
    html = ledger / 'ledger.html'
    if html.exists() and max(p.stat().st_mtime for p in md) > html.stat().st_mtime:
        warn('ledger.html', 1, 'html-stale', 'older than the markdown; regenerate with ledger_html.py')

    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--ledger', default='ledger')
    ap.add_argument('--strict', action='store_true', help='exit 1 if anything is found')
    ap.add_argument('--max', type=int, default=0, help='print at most N findings (0 = all)')
    a = ap.parse_args(argv)
    found = lint(Path(a.ledger), a.max)
    shown = found[:a.max] if a.max else found
    for f in shown:
        print(f)
    if a.max and len(found) > a.max:
        print(f'... {len(found) - a.max} more')
    print(f'{len(found)} finding(s)', file=sys.stderr)
    return 1 if (a.strict and found) else 0


if __name__ == '__main__':
    sys.exit(main())
