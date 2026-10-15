#!/usr/bin/env bash
# Assemble handover/<name>/ for every inductee and zip the lot for IHH.
#   bash tools/package_handover.sh
# Rebuilds first, so the package can never drift from copy.md and the manifest.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/tools/build_profile.py" --all
for dir in "$ROOT"/inductees/*/; do
  name="$(basename "$dir")"
  out="$ROOT/handover/$name"
  rm -rf "$out"; mkdir -p "$out/media"
  cp "$dir"/copy.html "$dir"/copy-full.md "$dir"/preview.html \
     "$dir"/media-manifest.csv "$dir"/search-log.csv "$out/"
  cp -R "$dir/media/web" "$out/media/web"
done
python3 "$ROOT/tools/open_items.py" > "$ROOT/handover/OPEN-ITEMS.md"
cd "$ROOT"
rm -f handover/IHH-inductee-profiles.zip
zip -qr handover/IHH-inductee-profiles.zip handover -x 'handover/*.zip'
echo "handover/ ready: $(du -sh handover/IHH-inductee-profiles.zip | cut -f1) zip"
