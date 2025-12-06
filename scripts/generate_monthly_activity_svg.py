import os
from datetime import datetime, timezone


def generate_monthly_svg(output_path: str) -> None:
    """
    Generate a simple placeholder monthly activity SVG.

    Shows total hours per week (4 weeks).
    """

    weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    hours = [14.0, 18.5, 10.0, 20.2]

    max_hours = max(hours) or 1.0
    width = 600
    height = 220
    bg = "#2e3440"

    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    bar_width = 60
    bar_gap = 30
    chart_left = 80
    chart_bottom = 150
    chart_height = 90

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
    svg.append(
        '<style>'
        '.title{font:bold 18px sans-serif;fill:#eceff4;}'
        '.label{font:12px sans-serif;fill:#e5e9f0;}'
        '.hours{font:12px monospace;fill:#eceff4;}'
        '</style>'
    )

    svg.append(f'<rect width="100%" height="100%" fill="{bg}" rx="16" />')
    svg.append('<text x="24" y="32" class="title">Monthly Activity (placeholder)</text>')
    svg.append(
        '<text x="24" y="52" class="label">'
        'Sample weekly totals – real GitHub data integration coming soon.'
        '</text>'
    )

    for idx, (week, h) in enumerate(zip(weeks, hours)):
        x = chart_left + idx * (bar_width + bar_gap)
        bar_height = (h / max_hours) * chart_height
        y = chart_bottom - bar_height

        svg.append(
            f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" '
            f'rx="6" fill="#a3be8c" />'
        )
        svg.append(
            f'<text x="{x + bar_width/2}" y="{chart_bottom + 16}" '
            f'text-anchor="middle" class="label">{week}</text>'
        )
        svg.append(
            f'<text x="{x + bar_width/2}" y="{y - 4}" text-anchor="middle" '
            f'class="hours">{h:.1f}h</text>'
        )

    svg.append(
        f'<text x="24" y="{height - 16}" class="label">'
        f'Last updated on {updated_at}</text>'
    )

    svg.append('</svg>')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def main() -> None:
    output_path = os.path.join("assets", "monthly_activity.svg")
    print(f"[INFO] Generating monthly activity SVG at {output_path}")
    generate_monthly_svg(output_path)
    print("[INFO] Done.")


if __name__ == "__main__":
    main()
