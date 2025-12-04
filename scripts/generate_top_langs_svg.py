#!/usr/bin/env python3
import os
import math
import requests
from pathlib import Path
from collections import defaultdict

GITHUB_API = "https://api.github.com"


def get_github_session():
    """Create a requests session with optional GitHub token."""
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    session = requests.Session()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "h4m1dr-lang-stats-script",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    session.headers.update(headers)
    return session


def fetch_repos(username: str, session: requests.Session):
    """Fetch all non-fork public repos for the given user."""
    repos = []
    page = 1
    while True:
        url = f"{GITHUB_API}/users/{username}/repos"
        params = {
            "per_page": 100,
            "page": page,
            "type": "owner",
            "sort": "full_name",
        }
        resp = session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        for repo in batch:
            if not repo.get("fork"):
                repos.append(repo)
        page += 1
    return repos


def fetch_languages_for_repo(repo, session: requests.Session):
    """Fetch language byte breakdown for a single repository."""
    url = repo.get("languages_url")
    if not url:
        return {}
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json() or {}


def aggregate_languages(username: str):
    """
    Aggregate language bytes over all non-fork public repos.

    Returns:
        dict[str, int]: language -> total bytes
    """
    session = get_github_session()
    repos = fetch_repos(username, session)

    language_totals = defaultdict(int)
    for repo in repos:
        langs = fetch_languages_for_repo(repo, session)
        for lang, size in langs.items():
            language_totals[lang] += int(size)

    return dict(language_totals)


# Simple GitHub-style language colors for nicer legend
LANG_COLORS = {
    "Python": "#3572A5",
    "Shell": "#89e051",
    "HTML": "#e34c26",
    "Dockerfile": "#384d54",
    "Makefile": "#427819",
}

DEFAULT_COLORS = [
    "#4C78A8",
    "#F58518",
    "#E45756",
    "#72B7B2",
    "#54A24B",
    "#EECA3B",
    "#B279A2",
]


def pick_color(lang: str, index: int) -> str:
    """Pick a color for the given language."""
    if lang in LANG_COLORS:
        return LANG_COLORS[lang]
    return DEFAULT_COLORS[index % len(DEFAULT_COLORS)]


def generate_donut_svg(lang_bytes: dict, output_path: Path):
    """
    Generate a donut chart SVG similar to 'Top Languages by Repo' cards.

    The chart:
      - Title at the top left
      - Legend on the left
      - Donut chart on the right
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle empty data
    if not lang_bytes:
        svg = """<svg xmlns="http://www.w3.org/2000/svg" width="500" height="260">
  <rect width="100%" height="100%" fill="#0d1117"/>
  <text x="50%" y="50%" text-anchor="middle" fill="#c9d1d9"
        font-size="16" font-family="Segoe UI, system-ui">
    No language data
  </text>
</svg>
"""
        output_path.write_text(svg, encoding="utf-8")
        return

    # Sort languages by bytes desc and keep top N
    TOP_N = 5
    items = sorted(lang_bytes.items(), key=lambda kv: kv[1], reverse=True)
    top_items = items[:TOP_N]
    if len(items) > TOP_N:
        other_total = sum(v for _, v in items[TOP_N:])
        top_items.append(("Other", other_total))

    total_bytes = sum(v for _, v in top_items)

    width, height = 500, 260
    cx, cy = 330, 145  # donut center (right side)
    r_outer, r_inner = 80, 45

    def arc_path(start_angle: float, end_angle: float, r_out: float, r_in: float) -> str:
        """Return SVG path for a donut slice between two angles (radians)."""
        x0 = cx + r_out * math.cos(start_angle)
        y0 = cy + r_out * math.sin(start_angle)
        x1 = cx + r_out * math.cos(end_angle)
        y1 = cy + r_out * math.sin(end_angle)

        x2 = cx + r_in * math.cos(end_angle)
        y2 = cy + r_in * math.sin(end_angle)
        x3 = cx + r_in * math.cos(start_angle)
        y3 = cy + r_in * math.sin(start_angle)

        large_arc_flag = 1 if (end_angle - start_angle) > math.pi else 0

        d = (
            f"M {x0:.2f} {y0:.2f} "
            f"A {r_out:.2f} {r_out:.2f} 0 {large_arc_flag} 1 {x1:.2f} {y1:.2f} "
            f"L {x2:.2f} {y2:.2f} "
            f"A {r_in:.2f} {r_in:.2f} 0 {large_arc_flag} 0 {x3:.2f} {y3:.2f} "
            "Z"
        )
        return d

    # Build SVG
    svg_parts = []
    svg_parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        'role="img" aria-labelledby="title desc">'
    )
    svg_parts.append('<title id="title">Top Languages by Repo</title>')
    svg_parts.append('<desc id="desc">Donut chart of top programming languages.</desc>')
    svg_parts.append('<rect width="100%" height="100%" fill="#0d1117" rx="8" />')

    # Title
    svg_parts.append(
        '<text x="32" y="40" fill="#c9d1d9" '
        'font-size="20" font-family="Segoe UI, system-ui">Top Languages by Repo</text>'
    )

    # Legend on the left
    legend_x = 40
    legend_y_start = 70
    legend_line_height = 22

    for idx, (lang, value) in enumerate(top_items):
        if value <= 0:
            continue
        color = pick_color(lang, idx)
        y = legend_y_start + idx * legend_line_height
        svg_parts.append(
            f'<rect x="{legend_x}" y="{y - 12}" width="14" height="14" '
            f'fill="{color}" rx="2" />'
        )

        percent = (value / total_bytes) * 100.0
        label = f"{lang} ({percent:.1f}%)"

        svg_parts.append(
            f'<text x="{legend_x + 22}" y="{y}" fill="#c9d1d9" '
            'font-size="13" font-family="Segoe UI, system-ui">'
            f"{label}</text>"
        )

    # Donut slices
    current_angle = -math.pi / 2  # start at top
    for idx, (lang, value) in enumerate(top_items):
        if value <= 0:
            continue
        color = pick_color(lang, idx)
        frac = value / total_bytes
        angle = frac * 2 * math.pi
        start_angle = current_angle
        end_angle = current_angle + angle
        current_angle = end_angle

        d = arc_path(start_angle, end_angle, r_outer, r_inner)
        svg_parts.append(
            f'<path d="{d}" fill="{color}" stroke="#0d1117" stroke-width="1"/>'
        )

    # Center text (optional – small label)
    svg_parts.append(
        f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" fill="#c9d1d9" '
        'font-size="12" font-family="Segoe UI, system-ui">Lang Stats</text>'
    )

    svg_parts.append("</svg>")

    output_path.write_text("\n".join(svg_parts), encoding="utf-8")


def main():
    # Try to detect username from environment; fallback to h4m1dr
    username = (
        os.getenv("GITHUB_USERNAME")
        or os.getenv("GITHUB_ACTOR")
        or "h4m1dr"
    )

    base_dir = Path(__file__).resolve().parents[1]
    output_svg = base_dir / "assets" / "top_langs.svg"

    lang_bytes = aggregate_languages(username)
    generate_donut_svg(lang_bytes, output_svg)
    print(f"Generated donut chart for {username} at {output_svg}")


if __name__ == "__main__":
    main()
