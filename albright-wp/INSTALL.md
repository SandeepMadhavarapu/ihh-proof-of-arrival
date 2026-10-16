# Madeleine Albright profile — how to put this on the website

Written for somebody who does not write code. The twenty-minute installation time is an
**untested designer estimate, not an observed volunteer result**; image retrieval, rights
review, editorial approval, and troubleshooting may take longer. WordPress editing permission
and an accountable technical owner are required. No additional runtime plugin is supplied.

---

## Step 1 — Put your name on it (two minutes, and do it first)

Open `copy.html` in any text editor. Search for `[NAME OF THE PERSON WHO CHECKED THIS]`.
It appears 2 times, highlighted in yellow on the page so you cannot miss it, and 2 more times in copy-full.md.

Replace it with the name of the person who has read this page and checked it, and replace
`[MONTH YEAR]` with the month you publish.

**Do not publish with the placeholder still in it.** The byline is a promise that a named
human stands behind the facts. If nobody has checked it, that is the thing to fix before
publishing, not the placeholder.

## Step 2 — Get the photographs (fifteen minutes)

`albright-wp/media/` lacks the six archival photographs. The ten portraits shipped in
`site/media/portraits/` belong to the separate demo and do not fill these slots. Consult each
archival item record and transcribe its actual rights wording; do not assume that every image
held by a federal institution is cleared for the intended use. Earlier retrieval attempts
failed in the build environment; those logs do not establish present-day availability.

Run `media/fetch-media.sh` on any computer with normal internet access, **or** do it by hand:

1. Open `media-manifest.csv` in Excel or Numbers.
2. For each of the six rows whose `kind` is a photograph, open the `stable_item_url`.
3. Use the record's own **Download** control and save at the largest size offered.
4. Save it into the `media/` folder using exactly the name in the `filename` column.

**Save the originals somewhere separate before you resize anything.** When you do resize,
use "Save As" rather than "Save for Web" — the latter strips the embedded rights metadata,
and removing that metadata can create a separate legal problem under 17 U.S.C. §1202 even
when the use itself is perfectly fine. Longest edge 2000 pixels is plenty.

### Then switch the photograph on

There are **seven** image slots to switch on, not one:

- the big anchor photograph: find `<span class="ph">`, delete that whole block, and un-comment
  the `<img>` tag directly beneath it (remove the `<!--` and `-->` around it);
- **six thumbnails** in the source list: each is a `<span class="th ph-th">` block with its own
  commented-out `<img>` directly beneath. Same operation, six times. Each one names the file it
  wants.

Search `copy.html` for `ph-th` to find them all.

Until you do this each slot shows a labelled box explaining the photograph is missing.
That is deliberate. It is better than a broken image and much better than a fake one.

## Step 3 — Paste it in (three minutes)

**Self-hosted WordPress:** create the page, add one **Custom HTML** block, paste the entire
contents of `copy.html` into it, publish. One thing about the images: the `<img>` tags you
switched on in Step 2 point at `media/…`, which is a path relative to the page and will **not**
resolve on a live site. Upload the six photographs through the WordPress **media library**, then
in the pasted HTML change each `src="media/<name>"` to the URL the library gives you. Until you
do, each slot keeps showing its labelled "image not supplied" box rather than a broken image.

**One thing to check before you publish.** Most themes print the page title as a large
heading at the top. If yours does, the page would then have two first-level headings — the
theme's and the one inside this block. Open `copy.html`, find the comment that says so, and
delete the single line `<h1>Madeleine Albright</h1>` beneath it. If your theme does *not*
print a title, leave it alone. Either way, name the WordPress page **Madeleine Albright**.

**WordPress.com:** Custom HTML blocks are restricted on the cheaper plans. If your paste is
stripped, use **`copy-full.md`** and rebuild with ordinary blocks — Image, Paragraph, Heading,
Details, Quote, List. Use `copy-full.md`, **not** `copy.md`: the short file is the editorial text only, while `copy-full.md` also carries the fourteen source items, every rights statement and required credit, the documented-deviation note and the byline. Publishing from `copy.md` would put an uncredited page on the site. You lose the styling and keep every word.

Upload the images through the WordPress media library and point the `src` attributes at the
URLs it gives you, instead of `media/…`.

---

## What this page will and will not do

**It has no JavaScript at all.** The expanding sections are the browser's own `<details>`
element. No build step or third-party request is required at visitor runtime. Editorial
upkeep, source-link and rights review, WordPress integration checks after updates, and named
technical ownership are still required.

**All its styling is scoped to `.ihh-profile`.** The supplied QA fixture checks that those styles do not restyle its host. Test the
museum's actual theme and plugins in staging; this is not a universal compatibility guarantee.

**It loads nothing from anywhere else.** No font, no script, no tracker, no API. Local HTML and image assets can be retained for offline reading, but linked sources
need network access. Browser and WordPress changes may affect rendering over time; no
identical-rendering or maintenance-free lifetime is promised.

**It follows your system's light or dark setting** automatically.

**It prints cleanly** — every collapsed section opens on paper.

---

## Three things you should know before you publish

**1. One document on this page has never been opened by anyone who worked on it.**
The 1998 State Department press statement is the natural centrepiece of this story. The
machine that built this page could not reach the archived State Department website on any
route. Rather than quote it anyway, the page says plainly that it has not been read, and
uses a wire report of the same ceremony instead. **If you can open it, please do** — and
tell whoever maintains this page, because several details would improve.

**2. The date of that ceremony is 10 November 1998, often miscited as 11 November.** The
archived filename, the page title and the Associated Press dateline all give 10 November, and
10 November 1998 was the Tuesday the AP report names. The page states 10 November and notes the
common miscitation; do not "correct" it to the 11th.

**3. The long descriptions of the photographs were written from catalogue metadata, not
from looking at the pictures.** The manifest marks them
`METADATA-DERIVED, NOT VERIFIED AGAINST THE IMAGE`. After Step 2, look at each photograph
and rewrite its long description from what you actually see. This matters most for the
three Record Group 59 items, whose subject is not confirmed at all — the manifest says
`USE ONLY AFTER VIEWING`.

---

## The one favour we would ask

Whoever does this: please write down how long it took and every point where you had to
stop and work something out that this file did not explain. That answer decides how the
next three profiles get built.

**Nobody has yet run this handoff with a real volunteer.** The twenty-minute estimate is a
designer's guess, not a measurement, and should be treated as one.
