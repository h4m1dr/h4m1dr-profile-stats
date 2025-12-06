# h4m1dr-profile-stats

This repository is the engine behind my GitHub profile widgets.

It is responsible for:
- Generating custom **Top Languages** SVG
- (Soon) Generating **weekly** and **monthly** activity stats
- (Soon) Generating **WakaTime** coding activity SVGs
- Periodically updating assets via GitHub Actions

## Output folders

- `assets/` → Public SVG files that can be embedded in my main profile README  
- `dist/` → Markdown snippets or other text outputs

Example usage in my main profile README:

```md
![Top Languages](https://raw.githubusercontent.com/h4m1dr/h4m1dr-profile-stats/main/assets/top_langs.svg)
````

More widgets and stats coming soon.
