#!/usr/bin/env python3
"""
Restore site search on the Emily-redesigned pages (which dropped Material's search).
1) Build site/search-index.json from every generated article (title, category, url, heading keywords).
2) Inject an on-theme command-palette search (top-right button + ⌘K modal) into every category page
   and article that doesn't already have it. Pure client-side, works on static hosting.
Run after gen_categories.py + gen_articles.py. Idempotent.
"""
import os, re, json
try:
    from PIL import Image
except Exception:
    Image = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # repo root (this file is in redesign/)
OUT  = os.path.join(ROOT, "site")

# cache of intrinsic (w,h) per asset path so we don't re-open an image once per page that uses it
_DIM_CACHE = {}
def intrinsic_dims(src):
    """Return (w,h) for a root-relative /assets/... img src, or None if unreadable."""
    if Image is None or not src.startswith("/"):
        return None
    if src in _DIM_CACHE:
        return _DIM_CACHE[src]
    fp = os.path.join(OUT, src.lstrip("/"))
    dims = None
    try:
        with Image.open(fp) as im:
            dims = im.size
    except Exception:
        dims = None
    _DIM_CACHE[src] = dims
    return dims

def add_img_heights(html):
    """CLS fix: body <img> tags carry width= but no height=, so the browser reserves 0px until
    decode and then reflows. Derive height= from each image's intrinsic aspect ratio and the
    authored width=. Rendered size is unchanged (max-width:100%;height:auto still scales it);
    only the pre-decode placeholder box changes. Design-neutral."""
    n = [0]
    def repl(m):
        tag = m.group(0)
        if re.search(r'\bheight\s*=', tag):
            return tag
        wm = re.search(r'\bwidth="(\d+)"', tag)
        sm = re.search(r'\bsrc="([^"]+)"', tag)
        if not wm or not sm:
            return tag
        dims = intrinsic_dims(sm.group(1))
        if not dims:
            return tag
        iw, ih = dims
        if not iw:
            return tag
        w = int(wm.group(1))
        h = round(w * ih / iw)
        n[0] += 1
        return tag[:-1].rstrip() + f' height="{h}">' if tag.endswith(">") else tag
    out = re.sub(r'<img\b[^>]*>', repl, html)
    return out, n[0]
CATS = ["anatomy","imaging-modalities","degenerative-disease","trauma","neoplasms","infection",
        "inflammatory-autoimmune","congenital-developmental","vascular","metabolic-systemic",
        "post-surgical-spine","special-topics"]
LABEL = {"anatomy":"Anatomy","imaging-modalities":"Imaging","degenerative-disease":"Degenerative",
         "trauma":"Trauma","neoplasms":"Neoplasms","infection":"Infection",
         "inflammatory-autoimmune":"Inflammatory","congenital-developmental":"Congenital",
         "vascular":"Vascular","metabolic-systemic":"Metabolic",
         "post-surgical-spine":"Post-Surgical","special-topics":"Special Topics"}

def text(s):
    s = re.sub(r'<[^>]+>', ' ', s).replace('¶', ' ')
    return re.sub(r'\s+', ' ', s).strip()

# ---- 1. build the index ----
index = []
for cat in CATS:
    for slug in sorted(os.listdir(os.path.join(OUT, cat))):
        p = os.path.join(OUT, cat, slug, "index.html")
        if not os.path.isdir(os.path.join(OUT, cat, slug)) or not os.path.exists(p):
            continue
        h = open(p, encoding="utf-8").read()
        if "height:1267px" not in h:   # only Emily-generated articles
            continue
        tt = re.search(r'<h1 class="head__title">(.*?)</h1>', h, re.S)
        title = text(tt.group(1)) if tt else slug
        bm = re.search(r'<article class="article-body">(.*?)</article>', h, re.S)
        btext = text(bm.group(1)) if bm else ""        # full-text body (like Material's index)
        index.append({"t": title, "c": LABEL[cat], "u": f"/{cat}/{slug}/", "k": btext[:3000]})
