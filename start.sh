#!/usr/bin/env bash
# riffscribe launcher — one command to set up (first run) and open the app.
# Double-click riffscribe.command, or run ./start.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$REPO/backend"
VENV="$BACKEND/.venv"
PORT="${RIFFSCRIBE_PORT:-8000}"
URL="http://localhost:$PORT"

# Basic Pitch needs Python 3.10–3.12 (no ML wheels for 3.13+ yet).
find_py() {
  for p in python3.12 python3.11 python3.10 \
           /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3.11; do
    if command -v "$p" >/dev/null 2>&1; then echo "$p"; return 0; fi
  done
  return 1
}

if [ ! -x "$VENV/bin/python" ]; then
  if ! PY="$(find_py)"; then
    echo "❌ riffscribe needs Python 3.10–3.12 (Basic Pitch doesn't support 3.13+)."
    echo "   Install it with:  brew install python@3.12"
    exit 1
  fi
  echo "🎸 First-time setup with $PY — downloading ML deps, this takes a few minutes…"
  "$PY" -m venv "$VENV"
  "$VENV/bin/pip" install --upgrade pip >/dev/null
  "$VENV/bin/pip" install -e "$BACKEND" "basic-pitch[onnx]" "setuptools<81"
fi

# Safety net: make sure the transcription engine is importable.
if ! "$VENV/bin/python" -c "import basic_pitch" >/dev/null 2>&1; then
  echo "Finishing engine install…"
  "$VENV/bin/pip" install "basic-pitch[onnx]" "setuptools<81"
fi

echo ""
echo "🎸 riffscribe is running at $URL   (press Ctrl+C to stop)"
( sleep 3; open "$URL" >/dev/null 2>&1 || true ) &
cd "$BACKEND"
exec "$VENV/bin/python" -m uvicorn app.main:app --port "$PORT"
