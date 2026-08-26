#!/usr/bin/env python3
"""Put an Instagram post on the site's Recent-posts strip.

    python3 dev/add-post.py <post-url> --date 2026-08-24 \
        --caption "Short version for the card" \
        --alt "What the picture shows, for someone who cannot see it"

Downloads the post's picture, resizes it to a web-sized WebP in assets/posts/,
works out whether it is a carousel or a reel, and writes the entry into
assets/posts.json. Run it again on the same URL to update that entry in place.

WHAT THIS IS AND IS NOT
This is a hand-run helper, not a pipeline. It fetches one post, when you ask it
to, from your own machine, for your own campaign's account. That is a different
thing from a scheduled job hammering Instagram from a datacenter IP, which is
what would actually risk the account and is why the site does not have one. Keep
it that way: do not put this in a cron job or a GitHub Action.

It reads the public embed page, which is the same thing your browser loads when
a post is embedded. Instagram can change that page's shape at any time and this
will break. When it does, the fix is a regex, and the fallback is to save the
picture by hand and edit assets/posts.json yourself. Nothing here is load-bearing
for the site: posts.json is plain data that a human can always write.

CAPTION AND ALT ARE YOURS TO WRITE
Deliberately not scraped. The card wants a trimmed line, not the full post with
its hashtags, and alt text is the only version of a picture some readers get, so
it is worth a human sentence. Leave --alt off and the tool will complain, loudly,
and write the entry anyway with an empty string so you can fill it in later.

Stdlib only, plus cwebp (brew install webp).
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_JSON = ROOT / "assets" / "posts.json"
POSTS_DIR = ROOT / "assets" / "posts"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Safari/605.1.15")


def die(msg):
    sys.exit("add-post: " + msg)


def get(url, timeout=30):
    """Fetch via curl rather than urllib.

    Not a style choice. The python.org build of Python on macOS ships without a
    usable CA bundle, so urllib raises CERTIFICATE_VERIFY_FAILED on every HTTPS
    call until someone runs Install Certificates.command. curl uses the system
    trust store, is on every Mac, and sidesteps the whole class of problem.
    """
    try:
        r = subprocess.run(
            ["curl", "-sSL", "--fail", "--max-time", str(timeout), "-A", UA, url],
            capture_output=True, check=True,
        )
    except FileNotFoundError:
        die("curl not found, which should not be possible on macOS.")
    except subprocess.CalledProcessError as e:
        die("fetch failed (curl exit %s) for %s\n  %s"
            % (e.returncode, url, e.stderr.decode("utf-8", "replace").strip()))
    return r.stdout


def shortcode_of(url):
    m = re.search(r"/(?:p|reel|tv)/([A-Za-z0-9_-]+)", url)
    if not m:
        die("could not find a shortcode in %r (expected .../p/<code>/ "
            "or .../reel/<code>/)" % url)
    return m.group(1)


def scrape(shortcode):
    """Pull picture URL, size and kind out of the post's embed page."""
    html = get("https://www.instagram.com/p/%s/embed/captioned/" % shortcode)
    html = html.decode("utf-8", "replace")

    # The blob is JSON inside JSON, so quotes and slashes arrive double-escaped.
    # Matching each field rather than parsing the whole object keeps this working
    # when Instagram reshuffles the structure around it, which it does.
    m = re.search(r'display_url\\*":\\*"([^"]+?)\\*"', html)
    if not m:
        die("no display_url in the embed for %s. Either the post is not public, "
            "or Instagram changed the page. Save the picture by hand and edit "
            "assets/posts.json instead." % shortcode)
    # URLs never contain backslashes, so dropping every one un-escapes the path.
    img_url = re.sub(r"\\+", "", m.group(1))

    d = re.search(r"dimensions[^0-9]{0,40}?height[^0-9]{0,6}(\d+)"
                  r"[^0-9]{0,25}?width[^0-9]{0,6}(\d+)", html)
    src_h, src_w = (int(d.group(1)), int(d.group(2))) if d else (0, 0)

    is_video = bool(re.search(r'is_video\\*":\s*true', html))
    is_carousel = "edge_sidecar_to_children" in html
    # Reel beats carousel: a video with multiple frames is still a video to a
    # reader, and the play mark is the more useful of the two to show.
    kind = "reel" if is_video else ("carousel" if is_carousel else "image")

    return img_url, src_w, src_h, kind


