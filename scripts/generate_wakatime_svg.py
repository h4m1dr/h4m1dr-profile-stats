import os
from datetime import datetime, timezone


def generate_wakatime_svg(output_path: str) -> None:
    """
    Generate a placeholder WakaTime SVG.

    Real WakaTime API integration will be added later.
    """

    width = 600
    height = 180
    bg = "#2e3440"

    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
    svg.append(
        '<style>'
        '.title{font:bold 18px sans-serif;fill:#eceff4;}'
        '.label{font:13px sans-serif;fill:#e5e9f0;}'
        '.mono{font:13px monospace;fill:#eceff4;}'
        '</style>'
    )

    svg.append(f'<rect width="100%" height="100%" fill="{bg}" rx="16" />')
    svg.append('<text x="24" y="32" class="title">WakaTime (placeholder)</text>')
    svg.append(
        '<text x="24" y="56" class="label">'
        'Real coding time from WakaTime API will appear here.'
        '</text>'
    )

    svg.append(
        '<text x="24" y="84" class="label">'
        'To enable this, add your WakaTime API key as a GitHub secret and '
        'update the generator script.'
        '</text>'
    )

    svg.append(
        f'<text x="24" y="{height - 16}" class="mono">'
        f'Last updated on {updated_at}</text>'
    )

    svg.append('</svg>')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def main() -> None:
    output_path = os.path.join("assets", "wakatime.svg")
    print(f"[INFO] Generating WakaTime SVG at {output_path}")
    generate_wakatime_svg(output_path)
    print("[INFO] Done.")


if __name__ == "__main__":
    main()
