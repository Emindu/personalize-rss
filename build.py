#!/usr/bin/env python3
"""Build an RSS 2.0 feed (plus simple HTML pages) from Markdown notes.

Usage:
    python build.py [--notes notes] [--out _site] [--site-url https://user.github.io/repo/]

Each note is a Markdown file in notes/ (subfolders allowed). Optional front matter:

    ---
    title: My note
    date: 2026-11-16 08:30
    tags: [finance, ideas]
    summary: One or two sentences for the preview.
    ---
"""

import argparse
import html
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

import markdown

FEED_TITLE = os.environ.get("FEED_TITLE", "My Reading")
FEED_DESCRIPTION = os.environ.get("FEED_DESCRIPTION", "Notes and articles I saved myself")
FEED_LANGUAGE = os.environ.get("FEED_LANGUAGE", "en")
MAX_ITEMS = int(os.environ.get("FEED_MAX_ITEMS", "50"))

FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def parse_front_matter(text):
    """Minimal 'key: value' front matter parser (supports [a, b] lists)."""
    meta = {}
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return meta, text
    for line in m.group(1).splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
        else:
            value = value.strip("'\"")
        meta[key.strip().lower()] = value
    return meta, text[m.end():]


def parse_date(value):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    try:
        dt = datetime.fromisoformat(value)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def file_date(path):
    """Last git commit time of the file (CI checkouts reset mtimes), else mtime."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(path)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        if out:
            return datetime.fromisoformat(out).astimezone(timezone.utc)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        pass
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[\s_-]+", "-", text) or "note"


def first_paragraph(body_html, limit=300):
    m = re.search(r"<p>(.*?)</p>", body_html, re.DOTALL)
    text = re.sub(r"<[^>]+>", "", m.group(1) if m else body_html)
    text = html.unescape(" ".join(text.split()))
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "…"


def strip_images(body_html):
    """Kindle-friendly: drop <img> tags, keep alt text."""
    return re.sub(
        r'<img[^>]*?alt="([^"]*)"[^>]*>|<img[^>]*>',
        lambda m: f"[{m.group(1)}]" if m.group(1) else "",
        body_html,
    )


def cdata(text):
    return "<![CDATA[" + text.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def load_notes(notes_dir, keep_images):
    notes = []
    for path in sorted(notes_dir.rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(raw)
        if str(meta.get("draft", "")).lower() in ("true", "yes", "1"):
            continue

        title = meta.get("title")
        if not title:
            h1 = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
            title = h1.group(1).strip() if h1 else path.stem.replace("-", " ").replace("_", " ").title()

        body_html = markdown.markdown(body, extensions=["extra", "sane_lists"])
        if not keep_images:
            body_html = strip_images(body_html)
        # Make sure the article starts with its title.
        if not re.match(r"\s*<h1", body_html):
            body_html = f"<h1>{html.escape(title)}</h1>\n{body_html}"

        date = parse_date(str(meta["date"])) if meta.get("date") else None
        date = date or file_date(path)

        rel = path.relative_to(notes_dir)
        tags = meta.get("tags") or meta.get("category") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        if not tags and len(rel.parts) > 1:
            tags = [rel.parts[0]]  # folder name as category

        slug = slugify(meta.get("slug") or str(rel.with_suffix("")).replace(os.sep, "-"))
        notes.append({
            "title": title,
            "slug": slug,
            "guid": f"notes/{rel.as_posix()}",
            "date": date,
            "tags": tags,
            "summary": meta.get("summary") or first_paragraph(body_html.split("</h1>", 1)[-1]),
            "html": body_html,
        })
    notes.sort(key=lambda n: n["date"], reverse=True)
    return notes


def page(title, body, site_url, feed_title):
    return f"""<!doctype html>
<html lang="{FEED_LANGUAGE}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="alternate" type="application/rss+xml" title="{html.escape(feed_title)}" href="{site_url}feed.xml">
<style>
body{{max-width:42rem;margin:2rem auto;padding:0 1rem;font:1.05rem/1.6 Georgia,serif;color:#111;background:#fff}}
a{{color:#0645ad}} .meta{{color:#666;font-size:.9rem}} pre{{overflow:auto;background:#f4f4f4;padding:.75rem}}
li{{margin:.4rem 0}}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def build(notes_dir, out_dir, site_url, keep_images):
    site_url = site_url.rstrip("/") + "/"
    notes = load_notes(notes_dir, keep_images)
    (out_dir / "notes").mkdir(parents=True, exist_ok=True)

    for n in notes:
        meta = f'<p class="meta">{n["date"]:%Y-%m-%d}{" · " + ", ".join(map(html.escape, n["tags"])) if n["tags"] else ""} · <a href="../">all notes</a></p>'
        (out_dir / "notes" / f"{n['slug']}.html").write_text(
            page(n["title"], n["html"] + "\n" + meta, site_url, FEED_TITLE), encoding="utf-8")

    items = "\n".join(
        f'<li><a href="notes/{n["slug"]}.html">{html.escape(n["title"])}</a> '
        f'<span class="meta">{n["date"]:%Y-%m-%d}</span></li>' for n in notes)
    index = (f"<h1>{html.escape(FEED_TITLE)}</h1>\n<p>{html.escape(FEED_DESCRIPTION)}</p>\n"
             f'<p>RSS feed: <a href="feed.xml">{site_url}feed.xml</a></p>\n<ul>\n{items}\n</ul>')
    (out_dir / "index.html").write_text(page(FEED_TITLE, index, site_url, FEED_TITLE), encoding="utf-8")

    now = format_datetime(notes[0]["date"] if notes else datetime.now(timezone.utc))
    xml_items = []
    for n in notes[:MAX_ITEMS]:
        cats = "".join(f"\n      <category>{html.escape(t)}</category>" for t in n["tags"])
        xml_items.append(f"""    <item>
      <title>{html.escape(n["title"])}</title>
      <link>{site_url}notes/{n["slug"]}.html</link>
      <guid isPermaLink="false">{html.escape(n["guid"])}</guid>
      <pubDate>{format_datetime(n["date"])}</pubDate>{cats}
      <description>{cdata(n["summary"])}</description>
      <content:encoded>{cdata(n["html"])}</content:encoded>
    </item>""")

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{html.escape(FEED_TITLE)}</title>
    <link>{site_url}</link>
    <description>{html.escape(FEED_DESCRIPTION)}</description>
    <language>{FEED_LANGUAGE}</language>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{site_url}feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(xml_items)}
  </channel>
</rss>
"""
    (out_dir / "feed.xml").write_text(feed, encoding="utf-8")
    (out_dir / ".nojekyll").write_text("")
    print(f"Built {len(notes)} notes ({min(len(notes), MAX_ITEMS)} in feed) -> {out_dir}/feed.xml")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--notes", default="notes", type=Path)
    ap.add_argument("--out", default="_site", type=Path)
    ap.add_argument("--site-url", default=os.environ.get("SITE_URL", "http://localhost:8000/"))
    ap.add_argument("--keep-images", action="store_true", help="keep <img> tags in the feed")
    args = ap.parse_args()
    if not args.notes.is_dir():
        sys.exit(f"Notes folder not found: {args.notes}")
    build(args.notes, args.out, args.site_url, args.keep_images)


if __name__ == "__main__":
    main()
