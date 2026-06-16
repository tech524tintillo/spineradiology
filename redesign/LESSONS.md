# SpineRadiology redesign — lessons (2026-06-16)

Hard-won today. Read before touching the redesign again.

## 1. Use Emily's LITERAL HTML. Never rebuild her design.
Emily's templates in `~/Downloads/Template design/` ARE the design. Copy the literal file and
change ONLY: the subnav, per-article head (crest/title/sub/meta), the body content, prev/next.
Do NOT reproduce her components in MkDocs/overrides — every recreation came out subtly worse and
got rejected. Do NOT change fonts, sizing, colors, table styling. The generators already do this;
keep it that way.

## 2. Match the REAL deployed layout + link to REAL slugs.
- Output to the live URL structure: category → `site/<cat>/index.html` (`/<cat>/`),
  article → `site/<cat>/<slug>/index.html` (`/<cat>/<slug>/`).
- All links root-relative real paths: `/`, `/anatomy/`, `/<cat>/<slug>/`, `/imaging-modalities/`…
  so preview paths == deploy paths == file paths.
- Emily's template filenames are NOT the real article slugs. Link to the actual built dir slug.
  e.g. Emily wrote `vacuum-disc-phenomenon` but the real article is `vacuum-disc`;
  `article-template-v2.html` was the placeholder for `vertebral-column-overview`.
  Kill `Spine Radiology - Redesign.html`, `category-template-v2.html`, `article-template-v2.html`.

## 3. The preview server MUST be threaded + no-cache.
- Single-threaded `socketserver.TCPServer` → keep-alive connections block it → `ERR_CONNECTION_TIMED_OUT`.
  Use `http.server.ThreadingHTTPServer`. (`python -m http.server` is already threaded.)
- Standalone HTML has no cache-busting, so the browser serves STALE pages after a rebuild.
  Serve with `Cache-Control: no-store`. Script: `/tmp/nocache_server.py` (chdir to `site/`, port 8765).
- **When the user says the output "looks different/wrong" but the files are byte-identical: suspect
  browser cache FIRST.** Don't re-compare and re-tweak — that wasted a lot of trust today. Verify the
  served bytes (curl/MCP browser with ignoreCache), then fix the real cause (cache, not the file).

## 4. The pipeline (all re-runnable, idempotent)
- `redesign/gen_categories.py` — swaps the bar onto Emily's category files → `site/<cat>/index.html`.
- `redesign/gen_articles.py` — Emily article template + real body → `site/<cat>/<slug>/index.html`.
  `BUILD` list selects categories. Bodies cached to `redesign/bodies/<cat>/` (pristine MkDocs build).
- The approved subnav: 12-category bar, two discrete pages (Home+5, then the rest), squared chevrons,
  full-width `flex:1` tabs, no dangling divider on the last page-1 tab. Article-only: cap
  `.page::after{height:1267px}` so Emily's %-positioned starfield dots cluster at the header
  (tall pages spread them invisibly thin).

## 5. Don't over-engineer or over-explain.
The user reviews category-by-category and wants the literal file + the one change asked, nothing more.
Verify in the browser before sending. State the real cause once; don't litigate it.

## Status (2026-06-16)
Done in Emily's design: **anatomy** (25 articles), **imaging-modalities** (15), **degenerative-disease** (31).
Blocked: the other 9 categories' CATEGORY pages need Emily's filled files (she's provided 3 of 12).
Their ARTICLES can be generated now from the MkDocs build (article template is generic/approved).
