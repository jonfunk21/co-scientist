#!/usr/bin/env python3
"""Render a co-scientist ledger as one self-contained HTML page.

    python scripts/ledger_html.py                      # ledger/ -> ledger/ledger.html
    python scripts/ledger_html.py --ledger path/to/ledger --out report.html

Design constraints, in order of priority:

1. SELF-CONTAINED. One file, no CDN, no network, no sibling assets. Figures are
   embedded as base64 data URIs. This is the property that makes the file
   useful: it can be emailed, opened offline, and archived with the project.
   It is also why Mermaid diagrams are NOT rendered by default -- doing so
   needs a 2 MB script from a CDN, which would break every one of those.

2. NOT CLUTTERED. A ledger is a working record and most of it is reference
   material. The page leads with the question, the current conclusion and the
   claims; everything else is collapsed by default and expands on click. If
   the overview does not fit on a screen or two, the page has failed.

3. ROBUST TO ANY LEDGER. Nothing here knows about any particular project.
   Files may be missing, IDs may use any letter prefix, the figure manifest is
   optional. The only assumption is the item grammar from the research-ledger
   skill: `### <ID> — <title>` followed by `- field: value` bullets.

Cross-references: every mention of a known ID anywhere in the ledger becomes a
link, and each item gets an automatically computed "referenced by" list. That
backlink list is not in the markdown -- it is derived, and it is most of the
value of reading the ledger as a page rather than as files.

Figures are opt-in via `ledger/figures.md`, using the same item grammar:

    ### F1 — Short title
    - file: figures/fig_data_regime.png
    - supports: C1
    - caption: what the reader should take from it

Only figures listed there are embedded, so a draft plot in figures/ never
appears by accident.
"""
import argparse
import base64
import html
import json
import mimetypes
import re
import sys
from pathlib import Path

# `### C1 — Title`. Any letter prefix, so other projects' schemes work.
ITEM_RE = re.compile(r'^###\s+([A-Z]{1,3})(\d+)\s*[—–-]\s*(.*)$')
# Group 1 is the opening bold marker, if the whole bullet was emphasised as
# `- **status: ...**`. That form is natural to write and legitimate markdown,
# but it leaves the closing ** stranded at the end of the VALUE once the key
# has been parsed off, which then rendered as a literal '**'.
FIELD_RE = re.compile(
    r'^-\s+(\*{0,2})([a-z][a-z0-9 _/-]{0,30})\*{0,2}\s*:\s*(.*)$', re.I)
WIKI_RE = re.compile(r'\[\[([^\]|]+?)(?:\|([^\]]+))?\]\]')
ID_RE = re.compile(r'\b([A-Z]{1,3}\d+)\b')

# (singular, plural) -- English plurals are irregular enough that deriving them
# with +"s" produced "Analysiss" and "Literatures" on the first run.
KIND = {
    'O': ('Observation', 'Observations'), 'C': ('Claim', 'Claims'),
    'A': ('Analysis', 'Analyses'), 'D': ('Decision', 'Decisions'),
    'P': ('Parked', 'Parked questions'), 'L': ('Literature', 'References'),
    'F': ('Figure', 'Figures'),
}
# Preferred order for the kinds we know. Any OTHER prefix found in a ledger is
# appended after these rather than dropped -- see kinds_in_order(). An early
# version rendered only the known prefixes, so a project using its own scheme
# would have had items parsed, counted and then silently left off every page.
ORDER = ['O', 'A', 'D', 'L', 'P']


def kinds_in_order(present):
    """Known kinds first in ORDER, then anything else, alphabetically."""
    known = [k for k in ORDER if k in present]
    rest = sorted(k for k in present if k not in ORDER and k not in ('C', 'F'))
    return known + rest


def kind_label(k):
    """(singular, plural) for a prefix, inventing a label for unknown ones."""
    return KIND.get(k, (f'{k} item', f'{k} items'))

STATUS_CLASS = [
    ('retracted', 'bad'), ('refuted', 'bad'), ('weak', 'warn'),
    ('open', 'open'), ('supported', 'good'), ('resolved', 'good'),
    ('closed', 'good'), ('null', 'warn'),
]


