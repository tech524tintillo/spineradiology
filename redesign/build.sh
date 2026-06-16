#!/usr/bin/env bash
# One-command reproducible build. `mkdocs build` lays down fresh assets + the dir structure (and would
# otherwise wipe the redesign); restore.sh then re-applies Emily's pages + search overlay on top.
# Result: site/ is the deployable redesign. This is the "it's just a mkdocs build" answer.
set -e
cd "$(dirname "$0")/.."
echo "[1/2] mkdocs build…"
python3 -m mkdocs build
echo "[2/2] applying redesign overlay…"
bash redesign/restore.sh
echo "BUILD COMPLETE → site/ = Emily redesign + search, ready to deploy."
