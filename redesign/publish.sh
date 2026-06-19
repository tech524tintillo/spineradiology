#!/usr/bin/env bash
# =============================================================================
# publish.sh — reliable PUBLISH for a SpineRadiology editor edit.
#
# The hidden /admin editor can ONLY edit the BODY of an EXISTING article
# (it lists existing docs/<cat>/<slug>.md, edits text, commits the same path —
# no create/delete/rename). So publishing is a SURGICAL BODY-SPLICE:
#
#   1. regenerate the edited article through the real pipeline to get its
#      fully-TREATED body (mkdocs render + gen_search's link-canonicalization,
#      CLS image heights, aside handling),
#   2. restore the APPROVED redesign overlay over site/ (every page exactly as
#      shipped — approved chrome, dates, meta, numbering, nav),
#   3. splice ONLY the new <article class="article-body"> into the edited
#      article's approved page,
#   4. a hard DIFF-GATE (sha256/cmp) proves NOTHING but the edited article(s)
#      changed — else ABORT before any deploy,
#   5. deploy, then re-freeze the overlay tarball so future build.sh stays
#      consistent.
#
# Why not "just regenerate everything": a full regen drifts ~180 approved pages
# (git-revision "Updated" dates March 2026 -> real dates, + minor chrome) and
# hits gen_search/get_body idempotency landmines. The body-splice takes the
# body from the regen and EVERYTHING ELSE from the approved page, so it is
# immune to date drift, anatomy-ordering, and the get_body abort. See
# redesign/LESSONS and kevin-ops L-235/L-236.
#
# Usage:
#   redesign/publish.sh                  # changed docs = the merge commit (git diff HEAD^ HEAD)
#   redesign/publish.sh --files a.md ...  # explicit list (paths under docs/)
#   redesign/publish.sh --dry-run [...]   # do everything EXCEPT wrangler deploy + overlay re-freeze
#
# Requires: python3 with mkdocs + mkdocs-material + git-revision-date-localized
# plugin + Pillow; a full (non-shallow) clone; wrangler authenticated; the doc
# edit COMMITTED on the current branch.
# =============================================================================
set -euo pipefail

ROOT="/Users/light/Downloads/spineradiology"   # generators hard-code this path
cd "$ROOT"
SITE="$ROOT/site"
OVERLAY="$ROOT/redesign/snapshots/redesign-overlay.tar.gz"
BODIES="$ROOT/redesign/bodies"
PYBIN="${PUBLISH_PY:-python3}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

DRYRUN=0
if [ "${1:-}" = "--dry-run" ]; then DRYRUN=1; shift; fi

say(){ printf '\033[36m[publish]\033[0m %s\n' "$*"; }
die(){ printf '\033[31m[publish ABORT]\033[0m %s\n' "$*" >&2; exit "${2:-1}"; }

# -- 0. preflight --------------------------------------------------------------
"$PYBIN" -c "import mkdocs, mkdocs_git_revision_date_localized_plugin, PIL" 2>/dev/null \
  || die "python env missing mkdocs / git-revision-date-localized plugin / Pillow (set PUBLISH_PY)" 1
[ -f "$OVERLAY" ] || die "approved overlay tarball missing: $OVERLAY" 1
[ -f "$ROOT/.git/shallow" ] && die "shallow clone — git 'Updated' dates would be wrong; use a full clone" 1
# The diff-gate's baseline is the COMMITTED overlay; refuse to run on a dirty one.
git diff --quiet -- "$OVERLAY" 2>/dev/null || die "overlay tarball has uncommitted changes — commit or 'git checkout' it first" 1

# -- 1. resolve changed docs ---------------------------------------------------
CHANGED=()
if [ "${1:-}" = "--files" ]; then
  shift; CHANGED=("$@")
else
  while IFS= read -r line; do [ -n "$line" ] && CHANGED+=("$line"); done \
    < <(git diff --name-only HEAD^ HEAD -- 'docs/*/*.md' 2>/dev/null || true)
fi
[ "${#CHANGED[@]}" -gt 0 ] || { say "no docs/<cat>/<slug>.md changes vs HEAD^ — nothing to publish."; exit 0; }

# -- 2. baseline: extract the approved overlay --------------------------------
mkdir -p "$TMP/approved"; tar xzf "$OVERLAY" -C "$TMP/approved"

# -- 3. classify: every change MUST be a body edit of an EXISTING article -----
#       (the editor cannot add/delete/rename; if we ever see one, REFUSE rather
#        than silently mis-number a category / drop a search entry.)
SLUGS=()        # "<cat>/<slug>"
for f in "${CHANGED[@]}"; do
  rel="${f#docs/}"; cat="${rel%%/*}"; slug="$(basename "${rel%.md}")"
  [ "$slug" = "index" ] && die "$f is a category index — not editable via markdown (sourced from Emily's template)" 2
  printf '%s' "$slug" | grep -qE '^[a-z0-9-]+$' || die "slug '$slug' is not [a-z0-9-]+ — rename before publishing" 2
  [ -f "$TMP/approved/$cat/$slug/index.html" ] \
    || die "$cat/$slug is NEW (absent from approved overlay). Surgical publish = body edits only; an add needs a full rebuild + re-baseline." 2
  [ -f "$f" ] || die "$f was deleted. Surgical publish = body edits only; a delete needs a full rebuild + re-baseline." 2
  SLUGS+=("$cat/$slug")
done
say "body edit(s) to publish:"; for cs in "${SLUGS[@]}"; do say "    $cs"; done

