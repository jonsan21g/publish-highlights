#!/usr/bin/env python3
"""
Compiles all Markdown trip guides and the landing portal into standalone HTML pages.
Uses _layouts/default.html as the universal layout template.

Key capabilities:
1. Automatically scopes sticky navigation bar to specific trip pages.
2. Index page has NO sticky nav.
3. Sticky navigation is dynamic based on the Markdown file being rendered.
4. All country buttons and dropdown items are clickable and navigate directly to page sections.
5. All external links for items (attractions, dining, activities) default to open in a new tab.
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
        ("tokyo-west", ["tokyo — modern", "shinjuku", "shibuya"]),
        ("disneysea", ["disney", "disneysea"]),
        ("osaka", ["osaka"]),
        ("kyoto-nara", ["kyoto", "nara", "uji"]),
        ("tokyo-east", ["historic asakusa", "asakusa", "ginza", "skytree"]),
        # Bornholm
        ("north-bornholm", ["north bornholm", "hammershus", "allinge", "hammeren"]),
        ("central-bornholm", ["central bornholm", "almindingen", "østerlars", "osterlars", "ekkodalen"]),
        ("east-coast", ["east coast", "gudhjem", "svaneke"]),
        ("south-bornholm", ["south bornholm", "dueodde", "aakirkeby"]),
        ("transit-hub", ["transit hub", "copenhagen", "ystad", "rønne", "ronne"]),
        # Baltic Route
        ("poland", ["poland", "gdynia", "gdańsk", "gdansk", "malbork"]),
        ("lithuania", ["lithuania", "vilnius", "trakai"]),
        ("latvia", ["latvia", "riga", "sigulda"]),
        ("estonia", ["estonia", "tallinn", "pärnu", "parnu"]),
        ("sweden", ["sweden", "stockholm", "lake vättern", "lake vattern"]),
        # Iceland
        ("reykjanes", ["reykjanes", "arrival", "keflavík", "keflavik"]),
        ("snaefellsnes", ["snæfellsnes", "snaefellsnes", "west iceland", "grundarfjörður", "stykkishólmur"]),
        ("golden-circle", ["golden circle", "south-central uplands", "thingvellir", "geysir"]),
        ("deep-south", ["deep south", "vatnajökull", "vatnajokull", "vík", "vik"]),
        ("reykjavik", ["greater reykjavík", "greater reykjavik", "capital region"]),
    ]

    country_starts = {
        "prague": "country-czech",
        "vienna": "country-austria",
        "bratislava": "country-slovakia",
        "neuschwanstein": "country-germany",
        "tokyo-west": "region-tokyo-west",
        "disneysea": "region-disneysea",
        "osaka": "region-osaka",
        "kyoto-nara": "region-kyoto-nara",
        "tokyo-east": "region-tokyo-east",
        "north-bornholm": "region-north-bornholm",
        "central-bornholm": "region-central-bornholm",
        "east-coast": "region-east-coast",
        "south-bornholm": "region-south-bornholm",
        "transit-hub": "region-transit-hub",
        "poland": "country-poland",
        "lithuania": "country-lithuania",
        "latvia": "country-latvia",
        "estonia": "country-estonia",
        "sweden": "country-sweden",
        "reykjanes": "region-reykjanes",
        "snaefellsnes": "region-snaefellsnes",
        "golden-circle": "region-golden-circle",
        "deep-south": "region-deep-south",
        "reykjavik": "region-reykjavik",
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
            elif any(w in inner_clean for w in ["activit", "experience", "ride"]):
                sub_type = "activities"
            elif any(w in inner_clean for w in ["snack", "street food", "treat"]):
                sub_type = "snacks"
            elif any(w in inner_clean for w in ["dining", "tavern", "hut", "restaurant"]):
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


def make_external_links_open_in_new_tab(html_str):
    """
    Ensures every external link (http:// or https://) defaults to opening in a new tab
    with target="_blank" rel="noopener noreferrer".
    In-page anchor jumps (#...) remain in the same tab.
    """
    def repl_link(match):
        attrs = match.group(1)
        if re.search(r'href=[\'"]https?://', attrs):
            if 'target=' not in attrs:
                attrs += ' target="_blank"'
            if 'rel=' not in attrs:
                attrs += ' rel="noopener noreferrer"'
            return f'<a{attrs}>'
        return match.group(0)

    return re.sub(r'<a([^>]+)>', repl_link, html_str)


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
    </div>
  </nav>
"""


def get_japan_sticky_nav():
    """Generates the tailored, clickable 5-region navigation bar for Japan."""
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

      <!-- 5 Region Clickable Navigators & Drill-Downs -->
      <div class="nav-countries" id="navCountries">
        
        <!-- 1. Tokyo West & Modern -->
        <div class="nav-dropdown" data-country="tokyo-west">
          <div class="nav-btn-group">
            <a href="#tokyo-west" class="nav-country-link" title="Jump to Tokyo Modern section">
              <span>🏙️</span> <span>Tokyo Modern</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Tokyo Modern sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🏙️ Tokyo (Shinjuku & Shibuya)</span>
              <a href="#tokyo-west" class="dropdown-header-link">Region Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#tokyo-west-sights" class="dropdown-dest-title">🏛️ Top Sights & Vistas</a>
                <ul class="dropdown-links">
                  <li><a href="#tokyo-west-sights">TMG Observatories & Fuji</a></li>
                  <li><a href="#tokyo-west-sights">Shinjuku Kabukicho & Godzilla</a></li>
                  <li><a href="#tokyo-west-sights">Shibuya Crossing & Hachiko</a></li>
                  <li><a href="#tokyo-west-sights">Omoide & Nonbei Yokocho</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#tokyo-west-activities" class="dropdown-dest-title">🎯 Pop Culture & Dining</a>
                <ul class="dropdown-links">
                  <li><a href="#tokyo-west-activities">Nintendo & Pokémon Shibuya</a></li>
                  <li><a href="#tokyo-west-activities">Mega Don Quijote & Miyashita</a></li>
                  <li><a href="#tokyo-west-snacks">The Matcha Tokyo & Muroya</a></li>
                  <li><a href="#tokyo-west-dining">Kumachan Onsen & Blackhole</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. Tokyo DisneySea -->
        <div class="nav-dropdown" data-country="disneysea">
          <div class="nav-btn-group">
            <a href="#disneysea" class="nav-country-link" title="Jump to Tokyo DisneySea section">
              <span>🌊</span> <span>Tokyo DisneySea</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle DisneySea sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🌊 Tokyo Disney Resort (Maihama)</span>
              <a href="#disneysea" class="dropdown-header-link">Park Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#disneysea-sights" class="dropdown-dest-title">🏰 Ports & Thrill Rides</a>
                <ul class="dropdown-links">
                  <li><a href="#disneysea-sights">Mediterranean Harbor & Caldera</a></li>
                  <li><a href="#disneysea-activities">Journey to Center of the Earth</a></li>
                  <li><a href="#disneysea-activities">Soaring: Fantastic Flight</a></li>
                  <li><a href="#disneysea-activities">Tower of Terror & Indiana Jones</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#disneysea-snacks" class="dropdown-dest-title">🎪 Shows & Dining</a>
                <ul class="dropdown-links">
                  <li><a href="#disneysea-activities">Believe! Sea of Dreams Night Show</a></li>
                  <li><a href="#disneysea-snacks">Little Green Mochi & Popcorn</a></li>
                  <li><a href="#disneysea-dining">Zambini Brothers Ristorante</a></li>
                  <li><a href="#disneysea-dining">Horizon Bay & Vulcania</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. Osaka -->
        <div class="nav-dropdown" data-country="osaka">
          <div class="nav-btn-group">
            <a href="#osaka" class="nav-country-link" title="Jump to Osaka section">
              <span>🏯</span> <span>Osaka & USJ</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Osaka sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🏯 Osaka City & Universal Studios</span>
              <a href="#osaka" class="dropdown-header-link">City Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#osaka-sights" class="dropdown-dest-title">🎡 Sights & Universal Studios</a>
                <ul class="dropdown-links">
                  <li><a href="#osaka-sights">Osaka Castle & Dotonbori Glico</a></li>
                  <li><a href="#osaka-sights">Umeda Sky & Namba Yasaka</a></li>
                  <li><a href="#osaka-activities">Super Nintendo World & Mario Kart</a></li>
                  <li><a href="#osaka-activities">Donkey Kong Country & Flying Dino</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#osaka-dining" class="dropdown-dest-title">🥢 Soul Food & Street Treats</a>
                <ul class="dropdown-links">
                  <li><a href="#osaka-activities">Tsutenkaku Tower Slider & Cruise</a></li>
                  <li><a href="#osaka-snacks">Wanaka Takoyaki & Naruto Taiyaki</a></li>
                  <li><a href="#osaka-dining">Yakiniku Sakon Wagyu Buffet</a></li>
                  <li><a href="#osaka-dining">Mizuno Okonomiyaki & Daruma</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. Kyoto, Uji & Nara -->
        <div class="nav-dropdown align-right" data-country="kyoto-nara">
          <div class="nav-btn-group">
            <a href="#kyoto-nara" class="nav-country-link" title="Jump to Kyoto, Uji & Nara section">
              <span>⛩️</span> <span>Kyoto & Nara</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Kyoto & Nara sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">⛩️ Kyoto, Uji & Nara Traditions</span>
              <a href="#kyoto-nara" class="dropdown-header-link">Region Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#kyoto-nara-sights" class="dropdown-dest-title">🎋 Temples, Shrines & Deer</a>
                <ul class="dropdown-links">
                  <li><a href="#kyoto-nara-sights">Fushimi Inari 10,000 Torii</a></li>
                  <li><a href="#kyoto-nara-sights">Kinkaku-ji Golden Pavilion</a></li>
                  <li><a href="#kyoto-nara-sights">Arashiyama Bamboo & Kiyomizu</a></li>
                  <li><a href="#kyoto-nara-sights">Todai-ji Great Buddha & Deer</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#kyoto-nara-activities" class="dropdown-dest-title">🍵 Tea Ceremonies & Dining</a>
                <ul class="dropdown-links">
                  <li><a href="#kyoto-nara-activities">Maikoya Kimono Tea Ceremony</a></li>
                  <li><a href="#kyoto-nara-activities">Samurai & Ninja Museum & Nintendo</a></li>
                  <li><a href="#kyoto-nara-snacks">Uji Matcha & Ochanokosaisai</a></li>
                  <li><a href="#kyoto-nara-dining">HIRO Wagyu & Katsukura Tonkatsu</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 5. Tokyo Historic & Digital -->
        <div class="nav-dropdown align-right" data-country="tokyo-east">
          <div class="nav-btn-group">
            <a href="#tokyo-east" class="nav-country-link" title="Jump to Tokyo Historic & Digital section">
              <span>🏮</span> <span>Tokyo Historic</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Tokyo Historic sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🏮 Asakusa, Skytree & Ginza</span>
              <a href="#tokyo-east" class="dropdown-header-link">District Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#tokyo-east-sights" class="dropdown-dest-title">🗼 Heritage & Observation</a>
                <ul class="dropdown-links">
                  <li><a href="#tokyo-east-sights">Senso-ji Temple & Kaminarimon</a></li>
                  <li><a href="#tokyo-east-sights">Tokyo Skytree 450m Panorama</a></li>
                  <li><a href="#tokyo-east-sights">Meiji Jingu & Takeshita Street</a></li>
                  <li><a href="#tokyo-east-sights">Ginza Chuo-dori & Wako Clock</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#tokyo-east-activities" class="dropdown-dest-title">✨ Digital Art & Cuisine</a>
                <ul class="dropdown-links">
                  <li><a href="#tokyo-east-activities">teamLab Borderless & Shibuya SKY</a></li>
                  <li><a href="#tokyo-east-activities">Uniqlo & Itoya Flagships</a></li>
                  <li><a href="#tokyo-east-snacks">Suzukien No. 7 Matcha & Crepes</a></li>
                  <li><a href="#tokyo-east-dining">Gyukatsu Motomura & Midori Sushi</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  </nav>
"""




def get_bornholm_sticky_nav():
    """Generates the tailored, clickable 5-region navigation bar for Bornholm."""
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

      <!-- 5 Region Clickable Navigators & Drill-Downs -->
      <div class="nav-countries" id="navCountries">
        
        <!-- 1. North Bornholm -->
        <div class="nav-dropdown" data-country="north-bornholm">
          <div class="nav-btn-group">
            <a href="#north-bornholm" class="nav-country-link" title="Jump to North Bornholm section">
              <span>🏰</span> <span>North Bornholm</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle North Bornholm sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🏰 Allinge-Sandvig & Hammershus</span>
              <a href="#north-bornholm" class="dropdown-header-link">Region Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#north-bornholm-sights" class="dropdown-dest-title">🏛️ Fortress & Cliffs</a>
                <ul class="dropdown-links">
                  <li><a href="#north-bornholm-sights">Hammershus Castle Ruins</a></li>
                  <li><a href="#north-bornholm-sights">Hammeren & Hammerknuden</a></li>
                  <li><a href="#north-bornholm-sights">Opalsøen Quarry Lake</a></li>
                  <li><a href="#north-bornholm-sights">Helligdomsklipperne Rocks</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#north-bornholm-activities" class="dropdown-dest-title">🎯 Experiences & Dining</a>
                <ul class="dropdown-links">
                  <li><a href="#north-bornholm-activities">Brohuset Visitor Centre</a></li>
                  <li><a href="#north-bornholm-activities">Bornholms Kunstmuseum</a></li>
                  <li><a href="#north-bornholm-snacks">Kæmpestranden Kaffebar</a></li>
                  <li><a href="#north-bornholm-dining">Allinge Røgeri & Nordlandet</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. Central Bornholm -->
        <div class="nav-dropdown" data-country="central-bornholm">
          <div class="nav-btn-group">
            <a href="#central-bornholm" class="nav-country-link" title="Jump to Central Bornholm section">
              <span>🌲</span> <span>Central Bornholm</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Central Bornholm sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🌲 Almindingen & Østerlars</span>
              <a href="#central-bornholm" class="dropdown-header-link">Forest Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#central-bornholm-sights" class="dropdown-dest-title">🏛️ Valleys & Heritage</a>
                <ul class="dropdown-links">
                  <li><a href="#central-bornholm-sights">Ekkodalen Echo Valley</a></li>
                  <li><a href="#central-bornholm-sights">Rytterknægten Tower</a></li>
                  <li><a href="#central-bornholm-sights">Bisonskoven Wild Bison</a></li>
                  <li><a href="#central-bornholm-sights">Østerlars Fortified Church</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#central-bornholm-activities" class="dropdown-dest-title">🎯 Living History & Dining</a>
                <ul class="dropdown-links">
                  <li><a href="#central-bornholm-activities">Bornholms Middelaldercenter</a></li>
                  <li><a href="#central-bornholm-activities">Bornholms Rovfugleshow</a></li>
                  <li><a href="#central-bornholm-snacks">Café Ekkodalshuset Giant Tartlet</a></li>
                  <li><a href="#central-bornholm-dining">Christianshøjkroen Inn</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. East Coast -->
        <div class="nav-dropdown" data-country="east-coast">
          <div class="nav-btn-group">
            <a href="#east-coast" class="nav-country-link" title="Jump to East Coast section">
              <span>⛵</span> <span>East Coast</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle East Coast sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">⛵ Gudhjem, Melsted & Svaneke</span>
              <a href="#east-coast" class="dropdown-header-link">Coastline Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#east-coast-sights" class="dropdown-dest-title">🏛️ Towns & Scenic Harbors</a>
                <ul class="dropdown-links">
                  <li><a href="#east-coast-sights">Gudhjem Mountain Town & Bokul</a></li>
                  <li><a href="#east-coast-sights">Svaneke Historic Market Town</a></li>
                  <li><a href="#east-coast-sights">Hullehavn Rocky Beach</a></li>
                  <li><a href="#east-coast-activities">Joboland Brændesgårdshaven</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#east-coast-activities" class="dropdown-dest-title">🎯 Workshops & Breweries</a>
                <ul class="dropdown-links">
                  <li><a href="#east-coast-activities">Melstedgård Living Farm</a></li>
                  <li><a href="#east-coast-activities">Pernille Bülow Glassblowing</a></li>
                  <li><a href="#east-coast-snacks">Karamel Kompagniet & Svaneke Is</a></li>
                  <li><a href="#east-coast-dining">Svaneke Bryghus & Gudhjem Røgeri</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. South Bornholm -->
        <div class="nav-dropdown align-right" data-country="south-bornholm">
          <div class="nav-btn-group">
            <a href="#south-bornholm" class="nav-country-link" title="Jump to South Bornholm section">
              <span>🏖️</span> <span>South Bornholm</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle South Bornholm sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🏖️ Dueodde & Snogebæk</span>
              <a href="#south-bornholm" class="dropdown-header-link">Dunes Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#south-bornholm-sights" class="dropdown-dest-title">🏛️ Dunes & Geology</a>
                <ul class="dropdown-links">
                  <li><a href="#south-bornholm-sights">Dueodde Quartz White Sand</a></li>
                  <li><a href="#south-bornholm-sights">Dueodde 47m Lighthouse</a></li>
                  <li><a href="#south-bornholm-sights">Snogebæk Island Harbor</a></li>
                  <li><a href="#south-bornholm-activities">NaturBornholm Dino Centre</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#south-bornholm-activities" class="dropdown-dest-title">🎯 Chocolatiers & Dining</a>
                <ul class="dropdown-links">
                  <li><a href="#south-bornholm-activities">Kjærstrup Chokolade Atelier</a></li>
                  <li><a href="#south-bornholm-snacks">Gourmet Flødebolle & Soft Ice</a></li>
                  <li><a href="#south-bornholm-dining">Restaurant Bakken Dueodde</a></li>
                  <li><a href="#south-bornholm-dining">Nexø Gamle Røgeri</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 5. Transit Hub & Rønne -->
        <div class="nav-dropdown align-right" data-country="transit-hub">
          <div class="nav-btn-group">
            <a href="#transit-hub" class="nav-country-link" title="Jump to Transit Hub section">
              <span>🚢</span> <span>Rønne & Transit</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Transit Hub sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🚢 Gateway, Ferries & Rønne Old Town</span>
              <a href="#transit-hub" class="dropdown-header-link">Gateway Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#transit-hub-sights" class="dropdown-dest-title">🏛️ Gateway Sights</a>
                <ul class="dropdown-links">
                  <li><a href="#transit-hub-sights">Øresund Bridge Crossing</a></li>
                  <li><a href="#transit-hub-sights">Rønne Old Town & Laksegade</a></li>
                  <li><a href="#transit-hub-activities">Bornholmslinjen Express Ferry</a></li>
                  <li><a href="#transit-hub-activities">Hjorths Ceramic Factory</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#transit-hub-snacks" class="dropdown-dest-title">🎯 Market & Dining</a>
                <ul class="dropdown-links">
                  <li><a href="#transit-hub-snacks">Torve-Hallen Local Food Market</a></li>
                  <li><a href="#transit-hub-dining">Rådhuskroen Cozy Basement</a></li>
                  <li><a href="#transit-hub-dining">Det Røde Pakhus Harbor Bistro</a></li>
                  <li><a href="#transit-hub-dining">Mr. Long Asian Bistro</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  </nav>
"""


def get_baltic_sticky_nav():
    """Generates the tailored, clickable 5-country navigation bar for Baltic Route."""
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

      <!-- 5 Country Clickable Navigators & Drill-Downs -->
      <div class="nav-countries" id="navCountries">
        
        <!-- 1. Poland -->
        <div class="nav-dropdown" data-country="poland">
          <div class="nav-btn-group">
            <a href="#poland" class="nav-country-link" title="Jump to Poland section">
              <span>🇵🇱</span> <span>Poland</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Poland sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🇵🇱 Gdańsk, Gdynia & Malbork</span>
              <a href="#poland" class="dropdown-header-link">Country Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#poland-sights" class="dropdown-dest-title">🏛️ Hanseatic & Teutonic Heritage</a>
                <ul class="dropdown-links">
                  <li><a href="#poland-sights">WWII Museum Underground</a></li>
                  <li><a href="#poland-sights">Długi Targ & Neptune Fountain</a></li>
                  <li><a href="#poland-sights">Gdańsk Medieval Port Crane</a></li>
                  <li><a href="#poland-sights">Malbork Teutonic Castle</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#poland-activities" class="dropdown-dest-title">🎯 Markets & Pierogi</a>
                <ul class="dropdown-links">
                  <li><a href="#poland-activities">Stena Line Baltic Crossing</a></li>
                  <li><a href="#poland-activities">Gdańsk Christmas Market</a></li>
                  <li><a href="#poland-snacks">Dobra Pączkarnia Brioche Doughnuts</a></li>
                  <li><a href="#poland-dining">Mandu Handmade Pierogi</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. Lithuania -->
        <div class="nav-dropdown" data-country="lithuania">
          <div class="nav-btn-group">
            <a href="#lithuania" class="nav-country-link" title="Jump to Lithuania section">
              <span>🇱🇹</span> <span>Lithuania</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Lithuania sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🇱🇹 Vilnius & Trakai Island Castle</span>
              <a href="#lithuania" class="dropdown-header-link">Country Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#lithuania-sights" class="dropdown-dest-title">🏛️ Baroque & Castles</a>
                <ul class="dropdown-links">
                  <li><a href="#lithuania-sights">Vilnius UNESCO Old Town</a></li>
                  <li><a href="#lithuania-sights">Republic of Užupis</a></li>
                  <li><a href="#lithuania-sights">Trakai Island Castle</a></li>
                  <li><a href="#lithuania-sights">Hill of Crosses Pilgrimage</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#lithuania-activities" class="dropdown-dest-title">🎯 Illusions & Forest Dining</a>
                <ul class="dropdown-links">
                  <li><a href="#lithuania-activities">Vilnius Museum of Illusions</a></li>
                  <li><a href="#lithuania-activities">Cathedral Christmas Town</a></li>
                  <li><a href="#lithuania-snacks">Senoji Kibininė Pastries</a></li>
                  <li><a href="#lithuania-dining">Restoranas Lokys Wild Game</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. Latvia -->
        <div class="nav-dropdown" data-country="latvia">
          <div class="nav-btn-group">
            <a href="#latvia" class="nav-country-link" title="Jump to Latvia section">
              <span>🇱🇻</span> <span>Latvia</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Latvia sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🇱🇻 Riga & Sigulda Bobsleigh</span>
              <a href="#latvia" class="dropdown-header-link">Country Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#latvia-sights" class="dropdown-dest-title">🏛️ Art Nouveau & Fortress</a>
                <ul class="dropdown-links">
                  <li><a href="#latvia-sights">House of the Black Heads</a></li>
                  <li><a href="#latvia-sights">Art Nouveau Masterpieces</a></li>
                  <li><a href="#latvia-sights">Turaida Stone Castle</a></li>
                  <li><a href="#latvia-activities">Sigulda Olympic Bobsleigh</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#latvia-activities" class="dropdown-dest-title">🎯 Motor Museum & Taverns</a>
                <ul class="dropdown-links">
                  <li><a href="#latvia-activities">Riga Kremlin Motor Museum</a></li>
                  <li><a href="#latvia-activities">Dome Square Christmas Market</a></li>
                  <li><a href="#latvia-snacks">Black Magic Balsam Truffles</a></li>
                  <li><a href="#latvia-dining">Folkklubs ALA Medieval Cellar</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. Estonia -->
        <div class="nav-dropdown align-right" data-country="estonia">
          <div class="nav-btn-group">
            <a href="#estonia" class="nav-country-link" title="Jump to Estonia section">
              <span>🇪🇪</span> <span>Estonia</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Estonia sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🇪🇪 Medieval Tallinn & Seaplane Harbour</span>
              <a href="#estonia" class="dropdown-header-link">Country Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#estonia-sights" class="dropdown-dest-title">🏛️ Hanseatic Sights</a>
                <ul class="dropdown-links">
                  <li><a href="#estonia-sights">Tallinn Walled Old Town</a></li>
                  <li><a href="#estonia-sights">Toompea Panoramic Viewpoints</a></li>
                  <li><a href="#estonia-sights">Alexander Nevsky Cathedral</a></li>
                  <li><a href="#estonia-activities">Lennusadam Seaplane Harbour</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#estonia-activities" class="dropdown-dest-title">🎯 Maritime & Dining</a>
                <ul class="dropdown-links">
                  <li><a href="#estonia-activities">Tallinn Fairy-tale Market</a></li>
                  <li><a href="#estonia-activities">Tallink Silja Cruise Ferry</a></li>
                  <li><a href="#estonia-snacks">III Draakon Wild Elk Pies</a></li>
                  <li><a href="#estonia-dining">Rataskaevu 16 & Olde Hansa</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 5. Sweden -->
        <div class="nav-dropdown align-right" data-country="sweden">
          <div class="nav-btn-group">
            <a href="#sweden" class="nav-country-link" title="Jump to Sweden section">
              <span>🇸🇪</span> <span>Sweden</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Sweden sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🇸🇪 Stockholm Capital & Lake Vättern</span>
              <a href="#sweden" class="dropdown-header-link">Country Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#sweden-sights" class="dropdown-dest-title">🏛️ Maritime & Palaces</a>
                <ul class="dropdown-links">
                  <li><a href="#sweden-sights">Vasa Museum 1628 Warship</a></li>
                  <li><a href="#sweden-sights">Gamla Stan & Royal Palace</a></li>
                  <li><a href="#sweden-sights">Brahehus Castle Cliff Ruins</a></li>
                  <li><a href="#sweden-activities">Skansen Open-Air Museum</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#sweden-activities" class="dropdown-dest-title">🎯 Candy & Meatballs</a>
                <ul class="dropdown-links">
                  <li><a href="#sweden-activities">NYE Harbor Fireworks</a></li>
                  <li><a href="#sweden-snacks">Gränna Polkagris Candy Cane</a></li>
                  <li><a href="#sweden-snacks">Artisan Cardamom Buns</a></li>
                  <li><a href="#sweden-dining">Restaurang Tradition Meatballs</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  </nav>
"""


def get_iceland_sticky_nav():
    """Generates the tailored, clickable 5-region navigation bar for Iceland."""
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

      <!-- 5 Region Clickable Navigators & Drill-Downs -->
      <div class="nav-countries" id="navCountries">
        
        <!-- 1. Reykjanes -->
        <div class="nav-dropdown" data-country="reykjanes">
          <div class="nav-btn-group">
            <a href="#reykjanes" class="nav-country-link" title="Jump to Reykjanes section">
              <span>🌋</span> <span>Reykjanes</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Reykjanes sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🌋 Reykjanes Peninsula & Blue Lagoon</span>
              <a href="#reykjanes" class="dropdown-header-link">Region Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#reykjanes-sights" class="dropdown-dest-title">🏛️ Tectonics & Geothermal</a>
                <ul class="dropdown-links">
                  <li><a href="#reykjanes-sights">Bridge Between Continents</a></li>
                  <li><a href="#reykjanes-sights">Gunnuhver Mud Geysers</a></li>
                  <li><a href="#reykjanes-sights">Reykjanesviti Lighthouse</a></li>
                  <li><a href="#reykjanes-activities">Blue Lagoon Geothermal Spa</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#reykjanes-snacks" class="dropdown-dest-title">🎯 Bakeries & Dining</a>
                <ul class="dropdown-links">
                  <li><a href="#reykjanes-activities">Keflavík 4x4 Rental Hub</a></li>
                  <li><a href="#reykjanes-snacks">Kökulist Cinnamon Swirls</a></li>
                  <li><a href="#reykjanes-dining">Kaffi Duus Maritime Chowder</a></li>
                  <li><a href="#reykjanes-dining">Vocal Restaurant Lamb</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. Snæfellsnes -->
        <div class="nav-dropdown" data-country="snaefellsnes">
          <div class="nav-btn-group">
            <a href="#snaefellsnes" class="nav-country-link" title="Jump to Snæfellsnes section">
              <span>🏔️</span> <span>Snæfellsnes</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Snæfellsnes sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🏔️ West Iceland & Kirkjufell</span>
              <a href="#snaefellsnes" class="dropdown-header-link">Peninsula Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#snaefellsnes-sights" class="dropdown-dest-title">🏛️ Volcanic Landscapes</a>
                <ul class="dropdown-links">
                  <li><a href="#snaefellsnes-sights">Búðakirkja Black Church</a></li>
                  <li><a href="#snaefellsnes-sights">Arnarstapi Basalt Arches</a></li>
                  <li><a href="#snaefellsnes-sights">Djúpalónssandur Black Beach</a></li>
                  <li><a href="#snaefellsnes-sights">Kirkjufell Arrowhead Mountain</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#snaefellsnes-activities" class="dropdown-dest-title">🎯 Lava Tubes & Mussels</a>
                <ul class="dropdown-links">
                  <li><a href="#snaefellsnes-activities">Vatnshellir 8,000y Lava Cave</a></li>
                  <li><a href="#snaefellsnes-activities">Krauma Nature Geothermal Baths</a></li>
                  <li><a href="#snaefellsnes-snacks">Nesbrauð Dark Rye Bakery</a></li>
                  <li><a href="#snaefellsnes-dining">Bjargarsteinn & Narfeyrarstofa</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. Golden Circle -->
        <div class="nav-dropdown" data-country="golden-circle">
          <div class="nav-btn-group">
            <a href="#golden-circle" class="nav-country-link" title="Jump to Golden Circle section">
              <span>💨</span> <span>Golden Circle</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Golden Circle sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">💨 Geysir, Gullfoss & Tectonics</span>
              <a href="#golden-circle" class="dropdown-header-link">Route Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#golden-circle-sights" class="dropdown-dest-title">🏛️ Wonders & Waterfalls</a>
                <ul class="dropdown-links">
                  <li><a href="#golden-circle-sights">Þingvellir National Park</a></li>
                  <li><a href="#golden-circle-sights">Strokkur Boiling Geysir</a></li>
                  <li><a href="#golden-circle-sights">Gullfoss Golden Waterfall</a></li>
                  <li><a href="#golden-circle-sights">Kerið Red Crater Basin</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#golden-circle-activities" class="dropdown-dest-title">🎯 Geothermal Bread & Soup</a>
                <ul class="dropdown-links">
                  <li><a href="#golden-circle-activities">Fontana Geothermal Rye Bread</a></li>
                  <li><a href="#golden-circle-activities">Secret Lagoon Thermal Springs</a></li>
                  <li><a href="#golden-circle-snacks">Efstidalur Dairy Cow Gelato</a></li>
                  <li><a href="#golden-circle-dining">Friðheimar Tomato Greenhouse</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. Deep South -->
        <div class="nav-dropdown align-right" data-country="deep-south">
          <div class="nav-btn-group">
            <a href="#deep-south" class="nav-country-link" title="Jump to Deep South section">
              <span>🧊</span> <span>Deep South</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Deep South sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🧊 Glaciers, Waterfalls & Vík</span>
              <a href="#deep-south" class="dropdown-header-link">South Coast Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#deep-south-sights" class="dropdown-dest-title">🏛️ Waterfalls & Lagoons</a>
                <ul class="dropdown-links">
                  <li><a href="#deep-south-sights">Seljalandsfoss Walk-Behind</a></li>
                  <li><a href="#deep-south-sights">Skógafoss 60m Spray</a></li>
                  <li><a href="#deep-south-sights">Reynisfjara Basalt Columns</a></li>
                  <li><a href="#deep-south-sights">Jökulsárlón Glacier Lagoon</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#deep-south-activities" class="dropdown-dest-title">🎯 Ice Caves & Lava</a>
                <ul class="dropdown-links">
                  <li><a href="#deep-south-activities">Live Molten Lava Show Vík</a></li>
                  <li><a href="#deep-south-activities">Natural Blue Ice Cave Tour</a></li>
                  <li><a href="#deep-south-snacks">Skool Beans School Bus Cafe</a></li>
                  <li><a href="#deep-south-dining">The Soup Company Sourdough</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 5. Reykjavík -->
        <div class="nav-dropdown align-right" data-country="reykjavik">
          <div class="nav-btn-group">
            <a href="#reykjavik" class="nav-country-link" title="Jump to Reykjavík section">
              <span>🌈</span> <span>Reykjavík</span>
            </a>
            <button class="nav-caret-btn" type="button" aria-label="Toggle Reykjavík sections">▾</button>
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-header-title">🌈 Capital Architecture & Sky Lagoon</span>
              <a href="#reykjavik" class="dropdown-header-link">Capital Overview ➔</a>
            </div>
            <div class="dropdown-grid cols-2">
              <div class="dropdown-col">
                <a href="#reykjavik-sights" class="dropdown-dest-title">🏛️ Skyline & Icons</a>
                <ul class="dropdown-links">
                  <li><a href="#reykjavik-sights">Hallgrímskirkja Tower View</a></li>
                  <li><a href="#reykjavik-sights">Rainbow Street Boutiques</a></li>
                  <li><a href="#reykjavik-sights">Harpa Glass Concert Hall</a></li>
                  <li><a href="#reykjavik-sights">The Sun Voyager Sculpture</a></li>
                </ul>
              </div>
              <div class="dropdown-col">
                <a href="#reykjavik-activities" class="dropdown-dest-title">🎯 7-Step Spa & Seafood</a>
                <ul class="dropdown-links">
                  <li><a href="#reykjavik-activities">Sky Lagoon 7-Step Ocean Spa</a></li>
                  <li><a href="#reykjavik-activities">FlyOver Iceland Simulation</a></li>
                  <li><a href="#reykjavik-snacks">Bæjarins Beztu Lamb Hot Dog</a></li>
                  <li><a href="#reykjavik-dining">Messinn Pan-Sautéed Arctic Char</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  </nav>
"""

def generate_sticky_nav(fname, meta, body_md):
    """
    Determines whether a page should have a sticky nav and dynamically builds it.
    - index.md: NEVER has sticky nav (returns empty string).
    - czech-austria-slovakia-germany.md: Returns curated 4-country drill-down nav.
    - japan.md: Returns curated 5-region drill-down nav.
    - Future trip guides: Returns dynamically generated nav based on markdown headings.
    """
    sticky_nav_setting = str(meta.get("sticky_nav", "")).lower().strip()

    # index page NEVER has sticky nav
    if fname == "index.md" or sticky_nav_setting in ["false", "none", "no", "off"]:
        return ""

    if fname == "czech-austria-slovakia-germany.md" or sticky_nav_setting == "central-europe":
        return get_central_europe_sticky_nav()

    if fname == "japan.md" or sticky_nav_setting in ["japan", "japan-winter"]:
        return get_japan_sticky_nav()

    if fname == "bornholm.md" or sticky_nav_setting in ["bornholm", "bornholm-autumn"]:
        return get_bornholm_sticky_nav()

    if fname == "baltic-route.md" or sticky_nav_setting in ["baltic", "baltic-route", "baltics"]:
        return get_baltic_sticky_nav()

    if fname == "iceland.md" or sticky_nav_setting in ["iceland", "iceland-ring"]:
        return get_iceland_sticky_nav()

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

        # Statically wrap all tables in responsive scrolling containers
        content_html = re.sub(r'(<table\b[^>]*>.*?</table>)', r'<div class="table-container">\1</div>', content_html, flags=re.DOTALL)

        # Inject semantic IDs for headings (so anchor links jump with precision)
        content_html = inject_heading_ids(content_html)

        # Ensure all external item links default to open in a new tab
        content_html = make_external_links_open_in_new_tab(content_html)

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
