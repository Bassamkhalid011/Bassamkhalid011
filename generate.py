"""
Generate all SVG assets for Bassamkhalid011 GitHub profile.
Produces: radar charts (dark + light), project cards (dark + light), stat card (dark + light).
Run: python generate.py
"""

import json
import math
import urllib.request
import urllib.error
import os

ACCENT   = "#6366F1"
USERNAME = "Bassamkhalid011"

# ── colours ──────────────────────────────────────────────────────────────────
DARK  = {"bg": "#0D1117", "surface": "#161B22", "border": "#30363D",
         "text": "#E6EDF3", "muted": "#8B949E", "accent": ACCENT,
         "fill": "#6366F122", "stroke": ACCENT}
LIGHT = {"bg": "#FFFFFF", "surface": "#F6F8FA", "border": "#D0D7DE",
         "text": "#1F2328", "muted": "#656D76", "accent": ACCENT,
         "fill": "#6366F115", "stroke": ACCENT}

os.makedirs("assets", exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# RADAR CHART
# ─────────────────────────────────────────────────────────────────────────────
def radar_svg(axes, title, theme, w=420, h=360):
    c  = theme
    cx, cy, r = w // 2, h // 2 + 10, min(w, h) // 2 - 60
    n  = len(axes)

    def pt(i, pct, radius=None):
        rad   = radius if radius else r
        angle = math.pi / 2 - 2 * math.pi * i / n
        return cx + rad * pct * math.cos(angle), cy - rad * pct * math.sin(angle)

    lines = []
    # background rings
    for ring in [0.25, 0.5, 0.75, 1.0]:
        pts = " ".join(f"{pt(i, ring)[0]:.1f},{pt(i, ring)[1]:.1f}" for i in range(n))
        lines.append(f'<polygon points="{pts}" fill="none" stroke="{c["border"]}" stroke-width="1"/>')

    # spokes
    for i in range(n):
        x2, y2 = pt(i, 1.0)
        lines.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c["border"]}" stroke-width="1"/>')

    # data polygon
    data_pts = " ".join(f"{pt(i, ax['value']/100)[0]:.1f},{pt(i, ax['value']/100)[1]:.1f}" for i, ax in enumerate(axes))
    lines.append(f'<polygon points="{data_pts}" fill="{c["fill"]}" stroke="{c["stroke"]}" stroke-width="2"/>')

    # dots
    for i, ax in enumerate(axes):
        x, y = pt(i, ax["value"] / 100)
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{c["accent"]}"/>')

    # labels
    for i, ax in enumerate(axes):
        lx, ly = pt(i, 1.28)
        anchor = "middle"
        if lx < cx - 10: anchor = "end"
        elif lx > cx + 10: anchor = "start"
        lines.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-family="JetBrains Mono,monospace" font-size="11" fill="{c["muted"]}">{ax["label"]}</text>')
        lines.append(f'<text x="{lx:.1f}" y="{ly+13:.1f}" text-anchor="{anchor}" font-family="JetBrains Mono,monospace" font-size="10" fill="{c["accent"]}" font-weight="600">{ax["value"]}</text>')

    # title
    lines.append(f'<text x="{cx}" y="22" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="12" fill="{c["muted"]}" letter-spacing="2">{title.upper()}</text>')

    inner = "\n  ".join(lines)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="{w}" height="{h}" rx="10" fill="{c['bg']}"/>
  {inner}
