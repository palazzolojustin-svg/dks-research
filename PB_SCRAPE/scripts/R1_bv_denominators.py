"""R1: all-brand monthly review totals per dicks.com BV category, by review-source variant.

Variants (CampaignId filter on reviews.json, single CategoryAncestorId + SubmissionTime month range, Limit=1):
  ALL     no campaign filter (native reviews)
  PIE     CampaignId = ESP_PIE_INCENTIVE  (post-purchase incentive email; purchase-triggered)
  NONPIE  CampaignId != ESP_PIE_INCENTIVE
  NULL    CampaignId = null  (organic: written unprompted on the PDP)
  MYACC   CampaignId = MyAccount (organic: written from the order history page)
  BVDISP  CampaignId = BV_REVIEW_DISPLAY ; BVMOB CampaignId = BV_MOBILE_REVIEW_DISPLAY (organic widget submits)
ORGANIC = NULL + MYACC + BVDISP + BVMOB (no incentive, no sampling).
Output: raw/R1_category_month_totals.csv (category, month, variant, total, pulled_at). Resumable; rows for the last
REFRESH_MONTHS months are always re-pulled (appended with a newer pulled_at; analysis keeps the latest).
RERUN weekly: python R1_bv_denominators.py
"""
import csv, os, sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from X01_bv_reviews import session_for, get, RAW
from X01_bv_category_totals import CATS, months

VARIANTS = {"ALL": [], "PIE": [("Filter", "CampaignId:eq:ESP_PIE_INCENTIVE")],
            "NONPIE": [("Filter", "CampaignId:neq:ESP_PIE_INCENTIVE")], "NULL": [("Filter", "CampaignId:eq:null")],
            "MYACC": [("Filter", "CampaignId:eq:MyAccount")], "BVDISP": [("Filter", "CampaignId:eq:BV_REVIEW_DISPLAY")],
            "BVMOB": [("Filter", "CampaignId:eq:BV_MOBILE_REVIEW_DISPLAY")]}
REFRESH_MONTHS = 4
PATH = os.path.join(RAW, "R1_category_month_totals.csv")


def main(cats=None):
    s = session_for("dsg")
    cats = cats or CATS["dsg"]
    ms = months()
    recent = {m for m, _, _ in ms[-REFRESH_MONTHS:]}
    done = set()
    if os.path.exists(PATH):
        with open(PATH, encoding="utf-8") as f:
            done = {(r["category"], r["month"], r["variant"]) for r in csv.DictReader(f)}
    # seed ALL/PIE from X01 if present (pulled 2026-10-07 ~03:00 CDT)
    jobs = [(c, m, a, b, v) for c in cats for (m, a, b) in ms for v in VARIANTS
            if (c, m, v) not in done or m in recent]
    new = not os.path.exists(PATH)
    f = open(PATH, "a", newline="", encoding="utf-8"); w = csv.writer(f)
    if new:
        w.writerow(["category", "month", "variant", "total", "pulled_at"])
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")

    def q(j):
        c, m, a, b, v = j
        p = [("Filter", f"CategoryAncestorId:eq:{c}"), ("Filter", f"SubmissionTime:gte:{a}"),
             ("Filter", f"SubmissionTime:lt:{b}"), ("Limit", "1")] + VARIANTS[v]
        return c, m, v, get(s, "dsg", "reviews", p).get("TotalResults"), now
    print("jobs", len(jobs), flush=True)
    with ThreadPoolExecutor(6) as ex:
        for i, row in enumerate(ex.map(q, jobs)):
            if row[3] is not None:
                w.writerow(row)
            if i % 500 == 0:
                f.flush(); print(i, flush=True)
    f.close()


if __name__ == "__main__":
    main(sys.argv[1:] or None)
