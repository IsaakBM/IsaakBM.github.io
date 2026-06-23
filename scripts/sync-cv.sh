#!/usr/bin/env bash
set -euo pipefail

SOURCE_CV="${CV_SOURCE:-/Users/ibrito/Developer/career-materials/cv/outputs/isaac_brito_morales_academic_cv.pdf}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET_CV="$SITE_DIR/content/pdf/isaac_brito_morales_academic_cv.pdf"

if [[ ! -f "$SOURCE_CV" ]]; then
  echo "CV sync skipped: source PDF not found at $SOURCE_CV" >&2
  exit 0
fi

mkdir -p "$(dirname "$TARGET_CV")"
cp "$SOURCE_CV" "$TARGET_CV"
echo "Synced CV from $SOURCE_CV to $TARGET_CV"
