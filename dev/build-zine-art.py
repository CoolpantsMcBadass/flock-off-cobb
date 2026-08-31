#!/usr/bin/env python3
"""Rebuild assets/zine/*.webp from the imposed zine sheets.

Run this whenever the creator sends a new revision, after dropping the two PDFs
on assets/zine/deflock-zine-sheet-{1,2}.pdf. It is not a one-off script: doing
this by hand went wrong twice in ways that are genuinely hard to see.

    python3 dev/build-zine-art.py            # rebuild
    python3 dev/build-zine-art.py --check    # report differences, write nothing

Two things this exists to get right.

ORIENTATION. A PDF places a raster under a transformation matrix, so the bytes
stored in the file are not necessarily what prints. On these sheets the plate is
placed mirrored and pole-crowd is placed upside down, and an earlier hand-built
pass shipped both wrong — page 3 and the whole back cover ran left-for-right for
a week without anyone noticing. Every drawing is therefore checked against the
page: its own bounding box is rendered at native resolution and the stored raster
is scored against that render, its mirror and its 180 degree rotation. Whichever
wins is what gets written. If the source ever changes handedness again this
notices on its own.

LIFTING VS RENDERING. Drawings are lifted from the PDF as embedded rasters, not
rendered, so nothing is rescaled on the way in and — more importantly — no type
is baked in. The map is why that matters: its "124 surveillance cameras per
1,000 people" caption is printed over the artwork and is a live overlay in the
page, so a rendered map would show it twice. The plate is the one exception. It
is two rasters stacked at the same origin and only the renderer knows which is
on top, so it is rendered — safe there because no type sits on that panel.

Requires: pdfplumber, Pillow, and poppler's pdfimages (brew install poppler).
"""
import argparse, os, shutil, subprocess, sys, tempfile

import numpy as np
import pdfplumber
from PIL import Image, ImageOps

HERE  = os.path.dirname(os.path.abspath(__file__))
ZINE  = os.path.join(HERE, "..", "assets", "zine")
SHEET = {1: os.path.join(ZINE, "deflock-zine-sheet-1.pdf"),
         2: os.path.join(ZINE, "deflock-zine-sheet-2.pdf")}

# Which drawing is which, keyed by the sheet it lives on and its stored pixel
# size. Sizes are the stable identifier: panel positions move between revisions,
# stored sizes have not. A size that no longer matches is a loud failure rather
# than a silently skipped asset.
DRAWINGS = {
    (1, (790, 510)): "atlanta-map.webp",
    (1, (675, 559)): "cover-camera.webp",
    (1, (600, 314)): "phone-bluetooth.webp",
    (1, (533, 198)): "pole-crowd.webp",
    (2, (360, 254)): "neighborhood.webp",
    (2, (637, 352)): "protest-consent.webp",
    (2, (954, 366)): "reticles.webp",
    (2, (589, 370)): "truck-callouts.webp",
    (2, (744, 300)): "window-watchers.webp",
    (2, (667, 461)): "agents-detain.webp",
}
PLATE = "camera-pole-tall.webp"   # rendered, see the module docstring
BACK  = "back-cover-camera.webp"  # derived from the plate, see cut_back_cover()

# The plate ships mirrored from how the PDF renders it. Both pdfium and poppler
# draw that panel with the camera looking in from the left, and the placement
# matrix agrees with them, but the zine it has to match reads the other way, so
# the artifact wins over the file. Will confirmed this against the printed copy
# on 2026-08-29; do not "fix" it back on the strength of a renderer.
#
# Applied last, after the back cover has been cut, so the fade geometry in
# cut_back_cover() stays measured against the orientation it was measured in and
# the two assets cannot drift apart.
MIRROR = {PLATE, BACK}


def knockout(img):
    """White to a binary alpha, then trim. The recipe the whole set was cut to:
    every asset has hard alpha, and the pages composite them with
    mix-blend-mode:multiply, so partial alpha would double up the paper."""
    img = img.convert("RGB")
    lum = np.array(img.convert("L"))
    a = np.where(lum >= 250, 0, 255).astype("uint8")
    out = Image.fromarray(np.dstack([np.array(img), a]), "RGBA")
    box = out.getbbox()
    return out.crop(box) if box else out


def score(a, b):
    """Mean absolute luma difference at a common size. Small is alike."""
    s = (240, 240)
    A = np.asarray(a.convert("L").resize(s), float)
    B = np.asarray(b.convert("L").resize(s), float)
    return float(np.abs(A - B).mean())


def oriented(raw, page, im):
    """Return the stored raster turned the way the page actually prints it."""
    dpi = round(im["srcsize"][0] / (im["x1"] - im["x0"]) * 72)
    ref = page.crop((im["x0"], im["top"], im["x1"], im["bottom"])) \
              .to_image(resolution=dpi).original
    if ((im["top"] + im["bottom"]) / 2) < page.height / 2:
        ref = ref.rotate(180, expand=True)   # the top row is imposed upside down
    cands = {"as-stored": raw,
             "mirrored":  ImageOps.mirror(raw),
             "rot180":    raw.rotate(180, expand=True)}
    scores = {k: score(ref, v) for k, v in cands.items()}
    best = min(scores, key=scores.get)
    return cands[best], best, scores


