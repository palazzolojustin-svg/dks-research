"""R1 (d): fair Q3 FY26-to-date read. PIE emails go out weekly on Tuesdays; the last batch before the current pause
was 2026-08-11. So compare identical calendar windows that contain the same two Tuesday batches:
2025-08-01..2025-08-17 (batches Aug 5, Aug 12) vs 2026-08-01..2026-08-17 (batches Aug 4, Aug 11).
Denominators pulled live from BV (category + date range); numerators from X01 owned + R1 national reviews.
Output raw/R1_q3_lfl.csv ; printed table. RERUN: python R1_q3_like_for_like.py
"""
import os, sys, datetime as dt
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from X01_bv_reviews import session_for, get
from R1_analyze import RAW, BASKETS
from R1_head2head import load_all

WIN = {2025: ("2025-08-01", "2025-08-18"), 2026: ("2026-08-01", "2026-08-18")}
VARS = {"PIE": [("Filter", "CampaignId:eq:ESP_PIE_INCENTIVE")], "ALL": []}


def ep(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp())


s = session_for("dsg")
prod, rev = load_all()
anc = prod.set_index("product_id").ancestry.fillna("").str.split("|").to_dict()
rows = []
for b, cats in BASKETS.items():
    for y, (a, z) in WIN.items():
        for v, flt in VARS.items():
            tot = 0
            num = {}
            for cat in cats:
                r = get(s, "dsg", "reviews", [("Filter", f"CategoryAncestorId:eq:{cat}"), ("Filter", f"SubmissionTime:gte:{ep(a)}"),
                                              ("Filter", f"SubmissionTime:lt:{ep(z)}"), ("Limit", "1")] + flt)
                tot += r.get("TotalResults") or 0
                pids = {k for k, vv in anc.items() if cat in vv}
                sub = rev[rev.product_id.isin(pids) & (rev.submission_time >= a) & (rev.submission_time < z)].drop_duplicates("review_id")
                if v == "PIE":
                    sub = sub[sub.typ == "PIE"]
                for g, n in sub.groupby("grp").size().items():
                    num[g] = num.get(g, 0) + n
                num["ALL OWNED"] = num.get("ALL OWNED", 0) + int((sub.owned == 1).sum())
            for g, n in num.items():
                rows.append((b, y, v, g, n, tot))
d = pd.DataFrame(rows, columns=["basket", "year", "variant", "grp", "n", "total"])
d["share"] = d.n / d.total
d.to_csv(os.path.join(RAW, "R1_q3_lfl.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
x = d[d.variant == "PIE"].pivot_table(index=["basket", "grp"], columns="year", values="share") * 100
x["d"] = x[2026] - x[2025]
t = d[d.variant == "PIE"].drop_duplicates(["basket", "year"]).pivot_table(index="basket", columns="year", values="total")
print(x[(x[2025] > 2) | (x[2026] > 2)].round(1).to_string()); print(t.to_string())