class Item:
    def __init__(self, iid, title, src):
        self.id, self.title, self.src = iid, title, src
        self.kind = re.match(r'[A-Z]+', iid).group(0)
        self.fields, self.body, self.refs = [], [], set()

    @property
    def status(self):
        for k, v in self.fields:
            if k.lower() == 'status':
                return re.sub(r'[*_`]', '', v).strip()
        return ''

    @property
    def status_short(self):
        """A short token for the badge — never a truncated sentence.

        A status is often a sentence: "supported, for close neighbourhoods in
        this library and assay". Clipping that to fit a badge produced
        "supported, for close neighbourhoods in this…", which hides the part
        that qualifies the claim — the half that matters most. So the badge
        carries only the leading clause, and if even that is long it falls
        back to the bare status word. The full text is always shown as a
        field, so nothing is ever only-available-truncated.
        """
        t = re.sub(r'[*_`]', '', self.status).strip()
        t = re.split(r'[.,;]', t)[0].strip()
        if len(t) > 28:
            low = t.lower()
            for word, _ in STATUS_CLASS:
                if word in low:
                    return word
            t = t.split()[0] if t.split() else t
        return t

    def status_class(self):
        s = self.status.lower()
        for word, cls in STATUS_CLASS:
            if word in s:
                return cls
        return ''

    def field(self, name):
        for k, v in self.fields:
            if k.lower() == name:
                return v
        return ''


def clip(text, n=40):
    """Truncate on a word boundary. Cutting at a fixed character count gave
    nav entries like "Co-folding's performance is not an art"."""
    text = text.strip()
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(' ', 1)[0].rstrip(' ,;:—–-')
    return (cut or text[:n]) + '…'

def parse_file(path):
    """Return (frontmatter, h1, prose_sections, items)."""
    text = path.read_text(encoding='utf-8')
    fm = {}
    if text.startswith('---\n'):
        end = text.find('\n---\n', 4)
        if end != -1:
            for line in text[4:end].split('\n'):
                if ':' in line and not line.startswith(' '):
                    k, v = line.split(':', 1)
                    fm[k.strip()] = v.strip()
            text = text[end + 5:]

    h1, sections, items = '', [], []
    cur_item, cur_sec = None, None
    in_fence = in_field = False

    for raw in text.split('\n'):
        if raw.lstrip().startswith('```'):
            in_fence = not in_fence
        if not in_fence:
            if raw.startswith('# '):
                h1 = raw[2:].strip()
                cur_item = cur_sec = None
                continue
            m = ITEM_RE.match(raw)
            if m:
                cur_item = Item(m.group(1) + m.group(2), m.group(3).strip(), path.stem)
                items.append(cur_item)
                cur_sec, in_field = None, False
                continue
            if raw.startswith('## '):
                cur_sec = {'title': raw[3:].strip(), 'lines': []}
                sections.append(cur_sec)
                cur_item = None
                continue

        if cur_item is not None:
            fm_match = FIELD_RE.match(raw) if not in_fence else None
            # A field bullet only counts before any free prose/table starts,
            # otherwise "- source: x" inside a table would be swallowed.
            if fm_match and not cur_item.body:
                key, val = fm_match.group(2).strip(), fm_match.group(3).strip()
                if fm_match.group(1) == '**' and val.endswith('**'):
                    val = val[:-2].rstrip()
                cur_item.fields.append([key, val])
                in_field = True
            elif (in_field and not in_fence and cur_item.fields
                  and not cur_item.body and re.match(r'^\s{2,}\S', raw)):
                # Wrapped continuation of the field above. A blank line ends
                # the field, so an indented TABLE after a blank line (which
                # several observations use) still reaches the body instead of
                # being flattened into the field value.
                cur_item.fields[-1][1] += ' ' + raw.strip()
            else:
                if not raw.strip():
                    in_field = False
                if raw.strip() or cur_item.body:
                    cur_item.body.append(raw)
        elif cur_sec is not None:
            cur_sec['lines'].append(raw)

    for it in items:
        while it.body and not it.body[-1].strip():
            it.body.pop()
    return fm, h1, sections, items


def parse_ledger(d):
    index_fm, project, overview, items = {}, '', [], {}
    for path in sorted(d.glob('*.md')):
        fm, h1, sections, found = parse_file(path)
        if path.name.startswith('00'):
            index_fm, project, overview = fm, h1 or project, sections
        for it in found:
            if it.id not in items:
                items[it.id] = it
    # cross-references
    for it in items.values():
        blob = ' '.join(v for _, v in it.fields) + ' ' + '\n'.join(it.body)
        for other in ID_RE.findall(blob):
            if other in items and other != it.id:
                it.refs.add(other)
    return index_fm, project, overview, items


