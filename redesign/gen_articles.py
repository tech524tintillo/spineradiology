#!/usr/bin/env python3
"""
Build a category's articles in Emily's LITERAL article design, into the real deployed layout:
  article -> site/<cat>/<slug>/index.html  (URL /<cat>/<slug>/)

Article order/titles come from the already-generated Emily category page (site/<cat>/index.html) when
it exists, else from mkdocs.yml's nav (authoritative reading order). Subtitle = the category entry's
description if present, else the article's lead sentence. Bodies come from the pristine MkDocs build,
cached to redesign/bodies/<cat>/ for idempotent re-runs. Only Emily's subnav + per-article
head/body/nav + template-name links are touched.
"""
import re, os

ROOT  = "/Users/light/Downloads/spineradiology"
TPL   = "/Users/light/Downloads/Template design/article-template-v2.html"
OUT   = os.path.join(ROOT, "site")
CACHE_ROOT = os.path.join(ROOT, "redesign/bodies")
MKDOCS = open(os.path.join(ROOT, "mkdocs.yml"), encoding="utf-8").read().splitlines()

# every category -> its active subnav tab label
TAB = {
    "anatomy": "Anatomy", "imaging-modalities": "Imaging", "degenerative-disease": "Degenerative",
    "trauma": "Trauma", "neoplasms": "Neoplasms", "infection": "Infection",
    "inflammatory-autoimmune": "Inflammatory", "congenital-developmental": "Congenital",
    "vascular": "Vascular", "metabolic-systemic": "Metabolic",
    "post-surgical-spine": "Post-Surgical", "special-topics": "Special Topics",
}
# categories whose Emily category file now exists -> renumber articles to match her category order
BUILD = ["infection", "inflammatory-autoimmune", "congenital-developmental", "vascular"]

CATS = [
    ("Home", "/", "1"), ("Anatomy", "/anatomy/", "1"), ("Imaging", "/imaging-modalities/", "1"),
    ("Degenerative", "/degenerative-disease/", "1"), ("Trauma", "/trauma/", "1"), ("Neoplasms", "/neoplasms/", "1"),
    ("Infection", "/infection/", "2"), ("Inflammatory", "/inflammatory-autoimmune/", "2"),
    ("Congenital", "/congenital-developmental/", "2"), ("Vascular", "/vascular/", "2"),
    ("Metabolic", "/metabolic-systemic/", "2"), ("Post-Surgical", "/post-surgical-spine/", "2"),
    ("Special Topics", "/special-topics/", "2"),
]
def subnav_html(active):
    out = ['  <div class="subnav-shell">', '  <nav class="subnav">']
    for name, href, pg in CATS:
        cls = ' class="is-active"' if name == active else ''
        out.append(f'    <a href="{href}"{cls} data-pg="{pg}">{name}</a>')
    out += ['  </nav>',
            '  <button class="subnav-chev subnav-chev--prev" type="button" aria-label="Previous">&#8249;</button>',
            '  <button class="subnav-chev subnav-chev--next" type="button" aria-label="More">&#8250;</button>',
            '</div>']
    return "\n".join(out)

