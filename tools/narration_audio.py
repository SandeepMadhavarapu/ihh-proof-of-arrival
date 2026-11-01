#!/usr/bin/env python3
"""Record the narration (audio, and the vertical video shorts) from inductees/<slug>/narration.json.

    python3 tools/narration_audio.py --voice DIR [slug ...]

Run by hand, not by the rebuild: speech synthesis is not byte-for-byte repeatable, so instead of
regenerating the media the build checks it. Every file's SHA-256, and the SHA-256 of the exact
script it was made from, go into site-data/narration/manifest.json; tools/narration.py refuses to
build if a script changes without new audio, or if a media file changes without the manifest.

The voice is Piper (https://github.com/OHF-voice/piper1-gpl) with the "LibriTTS (high)" voice,
trained on LibriTTS: audiobook speech read by LibriVox volunteers, published under CC BY 4.0
(details and exact wording in site-data/narration/voice.json). It is one of that voice's 904
reader voices, each identified in the corpus only by a number. It is not, and does not imitate, any inductee or any famous person.
--voice is the folder holding en-us-libritts-high.onnx and its .json, as unpacked from
https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-libritts-high.tar.gz
(the model is about 120 MB and is not committed; its SHA-256 is checked against voice.json).

Each line is spoken separately, so every caption's timing is measured from the real recording.
The words spoken are the words on the page. The only change is SPOKEN below: a short, fixed list
of respellings so the voice pronounces names and numbers the way a person reading aloud would;
the transcript and captions always show the original words.
"""
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import narration as N  # noqa: E402

SPEAKER = 0          # LibriTTS speaker id 3922 in the voice's own speaker map (its first voice)
RATE = 22050
GAP, QUOTE_GAP, LEAD, TAIL = 0.35, 0.6, 0.3, 0.6
SPOKEN = [  # (written, spoken): pronunciation only; never changes meaning
    ("Löb Strauß", "Lerb Strauss"), ("Strauß", "Strauss"), ("Württemberg", "Wurttemberg"),
    ("Ieoh-ming Pe", "Yoh-ming Pay"), ("Tsuyee Pei", "Tsoo-yee Pay"), ("I. M. Pei", "I. M. Pay"), ("Pei", "Pay"),
    ("\"Pe,\"", "\"Pay,\""), ("Antheil", "Ant-hile"), ("Kiesler", "Keesler"),
    ("2,292,387", "two, two nine two, three eight seven"), ("Patent No. 139,121", "Patent Number one three nine, one two one"),
    ("& Company", "and Company"), ("1890s", "eighteen-nineties"), ("1870s", "eighteen-seventies"),
    ("YMCA", "Y.M.C.A."), ("D.C.", "D.C."),
]
W, H = 1080, 1920
PAPER, INK, CREAM, ACCENT, MUTED = (243, 235, 221), (33, 26, 18), (251, 246, 238), (140, 43, 27), (95, 78, 58)
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
LIVE = "https://sandeepmadhavarapu.github.io/ihh-proof-of-arrival"


def spoken(text):
    for a, b in SPOKEN:
        text = text.replace(a, b)
    return text


def sha(path):
    return N.file_sha(path)


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def load_voice(folder):
    from piper import PiperVoice
    with open(N.VOICE, encoding="utf-8") as f:
        meta = json.load(f)
    onnx = os.path.join(folder, meta["model"]["file"])
    if sha(onnx) != meta["model"]["sha256"]:
        sys.exit(f"{onnx}: SHA-256 differs from site-data/narration/voice.json; refusing to record with another voice")
    return PiperVoice.load(onnx, config_path=onnx + ".json"), meta


def say(voice, text, path):
    from piper import SynthesisConfig
    with wave.open(path, "wb") as w:
        voice.synthesize_wav(spoken(text), w, syn_config=SynthesisConfig(speaker_id=SPEAKER))
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def silence(path, seconds):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"\x00\x00" * int(round(seconds * RATE)))
    return int(round(seconds * RATE)) / RATE


