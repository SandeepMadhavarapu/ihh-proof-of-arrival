#!/usr/bin/env python3
"""Check the media folder against the manifest. Run after fetching the images.
Reports what is present, what is missing, and whether rights metadata survived."""
import csv, os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
rows=list(csv.DictReader(open(os.path.join(HERE,"media-manifest.csv"),encoding="utf-8")))
imgs=[r for r in rows if r["filename"].endswith(".jpg")]
missing=[]; present=[]
for r in imgs:
    p=os.path.join(HERE,"media",r["filename"])
    (present if os.path.exists(p) else missing).append(r)
print(f"Manifest lists {len(imgs)} image files.")
print(f"  present: {len(present)}   missing: {len(missing)}\n")
for r in missing:
    print(f"  MISSING  {r['filename']}\n           {r['stable_item_url']}")
for r in present:
    p=os.path.join(HERE,"media",r["filename"]); size=os.path.getsize(p)
    print(f"  present  {r['filename']}  {size//1024} KB")
    if r["long_description_status"].startswith("METADATA-DERIVED"):
        print(f"           ACTION: long description is metadata-derived. Look at the image and rewrite it.")
    if r["recommendation"].startswith("USE ONLY AFTER VIEWING"):
        print(f"           ACTION: subject unconfirmed. Do not caption until you have viewed it.")
try:
    from PIL import Image
    print("\nEmbedded metadata (checks that resizing did not strip rights information):")
    for r in present:
        im=Image.open(os.path.join(HERE,"media",r["filename"]))
        ex=im.getexif(); print(f"  {r['filename']}: {len(ex)} EXIF tags"
                               f"{'  <-- WARNING: no metadata, may have been stripped' if not ex else ''}")
except ImportError:
    print("\n(Install pillow to also check embedded rights metadata: pip install pillow)")
sys.exit(1 if missing else 0)