SUBNAV_STYLE = """<style>
/* match the category page's starfield: cap Emily's sparkle layer to a header-height band so her
   %-positioned dots cluster near the top like the short category page instead of spreading thin. */
.page::after{height:1267px!important;bottom:auto!important}
/* hold all 12 categories in her bar — two discrete pages (Home+5, then the rest) + squared chevrons */
.subnav-shell{position:relative}
.subnav-shell .subnav{flex-wrap:nowrap!important;justify-content:flex-start!important;padding:0 38px}
.subnav-shell .subnav a{flex:1 1 0%!important;white-space:nowrap!important}
.subnav-shell:not(.is-pg2) .subnav a[data-pg="2"]{display:none!important}
.subnav-shell.is-pg2 .subnav a[data-pg="1"]{display:none!important}
.subnav-shell .subnav a[data-pg="1"]:has(+ a[data-pg="2"]){border-right:0!important}
.subnav-chev{position:absolute;top:50%;transform:translateY(-50%);z-index:3;width:30px;height:30px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(143,212,224,.25);border-radius:7px;background:rgba(6,26,38,.94);color:#8fd4e0;cursor:pointer;font-size:1.1rem;transition:.2s}
.subnav-chev--prev{left:4px}.subnav-chev--next{right:4px}
.subnav-chev:hover{background:rgba(95,182,204,.2);border-color:#5fb6cc;color:#eef3fb}
.subnav-shell:not(.is-pg2) .subnav-chev--prev{opacity:.22;pointer-events:none}
.subnav-shell.is-pg2 .subnav-chev--next{opacity:.22;pointer-events:none}
</style>
<script>
(function(){var s=document.querySelector('.subnav-shell');if(!s)return;
var p=s.querySelector('.subnav-chev--prev'),nx=s.querySelector('.subnav-chev--next');
var act=s.querySelector('.subnav a.is-active');
if(act&&act.getAttribute('data-pg')==='2')s.classList.add('is-pg2');
p&&p.addEventListener('click',function(){s.classList.remove('is-pg2');});
nx&&nx.addEventListener('click',function(){s.classList.add('is-pg2');});})();
</script>"""

def make_template(active):
    T = open(TPL, encoding="utf-8").read()
    T = re.sub(r'  <!-- SUBNAV -->\s*<nav class="subnav">.*?</nav>', '  <!-- SUBNAV -->\n' + subnav_html(active), T, flags=re.S)
    T = T.replace("</body></html>", SUBNAV_STYLE + "\n</body></html>")
    T = T.replace("Spine Radiology - Redesign.html", "/")
    T = T.replace("category-template-v2.html", "/anatomy/").replace("article-template-v2.html", "/anatomy/")
    T = re.sub(r'(<div class="head__brand">).*?(</div>)', rf'\g<1>Spine Radiology · {active}\g<2>', T, flags=re.S)
    return T

def article_list(cat):
    """[(slug, title, desc-or-None)] in reading order."""
    cidx = os.path.join(OUT, cat, "index.html")
    if os.path.exists(cidx):
        h = open(cidx, encoding="utf-8").read()
        em = re.findall(rf'<a class="entry" href="/{cat}/([a-z0-9-]+)/"><span class="entry__num">\d+</span>'
                        r'<div class="entry__main"><h3>(.*?)</h3><p>(.*?)</p>', h, re.S)
        if em:
            out = [(s, t.strip(), d.strip()) for (s, t, d) in em]
            return _append_orphans(cat, out)
    # fall back to mkdocs.yml nav order
    out = []
    for line in MKDOCS:
        m = re.match(rf'\s*-\s*(?:(.+?):\s*)?{re.escape(cat)}/([a-z0-9-]+)\.md\s*$', line)
        if m:
            slug = m.group(2)
            if slug == "index":
                continue
            out.append((slug, (m.group(1) or slug).strip(), None))
    return _append_orphans(cat, out)

def _append_orphans(cat, listed):
    """Append any built article not in the category list, so every article gets a consistent number."""
    have = {s for s, _, _ in listed}
    for s in sorted(os.listdir(os.path.join(OUT, cat))):
        if os.path.isdir(os.path.join(OUT, cat, s)) and s not in have:
            listed.append((s, None, None))   # title=None -> use the built head title
    return listed

def get_body(cat, slug):
    cdir = os.path.join(CACHE_ROOT, cat); os.makedirs(cdir, exist_ok=True)
    cpath = os.path.join(cdir, slug + ".html")
    if os.path.exists(cpath):
        return open(cpath, encoding="utf-8").read()
    h = open(os.path.join(OUT, cat, slug, "index.html"), encoding="utf-8").read()
    if "height:1267px" in h:
        raise SystemExit(f"no pristine body cache for {cat}/{slug} and live file is already generated")
    m = re.search(r'<article class="article-body">(.*?)</article>', h, re.S)
    body = m.group(1) if m else ""
    body = re.sub(r'<aside[^>]*>(?:(?!</aside>).)*?(?:git-revision|md-source-file)(?:(?!</aside>).)*?</aside>', '', body, flags=re.S)
    body = re.sub(r'<aside class="md-source-file">.*?</aside>', '', body, flags=re.S)
    open(cpath, "w", encoding="utf-8").write(body)
    return body

