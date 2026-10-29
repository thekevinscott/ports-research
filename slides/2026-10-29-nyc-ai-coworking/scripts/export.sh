#!/usr/bin/env bash
# Build the hostable deck plus slides.pdf into OUT, for serving under BASE.
# Usage: scripts/export.sh OUT [BASE]
set -euo pipefail
cd "$(dirname "$0")/.."

out="${1:?usage: scripts/export.sh OUT [BASE]}"
base="${2:-/talks/2026-10-29-nyc-ai-coworking/}"

pnpm exec slidev build --base "$base" --out "$out" --router-mode hash
pnpm exec slidev export --output "$out/slides.pdf" --wait 1500 --timeout 120000
