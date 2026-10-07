"""Q2 task 2: refresh the DKS (dicks.com Bazaarvoice) apparel review-share read through today (2026-10-07).

Re-uses PB_SCRAPE/scripts/X01_bv_reviews.py (session_for, get, OWNED list) read-only; all output goes to
EVIDENCE_BOOK/Q2/ (nothing under PB_SCRAPE is written).

Steps
  cal   : daily ALL / PIE review counts, Apparel-129823, 2025-07-15..2025-10-07 and 2026-07-15..today
          -> Q2_dks_pie_daily.csv  (did a Tuesday post-purchase-email batch go out after 2026-08-11?)
  den   : all-brand denominators for the 4 apparel categories (R1 basket), by window x variant
          windows: A=Aug1-17, B=Aug18-Oct6, C=Aug1-Oct6 (both 2025 and 2026), variants ALL/PIE/NULL/MYACC/BVDISP/BVMOB
          -> Q2_dks_den_windows.csv
  prod  : fresh owned-brand product list (products.json by BrandId, all owned brands) -> Q2_dks_owned_products.csv
  rev   : native reviews since 2025-07-01 on owned products in the apparel basket with a review since then
          -> Q2_dks_owned_reviews_recent.csv
RERUN: python Q2_dks_refresh.py cal den prod rev ; then python Q2_did.py
Politeness: 4 threads, small sleep per call.
"""
import csv, os, sys, time, datetime as dt
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\scripts")
import X01_bv_reviews as X  # read-only import

OUT = os.path.dirname(os.path.abspath(__file__))
APP = ["WomensApparel-129841", "MensApparel-129824", "BoysApparel-129859", "girls-apparel-footwear"]
VARS = {"ALL": [], "PIE": [("Filter", "CampaignId:eq:ESP_PIE_INCENTIVE")], "NULL": [("Filter", "CampaignId:eq:null")],
        "MYACC": [("Filter", "CampaignId:eq:MyAccount")], "BVDISP": [("Filter", "CampaignId:eq:BV_REVIEW_DISPLAY")],
        "BVMOB": [("Filter", "CampaignId:eq:BV_MOBILE_REVIEW_DISPLAY")]}
WINS = {"A_Aug1-17": ("08-01", "08-18"), "B_Aug18-Oct6": ("08-18", "10-07"), "C_Aug1-Oct6": ("08-01", "10-07")}
S = X.session_for("dsg")


def ep(d):
    return int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp())


def g(params):
    time.sleep(0.15)
    return X.get(S, "dsg", "reviews", params)


def cal():
    days = []
    for y in (2025, 2026):
        d0, d1 = dt.date(y, 7, 15), min(dt.date(y, 10, 7), dt.date.today())
        days += [d0 + dt.timedelta(i) for i in range((d1 - d0).days + 1)]
    jobs = [(d, v) for d in days for v in ("ALL", "PIE")]

    def q(j):
        d, v = j
        a = ep(d)
        r = g([("Filter", "CategoryAncestorId:eq:Apparel-129823"), ("Filter", f"SubmissionTime:gte:{a}"),
               ("Filter", f"SubmissionTime:lt:{a + 86400}"), ("Limit", "1")] + VARS[v])
        return str(d), d.strftime("%a"), v, r.get("TotalResults")
    with ThreadPoolExecutor(4) as ex:
        rows = list(ex.map(q, jobs))
    with open(os.path.join(OUT, "Q2_dks_pie_daily.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["date", "dow", "variant", "total"]); w.writerows(rows)
    print("cal rows", len(rows))


def den():
    jobs = []
    for c in APP:
        for wn, (a, z) in WINS.items():
            for y in (2025, 2026):
                for v in VARS:
                    jobs.append((c, wn, y, v, f"{y}-{a}", f"{y}-{z}"))

    def q(j):
        c, wn, y, v, a, z = j
        A = ep(dt.date.fromisoformat(a)); Z = ep(dt.date.fromisoformat(z))
        r = g([("Filter", f"CategoryAncestorId:eq:{c}"), ("Filter", f"SubmissionTime:gte:{A}"),
               ("Filter", f"SubmissionTime:lt:{Z}"), ("Limit", "1")] + VARS[v])
        return c, wn, y, v, r.get("TotalResults")
    with ThreadPoolExecutor(4) as ex:
        rows = list(ex.map(q, jobs))
    with open(os.path.join(OUT, "Q2_dks_den_windows.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["category", "window", "year", "variant", "total"]); w.writerows(rows)
    print("den rows", len(rows), "failed", sum(r[4] is None for r in rows))


def prod():
    rows = []
    for b in X.OWNED:
        if b == "Field___Stream":
            continue
        n = X.get(S, "dsg", "products", [("Filter", f"BrandId:eq:{b}"), ("Limit", "1")]).get("TotalResults") or 0

        def page(o):
            time.sleep(0.15)
            return X.get(S, "dsg", "products", [("Filter", f"BrandId:eq:{b}"), ("Stats", "Reviews"), ("Limit", "100"), ("Offset", str(o))])
        with ThreadPoolExecutor(4) as ex:
            for r in ex.map(page, range(0, n, 100)):
                for x in r.get("Results", []):
                    st = x.get("ReviewStatistics") or {}
                    rows.append([x["Id"], b, x.get("Name"), "|".join(x.get("CategoryAncestryIds") or []), st.get("LastSubmissionTime")])
        print(b, n, flush=True)
    with open(os.path.join(OUT, "Q2_dks_owned_products.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["product_id", "brand_id", "name", "ancestry", "last_sub"]); w.writerows(rows)


def rev():
    since = ep(dt.date(2025, 7, 1))
    with open(os.path.join(OUT, "Q2_dks_owned_products.csv"), encoding="utf-8") as f:
        ps = [r for r in csv.DictReader(f) if (r["last_sub"] or "")[:10] >= "2025-07-01"
              and any(c in r["ancestry"].split("|") for c in APP)]
    # Quest food items are not apparel; apparel ancestry filter already excludes them
    ps = list({p["product_id"]: p for p in ps}.values())
    print("owned apparel products to pull", len(ps), flush=True)

    def one(p):
        out, off = [], 0
        while True:
            r = g([("Filter", f"ProductId:eq:{p['product_id']}"), ("Filter", f"SubmissionTime:gte:{since}"),
                   ("Filter", "IsSyndicated:eq:false"), ("Sort", "SubmissionTime:desc"), ("Limit", "100"), ("Offset", str(off))])
            res = r.get("Results", [])
            for x in res:
                out.append([x.get("Id"), p["product_id"], p["brand_id"], p["ancestry"], x.get("SubmissionTime"), x.get("CampaignId")])
            off += 100
            if r.get("TotalResults") is None or off >= (r.get("TotalResults") or 0) or not res:
                return out, r.get("TotalResults") is not None
    rows, fails = [], 0
    with ThreadPoolExecutor(4) as ex:
        for i, (o, ok) in enumerate(ex.map(one, ps)):
            rows += o; fails += (not ok)
            if i % 200 == 0:
                print(i, len(rows), flush=True)
    with open(os.path.join(OUT, "Q2_dks_owned_reviews_recent.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["review_id", "product_id", "brand_id", "ancestry", "submission_time", "campaign_id"]); w.writerows(rows)
    print("reviews", len(rows), "failed products", fails)


if __name__ == "__main__":
    for step in sys.argv[1:]:
        {"cal": cal, "den": den, "prod": prod, "rev": rev}[step]()
