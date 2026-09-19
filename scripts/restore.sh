#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
DIR="${1:-}"
if [ -z "$DIR" ] || [ ! -f "$DIR/postgres.dump" ]; then
  echo "Usage: ./scripts/restore.sh backups/YYYYMMDD-HHMMSS" >&2
  exit 1
fi

echo "WARNING: this restores the selected database dump into the local Docker database."
docker compose up -d postgres
docker compose exec -T postgres dropdb -U buktisaham --if-exists buktisaham
docker compose exec -T postgres createdb -U buktisaham buktisaham
cat "$DIR/postgres.dump" | docker compose exec -T postgres pg_restore -U buktisaham -d buktisaham --no-owner --no-privileges
echo "Restore completed."
