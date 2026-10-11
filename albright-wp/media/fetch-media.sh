#!/usr/bin/env bash
# Download the six archival photographs listed in media-manifest.csv.
# Run from any network that can reach catalog.archives.gov and diplomacy.state.gov.
# The environment that built this package is refused by both (HTTP 403 at its egress proxy).
set -u
cd "$(dirname "$0")"
echo "Saving into: $PWD"
echo

# Only the anchor has a known direct media URL. The rest must be taken from their
# record pages, because NARA's media paths are not derivable from the identifier.
# WARNING: this direct path was recorded from research notes and has NEVER been tested -
# the catalogue is unreachable from the machine that wrote this script. If it 404s, that is
# expected; use the record page instead. Do not trust it over the Download control.
ANCHOR_URL="https://catalog.archives.gov/medialz/stillpix/064-cfda/2016/Batch0002/20160914-01/64-CFDA-20160914-01-100.jpg"
echo "1/6  albright-2016-naturalization.jpg  (untested direct path - may fail)"
if curl -fL --retry 2 -o albright-2016-naturalization.jpg "$ANCHOR_URL"; then
  echo "     saved: $(du -h albright-2016-naturalization.jpg | cut -f1)"
else
  rm -f albright-2016-naturalization.jpg
  echo "     As expected if the path is wrong. Open https://catalog.archives.gov/id/445648831"
  echo "     and use the Download control on the record."
fi
echo
echo "All six are reliably obtained the same way: open the record, use its Download control."
echo "NARA does not expose a stable derivable media URL for them."
echo
echo "  albright-swearing-in-1997.jpg      https://catalog.archives.gov/id/131493882"
echo "  albright-rg59-505632161.jpg        https://catalog.archives.gov/id/505632161"
echo "  albright-rg59-505632159.jpg        https://catalog.archives.gov/id/505632159"
echo "  albright-rg59-505632157.jpg        https://catalog.archives.gov/id/505632157"
echo "  albright-commission-duplicate.jpg  https://diplomacy.state.gov/items/secretary-albrights-commission/"
echo
echo "Save each at the largest size offered, using exactly the filename above."
echo "Keep the originals somewhere else before resizing, and resize with 'Save As',"
echo "not 'Save for Web' - the latter strips embedded rights metadata."
echo
echo "Then verify what you got:"
echo "  python3 ../verify-media.py"
