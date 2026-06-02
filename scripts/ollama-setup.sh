#!/usr/bin/env bash
# FallMind · Stage 5 · register simon-mind in Ollama + pull 70B fallback
# ◊·κ=1 · run after scripts/merge.py completes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v ollama >/dev/null 2>&1; then
  echo "[err] ollama not installed · https://ollama.com/download"
  exit 1
fi

if [ ! -d "./simon-mind" ]; then
  echo "[err] ./simon-mind missing · run scripts/merge.py first"
  exit 1
fi

cp Modelfile.template Modelfile

echo "[step] ollama create simon-mind"
ollama create simon-mind -f Modelfile

echo "[step] smoke test"
ollama run simon-mind "Write the spec for a single-file sovereign HTML tool." \
  | head -40

echo "[step] pull T2.5 fallback · llama3.1:70b-instruct-q4_K_M (~40GB)"
ollama pull llama3.1:70b-instruct-q4_K_M

echo "[done] simon-mind registered · cascade ready"
echo "[next] open fallmind.html · the Ollama panel will detect simon-mind"
