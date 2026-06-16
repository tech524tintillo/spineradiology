#!/usr/bin/env bash
# Restore the Emily redesign + search onto site/  (e.g. after `mkdocs build` reverts it to Material).
set -e
cd "$(dirname "$0")/.."
[ -d site ] || { echo "site/ missing — run 'python3 -m mkdocs build' first."; exit 1; }
tar xzf redesign/snapshots/redesign-overlay.tar.gz -C site
echo "redesign restored onto site/ ($(tar tzf redesign/snapshots/redesign-overlay.tar.gz | wc -l | tr -d ' ') files)."
