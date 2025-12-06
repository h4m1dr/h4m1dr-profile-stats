import os
from datetime import datetime, timezone


def generate_weekly_svg(output_path: str) -> None:
    """
    Generate a simple placeholder weekly activity SVG.

    This does NOT use real GitHub data yet.
    It is only a visual component that can be embedded in the profile.
    """

    # Fake hours per day (placeholder values)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = [3.5, 4.2, 2.0, 5.1, 4.8, 1.2, 0.7]

    max_hours = max(hours) or 1.0
    width = 600
    height = 220
    bg = "#2e3440"

    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    bar_width = 40
    bar_gap = 20
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
    svg.append('<text x="24" y="32" class="title">Weekly Activity (placeholder)</text>')
    svg.append(
        '<text x="24" y="52" class="label">'
        'Sample hours per day – real GitHub data integration coming soon.'
        '</text>'
    )

    # Draw bars
    for idx, (day, h) in enumerate(zip(days, hours)):
        x = chart_left + idx * (bar_width + bar_gap)
        bar_height = (h / max_hours) * chart_height
        y = chart_bottom - bar_height

        svg.append(
            f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" '
            f'rx="6" fill="#5e81ac" />'
        )
        svg.append(
            f'<text x="{x + bar_width/2}" y="{chart_bottom + 16}" '
            f'text-anchor="middle" class="label">{day}</text>'
        )
        svg.append(
            f'<text x="{x + bar_width/2}" y="{y - 4}" text-anchor="middle" '
            f'class="hours">{h:.1f}h</text>'
        )

    # Last updated
    svg.append(
        f'<text x="24" y="{height - 16}" class="label">'
        f'Last updated on {updated_at}</text>'
    )

    svg.append('</svg>')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def main() -> None:
    output_path = os.path.join("assets", "weekly_activity.svg")
    print(f"[INFO] Generating weekly activity SVG at {output_path}")
    generate_weekly_svg(output_path)
    print("[INFO] Done.")


if __name__ == "__main__":
    main()
