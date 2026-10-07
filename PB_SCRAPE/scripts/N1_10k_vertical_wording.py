"""N1 (wave 2): DKS 10-K owned/vertical/private-brand WORDING tracker, FY2012-FY2025.

What it does
- Reads DKS 10-K documents already cached by X13 in PB_SCRAPE/raw/X13_edgar_cache (EDGAR primary docs,
  .htm or .htm.txt), plus optionally fetches any missing 10-K from EDGAR (SEC fair-access UA header).
- Splits each 10-K into sentences and keeps every sentence mentioning private/vertical/owned/exclusive brands
  or any DKS owned-brand name.
- Flags key phrases (forward-looking "improved space in-store / increased marketing / additional product
  categories", "growing vertical brands", "second largest ...", "$X billion", "approximately X%"),
  counts mentions per 10k words, and lists owned/licensed brand names present.

Outputs
- PB_SCRAPE/raw/N1_10k_vertical_sentences.csv   (fiscal_year, filed, sentence)
- PB_SCRAPE/raw/N1_10k_vertical_summary.csv     (one row per 10-K: flags, counts, brand lists)

Rerun each spring (new 10-K ~late March): add the new primary-doc URL to EXTRA_URLS (or drop its text into
the cache folder) and run:  python PB_SCRAPE/scripts/N1_10k_vertical_wording.py
Compare the new row's flags/sentences to the prior year (wording diffs are the signal).
"""
import csv, os, re, sys, time
from pathlib import Path

ROOT = Path(r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE")
CACHE = ROOT / "raw" / "X13_edgar_cache"
OUT_SENT = ROOT / "raw" / "N1_10k_vertical_sentences.csv"
OUT_SUM = ROOT / "raw" / "N1_10k_vertical_summary.csv"
UA = {"User-Agent": "DKS research palazzolojustin@gmail.com"}

# accession-folder doc -> (fiscal year label, filing date). Filing dates from EDGAR submissions JSON.
DOCS = {
    "a2208040z10_k_htm": ("FY2011", "2012-03"),
    "a2213667z10_k_htm": ("FY2012", "2013-03"),
    "dks_20140201x10k_htm": ("FY2013", "2014-03"),
    "dks_10k_20150131_htm": ("FY2014", "2015-03"),
    "dks_10k_20160130_htm": ("FY2015", "2016-03"),
    "dks_10k_20170128_htm": ("FY2016", "2017-03"),
    "dks_10k_20180203_htm": ("FY2017", "2018-03"),
    "dks_10k_20190202_htm": ("FY2018", "2019-03"),
    "dks_20200201_htm": ("FY2019", "2020-03"),
    "dks_20210130_htm": ("FY2020", "2021-03"),
    "dks_20220129_htm": ("FY2021", "2022-03"),
    "dks_20230128_htm": ("FY2022", "2023-03-23"),
    "dks_20240203_htm": ("FY2023", "2024-03-28"),
    "dks_20250201_htm": ("FY2024", "2025-03-27"),
    "dks_20260131_htm": ("FY2025", "2026-03-27"),
}

OWNED = ["Alpine Design", "CALIA", "DSG", "ETHOS", "Fitness Gear", "MAXFLI", "Maxfli", "Nishiki", "Quest",
         "Tommy Armour", "Top-Flite", "Top Flite", "VRST", "Walter Hagen", "Field & Stream", "Field and Stream",
         "Slazenger", "Ativa", "Primed", "Monarch", "Lady Fairway", "Umbro", "Velocity"]
LICENSED = ["adidas (football)", "adidas (baseball", "Cobra", "Marucci", "Lotto", "Prince", "Nike ACG", "Reebok"]
KEY = re.compile(r"(?i)(private[- ]brand|private[- ]label|vertical brand|owned brand|own brand|exclusive brand|"
                 r"proprietary brand|" + "|".join(re.escape(b) for b in OWNED) + r")")
PHRASES = {
    "fls_improved_space": r"(?i)improved space in-store",
    "fls_increased_marketing": r"(?i)increased marketing",
    "fls_additional_categories": r"(?i)(additional product categories|expanding product categories)",
    "growing_vertical": r"(?i)growing (vertical|private)",
    "second_largest": r"(?i)second largest (brand category|brand|vendor)",
    "higher_margin": r"(?i)higher (gross )?margins?",
    "rd_procurement_staff": r"(?i)research, development and procurement staff",
    "particularly_within_dicks": r"(?i)particularly within our DICK",
    "fls_grow_private_brand": r"(?i)plans to grow our (private|vertical) brand",
    "fls_new_private_brands": r"(?i)(addition|launch) of new (private|vertical) brands",
}


def text_of(path: Path) -> str:
    txt = path.with_name(path.name + ".txt")
    if txt.exists():
        return txt.read_text(encoding="utf-8", errors="ignore")
    raw = path.read_text(encoding="utf-8", errors="ignore")
    try:
        from bs4 import BeautifulSoup
        t = BeautifulSoup(raw, "html.parser").get_text(" ")
    except Exception:
        t = re.sub(r"<[^>]+>", " ", raw)
    t = re.sub(r"&#160;|&nbsp;", " ", t)
    t = re.sub(r"\s+", " ", t)
    txt.write_text(t, encoding="utf-8")
    return t


def find_doc(key: str):
    for p in CACHE.iterdir():
        if p.name.endswith(key) and "1089063" in p.name:
            return p
    return None


def main():
    sent_rows, sum_rows = [], []
    for key, (fy, filed) in DOCS.items():
        p = find_doc(key)
        if p is None:
            print("missing", key, file=sys.stderr)
            continue
        t = text_of(p)
        t = re.sub(r"\s+", " ", t)
        words = len(t.split())
        sents = re.split(r"(?<=[.;])\s+(?=[A-Z\u2022•])", t)
        hits = [s.strip() for s in sents if KEY.search(s) and len(s) < 4000]
        # de-dup
        seen, uniq = set(), []
        for s in hits:
            k = s[:200]
            if k not in seen:
                seen.add(k); uniq.append(s)
        for s in uniq:
            sent_rows.append({"fiscal_year": fy, "filed": filed, "sentence": s})
        n_vert = len(re.findall(r"(?i)vertical brand", t))
        n_priv = len(re.findall(r"(?i)private[- ]brand|private[- ]label", t))
        dollars = sorted(set(m.group(0) for s in uniq for m in re.finditer(r"\$\s?\d[\d.,]*\s?(billion|million)", s)))
        pcts = sorted(set(m.group(0) for s in uniq for m in re.finditer(r"approximately \d+(\.\d+)?%", s)))
        row = {"fiscal_year": fy, "filed": filed, "words": words, "n_vertical_brand": n_vert,
               "n_private_brand_label": n_priv, "per_10k_words": round((n_vert + n_priv) / words * 1e4, 2),
               "dollar_mentions": "; ".join(dollars), "pct_mentions": "; ".join(pcts),
               "owned_names_present": "; ".join(b for b in OWNED if re.search(r"\b" + re.escape(b) + r"\b", t)),
               "licensed_names_present": "; ".join(b for b in LICENSED if b in t)}
        for k, rx in PHRASES.items():
            row[k] = int(bool(re.search(rx, t)))
        sum_rows.append(row)
        print(fy, words, n_vert, n_priv, dollars, pcts)
    with OUT_SENT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["fiscal_year", "filed", "sentence"]); w.writeheader(); w.writerows(sent_rows)
    with OUT_SUM.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sum_rows[0].keys())); w.writeheader(); w.writerows(sum_rows)
    print("wrote", OUT_SENT, OUT_SUM)


if __name__ == "__main__":
    main()
