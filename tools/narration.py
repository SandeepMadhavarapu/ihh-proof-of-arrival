#!/usr/bin/env python3
"""Listen: narration you can check line by line, built from inductees/<slug>/narration.json.

    python3 tools/narration.py               # check every script (and its audio, once made)
    python3 tools/narration.py --handover    # also write handover/<slug>/listen-<slug>.html

Every narrated line is traced to the inductee's verified inductees/<slug>/copy.md. The check
refuses to build if, for any line:
  * fact / intro: its copy_md_sentence is not on line copy_md_line of copy.md, or the spoken line
    uses a word its source sentence does not (apart from a short list of joining words such as
    "he" or "the", and the inductee's own name), or a number, date or name its source lacks;
  * quote: the words are not in copy.md exactly, or the line before it is not an intro
    ("Einstein wrote:") that says whose words they are;
  * question / transition: it states a fact (a number, a date, a month, a place or another
    person's name);
  * anywhere outside a quotation: first person ("I", "my", "we", "our" ...), so the narrator never
    speaks as the inductee; or the words "AI", "artificial intelligence" or "generated", which
    belong on the player's label, not in the script;
  * the guide is not 260-300 words, the short is not 120-150 words, the guide has no quotation or
    does not end with a question, or the short does not end by pointing to the page.
Once audio exists (tools/narration_audio.py), it also refuses if a script changed after its audio
was made, or if any audio, caption or video file differs from the hashes in
site-data/narration/manifest.json.
These are mechanical checks. They prove every word, number and name has a source; they do not
prove the order of sentences gives a fair picture, which is why a person still reads the scripts.
"""
import hashlib
import html
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.artifacts import _names, _tokens, norm  # noqa: E402

NARR = os.path.join(ROOT, "site-data", "narration")
MANIFEST = os.path.join(NARR, "manifest.json")
VOICE = os.path.join(NARR, "voice.json")
E = html.escape
KINDS = {"fact", "intro", "quote", "question", "transition"}
RANGES = {"guide": (260, 300), "short": (120, 150)}
# Words a shortened sentence may use that its source sentence does not: pronouns and joining words
# that cannot add a fact. Words that change time, number or certainty ("after", "first", "only",
# "never") are deliberately absent.
GLUE = set("""he she his her him hers they their them it its the a an and but so this that these those
who whom whose which was were is are had has have as in on at of to for from with by""".split())
INTRO_GLUE = GLUE | set("said says wrote reads words own this about".split())
FIRST_PERSON = re.compile(r"\b(I|I'm|I've|I'd|I'll)\b|\b(me|my|mine|myself|we|we're|we've|we'd|our|ours|ourselves|us)\b",
                          re.IGNORECASE)
BANNED = re.compile(r"\b(AI|A\.I\.|artificial intelligence|generated|synthetic)\b", re.IGNORECASE)
POINTER = "on this page"


class CheckError(Exception):
    pass


def slugs():
    with open(os.path.join(ROOT, "site-data", "published.json"), encoding="utf-8") as f:
        return json.load(f)["published"]


def plain(s):
    """copy.md text as a listener hears it: markdown emphasis and link targets removed."""
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"(\*\*|\*|__|`)", "", s)
    s = re.sub(r"(?<![A-Za-z0-9])_([^_]+)_(?![A-Za-z0-9])", r"\1", s)
    return norm(s.replace("’", "'"))


def copy_lines(slug):
    with open(os.path.join(ROOT, "inductees", slug, "copy.md"), encoding="utf-8") as f:
        return [plain(x) for x in f.read().split("\n")]


def load(slug):
    with open(os.path.join(ROOT, "inductees", slug, "narration.json"), encoding="utf-8") as f:
        return json.load(f)


def words(s):
    return [w for w in re.findall(r"[a-z0-9]+(?:'[a-z]+)?", plain(s).lower())]


def count(lines):
    return sum(len(l["line"].split()) for l in lines)


def _no_first_person(text):
    t = re.sub(r"\bI\. ?(?=[A-Z])", "", text)  # "I. M. Pei", "I. Berlin": initials, not the pronoun
    m = FIRST_PERSON.search(t)
    return m.group(0) if m else None


