#!/usr/bin/env bash
set -e

# Incident Intelligence Platform Test Runner
# Usage: ./test.sh [backend|frontend|all]

TARGET="${1:-all}"

run_backend() {
  echo "=== Running Backend Pytest Suite (Docker container) ==="
  docker compose exec app uv run pytest tests/
}

run_frontend() {
  echo "=== Running Frontend Vitest Suite (Docker container) ==="
  docker run --rm -v "$(pwd)/frontend:/work" -w /work node:20-alpine npm test
}

case "$TARGET" in
  backend)
    run_backend
    ;;
  frontend)
    run_frontend
    ;;
  all)
    run_backend
    echo ""
    run_frontend
    ;;
  *)
    echo "Usage: $0 [backend|frontend|all]"
    exit 1
    ;;
esac
