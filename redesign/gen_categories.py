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
    {"src": "infection.html",           "cat": "infection",           "active": "Infection"},
    {"src": "inflammatory-autoimmune.html", "cat": "inflammatory-autoimmune", "active": "Inflammatory"},
    {"src": "congenital-developmental.html","cat": "congenital-developmental","active": "Congenital"},
    {"src": "vascular.html",            "cat": "vascular",            "active": "Vascular"},
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

# optional explicit overrides for slugs the heuristic can't resolve unambiguously: ("cat","emily")->built
SLUG_OVERRIDES = {}

class AmbiguousSlug(SystemExit):
    pass

def real_slug(cat, slug, built):
    """Map an Emily entry slug to the real built dir slug. Deterministic + self-checking:
    iterate `built` in sorted order so any tie is reproducible, and FAIL LOUDLY on an ambiguous
    (non-unique best-score) correction instead of silently picking whichever os.listdir() yielded.
    Resolve ambiguity via SLUG_OVERRIDES or by adding the correct entry to Emily's source."""
    if slug in built:
        return slug
    if (cat, slug) in SLUG_OVERRIDES:
        return SLUG_OVERRIDES[(cat, slug)]
    bsorted = sorted(built)                          # deterministic tie order
    stset = set(slug.split("-"))
    # (1) built slug whose tokens are all contained in Emily's slug -> most specific (most tokens).
    #     Emily's slugs are intentionally more verbose than the built dir (she writes
    #     'vacuum-disc-phenomenon' for the real 'vacuum-disc'), so the subset branch legitimately
    #     strips her extra descriptive tokens. We DON'T force the chosen slug to keep her longest
    #     token (that wrongly rejects the real corrections); we only guard against a NON-UNIQUE
    #     best, which is the actual order/tie-dependent defect.
    subset = [b for b in bsorted if set(b.split("-")) <= stset]
    if subset:
        best_n = max(len(b.split("-")) for b in subset)
        winners = [b for b in subset if len(b.split("-")) == best_n]
        if len(winners) > 1:
            raise AmbiguousSlug(
                f"CORRECTION-AMBIGUOUS (subset, {best_n} tokens) for {cat}/{slug}: candidates "
                f"{winners}; add SLUG_OVERRIDES[('{cat}','{slug}')] or fix Emily's source.")
        return winners[0]
    # (2) else the built slug sharing the most tokens (need >=2 to avoid coincidental single-word hits)
    scored = sorted(((len(set(b.split("-")) & stset), b) for b in bsorted),
                    key=lambda x: (-x[0], x[1]))
    best_score = scored[0][0] if scored else 0
    if best_score <= 1:
        return None
    top = [b for s, b in scored if s == best_score]
    if len(top) > 1:
        raise AmbiguousSlug(
            f"CORRECTION-AMBIGUOUS (overlap={best_score}) for {cat}/{slug}: candidates {top}; "
            f"add a SLUG_OVERRIDES[('{cat}','{slug}')] entry or fix Emily's source.")
    return top[0]

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
    fixed, bad, resolved = [], [], {}
    def repl(m):
        slug = m.group(1)
        rs = real_slug(cat, slug, built)
        if rs is None:
            bad.append(slug); return m.group(0)
        if rs != slug: fixed.append(f"{slug} -> {rs}")
        resolved.setdefault(rs, []).append(slug)   # detect many-to-one collapse
        return f'<a class="entry" href="/{cat}/{rs}/"'
    h = re.sub(r'<a class="entry" href="([a-z0-9-]+)\.html"', repl, h)

    # post-build assertions: no two Emily entries collapsed onto one built slug (would drop an
    # article), and every emitted /<cat>/<slug>/ href maps to a real built dir.
    collapsed = {rs: ss for rs, ss in resolved.items() if len(ss) > 1}
    if collapsed:
        raise SystemExit(f"[{cat}] MANY-TO-ONE slug collapse (an article would be dropped): {collapsed}")
    for rs in resolved:
        if not os.path.isdir(os.path.join(OUT, cat, rs)):
            raise SystemExit(f"[{cat}] emitted href /{cat}/{rs}/ has no built directory")

    out = os.path.join(OUT, cat, "index.html")
    open(out, "w", encoding="utf-8").write(h)
    print(f"[{cat}] -> site/{cat}/index.html  (active: {active})")
    if fixed: print("   slug corrections:", "; ".join(fixed))
    if bad:   print("   UNRESOLVED slugs:", bad)
    print("   leftover template-name links:",
          len(re.findall(r'(article-template-v2|category-template-v2|Spine Radiology - Redesign)\.html', h)))
