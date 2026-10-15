#!/usr/bin/env python3
"""
Compiles all Markdown trip guides and the landing portal into standalone HTML pages.
Uses _layouts/default.html as the universal layout template.
Automatically injects semantic IDs into headings for dynamic sticky navbar navigation.
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


def slugify(text):
    """Converts heading text to a clean URL-friendly slug."""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')


def inject_heading_ids(html_str):
    """
    Injects precise semantic IDs into <h2> and <h3> headings for seamless
    deep-linking from the country dropdown navigation bar.
    """
    dest_map = [
        ("prague", ["prague"]),
        ("south-bohemia", ["south bohemia", "český krumlov", "cesky krumlov"]),
        ("vienna", ["vienna", "wien"]),
        ("ramsau", ["ramsau"]),
        ("salzburg", ["salzburg"]),
        ("wildkogel", ["wildkogel"]),
        ("bratislava", ["bratislava"]),
        ("neuschwanstein", ["neuschwanstein"]),
        ("munich", ["munich", "münchen"]),
        ("allianz", ["allianz", "ingolstadt"]),
    ]

    country_starts = {
        "prague": "country-czech",
        "vienna": "country-austria",
        "bratislava": "country-slovakia",
        "neuschwanstein": "country-germany",
    }

    current_dest = None

    def repl_heading(match):
        nonlocal current_dest
        tag, attrs, inner = match.group(1), match.group(2), match.group(3)
        inner_clean = re.sub(r'<[^>]+>', '', inner).lower()

        if tag == "h2":
            assigned_id = None
            for dest_id, keywords in dest_map:
                if any(k in inner_clean for k in keywords):
                    assigned_id = dest_id
                    current_dest = dest_id
                    break
            
            if not assigned_id:
                assigned_id = slugify(inner)
                current_dest = assigned_id

            prefix = ""
            if assigned_id in country_starts:
                marker_id = country_starts[assigned_id]
                # Prepend country marker if not already present in the block
                prefix = f'<div id="{marker_id}" class="country-marker"></div>\n'

            if 'id=' in attrs:
                return prefix + match.group(0)
            return f'{prefix}<h2 id="{assigned_id}"{attrs}>{inner}</h2>'

        elif tag == "h3":
            sub_type = None
            if any(w in inner_clean for w in ["attraction", "sight"]):
                sub_type = "sights"
            elif any(w in inner_clean for w in ["activit", "experience"]):
                sub_type = "activities"
            elif any(w in inner_clean for w in ["snack", "street food", "treat"]):
                sub_type = "snacks"
            elif any(w in inner_clean for w in ["dining", "tavern", "hut"]):
                sub_type = "dining"
            else:
                sub_type = slugify(inner)

            if current_dest:
                assigned_id = f"{current_dest}-{sub_type}"
            else:
                assigned_id = slugify(inner)

            if 'id=' in attrs:
                return match.group(0)
            return f'<h3 id="{assigned_id}"{attrs}>{inner}</h3>'

        return match.group(0)

    return re.sub(r'<(h[23])([^>]*)>(.*?)</\1>', repl_heading, html_str, flags=re.DOTALL)


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

        # Inject semantic IDs for headings
        content_html = inject_heading_ids(content_html)

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
