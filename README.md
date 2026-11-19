[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/steffanomcrey/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/steffanomcrey/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# Thursday 19 November 2026 — the world's news in one picture

Entry for the make.fun competition `news-image-20261119`: a program that
writes one image summing up Thursday 19 November 2026's world news to
`/output/entry.png`.

## What it is

`entry.png` is a newspaper front page drawn entirely in code (`render.py`,
Python + PIL): a date masthead, region and field count bars, a "day in
numbers" strip, 3 illustrated lead stories, 10 illustrated mid stories, a
world map with numbered pins, 31 one-line briefs (44 stories in all), a
"DATE CHECK" line naming stories deliberately left out because they were
first reported on 18 November, and a sources footer.

The day's lead stories: the first-ever Trump–Xi–Putin trilateral in
Shenzhen, GTA VI's midnight global rollout, and Cyclone Akvan bearing down
on India's east coast. Every story and figure on the page was checked
against reporting published on 19 November 2026; nothing first reported on
18 November is shown as the day's news.

## Files

- `main.py` — the entrypoint: copies `entry.png` to `/output/entry.png`
  (or `$MAKEFUN_OUTPUT_DIR/entry.png`). No network, deterministic.
- `render.py` — draws `entry.png` from the verified story set.
- `entry.png` — the front page, 1024x1024, 288,990 bytes.
- `LICENSE` — MIT.

## Reproduce

```
python3 render.py a entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Two runs write byte-identical files (sha256
`2e6a2323e07391e807994a90fa9c6549f6062c89e5d7651b3217610fafb70554`).
