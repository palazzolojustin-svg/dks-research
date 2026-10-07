# Raw scrape data (not in git)

The three `raw/` scrape folders (~6.3 GB, ~11,900 files) are excluded via `.gitignore` and stored as assets on the GitHub release **`raw-data`** of this repo:

| Asset | Unpacks to | Files | Compressed |
|---|---|---|---|
| `FL_EUROPE_SCRAPE_raw.tar.gz` | `FL_EUROPE_SCRAPE/raw/` | 509 | 47 MB |
| `PB_SCRAPE_raw.tar.gz` | `PB_SCRAPE/raw/` | 2,510 | 518 MB |
| `THESIS_SCRAPE_raw.tar.gz` | `THESIS_SCRAPE/raw/` | 8,865 | 1,525 MB |

Only download what the task needs. All findings, verdicts and memos from these scrapes are already in git (`wave*/`, `confirmed/`, `STATE.md`, HTML memos, `EVIDENCE_BOOK/`).

From the repo root:

```bash
gh release download raw-data --pattern 'PB_SCRAPE_raw.tar.gz'
tar -xzf PB_SCRAPE_raw.tar.gz && rm PB_SCRAPE_raw.tar.gz
```

All three at once:

```bash
gh release download raw-data --pattern '*_raw.tar.gz'
for f in *_raw.tar.gz; do tar -xzf "$f" && rm "$f"; done
```
