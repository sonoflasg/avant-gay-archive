#!/usr/bin/env python3
"""Capture X profile pictures for persona entries into website/pfp/.

Usage:
  python3 scripts/pfp_capture.py profiles.json

profiles.json is the public X API users response (e.g. from GET /2/users/by
with user.fields=profile_image_url,protected), or a list of
{"username": ..., "profile_image_url": ..., "protected": false}.

For every entry with an `X: @handle` line, the matching picture is downloaded
at 400x400, centre-cropped, resized to 128px, saved as website/pfp/<handle>.jpg
and recorded in website/pfp/manifest.json (handle, source URL, capture time in
Melbourne time). Protected accounts are recorded without an image. The site only
ever serves these local copies; it never hotlinks pbs.twimg.com.
"""
import datetime
import io
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image  # pip install pillow (only needed for capture, not for build)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402

OUT = ROOT / "website" / "pfp"


def main(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    users = raw.get("data", raw) if isinstance(raw, dict) else raw
    prof = {u["username"].lower(): u for u in users}
    old = {}
    mf = OUT / "manifest.json"
    if mf.exists():
        old = {i["handle"].lower(): i for i in json.loads(mf.read_text(encoding="utf-8"))["items"]}
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=11)))
    items = []
    for p in sorted(build.collect_files()):
        m = build.XHANDLE.search(p.read_text(encoding="utf-8", errors="replace"))
        if not m:
            continue
        h = m.group(1)
        rel = str(p.relative_to(ROOT))
        prev = old.get(h.lower(), {})
        item = {"entry": rel, "handle": h, "confirmed_by": prev.get("confirmed_by", ""), "profile": f"https://x.com/{h}"}
        u = prof.get(h.lower())
        if u is None:
            if prev:
                prev["entry"] = rel
                items.append(prev)
            continue
        if u.get("protected"):
            item.update(image=None, note="no image: account is protected")
            items.append(item)
            continue
        src = u["profile_image_url"].replace("_normal.", "_400x400.")
        data = subprocess.run(["curl", "-sfL", src], capture_output=True).stdout
        im = Image.open(io.BytesIO(data)).convert("RGB")
        w, hh = im.size
        s = min(w, hh)
        im = im.crop(((w - s) // 2, (hh - s) // 2, (w - s) // 2 + s, (hh - s) // 2 + s)).resize((128, 128), Image.LANCZOS)
        name = re.sub(r"[^a-z0-9_]", "", h.lower()) + ".jpg"
        im.save(OUT / name, "JPEG", quality=78, optimize=True, progressive=True)
        item.update(image=f"pfp/{name}", source_url=src, captured=now.strftime("%d/%m/%Y %H:%M AEDT"))
        items.append(item)
    mf.write_text(json.dumps({"note": "X profile pictures captured from public profiles. Images may be artworks by other artists. The site serves only these local copies.", "items": items}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{sum(1 for i in items if i.get('image'))} pictures, {len(items)} handles → {mf.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1])
