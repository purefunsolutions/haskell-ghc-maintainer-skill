#!/usr/bin/env bash
# Search ghc/ghc on gitlab.haskell.org for issues and merge requests matching each term.
# Usage: ghc-search.sh [--open] [--since YYYY-MM-DD] TERM [TERM ...]
# Prints one line per hit: #N (issue) or !N (MR), state, creation date, title, author.
# Needs curl and python3; no token. Searches titles and descriptions, all states by default.
# With glab logged in to gitlab.haskell.org, `glab issue list` and `glab mr list` do more;
# see references/glab.md.
set -euo pipefail

usage() { sed -n '3,7p' "${BASH_SOURCE[0]}" | sed 's/^# //'; }

api=https://gitlab.haskell.org/api/v4/projects/1
open=0
since=""
while [ $# -gt 0 ]; do
  case $1 in
    --open) open=1; shift ;;
    --since) since=${2:?--since needs a date}; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) echo "ghc-search.sh: unknown option $1" >&2; usage >&2; exit 2 ;;
    *) break ;;
  esac
done
[ $# -gt 0 ] || { usage >&2; exit 2; }

fmt='
import json, sys
kind, term = sys.argv[1], sys.argv[2]
items = json.load(sys.stdin)
if not isinstance(items, list):
    sys.exit("ghc-search.sh: unexpected answer from GitLab: %r" % (items,))
sigil, what = ("#", "issues") if kind == "issues" else ("!", "MRs")
print("%s matching %r: %d%s" % (what, term, len(items), " (first 20)" if len(items) == 20 else ""))
for i in items:
    print("  %s%s [%s] %s %s (@%s)" % (sigil, i["iid"], i["state"], i["created_at"][:10],
                                       i["title"], i["author"]["username"]))
'

for term in "$@"; do
  for kind in issues merge_requests; do
    args=(-G "$api/$kind" --data-urlencode "search=$term" --data-urlencode "per_page=20")
    if [ "$open" = 1 ]; then
      args+=(--data-urlencode "state=opened")
    elif [ "$kind" = merge_requests ]; then
      args+=(--data-urlencode "state=all")
    fi
    if [ -n "$since" ]; then
      args+=(--data-urlencode "created_after=$since")
    fi
    curl -sS --fail --max-time 60 "${args[@]}" | python3 -I -c "$fmt" "$kind" "$term"
  done
done
