#!/usr/bin/env bash
# Re-snapshot the redesign overlay from the current site/  (run after regenerating/editing pages,
# i.e. after gen_categories.py + gen_articles.py + gen_search.py, so the overlay stays current).
set -euo pipefail
cd "$(dirname "$0")/../site"

# Refuse to freeze a partial overlay: a gen_search failure could leave <230 marked pages.
marked=$(grep -rl 'sr-search-btn' . --include=index.html | wc -l | tr -d ' ')
[ "$marked" -ge 230 ] || { echo "ABORT: only $marked sr-search-btn pages (<230) — overlay would be incomplete; not snapshotting." >&2; exit 3; }

OUT="../redesign/snapshots/redesign-overlay.tar.gz"
LIST="$(mktemp)"; trap 'rm -f "$LIST"' EXIT

# Redesign-owned files: every page carrying the search marker (12 category + 220 article pages)
# plus the loose hand-built files that DON'T carry the marker and so must be listed explicitly:
#   - ./index.html      (landing; has no sr-search-btn)
#   - ./search-index.json
#   - ./spine-regions.html  (hand-built; landing links to it — 404s after restore.sh without it)
# Any future loose redesign page MUST be added here or it is silently dropped from the overlay.
# One path per line (space-safe via tar -T, unlike the old unquoted $(grep) word-split).
{
  grep -rl 'sr-search-btn' . --include=index.html
  echo ./index.html
  echo ./search-index.json
  [ -f ./spine-regions.html ] && echo ./spine-regions.html
  true
} > "$LIST"

tar czf "$OUT.tmp" -T "$LIST"          # build to a temp file…
mv "$OUT.tmp" "$OUT"                    # …then atomic-mv into place (never a half-written overlay)
echo "overlay re-snapshotted: $(tar tzf "$OUT" | wc -l | tr -d ' ') files."