# -- 4. clean regen to obtain each edited article's TREATED body --------------
#       (clean site/ + bodies-cache bust = idempotent; avoids the get_body
#        'live file already generated' abort and the stale-cache republish.)
say "clean build + treat (mkdocs -> gen_categories -> gen_articles -> gen_search)…"
rm -rf "$SITE"
for cs in "${SLUGS[@]}"; do rm -f "$BODIES/$cs.html"; done
"$PYBIN" -m mkdocs build >/dev/null
cp "$ROOT/redesign/her-cat.html" "$SITE/anatomy/index.html"      # anatomy cat page (gen_categories omits it)
"$PYBIN" "$ROOT/redesign/gen_categories.py" >/dev/null
"$PYBIN" "$ROOT/redesign/gen_articles.py"  >/dev/null
cp "$ROOT/redesign/landing.html"       "$SITE/index.html"
[ -f "$ROOT/redesign/spine-regions.html" ] && cp "$ROOT/redesign/spine-regions.html" "$SITE/spine-regions.html"
"$PYBIN" "$ROOT/redesign/gen_search.py" >/dev/null

# capture the treated body for each edited slug
mkdir -p "$TMP/bodies"
for cs in "${SLUGS[@]}"; do
  out="$TMP/bodies/$(printf '%s' "$cs" | tr '/' '_').body"
  "$PYBIN" - "$SITE/$cs/index.html" "$out" <<'PY'
import re, sys
h = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r'<article class="article-body"[^>]*>(.*?)</article>', h, re.S)
if not m: sys.exit("could not extract treated body from %s" % sys.argv[1])
open(sys.argv[2], "w", encoding="utf-8").write(m.group(1))
PY
  [ -s "$out" ] || die "treated body for $cs is empty — regen failed" 5
done

# -- 5. restore APPROVED pages, then splice ONLY the new bodies ----------------
say "restore approved overlay + splice edited body(ies)…"
bash "$ROOT/redesign/restore.sh" >/dev/null
for cs in "${SLUGS[@]}"; do
  bf="$TMP/bodies/$(printf '%s' "$cs" | tr '/' '_').body"
  "$PYBIN" - "$SITE/$cs/index.html" "$bf" <<'PY'
import re, sys
p = sys.argv[1]; nb = open(sys.argv[2], encoding="utf-8").read()
h = open(p, encoding="utf-8").read()
h2, n = re.subn(r'(<article class="article-body"[^>]*>).*?(</article>)',
                lambda m: m.group(1) + nb + m.group(2), h, count=1, flags=re.S)
if n != 1: sys.exit("splice failed (matched %d article bodies) in %s" % (n, p))
open(p, "w", encoding="utf-8").write(h2)
PY
done

# -- 6. DIFF-GATE: ONLY the edited article page(s) may differ from approved ----
#       sha256 manifest comparison (space-safe; no diff-text parsing).
say "diff-gate: verifying only the edited page(s) changed…"
EXP="$TMP/expected.txt"; : > "$EXP"
for cs in "${SLUGS[@]}"; do echo "$cs/index.html" >> "$EXP"; done
sort -o "$EXP" "$EXP"

CHANGEDSET="$TMP/changed.txt"; : > "$CHANGEDSET"
while IFS= read -r af; do
  rel="${af#"$TMP/approved/"}"
  sf="$SITE/$rel"
  [ -f "$sf" ] || { echo "MISSING:$rel" >> "$CHANGEDSET"; continue; }
  cmp -s "$af" "$sf" || echo "$rel" >> "$CHANGEDSET"
done < <(find "$TMP/approved" -type f)
sort -o "$CHANGEDSET" "$CHANGEDSET"

# unexpected = changed but not expected
UNEXPECTED="$(comm -23 "$CHANGEDSET" "$EXP" || true)"
[ -z "$UNEXPECTED" ] || { printf '%s\n' "$UNEXPECTED" >&2; die "unexpected page(s) changed vs approved — NOT deploying" 4; }
# and confirm every expected page actually changed (the edit really landed)
MISSING_EDIT="$(comm -13 "$CHANGEDSET" "$EXP" || true)"
[ -z "$MISSING_EDIT" ] || { printf '%s\n' "$MISSING_EDIT" >&2; die "edited page(s) did NOT change — edit didn't land (stale cache? wrong slug?)" 4; }
say "diff-gate PASSED — exactly ${#SLUGS[@]} edited page(s) changed, 0 collateral."

# -- 7. smoke check the full deploy dir ---------------------------------------
[ -s "$SITE/index.html" ]   || die "landing site/index.html missing/empty" 5
[ -d "$SITE/assets" ]       || die "site/assets missing" 5
marked="$(grep -rl 'sr-search-btn' "$SITE" --include=index.html | wc -l | tr -d ' ')"
[ "$marked" -ge 230 ] || die "only $marked redesign pages present (<230) — site looks incomplete" 5
say "smoke check OK ($marked redesign pages, landing + assets present)."

if [ "$DRYRUN" -eq 1 ]; then say "--dry-run: skipping deploy + overlay re-freeze. site/ is staged & verified."; exit 0; fi

# -- 8. deploy -----------------------------------------------------------------
npx wrangler whoami >/dev/null 2>&1 || die "wrangler not authenticated (run: npx wrangler login)" 6
say "deploying to production…"
npx wrangler deploy

# -- 9. re-freeze the overlay so future build.sh keeps the edit ---------------
bash "$ROOT/redesign/snapshot.sh"
say "DONE. Live + overlay re-frozen."
say "COMMIT the refreshed overlay so the repo stays source of truth:"
say "    git add redesign/snapshots/redesign-overlay.tar.gz && git commit -m 'publish: <article>'"
