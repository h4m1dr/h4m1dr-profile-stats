import os
import math
import requests
from collections import defaultdict
from typing import Dict, List, Tuple

GITHUB_API_URL = "https://api.github.com"
USERNAME = os.environ.get("GITHUB_USERNAME", "h4m1dr")
TOKEN = os.environ.get("GITHUB_TOKEN")


# -------------------------------
# Fetching GitHub repository data
# -------------------------------

def get_session() -> requests.Session:
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
    repos: List[Dict] = []
    page = 1

    while True:
        resp = session.get(
            f"{GITHUB_API_URL}/users/{username}/repos",
            params={"per_page": 100, "page": page, "type": "owner"},
            timeout=20,
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
    resp = session.get(
        f"{GITHUB_API_URL}/repos/{owner}/{repo_name}/languages",
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def aggregate_languages(session: requests.Session, repos: List[Dict]) -> Dict[str, int]:
    totals: Dict[str, int] = defaultdict(int)

    for repo in repos:
        name = repo["name"]
        owner = repo["owner"]["login"]

        try:
            langs = fetch_repo_languages(session, owner, name)
        except Exception as e:
            print(f"[WARN] Failed to fetch languages for {name}: {e}")
            continue

        for lang, bytes_count in langs.items():
            totals[lang] += int(bytes_count)

    return totals


def compute_percentages(language_totals: Dict[str, int]) -> List[Tuple[str, float]]:
    total = sum(language_totals.values())
    if total == 0:
        return []

    result = [
        (lang, (count / total) * 100.0)
        for lang, count in language_totals.items()
    ]

    result.sort(key=lambda x: x[1], reverse=True)
    return result


def format_percentage(v: float) -> str:
    return f"{v:.1f}%"


# -------------------------------
# Donut chart SVG generator
# -------------------------------

def generate_svg(lang_percentages: List[Tuple[str, float]], output_path: str) -> None:
    """
    Draws a donut chart SVG for top languages.
    Smaller radius + larger fonts.
    """
    top_n = 6
    langs = lang_percentages[:top_n]

    width = 600
    height = 260
    bg = "#2e3440"

    if not langs:
        svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="120">
  <rect width="100%" height="100%" fill="{bg}" />
  <text x="50%" y="50%" text-anchor="middle" fill="#eceff4" font-size="16">
    No language data available
  </text>
</svg>
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg)
        return

    # Donut geometry (smaller)
    cx, cy = 150, 140
    radius = 50
    stroke_width = 24
    circumference = 2 * math.pi * radius

    palette = ["#5e81ac", "#a3be8c", "#ebcb8b", "#bf616a", "#b48ead", "#88c0d0"]

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')

    svg.append(
        '<style>'
        '.title{font:bold 20px sans-serif;fill:#eceff4;}'
        '.legend{font:13px sans-serif;fill:#eceff4;}'
        '.percent{font:13px monospace;fill:#eceff4;}'
        '</style>'
    )

    svg.append(f'<rect width="100%" height="100%" fill="{bg}" rx="16" />')
    svg.append(f'<text x="24" y="32" class="title">Top Languages – {USERNAME}</text>')

    # Background ring
    svg.append(
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" '
        f'stroke="#3b4252" stroke-width="{stroke_width}" fill="none" />'
    )

    # Draw segments
    offset = -0.25 * circumference
    for i, (lang, perc) in enumerate(langs):
        seg_len = circumference * (perc / 100)
        color = palette[i % len(palette)]

        svg.append(
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" '
            f'stroke="{color}" stroke-width="{stroke_width}" '
            f'stroke-dasharray="{seg_len:.2f} {circumference - seg_len:.2f}" '
            f'stroke-dashoffset="{offset:.2f}" stroke-linecap="round" />'
        )

        offset -= seg_len

    # Inner hole
    svg.append(
        f'<circle cx="{cx}" cy="{cy}" r="{radius - stroke_width/2 + 4}" fill="{bg}" />'
    )

    # Legend
    lx, ly = 250, 80
    row_h = 24

    for i, (lang, perc) in enumerate(langs):
        color = palette[i % len(palette)]
        y = ly + i * row_h

        svg.append(
            f'<rect x="{lx}" y="{y - 12}" width="14" height="14" rx="3" fill="{color}" />'
        )
        svg.append(
            f'<text x="{lx + 22}" y="{y}" class="legend">{lang}</text>'
        )
        svg.append(
            f'<text x="{lx + 160}" y="{y}" class="percent">{format_percentage(perc)}</text>'
        )

    svg.append("</svg>")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


# -------------------------------
# Main runner
# -------------------------------

def main():
    print(f"[INFO] Generating top languages donut for: {USERNAME}")

    session = get_session()
    repos = fetch_repos(session, USERNAME)
    totals = aggregate_languages(session, repos)
    percentages = compute_percentages(totals)

    generate_svg(percentages, os.path.join("assets", "top_langs.svg"))
    print("[INFO] Done.")


if __name__ == "__main__":
    main()
