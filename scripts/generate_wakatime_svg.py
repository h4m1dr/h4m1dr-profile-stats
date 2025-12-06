import os


def main() -> None:
    """Generate a placeholder SVG for WakaTime stats."""
    svg_content = """
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="80">
  <style>
    .title { font: bold 16px sans-serif; fill: #e5e9f0; }
    .subtitle { font: 12px sans-serif; fill: #e5e9f0; }
  </style>
  <rect width="100%" height="100%" fill="#3b4252" rx="8" ry="8" />
  <text x="20" y="30" class="title">WakaTime</text>
  <text x="20" y="55" class="subtitle">Coming soon…</text>
</svg>
""".strip()

    os.makedirs("assets", exist_ok=True)
    output_path = os.path.join("assets", "wakatime.svg")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[INFO] Wrote placeholder WakaTime SVG to: {output_path}")


if __name__ == "__main__":
    main()
