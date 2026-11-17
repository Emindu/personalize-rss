# personalize-rss

My personal RSS feed, built from Markdown notes and hosted on GitHub Pages.

**Feed URL:** `https://emindu.github.io/personalize-rss/feed.xml`

## Add a note

### Upload page (easiest)

Open `https://emindu.github.io/personalize-rss/upload/`, then:

1. **Settings** (once): paste a [fine-grained GitHub token](https://github.com/settings/personal-access-tokens/new)
   limited to this repo, with **Contents: Read and write** and **Actions: Read and write**.
   The token is stored only in your browser.
2. Drop `.md` files onto the page, or write a note in the built-in editor. Optionally pick a
   folder, which becomes the category.
3. Click **Publish**. Every queued file goes into one commit, which triggers the GitHub Action.
   The page shows the Action's progress until the feed is deployed.

The page can also delete notes: tick several (or **Select all**, optionally after filtering) and click
**Delete selected**. They are removed in one commit, so the feed rebuilds once. **Rebuild feed now**
runs the workflow manually.
Anyone can open the page, but it can't do anything without your token.

### Directly in GitHub

Add a `.md` file under `notes/` and push to `main`. You can do this in the GitHub web
UI or app with **Add file → Create new file**. GitHub Actions rebuilds the feed and
deploys it in about a minute.

Front matter is optional:

```markdown
---
title: My note
date: 2026-11-16 08:30
tags: [finance, ideas]
summary: One or two sentences shown as the preview.
draft: false
---

The note body in Markdown.
```

| Field     | If omitted |
|-----------|------------|
| `title`   | First `# heading`, else the file name |
| `date`    | Time of the file's last commit |
| `tags`    | Subfolder name (e.g. `notes/finance/x.md` → `finance`) |
| `summary` | First paragraph |
| `draft: true` | Leaves the note out of the feed |

The `guid` of each item is its file path (`notes/…/file.md`), so **don't rename a note
file** after publishing, or readers will show it as a new unread item.

## Feed details

- RSS 2.0 with the full note as HTML in `<content:encoded>`, newest first, latest 50 notes.
- Images stay in the article (see **Images** below). Iframes, audio players and scripts are removed,
  because readers can't run them.
- Notes saved with the Obsidian Web Clipper work as they are: `author`, `published`, `source`
  and `description` become a byline under the title, a link to the original, and the preview text.
- Each note also gets an HTML page, plus an index page at the site root.
- Title and description can be changed with the `FEED_TITLE` and `FEED_DESCRIPTION`
  environment variables in `.github/workflows/pages.yml`.

## Images

Images in a note show up when you open the article in your reader, as long as the device is online.
- **Online images** (`![](https://…)`, as the Web Clipper saves them) stay as links to the original
  site. Substack and X/Twitter images are requested as JPEG at 800px wide, because many e-readers
  can't show WebP and large images use a lot of memory. Set the width with `FEED_IMAGE_WIDTH`.
- **Your own images:** put the file next to the note, for example `notes/ai/chart.png`, and reference it
  as `![](chart.png)`. It is published at `…/files/ai/chart.png` and the link is rewritten for you.
- **No images at all:** set `FEED_IMAGES: strip` in the workflow's build step `env`.

**KOReader news downloader:** the feed already contains the full article, so don't make it fetch the page.
Do turn images on, in `news/feed_config.lua`:

```lua
{ "https://emindu.github.io/personalize-rss/feed.xml", limit = 20, download_full_article = false, include_images = true },
```

## One-time setup

1. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Push to `main` (or run the workflow manually from the **Actions** tab).

## Build locally

```bash
pip install -r requirements.txt
python build.py
python -m http.server 8000 -d _site
```

Then open `http://localhost:8000/feed.xml`.

**Privacy:** GitHub Pages sites are public, even if the repo is private (private-repo
Pages requires a paid plan). Don't put anything here you wouldn't want others to read.