def convert(raw, out_path, width, quality):
    tmp = out_path.with_suffix(".src")
    tmp.write_bytes(raw)
    try:
        subprocess.run(
            ["cwebp", "-quiet", "-q", str(quality), "-resize", str(width), "0",
             str(tmp), "-o", str(out_path)],
            check=True,
        )
    except FileNotFoundError:
        die("cwebp not found. Install it with:  brew install webp")
    except subprocess.CalledProcessError as e:
        die("cwebp failed (exit %s) on %s" % (e.returncode, tmp))
    finally:
        tmp.unlink(missing_ok=True)


def load_posts():
    if not POSTS_JSON.exists():
        return []
    try:
        data = json.loads(POSTS_JSON.read_text())
    except json.JSONDecodeError as e:
        die("%s is not valid JSON (%s). Fix it before running this." %
            (POSTS_JSON.name, e))
    return data if isinstance(data, list) else []


def main():
    ap = argparse.ArgumentParser(
        description="Add an Instagram post to assets/posts.json.")
    ap.add_argument("url", help="the post URL, e.g. https://www.instagram.com/p/ABC123/")
    ap.add_argument("--date", required=True, metavar="YYYY-MM-DD",
                    help="the date on the post. Required: it is printed on the "
                         "card and a wrong one is worse than none.")
    ap.add_argument("--caption", default="",
                    help="short line for the card. Trim it yourself; the full "
                         "post with hashtags does not fit.")
    ap.add_argument("--alt", default="",
                    help="what the picture shows, for readers who cannot see it.")
    ap.add_argument("--width", type=int, default=640,
                    help="output width in px (default 640, which covers a ~320px "
                         "tile on a retina screen)")
    ap.add_argument("--quality", type=int, default=80, help="WebP quality (default 80)")
    ap.add_argument("--dry-run", action="store_true",
                    help="say what would happen, write nothing")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        die("--date must look like 2026-08-24, got %r" % args.date)

    code = shortcode_of(args.url)
    canonical = "https://www.instagram.com/deflockcobb/%s/%s/" % (
        "reel" if "/reel/" in args.url else "p", code)

    print("fetching  %s" % code)
    img_url, src_w, src_h, kind = scrape(code)
    print("  kind    %s%s" % (kind, "  (source %dx%d)" % (src_w, src_h) if src_w else ""))

    out_name = "%s-%s.webp" % (args.date, code)
    out_path = POSTS_DIR / out_name
    rel = "assets/posts/" + out_name

    out_w = min(args.width, src_w) if src_w else args.width
    out_h = round(src_h * out_w / src_w) if src_w and src_h else 0

    if args.dry_run:
        print("  would write %s  (%dx%d)" % (rel, out_w, out_h))
        print("  would %s entry in %s" % (
            "update" if any(p.get("url") == canonical for p in load_posts()) else "add",
            POSTS_JSON.name))
        return

    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    print("  saving  %s" % rel)
    convert(get(img_url, timeout=60), out_path, out_w, args.quality)
    kb = out_path.stat().st_size / 1024
    print("  wrote   %.0f KB" % kb)

    entry = {
        "url": canonical,
        "date": args.date,
        "kind": kind,
        "caption": args.caption,
        "img": rel,
        "w": out_w,
        "h": out_h,
        "alt": args.alt,
    }

    posts = load_posts()
    # Keyed on the canonical URL so re-running replaces rather than duplicates.
    # Existing caption and alt survive a re-run that does not supply them, since
    # those are the hand-written parts and losing them to a refetch would be rude.
    for i, p in enumerate(posts):
        if p.get("url") == canonical:
            entry["caption"] = args.caption or p.get("caption", "")
            entry["alt"] = args.alt or p.get("alt", "")
            posts[i] = entry
            break
    else:
        posts.append(entry)

    posts.sort(key=lambda p: str(p.get("date", "")), reverse=True)
    POSTS_JSON.write_text(json.dumps(posts, indent=2, ensure_ascii=False) + "\n")
    print("  updated %s  (%d entries, newest first)" % (POSTS_JSON.name, len(posts)))

    if not entry["caption"]:
        print("\n  ! no caption. The card will be dropped until it has one.")
    if not entry["alt"]:
        print("\n  ! NO ALT TEXT. This is the only version of the picture a screen")
        print("    reader gets. Add it in %s before you commit." % POSTS_JSON.name)
    if len([p for p in posts if p.get("caption")]) > 4:
        print("\n  note: the strip shows the newest 4. Older entries stay in the")
        print("        file but will not render.")


if __name__ == "__main__":
    main()