def built_meta(cat, slug):
    h = open(os.path.join(OUT, cat, slug, "index.html"), encoding="utf-8").read()
    tt = re.search(r'<h1 class="head__title">(.*?)</h1>', h, re.S)
    gd = re.search(r'git-revision-date-localized-plugin-date"[^>]*>([^<]+)<', h)
    return (tt.group(1).strip() if tt else None), (gd.group(1).strip() if gd else "March 2026")

def lead_sentence(body):
    m = re.search(r'<p>(.*?)</p>', body, re.S)
    if not m:
        return ""
    txt = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    s = re.split(r'(?<=[.!?])\s', txt)[0].strip()
    return (s[:170] + ("…" if len(s) > 170 else ""))

def read_time(body):
    return max(1, round(len(re.sub(r'<[^>]+>', ' ', body).split()) / 200))

total = 0
for cat in BUILD:
    active = TAB[cat]
    items = article_list(cat)
    arts = []
    for i, (slug, title, desc) in enumerate(items):
        body = get_body(cat, slug)
        ti, date = built_meta(cat, slug)
        plain = title or re.sub(r'<[^>]+>', '', ti or slug).strip()   # orphans -> built head title
        arts.append({"slug": slug, "num": i + 1, "title": plain,
                     "desc": desc or lead_sentence(body), "title_inner": ti or plain,
                     "date": date, "body": body})
    n = len(arts)
    T = make_template(active)
    for i, a in enumerate(arts):
        body = re.sub(r'(\.\./)+assets/', '/assets/', a["body"]).replace("https://spineradiology.com/", "/")
        page = T
        page = re.sub(r'(<div class="head__crest">).*?(</div>)',
                      rf'\g<1><span style="color:#8fd4e0">ARTICLE {a["num"]:02d}</span>\g<2>', page, flags=re.S)
        page = re.sub(r'(<h1 class="head__title">).*?(</h1>)', lambda m: m.group(1)+a["title_inner"]+m.group(2), page, flags=re.S)
        page = re.sub(r'(<p class="head__sub">).*?(</p>)', lambda m: m.group(1)+a["desc"]+m.group(2), page, flags=re.S)
        meta = (f'    <div class="head__meta">\n      <span>Section · <b>{active}</b></span>\n'
                f'      <span>Updated · <b>{a["date"]}</b></span>\n'
                f'      <span>Read · <b>~{read_time(body)} min</b></span>\n    </div>')
        page = re.sub(r'    <div class="head__meta">.*?</div>', meta, page, flags=re.S)
        page = re.sub(r'<title>.*?</title>', f'<title>{a["title"]} — Spine Radiology</title>', page, flags=re.S)
        page = re.sub(r'(<article class="article-body">).*?(</article>)', lambda m: m.group(1)+body+m.group(2), page, flags=re.S)

        prev = arts[i-1] if i > 0 else None
        nxt  = arts[i+1] if i < n-1 else None
        prev_a = (f'<a class="prev" href="/{cat}/{prev["slug"]}/">\n      <span>Previous</span>\n      <b>{prev["title"]}</b>\n    </a>'
                  if prev else f'<a class="prev" href="/{cat}/">\n      <span>Section</span>\n      <b>{active}</b>\n    </a>')
        next_a = (f'<a class="next" href="/{cat}/{nxt["slug"]}/">\n      <span>Next article</span>\n      <b>{nxt["title"]}</b>\n    </a>'
                  if nxt else f'<a class="next" href="/{cat}/">\n      <span>Section</span>\n      <b>{active}</b>\n    </a>')
        page = re.sub(r'  <nav class="article-nav">.*?</nav>', f'  <nav class="article-nav">\n    {prev_a}\n    {next_a}\n  </nav>', page, flags=re.S)

        open(os.path.join(OUT, cat, a["slug"], "index.html"), "w", encoding="utf-8").write(page)
    total += n
    print(f"[{cat:26}] {n:2} articles  (active: {active})")
print(f"TOTAL: {total} articles across {len(BUILD)} categories")
