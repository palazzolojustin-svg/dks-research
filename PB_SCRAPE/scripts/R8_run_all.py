"""R8 monthly (or weekly) re-run of the DKS import-records pipeline. README:

    cd PB_SCRAPE\\scripts
    python R8_run_all.py            # refresh ImportYeti pages, then rebuild every R8 table
    python R8_run_all.py --offline  # rebuild tables from the payloads already in raw\\

Steps
 1. R8_iy_fetch.py: company/dick-s-merchandising-and-supply-cha (DKS's import entity), company/academy (control), and every
    DMSC supplier page (BOL windows). 20s spacing; ImportYeti soft-blocks an IP after bursts (pages come back as a "Not Found" shell).
    If that happens, stop and retry hours later; never try to get around it.
 2. Writes raw/R8_dmsc_monthly_<date>.csv (entity monthly shipments/TEU/kg) from the refreshed payload.
 3. R8_panel.py (supplier x quarter union panel, owned/national classes using DKS's factory list + BOL text, slug de-duplication,
    HS-chapter mix) -> R8_quarterly.py (kg split) -> R8_value_ieepa.py (value-weighted split + IEEPA reconciliation) -> R8_bol_monthly.py
    (BOL-level monthly check) -> R8_monthly_split.py (Jan-2023.. monthly CSV) -> R8_timing.py (seasonality/control) -> R8_academy_control.py.
What to look at each month: R8_value_weighted_quarterly.csv (owned_apparel_kg, own_share_val_classified[_exCDS]) for the current quarter vs
the same quarter of 2024 and 2023 (2025 is tariff-distorted); R8_bol_monthly_split.csv owned share; the latest months of R8_dmsc_monthly_*.csv
(note ImportYeti backfills the last 1-2 months upward). Add new suppliers to the class/group maps in R8_panel.py when they appear.
"""
import os, re, sys, json, csv, subprocess, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, "..", "raw")
PY = sys.executable


def run(*a):
    print(">>", " ".join(a), flush=True)
    subprocess.run([PY, *a], cwd=HERE, check=False)


if "--offline" not in sys.argv:
    run("R8_iy_fetch.py", "company", "dick-s-merchandising-and-supply-cha", "academy", "--force")
    p = os.path.join(RAW, "R8_iy_company_dick-s-merchandising-and-supply-cha.txt")
    if os.path.exists(p) and datetime.date.fromtimestamp(os.path.getmtime(p)) == datetime.date.today():
        big = open(p, encoding="utf-8").read()
        m = re.search(r'"data":\{("\d\d/\d\d/\d{4}":\{.*?\})\},"title":"[^"]*Total Sea Shipments Over Time"', big)
        if m:
            d = json.loads("{" + m.group(1) + "}")
            rows = sorted([f"{k[6:]}-{k[3:5]}", v["shipments"], v["teu"], v["weight"]] for k, v in d.items())
            with open(os.path.join(RAW, f"R8_dmsc_monthly_{datetime.date.today().isoformat()}.csv"), "w", newline="") as f:
                w = csv.writer(f); w.writerow(["month", "shipments", "teu", "weight_kg"]); w.writerows(rows)
    run("R8_iy_fetch.py", "dmsc_suppliers")
for s in ["R8_panel.py", "R8_quarterly.py", "R8_value_ieepa.py", "R8_bol_monthly.py", "R8_monthly_split.py", "R8_timing.py", "R8_academy_control.py", "R8_brand_tags.py"]:
    run(s)
