#!/usr/bin/env bash
# Install repo-shipped git hooks into .git/hooks.
# Run once after cloning the repo.

set -e
ROOT="$(git rev-parse --show-toplevel)"
SRC="$ROOT/scripts/git-hooks"
DST="$ROOT/.git/hooks"

for h in pre-push; do
    cp "$SRC/$h" "$DST/$h"
    chmod +x "$DST/$h"
    echo "installed: $DST/$h"
done

echo "Done. Hooks are now active."
