#!/usr/bin/env python3
"""Fetch one thumbnail per listing into site/thumbs/<id>.jpg.

Sources: Reverb listings use the public API's photo links; everything else uses
the product page's og:image meta tag. Thumbnails are resized to 360px wide
JPEGs so the board (which embeds them as data URIs) stays small. Existing
thumbs are kept — pass --refresh <id> to refetch one. Run before site.py.
"""
import io
import json
import os
import re
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(HERE, "database.json")
THUMBS = os.path.join(HERE, "site", "thumbs")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
THUMB_W = 360
JPEG_Q = 62


def curl(url, extra=None):
    cmd = ["curl", "-sS", "--max-time", "25", "-L", "-A", UA] + (extra or []) + [url]
    r = subprocess.run(cmd, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def reverb_photo(url):
    m = re.search(r"reverb\.com/item/(\d+)", url)
    if not m:
        return None
    raw = curl("https://api.reverb.com/api/listings/%s" % m.group(1),
               ["-H", "Accept: application/hal+json", "-H", "Accept-Version: 3.0"])
    if not raw:
        return None
    try:
        j = json.loads(raw)
        photos = j.get("photos") or []
        links = (photos[0].get("_links") or {}) if photos else {}
        for key in ("large_crop", "small_crop", "full"):
            if key in links:
                return links[key]["href"]
    except (ValueError, KeyError, IndexError):
        pass
    return None


def og_image(url):
    html = curl(url)
    if not html:
        return None
    text = html.decode("utf-8", errors="ignore")
    m = (re.search(r'property=["\']og:image["\']\s+content=["\']([^"\']+)', text) or
         re.search(r'content=["\']([^"\']+)["\']\s+property=["\']og:image', text))
    if not m:
        return None
    # plain HTTP dies at the egress proxy; these CDNs all serve HTTPS
    return re.sub(r"^http://", "https://", m.group(1).replace("&amp;", "&"))


def make_thumb(img_bytes, out_path):
    im = Image.open(io.BytesIO(img_bytes))
    im = im.convert("RGB")
    w, h = im.size
    if w > THUMB_W:
        im = im.resize((THUMB_W, max(1, round(h * THUMB_W / w))), Image.LANCZOS)
    im.save(out_path, "JPEG", quality=JPEG_Q, optimize=True)


def main():
    refresh = set()
    if "--refresh" in sys.argv:
        refresh = set(sys.argv[sys.argv.index("--refresh") + 1:])
    os.makedirs(THUMBS, exist_ok=True)
    with open(DB) as f:
        db = json.load(f)
    got, skipped, failed = 0, 0, []
    for g in db["guitars"]:
        if g.get("status") in ("SOLD", "EXCLUDED"):
            continue
        out = os.path.join(THUMBS, "%s.jpg" % g["id"])
        if os.path.exists(out) and g["id"] not in refresh:
            skipped += 1
            continue
        url = g.get("url") or ""
        src = reverb_photo(url) if "reverb.com" in url else og_image(url)
        img = curl(src) if src else None
        if img and len(img) > 4000:
            try:
                make_thumb(img, out)
                got += 1
                continue
            except OSError:
                pass
        failed.append(g["id"])
    print("thumbs: %d fetched, %d cached, %d failed %s"
          % (got, skipped, len(failed), failed or ""))


if __name__ == "__main__":
    main()
