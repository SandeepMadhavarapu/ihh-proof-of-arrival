#!/usr/bin/env bash
# Clean-rebuild check: run every generator and prove the generated files in the repo match
# what the generators produce from their sources (cases.py, copy.md, media-manifest.csv).
#   bash qa/rebuild.sh
set -eu
R="$(cd "$(dirname "$0")/.." && pwd)"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
GEN=(site/verify.html site/albright.html site/lamarr.html site/pei.html site/cruz.html)
for n in albright lamarr pei cruz; do
  GEN+=("inductees/$n/copy.html" "inductees/$n/copy-full.md" "inductees/$n/preview.html")
done
for f in "${GEN[@]}"; do mkdir -p "$T/$(dirname "$f")"; cp "$R/$f" "$T/$f"; done
python3 "$R/site/gen.py" >/dev/null
python3 "$R/tools/build_profile.py" --all >/dev/null
python3 "$R/tools/build_site_pages.py" >/dev/null
fail=0
for f in "${GEN[@]}"; do
  if diff -q "$T/$f" "$R/$f" >/dev/null; then echo "  OK   $f regenerates byte-identically"
  else echo "  FAIL $f drifted from its sources"; fail=1; fi
done
echo
[ $fail = 0 ] && echo "ALL GENERATED FILES MATCH THEIR SOURCES" || { echo "REBUILD CHECK FAILED"; exit 1; }
