#!/usr/bin/env bash
# Assemble handover/<name>/ for every inductee and zip the lot for IHH.
#   bash tools/package_handover.sh
# Rebuilds first, so the package can never drift from copy.md and the manifest.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/tools/build_profile.py" --all
for dir in "$ROOT"/inductees/*/; do
  [ -f "$dir/copy.md" ] || continue
  name="$(basename "$dir")"
  out="$ROOT/handover/$name"
  mkdir -p "$out/media/web"
  cp "$dir"/copy.html "$dir"/copy-full.md "$dir"/preview.html \
     "$dir"/media-manifest.csv "$out/"
  if [ -f "$dir/search-log.csv" ]; then
    cp "$dir/search-log.csv" "$out/"
  else
    if [ -e "$out/search-log.csv" ]; then
      echo "ERROR: $out/search-log.csv exists without an input log; review it manually before packaging." >&2
      exit 1
    fi
    echo "OPEN ITEM: $name/search-log.csv missing; team lead will supply the actual research log." >&2
  fi
  cp -R "$dir/media/web/." "$out/media/web/"
done
python3 "$ROOT/tools/open_items.py" > "$ROOT/handover/OPEN-ITEMS.md"
cd "$ROOT"
python3 - <<'PYZIP'
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
with ZipFile('handover/IHH-inductee-profiles.zip', 'w', compression=ZIP_DEFLATED) as archive:
    for path in sorted(Path('handover').rglob('*')):
        if path.is_file() and path.suffix != '.zip':
            entry = ZipInfo(path.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, path.read_bytes())
PYZIP
echo "handover/ assembled (human sign-off pending): $(du -sh handover/IHH-inductee-profiles.zip | cut -f1) zip"
