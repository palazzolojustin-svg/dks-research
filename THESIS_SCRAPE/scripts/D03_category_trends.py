"""D03: Google Trends (US) weekly interest for DKS category search terms, 2023-01-01..today.
Rerun: python THESIS_SCRAPE\\scripts\\D03_category_trends.py
Output: THESIS_SCRAPE\\raw\\D03_category_trends.csv and D03_category_trends_summary.csv
Each batch of <=5 terms is normalized within its own batch (Google scales 0-100 per request),
so compare each term only to itself across time (y/y by fiscal quarter window).
"""
import time, sys
import pandas as pd
from pytrends.request import TrendReq

BATCHES = [
    ["soccer cleats", "baseball bat", "football cleats", "basketball shoes", "volleyball shoes"],
    ["running shoes", "pickleball paddle", "golf clubs", "golf balls", "padel"],
    ["flag football", "youth soccer", "travel baseball", "lacrosse stick", "softball bat"],
    ["hoka", "on cloud", "new balance", "nike", "adidas"],
    ["dicks sporting goods", "academy sports", "scheels", "foot locker", "big 5"],
    ["workout clothes", "gym shoes", "trading cards", "fishing pole", "hunting license"],
]
TF = "2023-01-01 2026-10-06"
OUT = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D03_category_trends.csv"
SUM = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D03_category_trends_summary.csv"


def main():
    py = TrendReq(hl="en-US", tz=300, timeout=(10, 30), retries=3, backoff_factor=1.0)
    frames = []
    for b in BATCHES:
        for attempt in range(4):
            try:
                py.build_payload(b, timeframe=TF, geo="US")
                df = py.interest_over_time()
                if "isPartial" in df.columns:
                    df = df.drop(columns="isPartial")
                frames.append(df)
                print("ok", b, len(df), flush=True)
                break
            except Exception as e:
                print("err", b, e, flush=True)
                time.sleep(30 * (attempt + 1))
        time.sleep(8)
    allf = pd.concat(frames, axis=1)
    allf.to_csv(OUT)
    # fiscal-ish windows: Aug 2-Oct 4 (Q3 to date) and Jun-Jul, Feb-Apr (Q1)
    win = {
        "Q1_FebApr": ("02-01", "04-30"),
        "Q2_MayJul": ("05-01", "07-31"),
        "Q3TD_Aug1_Oct4": ("08-01", "10-04"),
    }
    rows = []
    for t in allf.columns:
        r = {"term": t}
        for w, (a, z) in win.items():
            for y in (2024, 2025, 2026):
                s = allf.loc[f"{y}-{a}":f"{y}-{z}", t]
                r[f"{w}_{y}"] = round(s.mean(), 2) if len(s) else None
            try:
                r[f"{w}_yoy26"] = round(r[f"{w}_2026"] / r[f"{w}_2025"] - 1, 3)
                r[f"{w}_yoy25"] = round(r[f"{w}_2025"] / r[f"{w}_2024"] - 1, 3)
            except Exception:
                pass
        rows.append(r)
    pd.DataFrame(rows).to_csv(SUM, index=False)
    print(pd.DataFrame(rows)[["term", "Q1_FebApr_yoy26", "Q2_MayJul_yoy26", "Q3TD_Aug1_Oct4_yoy25", "Q3TD_Aug1_Oct4_yoy26"]].to_string())


if __name__ == "__main__":
    main()
