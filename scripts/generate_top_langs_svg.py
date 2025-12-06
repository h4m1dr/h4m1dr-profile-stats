import os
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
    Generate a simple horizontal bar chart SVG for top languages.

    The SVG is intentionally minimal so that it renders quickly in GitHub.
    """
    top_n = 6
    langs = lang_percentages[:top_n]

    if not langs:
        svg_content = """
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="60">
  <style>
    .title { font: bold 16px sans-serif; fill: #e5e9f0; }
    .label { font: 12px sans-serif; fill: #e5e9f0; }
  </style>
  <rect width="100%" height="100%" fill="#2e3440" rx="8" ry="8" />
  <text x="50%" y="50%" text-anchor="middle" class="title">
    No language data available
  </text>
</svg>
""".strip()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        return

    width = 600
    bar_area_width = 400
    bar_height = 18
    bar_gap = 10
    top_margin = 40
    left_margin = 150

    total_bar_height = len(langs) * (bar_height + bar_gap) - bar_gap
    height = top_margin + total_bar_height + 30

    svg_lines: List[str] = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
    svg_lines.append(
        '<style>'
        '.title { font: bold 16px sans-serif; fill: #e5e9f0; }'
        '.label { font: 12px sans-serif; fill: #e5e9f0; }'
        '.percent { font: 12px monospace; fill: #eceff4; }'
        '</style>'
    )
    svg_lines.append(f'<rect width="100%" height="100%" fill="#2e3440" rx="8" ry="8" />')
    svg_lines.append(
        f'<text x="20" y="24" class="title">Top Languages – {USERNAME}</text>'
    )

    max_percentage = max(p for _, p in langs) or 1.0

    for idx, (lang, perc) in enumerate(langs):
        y = top_margin + idx * (bar_height + bar_gap)
        bar_width = bar_area_width * (perc / max_percentage)

        svg_lines.append(
            f'<text x="20" y="{y + bar_height - 4}" class="label">{lang}</text>'
        )

        svg_lines.append(
            f'<rect x="{left_margin}" y="{y}" width="{bar_width:.1f}" '
            f'height="{bar_height}" fill="#5e81ac" rx="4" ry="4" />'
        )

        svg_lines.append(
            f'<text x="{left_margin + bar_area_width + 10}" y="{y + bar_height - 4}" '
            f'class="percent">{format_percentage(perc)}</text>'
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
