import os
import math
import requests
from typing import Dict, List, Tuple

GITHUB_API = "https://api.github.com"
USERNAME = "h4m1dr"  # GitHub username


def get_github_session() -> requests.Session:
    """Create a requests.Session with optional auth using GITHUB_TOKEN."""
    token = os.environ.get("GITHUB_TOKEN")
    session = requests.Session()
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "h4m1dr-lang-stats-script",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    session.headers.update(headers)
    return session


def fetch_repositories(session: requests.Session) -> List[dict]:
    """Fetch all public, non-fork repositories for the user."""
    repos: List[dict] = []
    page = 1

    while True:
        url = f"{GITHUB_API}/users/{USERNAME}/repos"
        params = {
            "per_page": 100,
            "page": page,
            "type": "owner",
            "sort": "updated",
        }
        resp = session.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1

    # Filter out forks
    return [r for r in repos if not r.get("fork")]


def fetch_language_stats(session: requests.Session, repos: List[dict]) -> Dict[str, int]:
    """Aggregate language byte counts across all repositories."""
    totals: Dict[str, int] = {}

    for repo in repos:
        languages_url = repo.get("languages_url")
        if not languages_url:
            continue

        resp = session.get(languages_url, timeout=20)
        resp.raise_for_status()
        langs = resp.json()

        for lang, count in langs.items():
            totals[lang] = totals.get(lang, 0) + int(count)

    return totals


def pick_top_languages(totals: Dict[str, int], max_langs: int = 6) -> List[Tuple[str, int]]:
    """Return a sorted list of top languages (name, bytes)."""
    items = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    if len(items) <= max_langs:
        return items

    top = items[: max_langs - 1]
    rest = items[max_langs - 1 :]
    other_sum = sum(v for _, v in rest)
    top.append(("Other", other_sum))
    return top


def generate_svg(langs: List[Tuple[str, int]], output_path: str) -> None:
    """Generate a simple horizontal bar chart SVG."""
    if not langs:
        # Fallback SVG
        svg = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="260">
  <rect width="100%" height="100%" fill="#ffffff" rx="12" ry="12"/>
  <text x="50%" y="50%" text-anchor="middle"
        fill="#555" font-family="Segoe UI, Arial, sans-serif" font-size="18">
    No language data available yet.
  </text>
</svg>"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg)
        return

    total_bytes = sum(v for _, v in langs)
    # Colors for languages (fallback palette)
    palette = [
        "#3572A5",  # blue
        "#89e051",  # green
        "#e34c26",  # orange
        "#f1e05a",  # yellow
        "#563d7c",  # purple
        "#2b7489",  # teal
        "#6a737d",  # gray
    ]

    width = 600
    height = 260
    card_margin = 16
    card_rx = 12

    title_x = card_margin + 12
    title_y = card_margin + 24

    legend_x = card_margin + 24
    legend_y_start = title_y + 20
    legend_line_height = 22

    bars_x = width * 0.45
    bars_y_start = legend_y_start
    bar_height = 14
    bar_gap = 10
    max_bar_width = width - bars_x - card_margin - 10

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        f'  <rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff" rx="{card_rx}" ry="{card_rx}"/>',
        f'  <text x="{title_x}" y="{title_y}" fill="#24292f" font-family="Segoe UI, Arial, sans-serif" font-size="20" font-weight="600">',
        "    Top Languages by Repo",
        "  </text>",
    ]

    for idx, (lang, count) in enumerate(langs):
        percent = (count / total_bytes) * 100 if total_bytes > 0 else 0.0
        color = palette[idx % len(palette)]
        # Legend
        ly = legend_y_start + idx * legend_line_height
        svg_lines.append(
            f'  <rect x="{legend_x}" y="{ly - 12}" width="12" height="12" rx="2" ry="2" fill="{color}" />'
        )
        svg_lines.append(
            f'  <text x="{legend_x + 18}" y="{ly - 2}" fill="#24292f" font-family="Segoe UI, Arial, sans-serif" font-size="13">'
            f'{lang} – {percent:.1f}%</text>'
        )

        # Bar
        bar_width = max_bar_width * (percent / 100.0)
        by = bars_y_start + idx * (bar_height + bar_gap)
        svg_lines.append(
            f'  <rect x="{bars_x}" y="{by}" width="{bar_width:.2f}" height="{bar_height}" rx="4" ry="4" fill="{color}" />'
        )

    svg_lines.append("</svg>")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))


def main() -> None:
    print("Fetching repositories and language stats for:", USERNAME)
    session = get_github_session()
    repos = fetch_repositories(session)
    print(f"Found {len(repos)} non-fork repositories.")

    totals = fetch_language_stats(session, repos)
    if not totals:
        print("No language data found.")
    else:
        print("Aggregated language totals:")
        for lang, val in sorted(totals.items(), key=lambda kv: kv[1], reverse=True):
            print(f"  {lang}: {val} bytes")

    top_langs = pick_top_languages(totals, max_langs=6)
    print("Top languages to display:", top_langs)

    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets_dir, exist_ok=True)
    output_path = os.path.join(assets_dir, "top_langs.svg")

    generate_svg(top_langs, output_path)
    print("SVG chart written to:", output_path)


if __name__ == "__main__":
    main()
