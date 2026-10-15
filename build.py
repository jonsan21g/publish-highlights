#!/usr/bin/env python3
"""
Compiles all Markdown trip guides and the landing portal into standalone HTML pages.
Uses _layouts/default.html as the universal layout template.
"""

import os
import re
import sys
from markdown_it import MarkdownIt

# Fix Windows console UTF-8 output
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def parse_frontmatter(raw_text):
    """Extracts YAML frontmatter title, description, and the markdown body."""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", raw_text, re.DOTALL)
    if not match:
        return {}, raw_text
    
    yaml_block, body = match.group(1), match.group(2)
    meta = {}
    for line in yaml_block.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip().strip('"\'')
    return meta, body

def build_all():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    layout_path = os.path.join(base_dir, "_layouts", "default.html")

    with open(layout_path, "r", encoding="utf-8") as f:
        layout_template = f.read()

    md = MarkdownIt("commonmark").enable("table")

    # Find all markdown files (excluding README.md which is for repo root)
    md_files = [f for f in os.listdir(base_dir) if f.endswith(".md") and f != "README.md"]

    for fname in md_files:
        src_path = os.path.join(base_dir, fname)
        out_name = os.path.splitext(fname)[0] + ".html"
        out_path = os.path.join(base_dir, out_name)

        with open(src_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        meta, body_md = parse_frontmatter(raw_text)
        content_html = md.render(body_md)

        title = meta.get("title", "Curated Holiday & Travel Highlights Collection")
        desc = meta.get("description", "A curated collection of practical, tabularized holiday itineraries, destination highlights, alpine adventures, and authentic dining guides.")

        page_html = layout_template.replace("{{ content }}", content_html)
        page_html = page_html.replace("{{ page.title | default: site.title }}", title)
        page_html = page_html.replace("{{ page.description | default: site.description }}", desc)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page_html)

        print(f"Compiled '{fname}' ➔ '{out_name}' ({len(page_html):,} bytes)")

if __name__ == "__main__":
    build_all()
