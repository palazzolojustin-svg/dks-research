"""R1: DAILY review counts on dicks.com (Bazaarvoice) for a few big categories, to map the post-purchase
incentive-email (PIE) send calendar and detect pauses (Dec blackouts; the 2026-08-11 last batch).
Output raw/R1_pie_daily.csv (category, date, variant, total). Re-pulls the last 21 days every run.
RERUN weekly: python R1_bv_pie_calendar.py
"""
import csv, os, sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from X01_bv_reviews import session_for, get, RAW

CATS = ["Apparel-129823", "Golf-129239", "ShopBySport-128771"]
VAR = {"ALL": [], "PIE": [("Filter", "CampaignId:eq:ESP_PIE_INCENTIVE")]}
PATH = os.path.join(RAW, "R1_pie_daily.csv")


def main(start=dt.date(2024, 1, 1)):
    s = session_for("dsg")
    today = dt.datetime.now(dt.timezone.utc).date()
    days = [start + dt.timedelta(days=i) for i in range((today - start).days + 1)]
    done = set()
    if os.path.exists(PATH):
        with open(PATH, encoding="utf-8") as f:
            done = {(r["category"], r["date"], r["variant"]) for r in csv.DictReader(f)}
    recent = {str(d) for d in days[-21:]}
    jobs = [(c, d, v) for c in CATS for d in days for v in VAR if (c, str(d), v) not in done or str(d) in recent]
    new = not os.path.exists(PATH)
    f = open(PATH, "a", newline="", encoding="utf-8"); w = csv.writer(f)
    if new:
        w.writerow(["category", "date", "variant", "total"])

    def q(j):
        c, d, v = j
        a = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp())
        p = [("Filter", f"CategoryAncestorId:eq:{c}"), ("Filter", f"SubmissionTime:gte:{a}"),
             ("Filter", f"SubmissionTime:lt:{a + 86400}"), ("Limit", "1")] + VAR[v]
        return c, str(d), v, get(s, "dsg", "reviews", p).get("TotalResults")
    print("jobs", len(jobs), flush=True)
    with ThreadPoolExecutor(6) as ex:
        for i, row in enumerate(ex.map(q, jobs)):
            if row[3] is not None:
                w.writerow(row)
            if i % 500 == 0:
                f.flush(); print(i, flush=True)
    f.close()


if __name__ == "__main__":
    main()
