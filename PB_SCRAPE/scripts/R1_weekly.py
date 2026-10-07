"""R1 WEEKLY RE-RUN: DKS owned-brand review-share tracker (dicks.com Bazaarvoice front door; free, no login).

README
------
What it tracks: owned-brand (DSG, CALIA, VRST, Maxfli, Walter Hagen, Top-Flite, Tommy Armour, Alpine Design, ETHOS,
Fitness Gear, Nishiki, Quest, PRIMED) share of all-brand native reviews by category-month, split by review source:
  PIE  = post-purchase incentive email (purchase-triggered; best unit proxy; sent weekly on TUESDAYS)
  ORG  = organic (no campaign / MyAccount / BV display widgets)
plus head-to-head shares for ~35 national brands (Nike, Under Armour, adidas, Titleist, Callaway, ...).

Run (Windows PowerShell, from PB_SCRAPE\\scripts):   python R1_weekly.py
Steps (about 60-90 min, 6 threads; every step is resumable):
  1. R1_bv_pie_calendar.py   daily PIE counts -> raw/R1_pie_daily.csv. FIRST THING TO READ: did a Tuesday batch
                             go out? (PIE paused after 2026-08-11; if still paused, PIE-based Q3 reads end at Aug 17.)
  2. R1_bv_denominators.py   all-brand category-month totals by variant (re-pulls the last 4 months)
  3. incremental review pull for owned + national products with a review in the last LOOKBACK_DAYS
     (appends to raw/X01_reviews_dsg.csv and raw/R1_reviews_national.csv; duplicates removed in analysis)
  4. R1_analyze.py, R1_windows.py, R1_mix_index.py, R1_head2head.py, R1_charts_csv.py
What to look at: raw/R1_chart_owned_share_month.csv (APPAREL / MENS / KIDS / GOLFBALLS rows, column
owned_share_pie_plus_organic, same month y/y) and raw/R1_chart_h2h_fq.csv (owned vs Nike / Under Armour / Titleist).
Read-outs: compare SAME calendar windows y/y, never raw counts (review volume tripled mid-2025 when the PIE program
scaled, and fell ~30% y/y in 2026). Translate review-share change to sales-mix change with beta ~0.3-0.55
(back-test vs 10-K: FY23->FY24 0.29, FY24->FY25 0.54).
"""
import csv, datetime as dt, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
HERE = os.path.dirname(os.path.abspath(__file__))
from X01_bv_reviews import RAW
LOOKBACK_DAYS = 45


def run(script, *args):
    print(">>", script, *args, flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, script), *args], check=False, cwd=HERE)


def incremental():
    import R1_bv_national as N
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=LOOKBACK_DAYS)
    N.SINCE_EPOCH = int(cutoff.timestamp())
    stamp = dt.date.today().isoformat()
    # refresh product lists (new styles + last-review dates)
    for f in ("X01_products_dsg.csv", "R1_products_national.csv"):
        p = os.path.join(RAW, f)
        if os.path.exists(p):
            os.replace(p, p.replace(".csv", f"_prev.csv"))
    run("X01_bv_reviews.py", "products", "dsg")
    run("R1_bv_national.py", "products")
    for prodf, revf, tag, skip_fw in (("X01_products_dsg.csv", "X01_reviews_dsg.csv", "owned", False),
                                      ("R1_products_national.csv", "R1_reviews_national.csv", "national", True)):
        src = os.path.join(RAW, prodf)
        tmp = os.path.join(RAW, f"R1_tmp_recent_{tag}.csv")
        with open(src, encoding="utf-8") as fi, open(tmp, "w", newline="", encoding="utf-8") as fo:
            rd = csv.DictReader(fi); w = csv.DictWriter(fo, rd.fieldnames); w.writeheader()
            for r in rd:
                if r["last_sub"] and r["last_sub"][:10] >= cutoff.date().isoformat():
                    w.writerow(r)
        rpath = os.path.join(RAW, revf if tag == "national" else f"R1_reviews_owned_incr.csv")
        N.reviews(None, tmp, rpath, os.path.join(RAW, f"R1_done_{tag}_{stamp}.txt"), skip_fw)
    # merge owned increments into the X01 schema file used by R1_analyze
    import pandas as pd
    inc = os.path.join(RAW, "R1_reviews_owned_incr.csv")
    if os.path.exists(inc):
        a = pd.read_csv(os.path.join(RAW, "X01_reviews_dsg.csv"))
        b = pd.read_csv(inc)
        own = pd.read_csv(os.path.join(RAW, "X01_products_dsg.csv")).set_index("product_id").owned.to_dict()
        b["owned"] = b.product_id.map(own).fillna(1).astype(int)
        b = b[[c for c in a.columns if c in b.columns]]
        pd.concat([a, b]).drop_duplicates("review_id", keep="last").to_csv(os.path.join(RAW, "X01_reviews_dsg.csv"), index=False)


if __name__ == "__main__":
    run("R1_bv_pie_calendar.py")
    run("R1_bv_denominators.py")
    incremental()
    for s in ("R1_analyze.py", "R1_windows.py", "R1_mix_index.py", "R1_head2head.py", "R1_charts_csv.py"):
        run(s)