def _check_derived(where, l, src_line, name_words, glue):
    src = plain(l.get("copy_md_sentence", ""))
    if len(src) < 8 or src not in src_line:
        raise CheckError(f"{where}: copy_md_sentence is not on copy.md line {l['copy_md_line']}: {l.get('copy_md_sentence')!r}")
    extra = [w for w in words(l["line"]) if w not in set(words(src)) | glue | name_words]
    if extra:
        raise CheckError(f"{where}: words not in its source sentence: {extra}")
    missing = {t for t in _tokens(l["line"]) if t not in _tokens(src) and t not in src.lower()}
    if missing:
        raise CheckError(f"{where}: number/date not in its source sentence: {sorted(missing)}")
    unnamed = {n for n in _names(l["line"]) if n.lower() not in src.lower() and n.lower() not in name_words}
    if unnamed:
        raise CheckError(f"{where}: name not in its source sentence: {sorted(unnamed)}")


def _check_no_fact(where, line, name_words, copy_text):
    if re.search(r"\d", line) or _tokens(line):
        raise CheckError(f"{where}: a question or transition may not contain a number or date: {line!r}")
    rest = line.split(None, 1)[1] if " " in line.strip() else ""  # the first word is capitalised anyway
    others = {n for n in _names(rest) if n.lower() not in name_words}
    if others:
        raise CheckError(f"{where}: a question or transition may not name anyone or anywhere: {sorted(others)}")


def check_script(d, lines=None):
    slug = d["slug"]
    lines = lines if lines is not None else copy_lines(slug)
    name_words = set(words(d["name"]))
    if plain(d["name"]) != plain(lines[0].lstrip("# ")):
        raise CheckError(f"{slug}: name {d['name']!r} is not copy.md's heading")
    for part, (lo, hi) in RANGES.items():
        script = d.get(part) or []
        if not script:
            raise CheckError(f"{slug} {part}: empty")
        for i, l in enumerate(script):
            where = f"{slug} {part} line {i + 1}"
            kind, text = l.get("kind"), l.get("line", "")
            if kind not in KINDS:
                raise CheckError(f"{where}: unknown kind {kind!r}")
            if BANNED.search(text):
                raise CheckError(f"{where}: the script must not mention AI or generation; the player labels it")
            if kind != "quote":
                fp = _no_first_person(text)
                if fp:
                    raise CheckError(f"{where}: first person {fp!r} outside a quotation (the narrator never speaks as the inductee)")
            n = l.get("copy_md_line", 0)
            if kind in ("fact", "intro", "quote"):
                if not 1 <= n <= len(lines):
                    raise CheckError(f"{where}: copy_md_line {n} is not a line of copy.md")
            if kind == "fact":
                _check_derived(where, l, lines[n - 1], name_words, GLUE)
            elif kind == "intro":
                if not text.rstrip().endswith(":") or i + 1 >= len(script) or script[i + 1]["kind"] != "quote":
                    raise CheckError(f"{where}: an intro ends with ':' and is followed by the quotation")
                _check_derived(where, l, lines[n - 1], name_words, INTRO_GLUE)
            elif kind == "quote":
                q = plain(text).rstrip(".,;:!? ")
                src = lines[n - 1]
                if len(q) < 12 or not (q in src or (q[0].lower() + q[1:]) in src):
                    raise CheckError(f"{where}: quotation not found word for word on copy.md line {n}")
                if i == 0 or script[i - 1]["kind"] != "intro":
                    raise CheckError(f"{where}: a quotation must follow an intro saying whose words they are")
            else:
                if n != 0 or l.get("copy_md_sentence"):
                    raise CheckError(f"{where}: a {kind} has no source (copy_md_line 0, empty copy_md_sentence)")
                _check_no_fact(where, text, name_words, lines)
                if kind == "question" and not text.rstrip().endswith("?"):
                    raise CheckError(f"{where}: a question ends with '?'")
        c = count(script)
        if not lo <= c <= hi:
            raise CheckError(f"{slug} {part}: {c} words, needs {lo}-{hi}")
    if not any(l["kind"] == "quote" for l in d["guide"]):
        raise CheckError(f"{slug} guide: no quotation")
    if d["guide"][-1]["kind"] != "question":
        raise CheckError(f"{slug} guide: must end with a question for the listener")
    if POINTER not in d["short"][-1]["line"]:
        raise CheckError(f"{slug} short: must end by pointing to the full story {POINTER!r}")
    return d


