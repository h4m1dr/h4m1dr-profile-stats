# 🧬 h4m1dr – Top Languages Dashboard

This repository automatically generates an SVG chart showing my **top programming languages**
based on all my public GitHub repositories.

The SVG is updated regularly using **GitHub Actions** and the GitHub API.

---

## 📊 Top Languages (by bytes)

> Data is aggregated from all non-fork public repositories under **@h4m1dr**.

![Top Languages](https://raw.githubusercontent.com/h4m1dr/h4m1dr-lang-stats/main/assets/top_langs.svg)

---

## ⚙️ How it works

- `scripts/generate_top_langs_svg.py`  
  Fetches all repositories for `@h4m1dr`, calls the `/languages` API for each,
  aggregates the byte counts per language, and generates a clean SVG bar chart.

- `.github/workflows/update_langs.yml`  
  Runs on a schedule (cron) or manually via the **Actions** tab, regenerates the SVG,
  and commits it back to this repository.

---

## 🔗 Usage in other READMEs

In any other README (for example, in your main profile repo `h4m1dr/h4m1dr`),  
you can embed this chart with:

```md
![Top Languages](https://raw.githubusercontent.com/h4m1dr/h4m1dr-lang-stats/main/assets/top_langs.svg)
````

---

## 🛠 Roadmap

* [ ] Add per-repository breakdown
* [ ] Add support for grouping similar languages (e.g. TS/JS)
* [ ] Add alternative themes (dark / light)
* [ ] Add donut-style chart option