# --------------------------------------------------------------------------
# a small markdown renderer: only what a ledger actually contains
# --------------------------------------------------------------------------
def inline(text, items, link_ids=True):
    out = html.escape(text, quote=False)

    def wiki(m):
        target = (m.group(2) or m.group(1)).split('#')[-1]
        mid = ID_RE.search(m.group(1).split('#')[-1])
        label = re.sub(r'\s*[—–-]\s*.*$', '', target) if mid else target
        if mid and mid.group(1) in items:
            return f'<a class="ref" href="#{mid.group(1)}">{html.escape(label)}</a>'
        return f'<span class="wiki">{html.escape(target)}</span>'
    out = WIKI_RE.sub(wiki, out)

    out = re.sub(r'`([^`]+)`', r'<code>\1</code>', out)
    out = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', out)
    out = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'<em>\1</em>', out)
    out = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                 lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
                 out)
    if link_ids:
        def idlink(m):
            i = m.group(1)
            if i in items:
                t = html.escape(items[i].title, quote=True)
                return f'<a class="ref" href="#{i}" title="{t}">{i}</a>'
            return i
        # not inside an existing tag
        parts = re.split(r'(<[^>]+>)', out)
        out = ''.join(p if p.startswith('<') else ID_RE.sub(idlink, p) for p in parts)
    return out


def block(lines, items):
    """Render a list of markdown lines. Handles tables, fences, lists, quotes."""
    html_out, i = [], 0
    while i < len(lines):
        line = lines[i]

        if line.lstrip().startswith('```'):
            lang = line.strip().strip('`').strip()
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].lstrip().startswith('```'):
                buf.append(lines[i]); i += 1
            i += 1
            body = html.escape('\n'.join(buf))
            note = ('<div class="note">Diagram source — this page is '
                    'self-contained and does not load a renderer.</div>'
                    if lang == 'mermaid' else '')
            html_out.append(f'<pre class="code">{note}<code>{body}</code></pre>')
            continue

        if '|' in line and i + 1 < len(lines) and re.match(r'^\s*\|?[\s:|-]+\|[\s:|-]*$', lines[i + 1]):
            def cells(r):
                return [c.strip() for c in r.strip().strip('|').split('|')]
            head = cells(line)
            i += 2
            rows = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                rows.append(cells(lines[i])); i += 1
            th = ''.join(f'<th>{inline(c, items)}</th>' for c in head)
            tb = ''.join('<tr>' + ''.join(f'<td>{inline(c, items)}</td>' for c in r)
                         + '</tr>' for r in rows)
            html_out.append(f'<table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table>')
            continue

        m = re.match(r'^(\s*)[-*]\s+(.*)$', line)
        if m:
            buf = []
            while i < len(lines):
                mm = re.match(r'^(\s*)[-*]\s+(.*)$', lines[i])
                if mm:
                    buf.append(mm.group(2))
                    i += 1
                elif lines[i].startswith('  ') and lines[i].strip() and buf:
                    buf[-1] += ' ' + lines[i].strip()
                    i += 1
                else:
                    break
            lis = ''.join(f'<li>{inline(b, items)}</li>' for b in buf)
            html_out.append(f'<ul>{lis}</ul>')
            continue

        m = re.match(r'^(\s*)\d+\.\s+(.*)$', line)
        if m:
            buf = []
            while i < len(lines):
                mm = re.match(r'^(\s*)\d+\.\s+(.*)$', lines[i])
                if mm:
                    buf.append(mm.group(2)); i += 1
                elif lines[i].startswith('   ') and lines[i].strip() and buf:
                    buf[-1] += ' ' + lines[i].strip(); i += 1
                else:
                    break
            lis = ''.join(f'<li>{inline(b, items)}</li>' for b in buf)
            html_out.append(f'<ol>{lis}</ol>')
            continue

        if line.startswith('>'):
            buf = []
            while i < len(lines) and lines[i].startswith('>'):
                buf.append(lines[i].lstrip('> ')); i += 1
            html_out.append(f'<blockquote>{block(buf, items)}</blockquote>')
            continue

        if line.startswith('### '):
            html_out.append(f'<h4>{inline(line[4:], items)}</h4>'); i += 1; continue
        if line.startswith('## '):
            html_out.append(f'<h3>{inline(line[3:], items)}</h3>'); i += 1; continue

        if not line.strip():
            i += 1
            continue

        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(
                r'^(\s*[-*]\s|\s*\d+\.\s|>|#{2,4}\s|```)', lines[i]):
            buf.append(lines[i].strip()); i += 1
        if buf:
            html_out.append(f'<p>{inline(" ".join(buf), items)}</p>')
        else:
            # Nothing matched and nothing consumed. Emit the line and move on
            # rather than spinning: a stray '|' outside a table did exactly
            # that and hung the renderer.
            html_out.append(f'<p>{inline(lines[i].strip(), items)}</p>')
            i += 1
    return ''.join(html_out)


