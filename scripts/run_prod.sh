#!/usr/bin/env bash
# Route B: Mac mini + Cloudflare Tunnel. Run from the repository root.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -f .env.prod ]; then
  # shellcheck disable=SC1091
  set -a; . ./.env.prod; set +a
fi

export APP_ENV="${APP_ENV:-production}"
export PORT="${PORT:-8000}"
export DATABASE_URL="${DATABASE_URL:-sqlite:///./var/coldstart.db}"

if [ -z "${SECRET_KEY:-}" ]; then
  echo "SECRET_KEY belum diisi. Salin .env.prod.example ke .env.prod dan isi SECRET_KEY." >&2
  exit 1
fi
if [ "${DEMO_PASSWORD:-demo123}" = "demo123" ]; then
  echo "DEMO_PASSWORD masih default (demo123). Isi kata sandi lain di .env.prod." >&2
  exit 1
fi

mkdir -p var
exec .venv/bin/uvicorn app.main:app \
  --host 127.0.0.1 --port "$PORT" \
  --proxy-headers --forwarded-allow-ips='*'