def record(voice, lines, out_mp3, tmp):
    """Speak each line, join them with pauses, normalise loudness, encode MP3. Returns timings."""
    parts, timings, t = [], [], 0.0
    p = os.path.join(tmp, "lead.wav")
    t += silence(p, LEAD)
    parts.append(p)
    for i, l in enumerate(lines):
        if i:
            p = os.path.join(tmp, f"gap{i}.wav")
            t += silence(p, QUOTE_GAP if l["kind"] == "quote" or lines[i - 1]["kind"] == "quote" else GAP)
            parts.append(p)
        p = os.path.join(tmp, f"line{i}.wav")
        d = say(voice, l["line"], p)
        timings.append({"start": round(t, 3), "end": round(t + d, 3)})
        t += d
        parts.append(p)
    p = os.path.join(tmp, "tail.wav")
    t += silence(p, TAIL)
    parts.append(p)
    joined = os.path.join(tmp, "joined.wav")
    with wave.open(joined, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        for p in parts:
            with wave.open(p) as w:
                assert w.getframerate() == RATE and w.getnchannels() == 1
                out.writeframes(w.readframes(w.getnframes()))
    run(["ffmpeg", "-y", "-i", joined, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-ac", "1",
         "-c:a", "libmp3lame", "-b:a", "64k", "-map_metadata", "-1", "-id3v2_version", "0", "-write_xing", "0", out_mp3])
    return timings, round(t, 3), joined


# ── the vertical video short ──────────────────────────────────────────────

def eligible_images(slug):
    """Images on the profile whose rights determination says usable, with nothing left to confirm."""
    out = []
    with open(os.path.join(ROOT, "inductees", slug, "media-manifest.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            web = os.path.join(ROOT, "inductees", slug, "media", "web", os.path.splitext(r["filename"])[0] + ".jpg")
            if (r["our_rights_determination"].startswith("Usable") and "TO CONFIRM" not in r["status"].upper()
                    and os.path.isfile(web)):
                out.append({"file": os.path.basename(web), "path": web, "credit": r["required_credit"].strip(),
                            "title": r["title"].strip()})
    seen, uniq = set(), []
    for i in out:
        if i["file"] not in seen:
            seen.add(i["file"])
            uniq.append(i)
    return uniq


def _font(path, size):
    from PIL import ImageFont
    return ImageFont.truetype(path, size)


def _wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def frame(name, image, caption, path, end_card=False, slug=""):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    # persistent label band
    d.rectangle([0, 0, W, 190], fill=INK)
    d.text((W // 2, 62), "AI narration · synthetic voice", font=_font(SANS_B, 44), fill=CREAM, anchor="mm")
    d.text((W // 2, 128), f"not the voice of {name}", font=_font(SANS, 40), fill=CREAM, anchor="mm")
    d.text((W // 2, 262), name, font=_font(SERIF_B, 62), fill=INK, anchor="mm")
    d.text((W // 2, 322), "Student prototype for the Immigrant Hall of Honor", font=_font(SANS, 28), fill=MUTED, anchor="mm")
    if end_card:
        f = _font(SERIF, 54)
        y = 760
        for line in _wrap(d, "Every line comes from the museum's sourced profile:", f, 900):
            d.text((W // 2, y), line, font=f, fill=INK, anchor="mm")
            y += 74
        y += 40
        host, _, path_ = LIVE.replace("https://", "").partition("/")
        for line in (host, f"/{path_}/{slug}.html"):
            d.text((W // 2, y), line, font=_font(SANS_B, 40), fill=ACCENT, anchor="mm")
            y += 58
        y += 60
        for line in _wrap(d, "Captions, a full transcript and every source are on that page.", _font(SANS, 34), 900):
            d.text((W // 2, y), line, font=_font(SANS, 34), fill=MUTED, anchor="mm")
            y += 46
    else:
        pic = Image.open(image["path"]).convert("RGB")
        box_w, box_h = 940, 680
        pic.thumbnail((box_w, box_h))
        x0, y0 = (W - pic.width) // 2, 380 + (box_h - pic.height) // 2
        d.rectangle([x0 - 10, y0 - 10, x0 + pic.width + 10, y0 + pic.height + 10], fill=(255, 255, 255), outline=(138, 117, 88), width=2)
        im.paste(pic, (x0, y0))
        cf = _font(SANS, 26)
        cy = 380 + box_h + 40
        for line in _wrap(d, "Image: " + image["credit"], cf, 960)[:2]:
            d.text((W // 2, cy), line, font=cf, fill=MUTED, anchor="mm")
            cy += 34
    if caption:
        f = _font(SANS_B, 56)
        lines = _wrap(d, caption, f, 960)
        if len(lines) > 4:
            raise SystemExit(f"caption too long for the video frame: {caption!r}")
        lh = 70
        box_h = lh * len(lines) + 50
        top = 1600 - box_h  # bottom of the box sits 320 px above the bottom edge; 4 lines reach y=1270
        d.rounded_rectangle([40, top, W - 40, 1600], radius=18, fill=INK)
        for i, line in enumerate(lines):
            d.text((W // 2, top + 25 + lh * i + lh // 2), line, font=f, fill=CREAM, anchor="mm")
    im.save(path, quality=90)


def video(name, slug, cues, timings_end, audio_mp3, out_mp4, poster, tmp):
    imgs = eligible_images(slug)
    if not imgs:
        raise SystemExit(f"{slug}: no image is cleared for reuse; cannot make a video")
    facts = [c for c in cues]
    per = max(1, -(-len(facts) // len(imgs)))  # cues per image, rounded up
    concat = []
    prev = 0.0
    for i, c in enumerate(cues):
        img = imgs[min(i // per, len(imgs) - 1)]
        p = os.path.join(tmp, f"v{i:03d}.png")
        frame(name, img, c["text"], p)
        end = cues[i + 1]["start"] if i + 1 < len(cues) else timings_end
        concat.append((p, end - prev))
        prev = end
    used = []
    for i in range(len(cues)):
        img = imgs[min(i // per, len(imgs) - 1)]
        if img not in used:
            used.append(img)
    endp = os.path.join(tmp, "end.png")
    frame(name, None, "", endp, end_card=True, slug=slug)
    concat.append((endp, 3.0))
    listing = os.path.join(tmp, "frames.txt")
    with open(listing, "w") as f:
        for p, dur in concat:
            f.write(f"file '{p}'\nduration {dur:.3f}\n")
        f.write(f"file '{concat[-1][0]}'\n")
    total = prev + 3.0
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listing, "-i", audio_mp3,
         "-filter_complex", f"[1:a]apad=whole_dur={total:.3f}[a]", "-map", "0:v", "-map", "[a]",
         "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "30", "-tune", "stillimage",
         "-c:a", "aac", "-b:a", "64k", "-t", f"{total:.3f}", "-movflags", "+faststart", "-map_metadata", "-1", out_mp4])
    shutil.copy2(concat[0][0], poster.replace(".jpg", ".png"))
    from PIL import Image
    Image.open(concat[0][0]).convert("RGB").resize((540, 960)).save(poster, quality=82)
    os.remove(poster.replace(".jpg", ".png"))
    return [{"file": u["file"], "credit": u["credit"]} for u in used], round(total, 3)


def main(argv):
    if "--voice" not in argv:
        sys.exit(__doc__)
    folder = argv[argv.index("--voice") + 1]
    only = [a for a in argv if a in N.slugs()] or N.slugs()
    voice, meta = load_voice(folder)
    for d in (N.check_script(N.load(s)) for s in only):
        pass
    os.makedirs(os.path.join(N.NARR, "audio"), exist_ok=True)
    os.makedirs(os.path.join(N.NARR, "video"), exist_ok=True)
    manifest = N.load_manifest() or {"voice": "voice.json", "files": {}}
    for slug in only:
        d = N.load(slug)
        for part in ("guide", "short"):
            key = f"{slug}-{part}"
            with tempfile.TemporaryDirectory() as tmp:
                mp3 = os.path.join(N.NARR, "audio", f"{key}.mp3")
                timings, total, _ = record(voice, d[part], mp3, tmp)
                entry = {"slug": slug, "part": part, "script_sha256": N.script_sha(d[part]),
                         "spoken": [spoken(l["line"]) for l in d[part]],
                         "lines": timings, "duration_s": total,
                         "audio": {"file": f"audio/{key}.mp3", "sha256": sha(mp3), "bytes": os.path.getsize(mp3)}}
                if part == "short":
                    mp4 = os.path.join(N.NARR, "video", f"{key}.mp4")
                    poster = os.path.join(N.NARR, "video", f"{key}-poster.jpg")
                    cues = N.cues(d[part], timings)
                    used, vtotal = video(d["name"], slug, cues, total, mp3, mp4, poster, tmp)
                    entry["video"] = {"file": f"video/{key}.mp4", "sha256": sha(mp4), "bytes": os.path.getsize(mp4),
                                      "duration_s": vtotal, "width": W, "height": H, "images": used}
                    entry["poster"] = {"file": f"video/{key}-poster.jpg", "sha256": sha(poster)}
                manifest["files"][key] = entry
                print(f"{key}: {total:.1f} s audio" + (f", video {entry['video']['bytes'] / 1e6:.1f} MB" if "video" in entry else ""))
    with open(N.MANIFEST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
