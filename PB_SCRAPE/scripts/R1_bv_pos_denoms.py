"""R1: PIE review totals split by point of sale (ContextDataValue_POS = InStore / Online) per category-month.
Used to test whether the owned-share rise is a channel-mix artefact of the review-email program.
Output raw/R1_category_month_pos.csv (category, month, pos, total). RERUN: python R1_bv_pos_denoms.py
"""
import csv, os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from X01_bv_reviews import session_for, get, RAW
from X01_bv_category_totals import months
from R1_analyze import BASKETS

PATH = os.path.join(RAW, "R1_category_month_pos.csv")
s = session_for("dsg")
cats = sorted(set(sum(BASKETS.values(), [])))
jobs = [(c, m, a, b, pos) for c in cats for (m, a, b) in months() for pos in ("InStore", "Online")]


def q(j):
    c, m, a, b, pos = j
    r = get(s, "dsg", "reviews", [("Filter", f"CategoryAncestorId:eq:{c}"), ("Filter", f"SubmissionTime:gte:{a}"),
                                  ("Filter", f"SubmissionTime:lt:{b}"), ("Filter", "CampaignId:eq:ESP_PIE_INCENTIVE"),
                                  ("Filter", f"ContextDataValue_POS:eq:{pos}"), ("Limit", "1")])
    return c, m, pos, r.get("TotalResults")


with open(PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["category", "month", "pos", "total"])
    with ThreadPoolExecutor(6) as ex:
        for row in ex.map(q, jobs):
            if row[3] is not None:
                w.writerow(row)