def render_plate(page):
    """The plate is two rasters at one origin, so take what the renderer draws."""
    ims = [i for i in page.images if i["x0"] < 210 and i["top"] < 290]
    if len(ims) < 2:
        raise SystemExit("plate: expected two stacked rasters, found %d" % len(ims))
    box = (min(i["x0"] for i in ims), min(i["top"] for i in ims),
           max(i["x1"] for i in ims), max(i["bottom"] for i in ims))
    dpi = round(max(i["srcsize"][0] / (i["x1"] - i["x0"]) * 72 for i in ims))
    return page.crop(box).to_image(resolution=dpi).original.rotate(180, expand=True)


def cut_back_cover(plate):
    """Fade the plate down to just the camera, its mount and the pole.

    Measured against the drawing, so re-check these numbers if it is redrawn: the
    camera's underside is not level, it reaches lower in the middle than on the
    left, and the wall on the right ends lower still. The pole has to survive the
    fade all the way down, hence the full-height column; its shoulders are eased
    or the column leaves two hard vertical seams against the faded scene."""
    W, H = plate.size
    x = np.arange(W)[None, :].astype(float)
    y = np.arange(H)[:, None].astype(float)
    RAMP = 42.0

    start = np.where(x < 200, 500.0, np.where(x < 470, 528.0, 560.0))
    vert = np.clip((start + RAMP - y) / RAMP, 0, 1)

    edge = lambda v, a, b: np.clip((v - a) / (b - a), 0, 1)
    pole = np.broadcast_to(np.minimum(edge(x, 445, 470), 1 - edge(x, 535, 560)), (H, W))

    a = (np.array(plate.split()[3]).astype(float) * np.clip(vert + pole, 0, 1))
    out = plate.copy()
    out.putalpha(Image.fromarray(a.astype("uint8"), "L"))
    return out.crop(out.getbbox())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report what would change; write nothing")
    args = ap.parse_args()

    if not shutil.which("pdfimages"):
        sys.exit("pdfimages not found — brew install poppler")

    tmp = tempfile.mkdtemp(prefix="zine-art-")
    built = {}
    try:
        for n, pdf in SHEET.items():
            if not os.path.exists(pdf):
                sys.exit("missing %s" % pdf)
            subprocess.run(["pdfimages", "-png", "-all", pdf,
                            os.path.join(tmp, "s%d" % n)], check=True)
            raws = {}
            for f in sorted(os.listdir(tmp)):
                if not f.startswith("s%d-" % n):
                    continue
                im = Image.open(os.path.join(tmp, f))
                raws[im.size] = im

            with pdfplumber.open(pdf) as doc:
                page = doc.pages[0]
                for im in page.images:
                    key = (n, tuple(im["srcsize"]))
                    if key not in DRAWINGS:
                        continue
                    raw = raws.get(tuple(im["srcsize"]))
                    if raw is None:
                        sys.exit("no raster for %s" % (key,))
                    turned, how, scores = oriented(raw, page, im)
                    name = DRAWINGS[key]
                    built[name] = knockout(turned)
                    flag = "" if how == "as-stored" else "   <- %s" % how
                    print("%-24s %-9s %s%s" % (
                        name, "%dx%d" % built[name].size, how, flag))
                if n == 1:
                    built[PLATE] = knockout(render_plate(page))
                    print("%-24s %-9s rendered (two stacked rasters)" % (
                        PLATE, "%dx%d" % built[PLATE].size))

        missing = (set(DRAWINGS.values()) | {PLATE}) - set(built)
        if missing:
            sys.exit("not found in the sheets: %s" % ", ".join(sorted(missing)))

        built[BACK] = cut_back_cover(built[PLATE])
        print("%-24s %-9s derived from the plate" % (BACK, "%dx%d" % built[BACK].size))

        for name in MIRROR:
            built[name] = ImageOps.mirror(built[name])
            print("%-24s %-9s mirrored to match the printed zine" % (
                name, "%dx%d" % built[name].size))

        print()
        for name, img in sorted(built.items()):
            dst = os.path.join(ZINE, name)
            old = Image.open(dst).convert("RGBA") if os.path.exists(dst) else None
            if old is not None:
                def flat(i):
                    bg = Image.new("RGBA", i.size, (245, 241, 230, 255))
                    bg.alpha_composite(i)
                    return bg
                d = score(flat(old), flat(img))
                verdict = "unchanged" if d < 3 else "CHANGED"
                print("%-24s %-9s diff %5.1f  %s" % (name, "%dx%d" % img.size, d, verdict))
            else:
                print("%-24s %-9s NEW" % (name, "%dx%d" % img.size))
            if not args.check:
                img.save(dst, "WEBP", quality=82, method=6)
        print("\n%s" % ("checked only, nothing written" if args.check else "written"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
