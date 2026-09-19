#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
REMOTE_URL="${1:-}"
if [ -z "$REMOTE_URL" ]; then
  echo "Usage: ./scripts/git-init-and-push.sh https://github.com/<user>/<repo>.git" >&2
  exit 1
fi
if [ ! -d .git ]; then
  git init
  git branch -M main
fi
git add .
if ! git diff --cached --quiet; then
  git commit -m "feat: bootstrap BuktiSaham local Ollama free-data MVP"
fi
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi
git push -u origin main
