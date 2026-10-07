r"""N2_store_format_series.py
Builds three quarterly series from DKS earnings-release (8-K Ex 99.1) store/inventory tables, as transcribed in
WORKING_NOTES/W05_DKS_8K_PRESSRELEASES_A/B/C.md (verified against SOURCE/01_DKS_SEC_FILINGS/8-K/exhibits):
  1) House of Sport + Field House share of DICK'S-banner square footage (the formats where mgmt says vertical
     brands get "more space" but where the footwear deck is also ~50% larger).
  2) Golf Galaxy stores and Golf Galaxy Performance Centers (GGPC) vs management plans (golf = Maxfli/Walter
     Hagen/Top-Flite/Tommy Armour distribution).
  3) DICK'S Business inventory y/y vs DICK'S segment sales y/y.
Rerun: python PB_SCRAPE/scripts/N2_store_format_series.py -> PB_SCRAPE/raw/N2_store_format_series.csv
Update each quarter by appending a row from the new earnings release store-count table / inventory footnote.
"""
import csv, pathlib
OUT = pathlib.Path(r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\N2_store_format_series.csv")
# date, HoS count, FH count, HoS sqft M, FH sqft M, total DICK'S-banner sqft M, GG stores, GGPC, DKS-Bus inventory y/y %, DKS seg sales y/y %
rows = [
    ("2024-02-03", 12, 11, 1.2, 0.6, 39.3, 104, None, 1, 5.0),   # FY23 YE (FH count/sqft from FY24 begin column in Q4FY24 release)
    ("2024-11-02", 17, 22, None, None, 39.9, 109, None, 13, 0.5),  # first FH disclosure (Q3 FY24 release)
    ("2025-02-01", 19, 27, 2.2, 1.6, 40.1, 109, 24, 18, 3.5),      # FH 26->27 & 1.5->1.6 restated in Q1FY25 release
    ("2025-05-03", 21, 31, 2.5, 1.8, 40.1, 110, 27, 12, 5.2),
    ("2025-08-02", 22, 35, 2.6, 2.0, 40.2, 112, 30, 7, 5.0),
    ("2025-11-01", 35, 41, 3.8, 2.3, 40.8, 112, 31, 2, 5.9),       # inventory: DICK'S Business only from here
    ("2026-01-31", 35, 42, 3.8, 2.4, 40.6, 113, 33, 1, 4.0),
    ("2026-05-02", 36, 44, 3.9, 2.5, 40.6, 113, 36, 3, 6.4),
    ("2026-08-01", 41, 52, 4.5, 2.9, 41.0, 114, 37, 6, 5.6),
]
with OUT.open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["date", "hos", "fh", "hos_fh_sqft_m", "dicks_banner_sqft_m", "hos_fh_share_sqft_pct",
                "golf_galaxy_stores", "ggpc", "inventory_yoy_pct", "dks_sales_yoy_pct", "inv_minus_sales_pts"])
    for d, h, f, hs, fs, tot, gg, pc, inv, sal in rows:
        sq = (hs + fs) if hs is not None else None
        share = round(100 * sq / tot, 1) if sq is not None else None
        gap = round(inv - sal, 1) if (inv is not None and sal is not None) else None
        w.writerow([d, h, f, sq, tot, share, gg, pc, inv, sal, gap])
        print(d, "HoS+FH", h + f, "sqft", sq, "share%", share, "| GG", gg, "GGPC", pc, "| inv y/y", inv, "sales y/y", sal, "gap", gap)

