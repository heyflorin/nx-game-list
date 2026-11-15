#!/usr/bin/env bash
# Re-check every source and rebuild index.html. Run from the repository root.
# Needs: curl, git, python3, and the GitHub CLI (gh) signed in, for the issue search.
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
cd "$root/data"

echo "1/4 NX2Apple GAMES.md"
curl -fsSL -o dl2/GAMES.md https://raw.githubusercontent.com/LNPANDY/NX2Apple/main/GAMES.md

echo "2/4 nxnative dm/games profiles"
tmp="$(mktemp -d)"
# Full history without file contents: enough for each profile's last-changed date, and fast.
git clone -q --filter=blob:none --no-checkout https://github.com/seedds/nxnative.git "$tmp/nxn"
git -C "$tmp/nxn" sparse-checkout set --no-cone '/dm/games/README.md' '/dm/games/*/README.md'
git -C "$tmp/nxn" checkout -q
git -C "$tmp/nxn" log --format='@%cI' --name-only -- dm/games | python3 "$root/tools/profile_dates.py" > readmes/profile-dates.json
cp "$tmp/nxn/dm/games/README.md" readmes/games-index.md
for d in "$tmp"/nxn/dm/games/*/; do
  [ -f "$d/README.md" ] && cp "$d/README.md" "readmes/all/$(basename "$d").md"
done
echo "   nxnative commit $(git -C "$tmp/nxn" log -1 --format='%h %cd')"
printf '{"checked": "%s", "nxnative_commit": "%s", "nxnative_date": "%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%MZ)" "$(git -C "$tmp/nxn" log -1 --format=%h)" "$(TZ=UTC git -C "$tmp/nxn" log -1 --date=format-local:%Y-%m-%dT%H:%M:%SZ --format=%cd)" > meta.json
rm -rf "$tmp"

echo "3/4 issues in seedds/nxnative and LNPANDY/NX2Apple"
fields='.items[] | {number, title, state, state_reason, labels: [.labels[].name], body, created_at, updated_at, closed_at, comments}'
gh api -X GET search/issues -f q='repo:seedds/nxnative is:issue' -f per_page=100 --paginate --jq "$fields" > new1/all.jsonl
gh api -X GET search/issues -f q='repo:LNPANDY/NX2Apple is:issue' -f per_page=100 --paginate --jq "$fields" > new2/all.jsonl
wc -l new1/all.jsonl new2/all.jsonl

echo "4/4 parse, match and build"
python3 "$root/tools/refresh_engine.py"
python3 "$root/tools/parse.py" dl2/GAMES.md games.json
python3 "$root/tools/match.py" data.json new1/all.jsonl new1/matched.json > /dev/null
python3 "$root/tools/match.py" data.json new2/all.jsonl new2/matched.json > /dev/null

python3 "$root/tools/enrich.py" dl2/GAMES.md games.json data.json "$root/tools/template.html" "$root/build/artifact.html" "$root/index.html"
echo "Done: index.html"
