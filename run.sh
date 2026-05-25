#!/bin/bash
# ═══ 排爐系統 v3 — 一鍵啟動 ═══
set -e
REPO="https://github.com/FattyManAW/furnace-v3.git"

cd "$(dirname "$0")"

# Clone if missing
[ ! -d backend ] && git clone "$REPO" . 2>/dev/null && echo "✓ cloned"

# Build + start
export GIT_COMMIT=$(git rev-parse --short HEAD)
echo "🔧 GIT_COMMIT=$GIT_COMMIT"
docker compose build api 2>&1 | tail -2
docker compose up -d 2>&1

# Health check
for i in 1 2 3 4 5; do
  sleep 2
  if curl -sf http://localhost:${PORT:-8005}/health >/dev/null 2>&1; then
    echo "✓ furnace-v3 healthy on :${PORT:-8005}"
    echo "  API:      http://localhost:${PORT:-8005}/api/v1/health/full"
    echo "  Orders:   http://localhost:${PORT:-8005}/api/v1/orders"
    echo "  Kanban:   http://localhost:${PORT:-8005}/api/v1/kanban"
    echo "  UI:       http://localhost:8031"
    echo
    echo "🔄 Sync from v2: curl -X POST http://localhost:${PORT:-8005}/api/v1/sync/from-v2"
    exit 0
  fi
done
echo "⚠️ Health check timeout — check: docker logs furnace-v3-api"
exit 1
