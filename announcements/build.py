#!/usr/bin/env python3
"""Updates the announcements list in index.html, atom.xml, and gemini/ from .md files in posts/."""

from datetime import datetime, timezone
from pathlib import Path

from md2gemini import md2gemini

DIR = Path(__file__).parent
SITE = "https://crystalized.cc"
GEMINI = DIR.parent / "gemini" / "announcements"
START = "<!-- announcements:start -->"
END = "<!-- announcements:end -->"


def parse_md(path: Path) -> tuple[str, str]:
    lines = path.read_text().splitlines()
    title = ""
    desc_lines = []
    state = "seeking_heading"

    for line in lines:
        if state == "seeking_heading" and line.startswith("#"):
            title = line.lstrip("# ").strip()
            state = "skipping_blanks"
        elif state == "skipping_blanks":
            if line.strip() == "":
                continue
            state = "collecting_desc"
            desc_lines.append(line)
        elif state == "collecting_desc":
            if line.strip() == "" or line.startswith("#"):
                break
            desc_lines.append(line)

    return title, " ".join(desc_lines).strip()


def parse_date(path: Path) -> datetime:
    for line in path.read_text().splitlines():
        if line.startswith("Posted on:"):
            return datetime.strptime(line.split(":", 1)[1].strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    print(f"WARNING: {path.name} has no 'Posted on:' date, using file modification time")
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def build_entries(md_files):
    entries = []
    for f in md_files:
        title, desc = parse_md(f)
        date = parse_date(f)
        entries.append((f.name, title, desc, date))
    return entries


def write_feed(entries):
    ns = "http://www.w3.org/2005/Atom"
    feed_id = f"{SITE}/announcements/"
    latest = entries[0][3] if entries else datetime.now(tz=timezone.utc)

    items = []
    for name, title, desc, date in entries:
        items.append(f"""  <entry>
    <title>{title}</title>
    <link href="{SITE}/announcements/posts/{name}" rel="alternate"/>
    <id>{SITE}/announcements/posts/{name}</id>
    <updated>{date.isoformat()}</updated>
    <summary>{desc}</summary>
  </entry>""")

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="{ns}">
  <title>Crystalized Announcements</title>
  <link href="{feed_id}" rel="alternate"/>
  <link href="{SITE}/announcements/atom.xml" rel="self"/>
  <id>{feed_id}</id>
  <updated>{latest.isoformat()}</updated>
  <subtitle>Latest announcements from the Crystalized Minecraft server</subtitle>
{chr(10).join(items)}
</feed>
"""
    (DIR / "atom.xml").write_text(feed)
    return len(items)


def write_index(entries):
    list_items = []
    for name, title, desc, date in entries:
        list_items.append(f'\t\t<li><a href="/announcements/posts/{name}">{title}</a> \u2014 {date.strftime("%Y-%m-%d")}: {desc}...</li>')

    list_html = "\n".join(list_items)
    index = (DIR / "index.html").read_text()
    before = index[:index.index(START) + len(START)]
    after = index[index.index(END):]
    (DIR / "index.html").write_text(f"{before}\n{list_html}\n{after}")
    return len(entries)


def write_gemini_index(entries):
    GEMINI.mkdir(parents=True, exist_ok=True)
    lines = ["# Announcements", ""]
    for name, title, desc, date in entries:
        gmi_name = name.removesuffix(".md") + ".gmi"
        lines.append(f"=> posts/{gmi_name} {title} \u2014 {date.strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append("=> ../index.gmi Home")
    lines.append("")
    (GEMINI / "index.gmi").write_text("\n".join(lines))
    return len(entries)


def write_gemini_posts(md_files):
    (GEMINI / "posts").mkdir(parents=True, exist_ok=True)
    for f in md_files:
        gmi = md2gemini(f.read_text(), links="copy", plain=True, md_links=True)
        (GEMINI / "posts" / (f.stem + ".gmi")).write_text(gmi)
    return len(md_files)


def main():
    md_files = sorted((DIR / "posts").glob("*.md"), reverse=True)
    entries = build_entries(md_files)

    n = write_index(entries)
    print(f"Updated index.html ({n} announcements)")

    n = write_feed(entries)
    print(f"Updated atom.xml ({n} items)")

    n = write_gemini_index(entries)
    print(f"Updated gemini/announcements/index.gmi ({n} announcements)")

    n = write_gemini_posts(md_files)
    print(f"Updated gemini/announcements/posts/ ({n} posts)")


if __name__ == "__main__":
    main()
