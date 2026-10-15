#!/usr/bin/env python3
"""
Compiles all Markdown trip guides and the landing portal into standalone HTML pages.
Uses _layouts/default.html as the universal layout template.

Key capabilities:
1. Automatically scopes sticky navigation bar to specific trip pages.
2. Index page has NO sticky nav.
3. Sticky navigation is dynamic based on the Markdown file being rendered.
4. All country buttons and dropdown items are clickable and navigate directly to page sections.
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


def get_central_europe_sticky_nav():
    """Generates the tailored, clickable 4-country navigation bar for Central Europe."""
    return """
  <!-- Sticky Dynamic Navigation Bar (Persists on Scroll) -->
  <nav class="sticky-nav" id="stickyNav">
    <div class="container nav-wrapper">
      
      <!-- Home Link -->
      <div class="nav-left">
        <a href="index.html" class="nav-home-btn" id="navHome">
          <span>🏠</span> <span>All Trips</span>
        </a>
      </div>

      <!-- 4 Country Clickable Navigators & Drill-Downs -->
      <div class="nav-countries" id="navCountries">
        
        <!-- 1. Czech Republic -->
        <div class="nav-dropdown" data-country="czech">
          <div class="nav-btn-group">
            <a href="#country-czech" class="nav-country-link" title="Jump to Czech Republic section">
              <span>🇨🇿</span> <span>Czech Republic</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Czech Republic sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🇨🇿 Czech Republic Highlights</span>
              <a href="#country-czech" class="dropdown-header-link">Country Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#prague" class="dropdown-dest-title">🏰 Prague</a>
                <ul class="dropdown-links">
                  <li><a href="#prague-sights">🏛️ Top Sights & Baroque Library</a></li>
                  <li><a href="#prague-activities">🎯 Tech Museum & River Cruise</a></li>
                  <li><a href="#prague-snacks">☕ Trdelník & Chlebíčky Sandwiches</a></li>
                  <li><a href="#prague-dining">🍽️ Lokál, Mlejnice & Train Tavern</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#south-bohemia" class="dropdown-dest-title">🌲 South Bohemia (Český Krumlov)</a>
                <ul class="dropdown-links">
                  <li><a href="#south-bohemia-sights">🏛️ UNESCO Castle & Cloak Bridge</a></li>
                  <li><a href="#south-bohemia-activities">🎯 Lipno Alpine Coaster</a></li>
                  <li><a href="#south-bohemia-dining">🍽️ Medieval Prison Tavern</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. Austria -->
        <div class="nav-dropdown" data-country="austria">
          <div class="nav-btn-group">
            <a href="#country-austria" class="nav-country-link" title="Jump to Austria section">
              <span>🇦🇹</span> <span>Austria</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Austria sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🇦🇹 Austria Highlights</span>
              <a href="#country-austria" class="dropdown-header-link">Country Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-4">
              <div class="dropdown-col">
                <a href="#vienna" class="dropdown-dest-title">👑 Vienna</a>
                <ul class="dropdown-links">
                  <li><a href="#vienna-sights">🏛️ Schönbrunn & St. Stephen's</a></li>
                  <li><a href="#vienna-activities">🎯 Vienna Ice Dream & Sound Museum</a></li>
                  <li><a href="#vienna-snacks">☕ Cornetto Coffee & Käsekrainer</a></li>
                  <li><a href="#vienna-dining">🍽️ Figlmüller & Café Central</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#ramsau" class="dropdown-dest-title">🐎 Ramsau Dachstein</a>
                <ul class="dropdown-links">
                  <li><a href="#ramsau-sights">🏛️ High Alpine Glacier Plateau</a></li>
                  <li><a href="#ramsau-activities">🎯 Horse-Drawn Sleigh Ride</a></li>
                  <li><a href="#ramsau-dining">🍽️ Walcheralm Wooden Hut</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#salzburg" class="dropdown-dest-title">🎼 Salzburg & Lakes</a>
                <ul class="dropdown-links">
                  <li><a href="#salzburg-sights">🏛️ Hohensalzburg & Hallstatt</a></li>
                  <li><a href="#salzburg-activities">🎯 Red Bull Hangar-7 & Salt Mine</a></li>
                  <li><a href="#salzburg-snacks">☕ Original Bosna & Mozartkugel</a></li>
                  <li><a href="#salzburg-dining">🍽️ St. Peter 803 AD & Stieglkeller</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#wildkogel" class="dropdown-dest-title">🛷 Wildkogel & Rosenheim</a>
                <ul class="dropdown-links">
                  <li><a href="#wildkogel-sights">🏛️ Summit Panorama & Pass Thurn</a></li>
                  <li><a href="#wildkogel-activities">🎯 14 km Toboggan Run</a></li>
                  <li><a href="#wildkogel-snacks">☕ Giant Germknödel Dumpling</a></li>
                  <li><a href="#wildkogel-dining">🍽️ Wolkenstein & 1543 Brewery</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. Slovakia -->
        <div class="nav-dropdown" data-country="slovakia">
          <div class="nav-btn-group">
            <a href="#country-slovakia" class="nav-country-link" title="Jump to Slovakia section">
              <span>🇸🇰</span> <span>Slovakia</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Slovakia sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🇸🇰 Slovakia Highlights</span>
              <a href="#country-slovakia" class="dropdown-header-link">Country Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-1">
              <div class="dropdown-col">
                <a href="#bratislava" class="dropdown-dest-title">🏰 Bratislava</a>
                <ul class="dropdown-links">
                  <li><a href="#bratislava-sights">🏛️ Bratislava Castle & Statues</a></li>
                  <li><a href="#bratislava-activities">🎯 UFO Deck & Most SNP</a></li>
                  <li><a href="#bratislava-snacks">☕ Bratislavské Rožky Pastries</a></li>
                  <li><a href="#bratislava-dining">🍽️ Meštiansky Pivovar & Zylinder</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. Germany -->
        <div class="nav-dropdown align-right" data-country="germany">
          <div class="nav-btn-group">
            <a href="#country-germany" class="nav-country-link" title="Jump to Germany section">
              <span>🇩🇪</span> <span>Germany</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Germany sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🇩🇪 Germany Highlights</span>
              <a href="#country-germany" class="dropdown-header-link">Country Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-3">
              <div class="dropdown-col">
                <a href="#neuschwanstein" class="dropdown-dest-title">🏰 Neuschwanstein & Allgäu</a>
                <ul class="dropdown-links">
                  <li><a href="#neuschwanstein-sights">🏛️ Fairytale Palace & Bridge</a></li>
                  <li><a href="#neuschwanstein-activities">🎯 Mountain Shuttle & Lake Alpsee</a></li>
                  <li><a href="#neuschwanstein-dining">🍽️ Schlosswirt Castle Inn</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#munich" class="dropdown-dest-title">🍺 Munich, Bavaria</a>
                <ul class="dropdown-links">
                  <li><a href="#munich-sights">🏛️ Marienplatz, Eisbach & Parks</a></li>
                  <li><a href="#munich-activities">🎯 BMW Welt & Hypercars</a></li>
                  <li><a href="#munich-snacks">☕ Leberkässemmel & Schmalznudel</a></li>
                  <li><a href="#munich-dining">🍽️ Augustiner (1328) & Hofbräukeller</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#allianz" class="dropdown-dest-title">⚽ Allianz Arena & Outlet</a>
                <ul class="dropdown-links">
                  <li><a href="#allianz-sights">🏛️ Stadium Architecture & Store</a></li>
                  <li><a href="#allianz-activities">🎯 Guided Tour, Museum & Outlet</a></li>
                  <li><a href="#allianz-dining">🍽️ Designer Village Dining</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Real-time Filter -->
      <div class="search-box">
        <input type="text" id="liveSearch" placeholder="Filter sights, dishes, towns..." onkeyup="filterContent()">
      </div>

    </div>
  </nav>
