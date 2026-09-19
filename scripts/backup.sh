#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
STAMP=$(date +%Y%m%d-%H%M%S)
DEST="backups/$STAMP"
mkdir -p "$DEST"

echo "Backing up PostgreSQL..."
docker compose exec -T postgres pg_dump -U buktisaham -d buktisaham -Fc > "$DEST/postgres.dump"

echo "Saving configuration snapshot (secrets redacted)..."
grep -Ev 'PASSWORD|SECRET|TOKEN|KEY=' .env 2>/dev/null > "$DEST/env.redacted" || true

echo "$DEST" > backups/LATEST
echo "Backup written to $DEST"