</svg>'''


def make_radars():
    with open("assets/skills.json") as f:
        data = json.load(f)
    axes  = data["axes"]
    title = data.get("title", "Skills")

    for theme, name in [(DARK, "dark"), (LIGHT, "light")]:
        svg = radar_svg(axes, title, theme)
        path = f"assets/radar-{name}.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"  wrote {path}")


# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE RADAR  (GitHub public API)
# ─────────────────────────────────────────────────────────────────────────────
EXCLUDE = {"html", "css", "shell", "makefile", "dockerfile", "batchfile", "procfile",
           "powershell", "nix"}

def fetch_lang_bytes(username):
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    req = urllib.request.Request(url, headers={"User-Agent": "profile-generator"})
    with urllib.request.urlopen(req, timeout=10) as r:
        repos = json.loads(r.read())
    totals = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        lurl = repo.get("languages_url", "")
        if not lurl:
            continue
        try:
            req2 = urllib.request.Request(lurl, headers={"User-Agent": "profile-generator"})
            with urllib.request.urlopen(req2, timeout=8) as r2:
                langs = json.loads(r2.read())
            for lang, b in langs.items():
                if lang.lower() not in EXCLUDE:
                    totals[lang] = totals.get(lang, 0) + b
        except Exception:
            pass
    return totals

def make_lang_radar(username, limit=7, curve=0.4):
    print("  fetching language data from GitHub API…")
    try:
        totals = fetch_lang_bytes(username)
    except Exception as e:
        print(f"  API error: {e} — skipping language radar")
        return

    top = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:limit]
    if not top:
        return
    max_b = top[0][1]

    def scale(b):
        return round((b / max_b) ** curve * 100)

    axes = [{"label": lang, "value": scale(b), "raw": b} for lang, b in top]

    for theme, name in [(DARK, "dark"), (LIGHT, "light")]:
        svg = radar_svg(axes, "Lang Radar · real bytes", theme)
        path = f"assets/radar-langs-{name}.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"  wrote {path}")


# ─────────────────────────────────────────────────────────────────────────────
# PROJECT CARDS
# ─────────────────────────────────────────────────────────────────────────────
def fetch_repo(username, repo):
    url = f"https://api.github.com/repos/{username}/{repo}"
    req = urllib.request.Request(url, headers={"User-Agent": "profile-generator"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read())
    except Exception:
        return {}

def wrap_text(text, max_chars=58):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:3]

def card_svg(repo_name, description, stars, forks, language, theme, w=420, h=160):
    c = theme
    desc_lines = wrap_text(description)
    desc_svg = ""
    for i, line in enumerate(desc_lines):
        desc_svg += f'<text x="20" y="{72 + i*18}" font-family="Inter,sans-serif" font-size="12" fill="{c["muted"]}">{line}</text>\n  '

    lang_dot = f'<circle cx="20" cy="{h-22}" r="5" fill="{c["accent"]}"/>' if language else ""
    lang_txt = f'<text x="30" y="{h-18}" font-family="JetBrains Mono,monospace" font-size="11" fill="{c["muted"]}">{language}</text>' if language else ""

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="{w}" height="{h}" rx="10" fill="{c['surface']}" stroke="{c['border']}" stroke-width="1"/>
  <rect width="4" height="{h}" rx="2" fill="{c['accent']}"/>
  <text x="20" y="38" font-family="JetBrains Mono,monospace" font-size="14" font-weight="700" fill="{c['text']}">{repo_name}</text>
  {desc_svg}
  {lang_dot}
  {lang_txt}
  <text x="{w-90}" y="{h-18}" font-family="JetBrains Mono,monospace" font-size="11" fill="{c['muted']}">★ {stars}  ⑂ {forks}</text>
</svg>'''


def make_cards():
    with open("assets/projects.json") as f:
        data = json.load(f)

    for proj in data["projects"]:
        repo_name = proj["repo"]
        desc      = proj["description"]
        info      = fetch_repo(USERNAME, repo_name)
        stars     = info.get("stargazers_count", 0)
        forks     = info.get("forks_count", 0)
        language  = info.get("language", "")

        slug = repo_name.replace(" ", "-")
        for theme, name in [(DARK, "dark"), (LIGHT, "light")]:
            svg  = card_svg(repo_name, desc, stars, forks, language, theme)
            path = f"assets/card-{slug}-{name}.svg"
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
            print(f"  wrote {path}")


# ─────────────────────────────────────────────────────────────────────────────
# STAT CARD
# ─────────────────────────────────────────────────────────────────────────────
def fetch_stats(username):
    url = f"https://api.github.com/users/{username}"
    req = urllib.request.Request(url, headers={"User-Agent": "profile-generator"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read())

def stat_card_svg(stats, theme, w=800, h=120):
    c    = theme
    user = stats.get("login", USERNAME)
    repos = stats.get("public_repos", 0)
    followers = stats.get("followers", 0)
    following = stats.get("following", 0)

    tiles = [
        ("Public Repos", str(repos)),
        ("Followers",    str(followers)),
        ("Following",    str(following)),
    ]
    tile_w = w // len(tiles)
    tiles_svg = ""
    for i, (label, val) in enumerate(tiles):
        tx = i * tile_w + tile_w // 2
        tiles_svg += f'''
  <text x="{tx}" y="52" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="26" font-weight="700" fill="{c['text']}">{val}</text>
  <text x="{tx}" y="78" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="{c['muted']}" letter-spacing="1">{label.upper()}</text>'''
        if i < len(tiles) - 1:
            tiles_svg += f'<line x1="{(i+1)*tile_w}" y1="20" x2="{(i+1)*tile_w}" y2="{h-20}" stroke="{c["border"]}" stroke-width="1"/>'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="{w}" height="{h}" rx="10" fill="{c['surface']}" stroke="{c['border']}" stroke-width="1"/>
  <rect width="{w}" height="4" rx="2" fill="{c['accent']}"/>
  {tiles_svg}
</svg>'''

def make_stat_card():
    print("  fetching user stats…")
    try:
        stats = fetch_stats(USERNAME)
    except Exception as e:
        print(f"  API error: {e} — skipping stat card")
        return
    for theme, name in [(DARK, "dark"), (LIGHT, "light")]:
        svg  = stat_card_svg(stats, theme)
        path = f"assets/card-stats-{name}.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"  wrote {path}")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n[ radar — self-rated ]")
    make_radars()

    print("\n[ radar — language bytes ]")
    make_lang_radar(USERNAME)

    print("\n[ project cards ]")
    make_cards()

    print("\n[ stat card ]")
    make_stat_card()

    print("\nDone. All SVGs written to assets/")
    print("Next: add your photo as me.jpg and run:")
    print("  python scripts/dotify.py me.jpg -o assets/portrait --cols 100 --equalize --detail 0.5 --color")
