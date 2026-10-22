#!/usr/bin/env bash
# Run the whole stack for local development: Django backend + Next.js frontend.
#
# Usage:
#   ./scripts/dev.sh            # backend (8000) + frontend (3000) in one terminal
#   ./scripts/dev.sh --fresh    # reset the database first (migrate + seed from scratch)
#
# Logs from both processes are interleaved and prefixed with "backend"/"frontend".
# Ctrl-C stops both.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

if [[ "${1:-}" == "--fresh" ]]; then
    echo ">> Resetting database (migrate + seed from scratch)"
    (cd "$BACKEND" && python scripts/reset_database.py)
fi

# Backend deps + env
cd "$BACKEND"
if [[ ! -d .venv ]]; then
    echo ">> Creating backend virtualenv (uv)"
    uv sync
fi
[[ -f .env ]] || cp .env.sample .env

# Local OTP testing without a Telegram/Kavenegar account: print codes to console.
export OTP_BACKEND="${OTP_BACKEND:-console}"

# Frontend deps + env
cd "$FRONTEND"
[[ -d node_modules ]] || npm install
export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://127.0.0.1:8000}"
export NEXT_PUBLIC_SITE_URL="${NEXT_PUBLIC_SITE_URL:-http://localhost:3000}"

cd "$ROOT"
cleanup() { kill 0 2>/dev/null || true; }
trap cleanup EXIT INT TERM

echo ">> Backend:  http://127.0.0.1:8000  (admin at /admin/)"
echo ">> Frontend: http://localhost:3000"
echo ">> Ctrl-C to stop both."

(cd "$BACKEND" && sed -u 's/^/backend  | /' < <(uv run manage.py runserver 2>&1)) &
(cd "$FRONTEND" && sed -u 's/^/frontend | /' < <(npm run dev 2>&1)) &

wait