def script_text(lines):
    return "\n".join(l["line"] for l in lines)


def script_sha(lines):
    return hashlib.sha256(script_text(lines).encode("utf-8")).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest():
    if not os.path.exists(MANIFEST):
        return None
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def check_media(scripts, manifest):
    for d in scripts:
        for part in RANGES:
            key = f"{d['slug']}-{part}"
            m = manifest["files"].get(key)
            if not m:
                raise CheckError(f"{key}: no audio in the manifest; run tools/narration_audio.py")
            if m["script_sha256"] != script_sha(d[part]):
                raise CheckError(f"{key}: audio is stale (the script changed after it was recorded); run tools/narration_audio.py")
            if len(m["lines"]) != len(d[part]):
                raise CheckError(f"{key}: the manifest's line timings do not match the script")
            for kind in ("audio", "video", "poster"):
                if kind in m:
                    path = os.path.join(NARR, m[kind]["file"])
                    if not os.path.isfile(path) or file_sha(path) != m[kind]["sha256"]:
                        raise CheckError(f"{key}: {m[kind]['file']} is missing or differs from the manifest")
    return manifest


def _chunks(text, limit=80):
    """Split a long line into caption-sized pieces of similar length, at word boundaries."""
    if len(text) <= limit:
        return [text]
    words_ = text.split()
    n = -(-len(text) // limit)
    while True:
        target, out, cur = len(text) / n, [], ""
        for w in words_:
            if cur and len(cur) + 1 + len(w) > target and len(out) < n - 1:
                out.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        out.append(cur)
        if all(len(c) <= limit for c in out):
            return out
        n += 1


def caption_text(l):
    return f"\u201c{l['line']}\u201d" if l["kind"] == "quote" else l["line"]


def cues(lines, timings):
    """Caption cues: one per line, long lines split with the time shared in proportion to length."""
    out = []
    for l, t in zip(lines, timings):
        pieces = _chunks(caption_text(l))
        total = sum(len(p) for p in pieces)
        start, dur = t["start"], t["end"] - t["start"]
        for p in pieces:
            d = dur * len(p) / total
            out.append({"start": round(start, 3), "end": round(start + d, 3), "text": p})
            start += d
    return out


def _ts(x):
    ms = int(round(x * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}.{ms % 1000:03d}"


def vtt(lines, timings):
    body = "\n\n".join(f"{i}\n{_ts(c['start'])} --> {_ts(c['end'])}\n{c['text']}"
                        for i, c in enumerate(cues(lines, timings), 1))
    return "WEBVTT\n\n" + body + "\n"


def check():
    scripts = [check_script(load(s)) for s in slugs()]
    manifest = load_manifest()
    if manifest is not None:
        check_media(scripts, manifest)
    return scripts, manifest


# ── rendering ─────────────────────────────────────────────────────────────

class _Passages:
    """(id, visible text) for every element with an id in a profile fragment."""

    def __init__(self, fragment):
        from html.parser import HTMLParser
        found, stack = [], []

        class P(HTMLParser):
            def handle_starttag(self, tag, attrs):
                a = dict(attrs)
                stack.append([tag, a.get("id"), []])

            def handle_endtag(self, tag):
                while stack:
                    t, i, buf = stack.pop()
                    text = "".join(buf)
                    if stack:
                        stack[-1][2].append(text)
                    if i:
                        found.append((i, norm(text)))
                    if t == tag:
                        break

            def handle_data(self, data):
                if stack:
                    stack[-1][2].append(data)

        P(convert_charrefs=True).feed(fragment)
        # smallest element first, so a link points at the paragraph, not the whole section
        self.items = sorted(found, key=lambda x: len(x[1]))

    def find(self, sentence):
        s = plain(sentence).strip('"').rstrip(".")
        for i, text in self.items:
            if s and s in plain(text):
                return i
        return None


def voice_meta():
    with open(VOICE, encoding="utf-8") as f:
        return json.load(f)


def label(name):
    return f"AI narration · synthetic voice · not the voice of {name}"


def _mmss(s):
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"


def _transcript(d, part, passages, key):
    items = []
    for l in d[part]:
        text = E(l["line"])
        if l["kind"] == "quote":
            body = f'<q class="ls-q">{text}</q>'
        elif l["kind"] in ("question", "transition"):
            body = f"<em>{text}</em>"
        else:
            body = text
        src = ""
        if l.get("copy_md_sentence") and passages is not None:
            pid = passages.find(l["copy_md_sentence"])
            if pid:
                src = f' <a class="ls-src" href="#{E(pid)}">source</a>'
        items.append(f"<li>{body}{src}</li>")
    return "\n".join(items)


def media_paths(slug, base):
    return {k: f"{base}/{slug}-{k}" for k in ("guide.mp3", "short.mp3", "short.mp4", "short-poster.jpg",
                                               "guide.vtt", "short.vtt")}


def section(d, manifest, base, passages=None):
    slug, name = d["slug"], d["name"]
    g, s = manifest["files"][f"{slug}-guide"], manifest["files"][f"{slug}-short"]
    m = media_paths(slug, base)
    v = voice_meta()
    track = lambda vtt: f'<track kind="captions" srclang="en" label="English" src="{E(vtt)}" default>'
    return f'''<section class="listen" id="listen" aria-labelledby="listen-h">
<p class="ls-kick">Listen and watch</p>
<h2 id="listen-h">Hear this story in two minutes, or one</h2>
<p class="ls-label">{E(label(name))}</p>
<p class="ls-lede">Every sentence you will hear comes from this page, and the transcripts below link
each one to the passage it comes from. Quotations are read by the same synthetic voice and are
marked as quotations.</p>
<div class="ls-grid">
  <div class="ls-item">
    <h3 class="ls-h" id="ls-guide-h">Audio guide <span class="ls-len">{_mmss(g["duration_s"])}</span></h3>
    <audio controls preload="none" aria-labelledby="ls-guide-h"><source src="{E(m["guide.mp3"])}" type="audio/mpeg">{track(m["guide.vtt"])}</audio>
    <p class="ls-dl"><a href="{E(m["guide.mp3"])}" download>Download the audio guide (MP3)</a></p>
  </div>
  <div class="ls-item">
    <h3 class="ls-h" id="ls-short-h">Short <span class="ls-len">{_mmss(s["duration_s"])}</span></h3>
    <audio controls preload="none" aria-labelledby="ls-short-h"><source src="{E(m["short.mp3"])}" type="audio/mpeg">{track(m["short.vtt"])}</audio>
    <p class="ls-dl"><a href="{E(m["short.mp3"])}" download>Download the short (MP3)</a></p>
  </div>
  <div class="ls-item ls-video">
    <h3 class="ls-h" id="ls-video-h">Video short, with captions <span class="ls-len">{_mmss(s["video"]["duration_s"])}</span></h3>
    <video controls preload="none" playsinline width="{s["video"]["width"]}" height="{s["video"]["height"]}" poster="{E(m["short-poster.jpg"])}" aria-labelledby="ls-video-h"><source src="{E(m["short.mp4"])}" type="video/mp4">{track(m["short.vtt"])}</video>
    <p class="ls-dl"><a href="{E(m["short.mp4"])}" download>Download the video (MP4)</a></p>
  </div>
</div>
<details class="ls-tr">
  <summary>Read the transcript of the audio guide</summary>
  <ol class="ls-lines">
{_transcript(d, "guide", passages, "guide")}
  </ol>
</details>
<details class="ls-tr">
  <summary>Read the transcript of the short and the video</summary>
  <ol class="ls-lines">
{_transcript(d, "short", passages, "short")}
  </ol>
  <p class="ls-imgs">Images in the video: {"; ".join(E(i["credit"]) for i in s["video"]["images"])}.</p>
</details>
<p class="ls-credit">{E(v["credit"])} The voice is one of 904 reader voices in that collection, each
identified only by a number; nothing here imitates {E(name)}. A script checks every sentence against this
page before any audio is made; a person on the museum&rsquo;s team should still listen before it is published.</p>
</section>'''


def site_section(slug, scripts, manifest, fragment):
    if manifest is None:
        return ""
    d = next(x for x in scripts if x["slug"] == slug)
    return "\n" + section(d, manifest, f"media/{slug}/listen", _Passages(fragment))


def write_media(out_dir, d, manifest):
    """Copy one inductee's narration media into out_dir and write its two caption files."""
    os.makedirs(out_dir, exist_ok=True)
    slug = d["slug"]
    for part in RANGES:
        m = manifest["files"][f"{slug}-{part}"]
        for kind in ("audio", "video", "poster"):
            if kind in m:
                shutil.copy2(os.path.join(NARR, m[kind]["file"]), os.path.join(out_dir, os.path.basename(m[kind]["file"])))
        with open(os.path.join(out_dir, f"{slug}-{part}.vtt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(vtt(d[part], m["lines"]))


def copy_site_media(site, scripts, manifest):
    if manifest is None:
        return
    for d in scripts:
        write_media(os.path.join(site, "media", d["slug"], "listen"), d, manifest)


WP_CSS = """.ihh-listen{--ink:#1f1a17;--muted:#5a5048;--accent:#8b2a1d;--rule:#c3b293;--paper:#fbf7ef;
font:400 1.05rem/1.6 Georgia,'Times New Roman',serif;color:var(--ink);max-width:62rem;margin:2rem auto}
.ihh-listen *{box-sizing:border-box}.ihh-listen h2{font-size:1.6rem;line-height:1.25;margin:.2rem 0 .6rem}
.ihh-listen h3{font-size:1.05rem;margin:0 0 .4rem}.ihh-listen a{color:var(--accent)}
.ihh-listen .ls-kick{margin:0;font-size:.75rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
.ihh-listen .ls-label{display:inline-block;margin:.2rem 0 .6rem;padding:.25rem .6rem;background:var(--ink);color:#fbf6ee;font:600 .85rem/1.4 Arial,sans-serif}
.ihh-listen .ls-lede,.ihh-listen .ls-credit,.ihh-listen .ls-imgs{color:var(--muted);font-size:.9rem}
.ihh-listen .ls-grid{display:grid;gap:1.2rem;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr));margin:1rem 0}
.ihh-listen .ls-item{border:1px solid var(--rule);background:var(--paper);padding:1rem}
.ihh-listen audio{width:100%}.ihh-listen video{display:block;width:100%;max-width:360px;height:auto;background:#000}
.ihh-listen .ls-len{font-weight:400;color:var(--muted)}
.ihh-listen details{margin:.6rem 0;border:1px solid var(--rule);padding:.6rem 1rem}.ihh-listen summary{cursor:pointer;min-height:24px}
.ihh-listen .ls-dl a,.ihh-listen .ls-src{display:inline-block;min-height:24px}
"""


def wp_block(d, manifest, passages=None):
    return (f"<!-- LISTEN: {E(d['name'])}. Paste into ONE WordPress Custom HTML block. No JavaScript. "
            f"Upload the files in media/listen/ to the Media Library first and replace each media/listen/ path below. "
            f"Generated by tools/narration.py from inductees/{d['slug']}/narration.json and site-data/narration/manifest.json. -->\n"
            f'<div class="ihh-listen">\n<style>\n{WP_CSS}</style>\n'
            + section(d, manifest, "media/listen", passages) + "\n</div>\n")


def write_handover(handover):
    scripts, manifest = check()
    if manifest is None:
        raise CheckError("no narration audio yet; run tools/narration_audio.py")
    for d in scripts:
        out = os.path.join(handover, d["slug"])
        write_media(os.path.join(out, "media", "listen"), d, manifest)
        with open(os.path.join(ROOT, "inductees", d["slug"], "copy.html"), encoding="utf-8") as f:
            passages = _Passages(f.read())
        with open(os.path.join(out, f"listen-{d['slug']}.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(wp_block(d, manifest, passages))


if __name__ == "__main__":
    try:
        scripts, manifest = check()
    except CheckError as e:
        sys.exit(f"ERROR {e}")
    n = sum(len(d[p]) for d in scripts for p in RANGES)
    media = "audio and video match the manifest" if manifest else "no audio yet"
    print(f"narration: {len(scripts)} inductees, {n} lines, every line traced to copy.md; {media}")
    if "--handover" in sys.argv[1:]:
        write_handover(os.path.join(ROOT, "handover"))
