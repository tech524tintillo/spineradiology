#!/usr/bin/env python3
"""
Fix the bar on Emily's literal category pages and emit them to the real deployed path.
  source: Template design/<cat>.html   ->   site/<cat>/index.html  (URL /<cat>/)
Only Emily's <nav class="subnav"> is swapped for the approved 12-category paginated bar
(active = this category); template-name links become real root-relative paths; entry hrefs
are rewritten to /<cat>/<real-slug>/ (auto-corrected against the actual built article dirs).
Everything else of Emily's category design is untouched. Articles are a separate later step.
"""
import re, os

ROOT = "/Users/light/Downloads/spineradiology"
TD   = "/Users/light/Downloads/Template design"
OUT  = os.path.join(ROOT, "site")

CATEGORIES = [
    {"src": "imaging-modalities.html",  "cat": "imaging-modalities",  "active": "Imaging"},
    {"src": "degenerative-disease.html","cat": "degenerative-disease","active": "Degenerative"},
    {"src": "trauma.html",              "cat": "trauma",              "active": "Trauma"},
    {"src": "neoplasms.html",           "cat": "neoplasms",           "active": "Neoplasms"},
    {"src": "metabolic-systemic.html",  "cat": "metabolic-systemic",  "active": "Metabolic"},
    {"src": "post-surgical-spine.html", "cat": "post-surgical-spine", "active": "Post-Surgical"},
    {"src": "special-topics.html",      "cat": "special-topics",      "active": "Special Topics"},
]

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

CAT_STYLE = """<style>
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

def real_slug(cat, slug, built):
    if slug in built:
        return slug
    st = set(slug.split("-"))
    # built slug whose tokens are all contained in Emily's slug -> most specific (most tokens)
    subset = [b for b in built if set(b.split("-")) <= st]
    if subset:
        return max(subset, key=lambda b: len(b.split("-")))
    # else the built slug sharing the most tokens (need >=2 to avoid coincidental single-word hits)
    best, score = None, 1
    for b in built:
        ov = len(set(b.split("-")) & st)
        if ov > score:
            best, score = b, ov
    return best

for C in CATEGORIES:
    src = os.path.join(TD, C["src"])
    cat, active = C["cat"], C["active"]
    built = set(os.listdir(os.path.join(OUT, cat)))
    h = open(src, encoding="utf-8").read()

    # 1. swap the bar
    h = re.sub(r'(<!--\s*SUBNAV\s*-->\s*)?<nav class="subnav">.*?</nav>',
               '  <!-- SUBNAV -->\n' + subnav_html(active), h, flags=re.S)
    # 2. append the bar's style + script
    if "</body></html>" in h:
        h = h.replace("</body></html>", CAT_STYLE + "\n</body></html>")
    else:
        h = h.replace("</body>", CAT_STYLE + "\n</body>", 1)
    # 3. real links
    h = h.replace("Spine Radiology - Redesign.html", "/")
    h = h.replace("category-template-v2.html", "/anatomy/")
    h = h.replace("article-template-v2.html", "/anatomy/")
    h = h.replace("https://spineradiology.com/", "/")
    # 4. entry hrefs -> /<cat>/<real-slug>/  (auto-correct mismatches)
    fixed, bad = [], []
    def repl(m):
        slug = m.group(1)
        rs = real_slug(cat, slug, built)
        if rs is None:
            bad.append(slug); return m.group(0)
        if rs != slug: fixed.append(f"{slug} -> {rs}")
        return f'<a class="entry" href="/{cat}/{rs}/"'
    h = re.sub(r'<a class="entry" href="([a-z0-9-]+)\.html"', repl, h)

    out = os.path.join(OUT, cat, "index.html")
    open(out, "w", encoding="utf-8").write(h)
    print(f"[{cat}] -> site/{cat}/index.html  (active: {active})")
    if fixed: print("   slug corrections:", "; ".join(fixed))
    if bad:   print("   UNRESOLVED slugs:", bad)
    print("   leftover template-name links:",
          len(re.findall(r'(article-template-v2|category-template-v2|Spine Radiology - Redesign)\.html', h)))
