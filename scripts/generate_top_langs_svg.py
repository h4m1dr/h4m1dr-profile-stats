def generate_svg(lang_percentages: List[Tuple[str, float]], output_path: str) -> None:
    """
    Generate a donut chart SVG for top languages.

    The donut is slightly smaller and text a bit larger for better balance.
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
    .title {{ font: bold 20px sans-serif; fill: #e5e9f0; }}
    .label {{ font: 13px sans-serif; fill: #e5e9f0; }}
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

    # Donut chart geometry (smaller radius and slightly thinner ring)
    # Previous radius was 70; now we reduce it ~30%.
    center_x = 150
    center_y = 140
    radius = 50           # smaller donut
    stroke_width = 24     # slightly thinner stroke
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
        '.title { font: bold 20px sans-serif; fill: #e5e9f0; }'
        '.subtitle { font: 13px sans-serif; fill: #d8dee9; }'
        '.legend-label { font: 13px sans-serif; fill: #e5e9f0; }'
        '.legend-percent { font: 13px monospace; fill: #eceff4; }'
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
