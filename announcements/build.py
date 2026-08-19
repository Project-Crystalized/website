#!/usr/bin/env python3
"""Updates the announcements list in index.html from .md files in posts/."""

from datetime import datetime
from pathlib import Path

DIR = Path(__file__).parent
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


def main():
    md_files = sorted((DIR / "posts").glob("*.md"), reverse=True)

    entries = []
    for f in md_files:
        title, desc = parse_md(f)
        date = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
        entries.append(f'\t\t<li><a href="/announcements/posts/{f.name}">{title}</a> \u2014 {date}: {desc}...</li>')

    list_html = "\n".join(entries)

    index = (DIR / "index.html").read_text()
    before = index[:index.index(START) + len(START)]
    after = index[index.index(END):]
    (DIR / "index.html").write_text(f"{before}\n{list_html}\n{after}")
    print(f"Updated index.html ({len(entries)} announcements)")


if __name__ == "__main__":
    main()