def data_uri(path, max_width=1600):
    """Base64 data URI, downscaled if the image is wider than max_width.

    Embedding figures at full resolution produced a 4.5 MB page, which defeats
    the point of a file you can email. Matplotlib PNGs at 200+ dpi are far
    larger than any screen needs. Falls back to the raw bytes if Pillow is
    absent, so the tool still works without it.
    """
    mime = mimetypes.guess_type(str(path))[0] or 'image/png'
    raw = path.read_bytes()
    if max_width and mime.startswith('image/') and mime != 'image/svg+xml':
        try:
            import io
            from PIL import Image
            im = Image.open(io.BytesIO(raw))
            if im.width > max_width:
                h = round(im.height * max_width / im.width)
                im = im.convert('RGB').resize((max_width, h), Image.LANCZOS)
                buf = io.BytesIO()
                im.save(buf, 'JPEG', quality=88, optimize=True)
                if buf.tell() < len(raw):
                    raw, mime = buf.getvalue(), 'image/jpeg'
        except Exception:
            pass
    return f'data:{mime};base64,{base64.b64encode(raw).decode()}'


CSS = """
:root{--bg:#fbfaf8;--surface:#fff;--ink:#1d1c1a;--ink2:#53514c;--muted:#8a877f;
--line:#e5e2dc;--accent:#2a6ad6;--good:#1a7f52;--warn:#9a6b00;--bad:#b4341f;
--chip:#f1efea;--shadow:0 1px 2px rgba(0,0,0,.05),0 4px 14px rgba(0,0,0,.04)}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
--bg:#14150f;--surface:#1c1d17;--ink:#eceadf;--ink2:#b4b1a4;--muted:#85827a;
--line:#2e3029;--accent:#79a8ff;--good:#54c48c;--warn:#dba63a;--bad:#f08270;
--chip:#25271f;--shadow:0 1px 2px rgba(0,0,0,.3),0 4px 14px rgba(0,0,0,.25)}}
:root[data-theme=dark]{--bg:#14150f;--surface:#1c1d17;--ink:#eceadf;--ink2:#b4b1a4;
--muted:#85827a;--line:#2e3029;--accent:#79a8ff;--good:#54c48c;--warn:#dba63a;
--bad:#f08270;--chip:#25271f;--shadow:0 1px 2px rgba(0,0,0,.3),0 4px 14px rgba(0,0,0,.25)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.65 ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
-webkit-font-smoothing:antialiased}

/* ---- header + horizontal tab bar ---- */
header.top{background:var(--surface);border-bottom:1px solid var(--line)}
.hwrap,.tabwrap,.wrap{max-width:1180px;margin:0 auto;padding-left:32px;
padding-right:32px}
.hwrap{padding-top:28px;padding-bottom:18px}
h1{font-size:27px;line-height:1.25;margin:0 0 5px;letter-spacing:-.015em}
.meta{color:var(--muted);font-size:13px}
.meta a{color:var(--muted)}
nav.tabs{position:sticky;top:0;z-index:9;background:var(--surface);
border-bottom:1px solid var(--line)}
nav.tabs .tabwrap{display:flex;gap:4px;overflow-x:auto;padding-top:7px;
padding-bottom:7px;scrollbar-width:none}
nav.tabs .tabwrap::-webkit-scrollbar{display:none}
a.tab{display:inline-flex;align-items:center;gap:7px;white-space:nowrap;
font-size:13px;font-weight:500;color:var(--ink2);text-decoration:none;
padding:6px 11px;border-radius:7px}
a.tab:hover{background:var(--chip);color:var(--ink)}
a.tab.on{background:var(--accent);color:#fff}
a.tab .nid{font-size:11px;background:var(--chip);color:var(--ink2);padding:1px 6px;
border-radius:999px;font-variant-numeric:tabular-nums}
a.tab.on .nid{background:rgba(255,255,255,.24);color:#fff}

/* ---- two columns ---- */
.wrap{display:grid;grid-template-columns:214px minmax(0,1fr);gap:40px;
padding-top:6px}
nav.toc{position:sticky;top:48px;align-self:start;max-height:calc(100vh - 60px);
overflow-y:auto;overscroll-behavior:contain;padding:26px 0 36px;font-size:13px}
nav.toc h4{font-size:11px;letter-spacing:.09em;text-transform:uppercase;
color:var(--muted);margin:0 0 9px;font-weight:650}
nav.toc a{display:block;padding:3.5px 0 3.5px 10px;color:var(--ink2);
text-decoration:none;border-left:2px solid transparent;margin-left:-12px;
line-height:1.45}
nav.toc a:hover{color:var(--accent);border-left-color:var(--accent)}
nav.toc .nid{color:var(--muted);margin-right:6px;font-size:11.5px;font-weight:650}
main{padding:28px 0 120px;min-width:0}
.pagehead{display:none}
section{margin:0 0 30px;scroll-margin-top:62px}
h2{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);
font-weight:650;margin:0 0 14px;padding-bottom:8px;border-bottom:1px solid var(--line)}
h3{font-size:16px;margin:18px 0 6px}
h4{font-size:14.5px;margin:14px 0 4px;color:var(--ink2)}

/* ---- items ---- */
.card{background:var(--surface);border:1px solid var(--line);border-radius:11px;
padding:18px 20px;margin:12px 0;box-shadow:var(--shadow);scroll-margin-top:62px}
.card>h3{margin-top:0;display:flex;gap:9px;align-items:baseline;flex-wrap:wrap}
/* Sans, not monospace: in most monospace faces a capital O is near enough to a
   zero that "O1" reads as "01", which is bad in a ledger whose commonest item
   kind is the observation. */
.cid{font:650 12px/1 inherit;color:var(--accent);background:var(--chip);
padding:4px 7px;border-radius:5px;letter-spacing:.03em}
.badge{font-size:11px;font-weight:600;padding:3px 8px;border-radius:999px;
background:var(--chip);color:var(--ink2);letter-spacing:.02em;
flex:0 1 auto;max-width:100%}
.badge.good{color:var(--good)}.badge.warn{color:var(--warn)}
.badge.bad{color:var(--bad)}.badge.open{color:var(--accent)}
dl{margin:10px 0 0;display:grid;grid-template-columns:auto minmax(0,1fr);
gap:3px 14px;font-size:14.5px}
dt{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.05em;
padding-top:4px;white-space:nowrap}
dd{margin:0;color:var(--ink2)}
.body{margin-top:12px;font-size:14.5px;color:var(--ink2)}
.body>:first-child{margin-top:0}
p{margin:.55em 0}
ul,ol{margin:.5em 0;padding-left:1.25em}li{margin:.22em 0}
a{color:var(--accent)}
a.ref{text-decoration:none;font-weight:600;border-bottom:1px solid transparent}
a.ref:hover{border-bottom-color:var(--accent)}
code{font:0.88em ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--chip);
padding:1.5px 5px;border-radius:4px}
pre.code{background:var(--chip);padding:13px 15px;border-radius:8px;overflow-x:auto;
font-size:12.5px;line-height:1.5;margin:11px 0}
pre.code code{background:none;padding:0}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13.5px;
font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:7px 11px;border-bottom:1px solid var(--line);
vertical-align:top}
th{font-size:11.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);
font-weight:650}
blockquote{margin:11px 0;padding:2px 0 2px 15px;border-left:3px solid var(--line);
color:var(--ink2)}
.note{color:var(--muted);font-size:11.5px;margin-bottom:7px;font-style:italic}
details.item{border-bottom:1px solid var(--line);scroll-margin-top:62px}
details.item>summary{cursor:pointer;padding:10px 2px;list-style:none;display:flex;
gap:10px;align-items:baseline;flex-wrap:wrap}
details.item>summary::-webkit-details-marker{display:none}
details.item>summary:hover{color:var(--accent)}
details.item>summary::before{content:"▸";color:var(--muted);font-size:11px;
transition:transform .12s}
details.item[open]>summary::before{transform:rotate(90deg)}
.sum-t{flex:1;min-width:0}
.inner{padding:0 2px 18px 22px}
figure{margin:20px 0;background:var(--surface);border:1px solid var(--line);
border-radius:11px;padding:16px;box-shadow:var(--shadow);scroll-margin-top:62px}
figure img{width:100%;height:auto;border-radius:6px;display:block}
figcaption{font-size:13.5px;color:var(--ink2);margin-top:12px}
figcaption .cap{margin-top:7px;line-height:1.6}
figcaption dl.prov{margin-top:10px;padding-top:9px;border-top:1px dashed var(--line);
font-size:12px}
figcaption dl.prov dd{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
font-size:11.5px}
.backlinks{margin-top:12px;padding-top:10px;border-top:1px dashed var(--line);
font-size:12.5px;color:var(--muted)}
.theme{position:fixed;top:14px;right:16px;background:var(--surface);color:var(--ink2);
border:1px solid var(--line);border-radius:7px;padding:5px 10px;font-size:12px;
cursor:pointer;z-index:10}
:target{animation:flash 1.6s ease-out}
@keyframes flash{0%,22%{background:color-mix(in srgb,var(--accent) 16%,transparent)}
100%{background:transparent}}
@media (max-width:860px){.wrap{grid-template-columns:1fr;gap:0}
.hwrap,.tabwrap,.wrap{padding-left:18px;padding-right:18px}
nav.toc{display:none}main{padding-top:20px}}
@media print{nav.toc,nav.tabs,.theme{display:none}.wrap{grid-template-columns:1fr}
.pagehead{display:block}
[data-page][hidden]{display:block!important}
details.item{break-inside:avoid}details.item>summary::before{content:""}}
"""


