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

## 6. Build / deploy / restore — the redesign is a post-`mkdocs build` overlay
`site/` is gitignored and a `mkdocs build` reverts it to Material. So the redesign is captured two ways:
- **Source:** Emily's templates → `redesign/templates/` (in git), pristine article bodies →
  `redesign/bodies/<cat>/` (in git), generators `gen_categories.py` + `gen_articles.py` + `gen_search.py`.
- **Frozen overlay:** `redesign/snapshots/redesign-overlay.tar.gz` (234 files: 12 category pages +
  220 articles + landing + `search-index.json`) — the exact approved output.

Scripts (in `redesign/`):
- `build.sh`  → `mkdocs build` then `restore.sh`  = one-command deployable `site/`. **This is the
  "just make it a mkdocs build" answer.** Run it after any clobber.
- `restore.sh` → extracts the overlay onto `site/` (instant restore after a `mkdocs build` wipe).
- `snapshot.sh` → re-creates the overlay from the current `site/` (run after regenerating/editing pages).

**Search** (Material's was dropped by the standalone pages): restored as a custom on-theme command
palette (top-right button + `⌘K`/`/`), full-text over all 220 articles via `site/search-index.json`,
with match highlighting + context snippets. Built/injected by `gen_search.py` (idempotent).
TODO before a from-scratch source rebuild: wire anatomy's category into `gen_categories.py`
(currently its page comes from `redesign/her-cat.html`) and set `gen_articles.py` BUILD to all 12 +
`os.makedirs`. Until then, `build.sh`/`restore.sh` (overlay) is the reliable path.

## Status (2026-06-16) — REDESIGN COMPLETE
All **12/12 category pages + 220/220 articles** in Emily's design; **search restored**; 0 number
mismatches, 0 broken links. Backed up via the overlay snapshot + scripts above. NOT yet done: real
deploy (preview→prod), pre-deploy audit, and `spine-regions` (PARKED for real RamSoft MRI).
