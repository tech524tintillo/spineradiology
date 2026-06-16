#!/usr/bin/env bash
# Re-snapshot the redesign overlay from the current site/  (run after regenerating/editing pages,
# i.e. after gen_categories.py + gen_articles.py + gen_search.py, so the overlay stays current).
set -e
cd "$(dirname "$0")/../site"

# Redesign-owned files: every page carrying the search marker (the 12 category pages + 220 articles)
# plus the loose hand-built files that DON'T carry the marker and so must be listed explicitly:
#   - ./index.html      (landing; has no sr-search-btn)
#   - ./search-index.json
#   - ./spine-regions.html  (hand-built; landing links to it — without this it 404s after restore.sh)
# Any future loose redesign page MUST be added here or it is silently dropped from the overlay.
FILES=( $(grep -rl 'sr-search-btn' . --include=index.html) ./index.html ./search-index.json )
[ -f ./spine-regions.html ] && FILES+=( ./spine-regions.html )

tar czf ../redesign/snapshots/redesign-overlay.tar.gz "${FILES[@]}"
echo "overlay re-snapshotted: $(tar tzf ../redesign/snapshots/redesign-overlay.tar.gz | wc -l | tr -d ' ') files."
