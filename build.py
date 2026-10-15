#!/usr/bin/env python3
"""
Compiles index.md and _layouts/default.html into a standalone, production-ready index.html.
"""

import os
import re
from markdown_it import MarkdownIt

def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_path = os.path.join(base_dir, "index.md")
    layout_path = os.path.join(base_dir, "_layouts", "default.html")
    out_path = os.path.join(base_dir, "index.html")

    with open(md_path, "r", encoding="utf-8") as f:
        md_raw = f.read()

    # Strip YAML frontmatter if present
    content_md = re.sub(r"^---\n.*?\n---\n", "", md_raw, flags=re.DOTALL)

    md = MarkdownIt("commonmark").enable("table")
    content_html = md.render(content_md)

    with open(layout_path, "r", encoding="utf-8") as f:
        layout_html = f.read()

    final_html = layout_html.replace("{{ content }}", content_html)
    final_html = final_html.replace("{{ page.title | default: site.title }}", "Central Europe Winter Highlights & Dining Guide")
    final_html = final_html.replace("{{ page.description | default: site.description }}", "A curated, practical guide to cultural landmarks, alpine winter adventures, street treats, and authentic dining across Central Europe.")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"Successfully generated standalone index.html ({len(final_html):,} bytes) at {out_path}")

if __name__ == "__main__":
    build()
