#!/usr/bin/env bash
# Clean-rebuild check: extract the shipped ZIP somewhere else, run both generators,
# and prove the generated files in the package match what the generators produce.
set -eu
ZIP="${1:?usage: rebuild.sh /path/to/IHH-FINAL.zip}"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
unzip -q "$ZIP" -d "$T"
R="$T/IHH-FINAL"
echo "extracted to $R"
cp "$R/site/verify.html" "$T/verify.before"
cp "$R/albright-wp/copy.html"     "$T/copy.before"
cp "$R/albright-wp/copy-full.md"  "$T/full.before"
cp "$R/albright-wp/preview.html"  "$T/preview.before"
python3 "$R/site/gen.py"        >/dev/null
python3 "$R/albright-wp/build.py" >/dev/null
fail=0
if diff -q "$T/verify.before" "$R/site/verify.html" >/dev/null; then
  echo "  OK   site/verify.html regenerates byte-identically"
else echo "  FAIL site/verify.html drifted from cases.py"; fail=1; fi
if diff -q "$T/copy.before" "$R/albright-wp/copy.html" >/dev/null; then
  echo "  OK   albright-wp/copy.html regenerates byte-identically"
else echo "  FAIL albright-wp/copy.html drifted from copy.md / the manifest"; fail=1; fi
if diff -q "$T/full.before" "$R/albright-wp/copy-full.md" >/dev/null; then
  echo "  OK   albright-wp/copy-full.md regenerates byte-identically"
else echo "  FAIL albright-wp/copy-full.md drifted"; fail=1; fi
if diff -q "$T/preview.before" "$R/albright-wp/preview.html" >/dev/null; then
  echo "  OK   albright-wp/preview.html regenerates byte-identically"
else echo "  FAIL albright-wp/preview.html drifted"; fail=1; fi
echo "  OK   both generators ran from a path they had never seen"
exit $fail
