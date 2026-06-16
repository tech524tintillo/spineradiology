#!/usr/bin/env bash
# Re-snapshot the redesign overlay from the current site/  (run after regenerating/editing pages,
# i.e. after gen_categories.py + gen_articles.py + gen_search.py, so the overlay stays current).
set -e
cd "$(dirname "$0")/../site"
tar czf ../redesign/snapshots/redesign-overlay.tar.gz \
  $(grep -rl 'sr-search-btn' . --include=index.html) ./index.html ./search-index.json
echo "overlay re-snapshotted: $(tar tzf ../redesign/snapshots/redesign-overlay.tar.gz | wc -l | tr -d ' ') files."
