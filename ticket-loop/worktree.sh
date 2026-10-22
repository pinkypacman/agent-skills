#!/bin/bash
# Create a ticket worktree on its own branch and link every git-ignored path of the main checkout into it.
# Usage: worktree.sh [--dry] <main checkout> <worktree path> <branch> [base, default master]
# Wholly ignored folders become one link; ignored files inside tracked folders are linked one by one.
set -eu
DRY=0; [ "${1:-}" = --dry ] && { DRY=1; shift; }
MAIN="$(readlink -f "$1")"; WT="$2"; BR="$3"; BASE="${4:-master}"
run() { if [ "$DRY" = 1 ]; then echo "WOULD: $*"; else "$@"; fi; }

run git -C "$MAIN" worktree add -b "$BR" "$WT" "$BASE"
# link each ignored path (caches excluded) from the main checkout into the worktree
git -C "$MAIN" status --ignored --porcelain=v1 | sed -n 's/^!! //p' | grep -vE '(^|/)__pycache__/|\.pyc$' |
while read -r p; do
  p="${p%/}"
  run mkdir -p "$WT/$(dirname "$p")"
  run ln -s "$MAIN/$p" "$WT/$p"
done
[ "$DRY" = 1 ] || git -C "$WT" status --short | head -5