JS = """
(function(){
 var d=document.documentElement;
 var b=document.getElementById('t');
 if(b)b.onclick=function(){
  var cur=d.getAttribute('data-theme')||
   (matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  d.setAttribute('data-theme',cur==='dark'?'light':'dark');};

 var P=[].slice.call(document.querySelectorAll('[data-page]'));
 if(!P.length)return;

 function show(slug){
  if(!P.some(function(p){return p.dataset.page===slug;}))slug=P[0].dataset.page;
  P.forEach(function(p){p.hidden=p.dataset.page!==slug;});
  [].forEach.call(document.querySelectorAll('[data-navfor]'),function(n){
   n.hidden=n.dataset.navfor!==slug;});
  [].forEach.call(document.querySelectorAll('.tab'),function(a){
   a.classList.toggle('on',a.dataset.go===slug);});
 }

 function nav(h){
  if(!h)return;
  if(h.charAt(0)==='/'){show(h.slice(1));scrollTo(0,0);return;}
  var slug=PAGE[h]||(h.indexOf('s-')===0?'overview':null);
  if(slug)show(slug);
  var el=document.getElementById(h);
  if(!el)return;
  var x=el.closest?el.closest('details'):null;
  while(x){x.open=true;x=x.parentElement&&x.parentElement.closest('details');}
  if(el.tagName==='DETAILS')el.open=true;
  el.scrollIntoView({block:'start'});
 }

 // Navigate on the click itself rather than waiting for a hashchange event.
 // Embedded viewers (IDE preview panes, some mail clients) often do not update
 // location.hash for in-page links on file:// URLs, and the whole tab bar then
 // does nothing. Handling the click directly makes navigation independent of
 // that; the hash is still updated so links remain copyable, and hashchange is
 // still handled for back/forward and for a URL typed with a fragment.
 document.addEventListener('click',function(e){
  var a=e.target&&e.target.closest?e.target.closest('a[href^="#"]'):null;
  if(!a)return;
  var t=a.getAttribute('href').slice(1);
  if(!t)return;
  e.preventDefault();
  nav(t);
  try{history.replaceState(null,'','#'+t);}catch(_){ }
 });

 addEventListener('hashchange',function(){
  nav(decodeURIComponent(location.hash.slice(1)));});
 function start(){nav(decodeURIComponent(location.hash.slice(1)));}
 if(document.readyState!=='loading')start();
 else addEventListener('DOMContentLoaded',start);
})();
"""