"""


def build_dynamic_nav_from_headings(body_md):
    """
    Dynamically extracts ## and ### headings from any future markdown guide
    to automatically generate a sticky navigation bar with drill-downs.
    """
    sections = []
    current_section = None

    for line in body_md.splitlines():
        line = line.strip()
        if line.startswith("## ") and not line.startswith("## 📌"):
            title = line[3:].strip()
            slug = slugify(title)
            current_section = {"title": title, "slug": slug, "subs": []}
            sections.append(current_section)
        elif line.startswith("### ") and current_section is not None:
            sub_title = line[4:].strip()
            sub_slug = f"{current_section['slug']}-{slugify(sub_title)}"
            current_section["subs"].append({"title": sub_title, "slug": sub_slug})

    if not sections:
        return ""

    pills_html = []
    for sec in sections:
        if sec["subs"]:
            sub_links = "".join(f'<li><a href="#{sub["slug"]}">{sub["title"]}</a></li>' for sub in sec["subs"])
            pills_html.append(f"""
        <div class="nav-dropdown">
          <div class="nav-btn-group">
            <a href="#{sec['slug']}" class="nav-country-link"><span>{sec['title']}</span></a>
            <button class="nav-caret-btn" type="button">▾</button>
          </div>
          <div class="dropdown-menu">
            <ul class="dropdown-links">{sub_links}</ul>
          </div>
        </div>""")
        else:
            pills_html.append(f"""
        <div class="nav-btn-group">
          <a href="#{sec['slug']}" class="nav-country-link"><span>{sec['title']}</span></a>
        </div>""")

    items_joined = "\n".join(pills_html)
    return f"""
  <nav class="sticky-nav" id="stickyNav">
    <div class="container nav-wrapper">
      <div class="nav-left">
        <a href="index.html" class="nav-home-btn" id="navHome"><span>🏠</span> <span>All Trips</span></a>
      </div>
      <div class="nav-countries" id="navCountries">
{items_joined}
      </div>
      <div class="search-box">
        <input type="text" id="liveSearch" placeholder="Filter on page..." onkeyup="filterContent()">
      </div>
    </div>
  </nav>