json.dump(index, open(os.path.join(OUT, "search-index.json"), "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))
N = len(index)

# ---- 2. the search component (on-theme: deep teal, Source Serif titles, Manrope meta) ----
TRIGGER = '''  <button class="sr-search-btn" type="button" aria-label="Search articles">
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.6"/><path d="m20 20-3.2-3.2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
    <span>Search</span><kbd>⌘K</kbd>
  </button>'''

MODAL = '''<div class="sr-search-modal" hidden>
  <div class="sr-search-backdrop"></div>
  <div class="sr-search-panel" role="dialog" aria-modal="true" aria-label="Search articles">
    <div class="sr-search-field">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.6"/><path d="m20 20-3.2-3.2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
      <input type="text" class="sr-search-input" id="sr-search-input" role="combobox" aria-expanded="false" aria-controls="sr-search-results" aria-autocomplete="list" placeholder="Search __N__ articles…" autocomplete="off" spellcheck="false" aria-label="Search">
      <kbd>esc</kbd>
    </div>
    <ul class="sr-search-results" id="sr-search-results" role="listbox" aria-label="Search results"></ul>
    <div class="sr-search-empty" hidden>No matching articles</div>
    <div class="sr-search-status sr-visually-hidden" role="status" aria-live="polite"></div>
    <div class="sr-search-hint"><span><kbd>↑↓</kbd> navigate</span><span><kbd>↵</kbd> open</span><span><kbd>esc</kbd> close</span></div>
  </div>
</div>'''.replace("__N__", str(N))

STYLE = '''<style>
.sr-search-btn{position:absolute;top:18px;right:24px;z-index:21;display:flex;align-items:center;gap:.5rem;
  padding:.4rem .65rem;border:1px solid rgba(143,212,224,.28);border-radius:8px;background:rgba(6,26,38,.6);
  color:#9fb4c6;font-family:'Manrope',system-ui,sans-serif;font-size:.78rem;cursor:pointer;transition:.2s;backdrop-filter:blur(4px)}
.sr-search-btn:hover{border-color:#5fb6cc;color:#e8f1f7;background:rgba(16,58,82,.5)}
.sr-search-btn svg{width:15px;height:15px;color:#5fb6cc}
.sr-search-btn kbd{font-family:inherit;font-size:.68rem;padding:.1rem .35rem;border:1px solid rgba(143,212,224,.3);border-radius:4px;color:#8fd4e0;background:rgba(143,212,224,.08)}
@media(max-width:880px){.sr-search-btn{top:14px;right:14px;padding:.4rem}.sr-search-btn span,.sr-search-btn kbd{display:none}}
.sr-search-modal[hidden]{display:none}
.sr-search-modal{position:fixed;inset:0;z-index:120;display:flex;align-items:flex-start;justify-content:center}
.sr-search-backdrop{position:absolute;inset:0;background:rgba(2,10,16,.72);backdrop-filter:blur(3px);animation:srsFade .2s ease}
.sr-search-panel{position:relative;margin-top:11vh;width:min(620px,92vw);max-height:72vh;display:flex;flex-direction:column;
  background:linear-gradient(180deg,#0c2a3b,#081f2d);border:1px solid rgba(143,212,224,.22);border-radius:14px;overflow:hidden;
  box-shadow:0 0 0 1px rgba(143,212,224,.12),0 30px 80px -20px rgba(0,0,0,.8);animation:srsRise .22s cubic-bezier(.2,.8,.2,1)}
@keyframes srsFade{from{opacity:0}} @keyframes srsRise{from{opacity:0;transform:translateY(-10px)}}
.sr-search-field{display:flex;align-items:center;gap:.7rem;padding:1.05rem 1.2rem;border-bottom:1px solid rgba(231,238,247,.1)}
.sr-search-field svg{width:19px;height:19px;color:#5fb6cc;flex-shrink:0}
.sr-search-input{flex:1;background:none;border:none;outline:none;color:#e7eef7;font-family:'Manrope',system-ui,sans-serif;font-size:1.05rem}
.sr-search-input::placeholder{color:#6b7d92}
.sr-search-field kbd{font-family:'Manrope',sans-serif;font-size:.66rem;padding:.15rem .4rem;border:1px solid rgba(231,238,247,.18);border-radius:4px;color:#7d8ca4}
.sr-search-results{list-style:none;margin:0;padding:.4rem;overflow-y:auto}
.sr-search-item{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;padding:.6rem .85rem;border-radius:9px;cursor:pointer}
.sr-search-item.is-active,.sr-search-item:hover{background:rgba(95,182,204,.13)}
.sr-search-main{min-width:0;display:flex;flex-direction:column;gap:.18rem}
.sr-search-t{font-family:'Source Serif 4',Georgia,serif;font-size:1rem;color:#e7eef7;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sr-search-item.is-active .sr-search-t{color:#8fd4e0}
.sr-search-snip{font-family:'Manrope',sans-serif;font-size:.77rem;line-height:1.4;color:#7d8ca4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sr-search-c{flex-shrink:0;margin-top:.15rem;font-family:'Manrope',sans-serif;font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;
  color:#8fd4e0;padding:.2rem .5rem;border:1px solid rgba(143,212,224,.25);border-radius:20px}
mark.sr-hl{background:rgba(143,212,224,.22);color:#bfe6ee;border-radius:2px;padding:0 .05em}
.sr-search-empty{padding:1.6rem;text-align:center;color:#7d8ca4;font-family:'Manrope',sans-serif;font-size:.9rem}
.sr-search-hint{display:flex;gap:1.2rem;justify-content:flex-end;padding:.6rem 1.2rem;border-top:1px solid rgba(231,238,247,.08);
  font-family:'Manrope',sans-serif;font-size:.66rem;color:#6b7d92}
.sr-search-hint kbd{padding:.05rem .3rem;border:1px solid rgba(231,238,247,.16);border-radius:3px;color:#9fb4c6}
.sr-visually-hidden{position:absolute!important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
</style>'''

SCRIPT = '''<script>
(function(){
  var btn=document.querySelector('.sr-search-btn'),modal=document.querySelector('.sr-search-modal');
  if(!btn||!modal)return;
  var input=modal.querySelector('.sr-search-input'),list=modal.querySelector('.sr-search-results'),
      empty=modal.querySelector('.sr-search-empty'),backdrop=modal.querySelector('.sr-search-backdrop'),
      panel=modal.querySelector('.sr-search-panel'),status=modal.querySelector('.sr-search-status');
  var IDX=null,rows=[],active=-1,terms=[],opener=null;
  function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function load(){return IDX?Promise.resolve():fetch('/search-index.json').then(function(r){return r.json();}).then(function(d){IDX=d;});}
  function open(){opener=document.activeElement;modal.hidden=false;document.documentElement.style.overflow='hidden';
    input.setAttribute('aria-expanded','true');
    load().then(function(){input.value='';render('');setTimeout(function(){input.focus();},30);});}
  function close(){modal.hidden=true;document.documentElement.style.overflow='';active=-1;
    input.setAttribute('aria-expanded','false');input.removeAttribute('aria-activedescendant');
    var t=opener||btn;opener=null;if(t&&t.focus)try{t.focus();}catch(e){btn.focus();}}
  function tokens(q){return q.split(/\\s+/).filter(Boolean);}
  function match(it,tk){var hay=(it.t+' '+it.c+' '+(it.k||'')).toLowerCase(),tl=it.t.toLowerCase(),q=tk.join(' ');
    if(tl===q)return 500;if(tl.indexOf(q)===0)return 320;if(tl.indexOf(q)>0)return 220;
    var s=0,i;for(i=0;i<tk.length;i++){if(tl.indexOf(tk[i])>=0)s+=30;else if(hay.indexOf(tk[i])>=0)s+=8;else return 0;}
    return s;}
  function hl(str,tk){var out=esc(str);tk.forEach(function(t){if(!t)return;
    var re=new RegExp('('+t.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')+')','ig');
    out=out.replace(re,'<mark class="sr-hl">$1</mark>');});return out;}
  function snippet(it,tk){var body=it.k||'';if(!body)return '';var lo=body.toLowerCase(),pos=-1,i,p;
    for(i=0;i<tk.length;i++){p=lo.indexOf(tk[i]);if(p>=0&&(pos<0||p<pos))pos=p;}
    if(pos<0)return esc(body.slice(0,90))+'…';
    var st=Math.max(0,pos-40);return (st>0?'…':'')+hl(body.slice(st,st+120),tk)+'…';}
  function announce(q){if(!status)return;
    status.textContent=rows.length?(rows.length+' result'+(rows.length===1?'':'s')+(q?' for '+q:''))
      :(q?'No matching articles':'');}
  function syncActiveDesc(){var li=active>=0?list.children[active]:null;
    if(li)input.setAttribute('aria-activedescendant',li.id);else input.removeAttribute('aria-activedescendant');}
  function render(q){q=q.trim().toLowerCase();terms=tokens(q);
    if(!q){rows=IDX.slice(0,7);}else{rows=IDX.map(function(it){return[match(it,terms),it];})
      .filter(function(x){return x[0]>0;}).sort(function(a,b){return b[0]-a[0];}).slice(0,12)
      .map(function(x){return x[1];});}
    active=rows.length?0:-1;
    list.innerHTML=rows.map(function(it,i){
      var snip=q?'<span class="sr-search-snip">'+snippet(it,terms)+'</span>':'';
      return '<li class="sr-search-item'+(i===active?' is-active':'')+'" id="sr-opt-'+i+'" role="option" aria-selected="'+(i===active?'true':'false')+'" data-u="'+it.u+'">'+
        '<span class="sr-search-main"><span class="sr-search-t">'+(q?hl(it.t,terms):esc(it.t))+'</span>'+snip+'</span>'+
        '<span class="sr-search-c">'+esc(it.c)+'</span></li>';}).join('');
    empty.hidden=rows.length>0;
    syncActiveDesc();announce(q);
    [].forEach.call(list.children,function(li){li.addEventListener('click',function(){go(li.getAttribute('data-u'));});});}
  function go(u){if(u)location.href=u;}
  function move(d){if(!rows.length)return;active=(active+d+rows.length)%rows.length;
    [].forEach.call(list.children,function(li,i){var on=i===active;li.classList.toggle('is-active',on);
      li.setAttribute('aria-selected',on?'true':'false');if(on)li.scrollIntoView({block:'nearest'});});
    syncActiveDesc();}
  btn.addEventListener('click',open);
  backdrop.addEventListener('click',close);
  input.addEventListener('input',function(){render(input.value);});
  input.addEventListener('keydown',function(e){
    if(e.key==='ArrowDown'){e.preventDefault();move(1);}
    else if(e.key==='ArrowUp'){e.preventDefault();move(-1);}
    else if(e.key==='Enter'){e.preventDefault();if(active>=0)go(rows[active].u);}
    else if(e.key==='Escape'){close();}});
  // focus trap: the only focusable control in the dialog is the input; keep Tab inside
  panel.addEventListener('keydown',function(e){if(e.key==='Tab'){e.preventDefault();input.focus();}});
  document.addEventListener('keydown',function(e){
    var t=(e.target.tagName||'').toLowerCase(),typing=t==='input'||t==='textarea'||e.target.isContentEditable;
    if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();modal.hidden?open():close();}
    else if(e.key==='/'&&!typing&&modal.hidden){e.preventDefault();open();}
    else if(e.key==='Escape'&&!modal.hidden){close();}});
})();
</script>'''

# ---- 3. inject into every category page + article ----
def pages():
    for cat in CATS:
        yield os.path.join(OUT, cat, "index.html")
        for slug in os.listdir(os.path.join(OUT, cat)):
            p = os.path.join(OUT, cat, slug, "index.html")
            if os.path.isdir(os.path.join(OUT, cat, slug)) and os.path.exists(p):
                yield p

def root_relative_body_links(html, cat):
    """LESSONS rule #2: all links root-relative. Article bodies still carry Emily's MkDocs
    relative cross-links (../slug/ = same category, ../../cat/slug/ = cross category). Resolve
    each against this page's /<cat>/<slug>/ base and emit /<resolved>/ so preview==deploy==file
    paths. Identical destination + anchor text -> design-neutral. Only href values change."""
    n = [0]
    def repl(m):
        href = m.group(1)
        if href.startswith("../../"):
            r = "/" + href[6:]          # cross-category -> /<cat>/<slug>/
        elif href.startswith("../"):
            r = "/" + cat + "/" + href[3:]   # same-category -> /<cat>/<slug>/
        else:
            return m.group(0)
        n[0] += 1
        return f'href="{r}"'
    out = re.sub(r'href="((?:\.\./)+[a-z0-9/-]*/)"', repl, html)
    return out, n[0]

injected = metaed = tweaked = imgsized = reemitted = linksfixed = headed = 0
for p in pages():
    cat = os.path.relpath(p, OUT).split(os.sep)[0]   # site/<cat>/... -> <cat>
    h = open(p, encoding="utf-8").read()
    orig = h
    # per-page <meta description> from the head subtitle (the standalone pages had none -> SEO gap)
    if '<meta name="description"' not in h:
        m = re.search(r'<p class="head__sub">(.*?)</p>', h, re.S)
        d = text(m.group(1)).replace('"', "'")[:185] if m else ""
        if d:
            h = h.replace("</title>", '</title>\n<meta name="description" content="' + d + '">', 1)
            metaed += 1
    # a11y: main landmark + accessible chevrons (Lighthouse nits)
    # Article pages have no native <main>, so role="main" on <article> supplies the landmark.
    # Category pages DO have a native <main> wrapper; tagging the inner <section> too would create
    # a second main landmark (one-main-per-page violation) and push the substantive <aside> out of
    # the main landmark — so we rely on the native <main> there and leave the section untagged.
    if 'role="main"' not in h and '<main' not in h:
        h = h.replace('<article class="article-body">', '<article class="article-body" role="main">', 1)
    h = h.replace('aria-label="Previous">&#8249;</button>',
                  'aria-label="Previous"><span aria-hidden="true">&#8249;</span></button>')
    h = h.replace('aria-label="More">&#8250;</button>',
                  'aria-label="More"><span aria-hidden="true">&#8250;</span></button>')
    # a11y: the leftover edit-mode "tweaks" panel ships aria-hidden="true" but its <button>s stay in
    # the tab order (it is hidden only via opacity/pointer-events, not display:none) — axe
    # aria-hidden-focus. Add `inert` so the closed panel leaves the tab + a11y tree. inert has no
    # visual effect (panel is already opacity:0); the edit-mode host can clear it if it ever opens.
    if '<div class="tweaks" id="tweaks" aria-hidden="true">' in h:
        h = h.replace('<div class="tweaks" id="tweaks" aria-hidden="true">',
                      '<div class="tweaks" id="tweaks" aria-hidden="true" inert>', 1)
        tweaked += 1
    # CLS: give body <img> tags an intrinsic-ratio height= so the browser reserves the box pre-decode
    h, _nh = add_img_heights(h)
    imgsized += _nh
    # links: canonicalize article-body cross-links from relative (../slug/, ../../cat/slug/) to
    # root-relative /<cat>/<slug>/ (LESSONS rule #2). Same destination, just a non-brittle path.
    h, _nl = root_relative_body_links(h, cat)
    linksfixed += _nl
    # a11y: sidebar section titles are styled <div class="aside__label"> (no heading semantics, so
    # SR heading-nav skips them). Promote to <h2> keeping the class -> visuals identical (the class
    # drives all styling), structure now programmatic. h2 sits beside the page's other h2s.
    h, _nhd = re.subn(r'<div class="aside__label">([^<]*)</div>',
                      r'<h2 class="aside__label">\1</h2>', h)
    headed += _nhd
    # a11y: pagination chevrons had vague aria-labels ("Previous"/"More"). Make them explicit.
    h = h.replace('class="subnav-chev subnav-chev--prev" type="button" aria-label="Previous">',
                  'class="subnav-chev subnav-chev--prev" type="button" aria-label="Show previous categories">')
    h = h.replace('class="subnav-chev subnav-chev--next" type="button" aria-label="More">',
                  'class="subnav-chev subnav-chev--next" type="button" aria-label="Show more categories">')
    # search UI
    ins = MODAL + "\n" + STYLE + "\n" + SCRIPT
    if "sr-search-btn" not in h:
        # first injection: add the trigger button + append the modal/style/script block
        h = re.sub(r'(<a href="/" class="sr-brand">.*?</a>)', r'\1\n' + TRIGGER, h, count=1, flags=re.S)
        h = h.replace("</body></html>", ins + "\n</body></html>") if "</body></html>" in h \
            else h.replace("</body>", ins + "\n</body>", 1)
        injected += 1
    else:
        # already injected on a prior run: RE-EMIT the modal/style/script block so JS/ARIA fixes
        # reach pages built before this version (the old block is the last thing before </body>).
        # The trigger button HTML is unchanged, so only the appended block is replaced.
        new_h, n = re.subn(
            r'<div class="sr-search-modal" hidden>.*?</script>(?=\s*</body>)',
            lambda m: ins, h, count=1, flags=re.S)
        if n:
            h = new_h
            reemitted += 1
    if h != orig:
        open(p, "w", encoding="utf-8").write(h)

print(f"search-index.json: {N} articles")
print(f"search UI injected: {injected} pages | re-emitted (ARIA/focus refresh): {reemitted} | meta descriptions added: {metaed}")
print(f"tweaks panels made inert: {tweaked} | body images given height: {imgsized}")
print(f"body cross-links made root-relative: {linksfixed} | aside labels promoted to h2: {headed}")
