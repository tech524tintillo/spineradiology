#!/usr/bin/env python3
"""
Restore site search on the Emily-redesigned pages (which dropped Material's search).
1) Build site/search-index.json from every generated article (title, category, url, heading keywords).
2) Inject an on-theme command-palette search (top-right button + ⌘K modal) into every category page
   and article that doesn't already have it. Pure client-side, works on static hosting.
Run after gen_categories.py + gen_articles.py. Idempotent.
"""
import os, re, json

ROOT = "/Users/light/Downloads/spineradiology"
OUT  = os.path.join(ROOT, "site")
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
      <input type="text" class="sr-search-input" placeholder="Search __N__ articles…" autocomplete="off" spellcheck="false" aria-label="Search">
      <kbd>esc</kbd>
    </div>
    <ul class="sr-search-results" role="listbox"></ul>
    <div class="sr-search-empty" hidden>No matching articles</div>
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
</style>'''

SCRIPT = '''<script>
(function(){
  var btn=document.querySelector('.sr-search-btn'),modal=document.querySelector('.sr-search-modal');
  if(!btn||!modal)return;
  var input=modal.querySelector('.sr-search-input'),list=modal.querySelector('.sr-search-results'),
      empty=modal.querySelector('.sr-search-empty'),backdrop=modal.querySelector('.sr-search-backdrop');
  var IDX=null,rows=[],active=-1,terms=[];
  function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function load(){return IDX?Promise.resolve():fetch('/search-index.json').then(function(r){return r.json();}).then(function(d){IDX=d;});}
  function open(){modal.hidden=false;document.documentElement.style.overflow='hidden';
    load().then(function(){input.value='';render('');setTimeout(function(){input.focus();},30);});}
  function close(){modal.hidden=true;document.documentElement.style.overflow='';active=-1;}
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
  function render(q){q=q.trim().toLowerCase();terms=tokens(q);
    if(!q){rows=IDX.slice(0,7);}else{rows=IDX.map(function(it){return[match(it,terms),it];})
      .filter(function(x){return x[0]>0;}).sort(function(a,b){return b[0]-a[0];}).slice(0,12)
      .map(function(x){return x[1];});}
    active=rows.length?0:-1;
    list.innerHTML=rows.map(function(it,i){
      var snip=q?'<span class="sr-search-snip">'+snippet(it,terms)+'</span>':'';
      return '<li class="sr-search-item'+(i===active?' is-active':'')+'" role="option" data-u="'+it.u+'">'+
        '<span class="sr-search-main"><span class="sr-search-t">'+(q?hl(it.t,terms):esc(it.t))+'</span>'+snip+'</span>'+
        '<span class="sr-search-c">'+esc(it.c)+'</span></li>';}).join('');
    empty.hidden=rows.length>0;
    [].forEach.call(list.children,function(li){li.addEventListener('click',function(){go(li.getAttribute('data-u'));});});}
  function go(u){if(u)location.href=u;}
  function move(d){if(!rows.length)return;active=(active+d+rows.length)%rows.length;
    [].forEach.call(list.children,function(li,i){li.classList.toggle('is-active',i===active);
      if(i===active)li.scrollIntoView({block:'nearest'});});}
  btn.addEventListener('click',open);
  backdrop.addEventListener('click',close);
  input.addEventListener('input',function(){render(input.value);});
  input.addEventListener('keydown',function(e){
    if(e.key==='ArrowDown'){e.preventDefault();move(1);}
    else if(e.key==='ArrowUp'){e.preventDefault();move(-1);}
    else if(e.key==='Enter'){e.preventDefault();if(active>=0)go(rows[active].u);}
    else if(e.key==='Escape'){close();}});
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

injected = metaed = 0
for p in pages():
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
    if 'role="main"' not in h:
        h = h.replace('<article class="article-body">', '<article class="article-body" role="main">', 1)
        h = h.replace('<section class="list">', '<section class="list" role="main">', 1)
    h = h.replace('aria-label="Previous">&#8249;</button>',
                  'aria-label="Previous"><span aria-hidden="true">&#8249;</span></button>')
    h = h.replace('aria-label="More">&#8250;</button>',
                  'aria-label="More"><span aria-hidden="true">&#8250;</span></button>')
    # search UI
    if "sr-search-btn" not in h:
        h = re.sub(r'(<a href="/" class="sr-brand">.*?</a>)', r'\1\n' + TRIGGER, h, count=1, flags=re.S)
        ins = MODAL + "\n" + STYLE + "\n" + SCRIPT
        h = h.replace("</body></html>", ins + "\n</body></html>") if "</body></html>" in h \
            else h.replace("</body>", ins + "\n</body>", 1)
        injected += 1
    if h != orig:
        open(p, "w", encoding="utf-8").write(h)

print(f"search-index.json: {N} articles")
print(f"search UI injected: {injected} pages | meta descriptions added: {metaed}")
