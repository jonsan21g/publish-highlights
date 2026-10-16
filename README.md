# 🌍 Holiday Highlights & Curated Activity Guides

> An open, public collection of curated travel itineraries, destination highlights, alpine adventures, and authentic dining guides published directly via **GitHub Pages**.

---

## 🗺️ Available Holiday Guides

| Holiday Plan | Countries & Route | Key Highlights | Formats |
| :--- | :--- | :--- | :--- |
| **[Central Europe Winter Highlights](czech-austria-slovakia-germany.md)** | 🇨🇿 Czech Republic<br>🇦🇹 Austria<br>🇸🇰 Slovakia<br>🇩🇪 Germany | • Prague Castle, Klementinum & Old Town<br>• Český Krumlov UNESCO & Lipno Bobsleigh<br>• Vienna Palaces, Coffeehouses & Ice Dream<br>• Bratislava Castle & UFO Tower<br>• Ramsau am Dachstein Alpine Sleigh Ride<br>• Salzburg Fortress, Mozart & Hallstatt Skywalk<br>• Wildkogel 14 km World's Longest Toboggan Run<br>• Schloss Neuschwanstein "Disney Castle"<br>• Munich Hypercars, River Surfers & Breweries<br>• Allianz Arena Stadium Tour & Outlet Shopping | [📄 Markdown Guide](czech-austria-slovakia-germany.md)<br>[🌐 Standard Webpage](https://jonsan21g.github.io/publish-highlights/czech-austria-slovakia-germany.html)<br>[🎬 Video Edition](https://jonsan21g.github.io/publish-highlights/czech-austria-slovakia-germany-with-video.html) |
| **[Japan Winter Highlights & Dining Guide](japan.md)** | 🇯🇵 Japan<br>(Tokyo, Osaka, Kyoto, Uji, Nara) | • Tokyo Skyline, Shibuya Crossing & Parco<br>• Tokyo DisneySea & Fantasy Springs<br>• Osaka Castle, Dotonbori & USJ Super Nintendo World<br>• Fushimi Inari, Nara Deer & Uji Ceremonial Matcha<br>• Asakusa Senso-ji, Tokyo Skytree & Ginza Luxury<br>• teamLab Borderless, Kumachan Onsen & Gyukatsu | [📄 Markdown Guide](japan.md)<br>[🌐 Standard Webpage](https://jonsan21g.github.io/publish-highlights/japan.html)<br>[🎬 Video Edition](https://jonsan21g.github.io/publish-highlights/japan-with-video.html) |

---

## 🧭 Repository Structure

This repository is designed to host multiple independent holiday travel guides over time:

```text
publish-highlights/
├── README.md                           # Repository overview & collection directory (you are here)
├── index.md                            # GitHub Pages portal landing page listing all trips
├── czech-austria-slovakia-germany.md   # Central Europe winter trip guide (10 destinations, tabularized)
├── _config.yml                         # GitHub Pages / Jekyll configuration
├── _layouts/
│   └── default.html                    # Responsive layout with sticky nav, live search & table styling
├── build.py                            # Standalone static HTML compiler script
└── .gitignore                          # Clean repository ignores
```

---

## 🎯 Guide Design Standards

Every holiday plan in this collection follows strict publication standards:

1. **Zero PII & Universal Audience**: Free of personal names, ages, calendar dates, specific years, and private booking information. Any traveler can adapt the plan for their own journey.
2. **Structured Tabular Layout**: Every destination is organized into four standardized reference tables:
   - 🏛️ **Top Attractions & Sights**: Landmark name, architectural era, experience highlights, and practical visitor tips.
   - 🎯 **Activities & Unique Experiences**: Experience name, activity category, thrills, and booking requirements.
   - ☕ **Trending Snacks & Street Food**: Specialty, category, flavor profile, and where to try.
   - 🍽️ **Recommended Dining & Taverns**: Venue name, atmosphere, signature dishes, and **popular Asian dining alternatives** (pho, ramen, sushi).
3. **Verified Direct Links**: All venues, mountain railways, castles, and historic restaurants link directly to official websites.
4. **Mobile-First Responsive Web Design**: Tables feature smooth horizontal scrolling on mobile devices, live client-side search filtering, and sticky destination quick-jump links.

---

## ➕ Adding a New Holiday Plan in the Future

To add a new trip to this repository:
1. Create a new markdown file named after the trip (e.g., `nordic-summer-roadtrip.md` or `japan-autumn-highlights.md`).
2. Add the standard frontmatter at the top:
   ```yaml
   ---
   layout: default
   title: "Your Trip Title"
   description: "A brief summary of destinations and highlights."
   ---
   ```
3. Add a link to the new trip in [`index.md`](index.md) and [`README.md`](README.md).
4. Run `python build.py` to compile the static HTML page, then push to GitHub!

---

*Curated as a public travel resource for independent travelers.*
