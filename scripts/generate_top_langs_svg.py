import os
import math
import requests
from collections import defaultdict
from typing import Dict, List, Tuple


GITHUB_API_URL = "https://api.github.com"
USERNAME = os.environ.get("GITHUB_USERNAME", "h4m1dr")
TOKEN = os.environ.get("GITHUB_TOKEN")


def get_session() -> requests.Session:
    """Create a configured requests session for GitHub API."""
    session = requests.Session()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "h4m1dr-profile-stats",
    }
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    session.headers.update(headers)
    return session


def fetch_repos(session: requests.Session, username: str) -> List[Dict]:
    """Fetch all non-fork repositories for the given user."""
    repos: List[Dict] = []
    page = 1

    while True:
        resp = session.get(
            f"{GITHUB_API_URL}/users/{username}/repos",
            params={
                "per_page": 100,
                "page": page,
                "type": "owner",
                "sort": "updated",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break

        for repo in data:
            if not repo.get("fork", False):
                repos.append(repo)

        page += 1

    return repos


def fetch_repo_languages(session: requests.Session, owner: str, repo_name: str) -> Dict[str, int]:
    """Fetch language byte counts for a single repository."""
    resp = session.get(
        f"{GITHUB_API_URL}/repos/{owner}/{repo_name}/languages",
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def aggregate_languages(session: requests.Session, repos: List[Dict]) -> Dict[str, int]:
    """Aggregate language usage across all repositories."""
    totals: Dict[str, int] = defaultdict(int)

    for repo in repos:
        name = repo["name"]
        owner = repo["owner"]["login"]

        try:
            langs = fetch_repo_languages(session, owner, name)
        except requests.HTTPError as e:
            print(f"[WARN] Failed to fetch languages for {owner}/{name}: {e}")
            continue

        for lang, bytes_count in langs.items():
            totals[lang] += int(bytes_count)

    return totals


def compute_percentages(language_totals: Dict[str, int]) -> List[Tuple[str, float]]:
    """Convert byte counts to percentage values and sort by usage."""
    total_bytes = sum(language_totals.values())
    if total_bytes == 0:
        return []

    items: List[Tuple[str, float]] = []
    for lang, bytes_count in language_totals.items():
        percentage = (bytes_count / total_bytes) * 100.0
        items.append((lang, percentage))

    # Sort descending by percentage
    items.sort(key=lambda x: x[1], reverse=True)
    return items


def format_percentage(value: float) -> str:
    """Format percentage with one decimal place, e.g. 23.4%."""
    return f"{value:.1f}%"


def generate_svg(lang_percentages: List[Tuple[str, float]], output_path: str) -> None:
    """
    Generate a donut chart SVG for top languages.

    Each language is rendered as an arc around a circle using stroke-dasharray.
    """
    # Show only top N languages
    top_n = 6
    langs = lang_percentages[:top_n]

    # Basic layout
    width = 600
    height = 260
    bg_color = "#2e3440"

    if not langs:
        svg_content = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="120">
  <style>
    .title {{ font: bold 16px sans-serif; fill: #e5e9f0; }}
    .label {{ font: 12px sans-serif; fill: #e5e9f0; }}
  </style>
  <rect width="100%" height="100%" fill="{bg_color}" rx="8" ry="8" />
  <text x="50%" y="50%" text-anchor="middle" class="title">
    No language data available
  </text>
</svg>
""".strip()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        return

    # Donut chart geometry
    center_x = 150
    center_y = 140
    radius = 70
    stroke_width = 32
    circumference = 2 * math.pi * radius

    # Simple color palette (looped if there are more langs)
    palette = [
        "#5e81ac",  # blue
        "#a3be8c",  # green
        "#ebcb8b",  # yellow
        "#bf616a",  # red
        "#b48ead",  # purple
        "#88c0d0",  # cyan
    ]

    svg_lines: List[str] = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
    svg_lines.append(
        '<style>'
        '.title { font: bold 18px sans-serif; fill: #e5e9f0; }'
        '.subtitle { font: 12px sans-serif; fill: #d8dee9; }'
        '.legend-label { font: 12px sans-serif; fill: #e5e9f0; }'
        '.legend-percent { font: 12px monospace; fill: #eceff4; }'
        '</style>'
    )
    svg_lines.append(f'<rect width="100%" height="100%" fill="{bg_color}" rx="16" ry="16" />')

    # Title
    svg_lines.append(
        f'<text x="24" y="32" class="title">Top Languages – {USERNAME}</text>'
    )

    # Background circle (full ring, muted color)
    svg_lines.append(
        f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" '
        f'fill="none" stroke="#3b4252" stroke-width="{stroke_width}" />'
    )

    # Draw each segment as a separate circle with dasharray
    current_offset = -0.25 * circumference  # start from top (12 o'clock)
    for idx, (lang, perc) in enumerate(langs):
        segment_length = circumference * (perc / 100.0)
        color = palette[idx % len(palette)]

        svg_lines.append(
            f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" '
            f'fill="none" stroke="{color}" stroke-width="{stroke_width}" '
            f'stroke-dasharray="{segment_length:.2f} {circumference - segment_length:.2f}" '
            f'stroke-dashoffset="{current_offset:.2f}" '
            f'stroke-linecap="round" />'
        )

        current_offset -= segment_length

    # Inner circle to create the donut "hole"
    svg_lines.append(
        f'<circle cx="{center_x}" cy="{center_y}" r="{radius - stroke_width / 2 + 4}" '
        f'fill="{bg_color}" />'
    )

    # Legend on the right
    legend_start_x = 250
    legend_start_y = 80
    legend_row_height = 24

    for idx, (lang, perc) in enumerate(langs):
        color = palette[idx % len(palette)]
        y = legend_start_y + idx * legend_row_height

        # Color box
        svg_lines.append(
            f'<rect x="{legend_start_x}" y="{y - 12}" width="14" height="14" '
            f'rx="3" ry="3" fill="{color}" />'
        )

        # Language label
        svg_lines.append(
            f'<text x="{legend_start_x + 22}" y="{y}" class="legend-label">{lang}</text>'
        )

        # Percentage
        svg_lines.append(
            f'<text x="{legend_start_x + 160}" y="{y}" class="legend-percent">'
            f'{format_percentage(perc)}</text>'
        )

    svg_lines.append("</svg>")

    svg_content = "\n".join(svg_lines)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)


def main() -> None:
    """Entry point for the script."""
    print(f"[INFO] Generating top languages SVG for user: {USERNAME}")
    session = get_session()

    repos = fetch_repos(session, USERNAME)
    print(f"[INFO] Found {len(repos)} non-fork repositories")

    lang_totals = aggregate_languages(session, repos)
    lang_percentages = compute_percentages(lang_totals)

    output_path = os.path.join("assets", "top_langs.svg")
    generate_svg(lang_percentages, output_path)

    print(f"[INFO] Wrote SVG to: {output_path}")


if __name__ == "__main__":
    main()