"""


def generate_sticky_nav(fname, meta, body_md):
    """
    Determines whether a page should have a sticky nav and dynamically builds it.
    - index.md: NEVER has sticky nav (returns empty string).
    - czech-austria-slovakia-germany.md: Returns curated 4-country drill-down nav.
    - Future trip guides: Returns dynamically generated nav based on markdown headings.
    """
    sticky_nav_setting = str(meta.get("sticky_nav", "")).lower().strip()

    # index page NEVER has sticky nav
    if fname == "index.md" or sticky_nav_setting in ["false", "none", "no", "off"]:
        return ""

    if fname == "czech-austria-slovakia-germany.md" or sticky_nav_setting == "central-europe":
        return get_central_europe_sticky_nav()

    # Dynamic auto-generation for any future trip guide with sticky_nav enabled
    if sticky_nav_setting in ["true", "yes", "auto", "dynamic"]:
        return build_dynamic_nav_from_headings(body_md)

    return ""


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

        # Inject semantic IDs for headings (so anchor links jump with precision)
        content_html = inject_heading_ids(content_html)

        # Dynamically generate or omit sticky nav based on markdown source and page
        sticky_nav_html = generate_sticky_nav(fname, meta, body_md)

        title = meta.get("title", "Curated Holiday & Travel Highlights Collection")
        desc = meta.get("description", "A curated collection of practical, tabularized holiday itineraries, destination highlights, alpine adventures, and authentic dining guides.")

        page_html = layout_template.replace("{{ content }}", content_html)
        page_html = page_html.replace("{{ sticky_nav }}", sticky_nav_html)
        page_html = page_html.replace("{{ page.title | default: site.title }}", title)
        page_html = page_html.replace("{{ page.description | default: site.description }}", desc)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page_html)

        has_nav_str = "with Dynamic Sticky Nav" if sticky_nav_html else "NO Sticky Nav (Clean Portal)"
        print(f"Compiled '{fname}' ➔ '{out_name}' [{has_nav_str}] ({len(page_html):,} bytes)")

if __name__ == "__main__":
    build_all()