def render(ledger_dir, out_path, repo_root, max_width=1600, link_figs=False):
    fm, project, overview, items = parse_ledger(ledger_dir)
    if not items:
        sys.exit(f'No ledger items found in {ledger_dir}. Expected headings '
                 f'like "### O1 — Title".')

    backlinks = {i: [] for i in items}
    for it in items.values():
        for r in it.refs:
            backlinks[r].append(it.id)

    def key(i):
        m = re.match(r'([A-Z]+)(\d+)', i)
        return (m.group(1), int(m.group(2)))

    by_kind = {}
    for i in sorted(items, key=key):
        by_kind.setdefault(items[i].kind, []).append(items[i])

    # ---- figures: embed only what the manifest lists ----
    figs, missing = [], []
    for f in by_kind.get('F', []):
        rel = f.field('file')
        if not rel:
            continue
        p = (repo_root / rel)
        if p.exists():
            if link_figs:
                import os
                figs.append((f, os.path.relpath(p, out_path.parent)))
            else:
                figs.append((f, data_uri(p, max_width)))
        else:
            missing.append(rel)

    def badge_of(it):
        if not it.status:
            return ''
        return (f'<span class="badge {it.status_class()}">'
                f'{html.escape(it.status_short)}</span>')

    def fields_of(it):
        rows = []
        for k, v in it.fields:
            if k.lower() == 'status':
                full = re.sub(r'[*_`]', '', v).strip()
                if it.status_short == full:
                    continue      # the badge already says all of it
            rows.append(f'<dt>{html.escape(k)}</dt><dd>{inline(v, items)}</dd>')
        return f'<dl>{"".join(rows)}</dl>' if rows else ''

    def body_of(it):
        return f'<div class="body">{block(it.body, items)}</div>' if it.body else ''

    def backlinks_of(it):
        bl = backlinks.get(it.id) or []
        if not bl:
            return ''
        links = ', '.join(
            f'<a class="ref" href="#{b}" title="'
            f'{html.escape(items[b].title, quote=True)}">{b}</a>'
            for b in sorted(bl, key=key))
        return f'<div class="backlinks">Referenced by {links}</div>'

    def card(it, lead=False):
        head = (f'<h3><span class="cid">{it.id}</span>'
                f'<span>{inline(it.title, items, link_ids=False)}</span>'
                f'{badge_of(it)}</h3>')
        return (f'<div class="card" id="{it.id}">{head}{fields_of(it)}'
                f'{body_of(it)}{backlinks_of(it)}</div>')

    def collapsed(it):
        return (f'<details class="item" id="{it.id}"><summary>'
                f'<span class="cid">{it.id}</span>'
                f'<span class="sum-t">{inline(it.title, items, link_ids=False)}</span>'
                f'{badge_of(it)}</summary><div class="inner">{fields_of(it)}'
                f'{body_of(it)}{backlinks_of(it)}</div></details>')

    # ---- pages ----
    # Categories are tabs. Only the active one is shown, switched client-side,
    # so the file stays a single document.
    #
    # The FIRST page is rendered visible in the HTML and JavaScript hides the
    # others on load -- never the reverse. An earlier version marked every page
    # hidden and relied on the script to reveal one, which meant the whole file
    # rendered blank anywhere the script did not run: IDE preview panes that
    # restrict JavaScript, a mail client, a syntax error. Content first,
    # scripting as enhancement. <noscript> then restores the plain long page,
    # which is a perfectly good way to read a ledger.
    pages = [('overview', 'Overview', None)]
    if by_kind.get('C'):
        pages.append(('claims', 'Claims', 'C'))
    if figs:
        pages.append(('figures', 'Figures', 'F'))
    for k in kinds_in_order(by_kind):
        if by_kind.get(k):
            lab = kind_label(k)[1]
            pages.append((re.sub(r'[^a-z0-9]+', '-', lab.lower()).strip('-'), lab, k))

    page_of = {}
    for slug, _, k in pages:
        for it in by_kind.get(k, []):
            page_of[it.id] = slug
    first = pages[0][0]

    tabs = ['<nav class="tabs"><div class="tabwrap">']
    for slug, label, k in pages:
        n = len(by_kind.get(k, [])) if k else len(overview)
        on = ' on' if slug == first else ''
        tabs.append(f'<a class="tab{on}" data-go="{slug}" href="#/{slug}">{label}'
                    f'<span class="nid">{n}</span></a>')
    tabs.append('</div></nav>')

    toc = ['<nav class="toc">']
    for slug, label, k in pages:
        sub = []
        if k is None:
            for sec in overview:
                sid = re.sub(r'[^a-z0-9]+', '-', sec['title'].lower()).strip('-')
                sub.append(f'<a href="#s-{sid}">{html.escape(sec["title"])}</a>')
        else:
            for it in by_kind.get(k, []):
                sub.append(f'<a href="#{it.id}"><span class="nid">{it.id}</span>'
                           f'{html.escape(clip(it.title, 32))}</a>')
        hid = '' if slug == first else ' hidden'
        toc.append(f'<div class="subnav" data-navfor="{slug}"{hid}>'
                   f'<h4>{label}</h4>{"".join(sub)}</div>')
    toc.append('</nav>')

    # ---- main ----
    M = ['<main>']
    for slug, label, k in pages:
        hid = '' if slug == first else ' hidden'
        M.append(f'<div class="page" data-page="{slug}"{hid}>')
        M.append(f'<h2 class="pagehead">{html.escape(label)}</h2>')
        if k is None:
            for sec in overview:
                sid = re.sub(r'[^a-z0-9]+', '-', sec['title'].lower()).strip('-')
                M.append(f'<section id="s-{sid}"><h2>{html.escape(sec["title"])}</h2>'
                         f'{block(sec["lines"], items)}</section>')
        elif k == 'C':
            M.extend(card(c) for c in by_kind['C'])
        elif k == 'F':
            for f, uri in figs:
                sup = f.field('supports')
                cap = f.field('caption') or ''
                supl = (f' <span class="badge">supports {inline(sup, items)}</span>'
                        if sup else '')
                extra = ''.join(
                    f'<dt>{html.escape(kk)}</dt><dd>{inline(vv, items)}</dd>'
                    for kk, vv in f.fields
                    if kk.lower() not in ('caption', 'supports', 'file'))
                M.append(
                    f'<figure id="{f.id}"><img loading="lazy" '
                    f'alt="{html.escape(f.title, quote=True)}" src="{uri}">'
                    f'<figcaption><strong>{html.escape(f.id)} — '
                    f'{inline(f.title, items, link_ids=False)}</strong>{supl}'
                    f'<div class="cap">{inline(cap, items)}</div>'
                    + (f'<dl class="prov">{extra}</dl>' if extra else '')
                    + '</figcaption></figure>')
        else:
            M.extend(collapsed(it) for it in by_kind[k])
        M.append('</div>')
    M.append('</main>')

    stamp = fm.get('created_with', '')
    framework = fm.get('framework', '')
    meta = []
    if fm.get('updated'):
        meta.append(f'Updated {html.escape(fm["updated"])}')
    if stamp:
        st = html.escape(stamp)
        meta.append(f'<a href="{html.escape(framework, quote=True)}">{st}</a>'
                    if framework else st)
    header = (f'<header class="top"><div class="hwrap">'
              f'<h1>{html.escape(project or "Research ledger")}</h1>'
              f'<div class="meta">{" · ".join(meta)}</div></div></header>')
    page_map = json.dumps(page_of)

    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
           f'<meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{html.escape(project or "Ledger")}</title>'
           f'<style>{CSS}</style></head><body>'
           f'<noscript><style>[data-page][hidden]{{display:block!important}}'
           f'.subnav[hidden]{{display:block!important}}nav.tabs{{display:none}}'
           f'.pagehead{{display:block}}</style></noscript>'
           f'<button class="theme" id="t">◐</button>'
           f'{header}{"".join(tabs)}'
           f'<div class="wrap">{"".join(toc)}{"".join(M)}</div>'
           f'<script>var PAGE={page_map};{JS}</script></body></html>')
    out_path.write_text(doc, encoding='utf-8')

    kb = len(doc.encode()) / 1024
    how = 'linked' if link_figs else 'embedded'
    print(f'wrote {out_path}  ({kb:.0f} KB, {len(items)} items, '
          f'{len(figs)} figure(s) {how})')
    if link_figs and figs:
        print('    NOT self-contained: the figures/ folder must travel with it')
    for k in kinds_in_order(by_kind) + ['C', 'F']:
        if by_kind.get(k):
            print(f'    {kind_label(k)[1]:<18} {len(by_kind[k])}')
    if missing:
        print('  figures listed but not found (skipped):')
        for m in missing:
            print(f'    {m}')
    if not figs and not by_kind.get('F'):
        print('  no ledger/figures.md -- add one to embed accepted figures')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--ledger', default='ledger', type=Path)
    ap.add_argument('--out', type=Path, default=None)
    ap.add_argument('--root', type=Path, default=None,
                    help='base for figure paths (default: ledger parent)')
    ap.add_argument('--max-width', type=int, default=1600,
                    help='downscale embedded figures wider than this (0 = off)')
    ap.add_argument('--no-embed', action='store_true',
                    help='link figures instead of embedding them. Produces a '
                         'small file that needs its figures/ folder alongside. '
                         'Use when an embedded-data-URI viewer (some IDE HTML '
                         'previews) refuses to show the page.')
    a = ap.parse_args()
    if not a.ledger.is_dir():
        sys.exit(f'No such ledger directory: {a.ledger}')
    root = a.root or a.ledger.parent
    render(a.ledger, a.out or a.ledger / 'ledger.html', root,
           0 if a.no_embed else a.max_width, a.no_embed)


if __name__ == '__main__':
    main()
