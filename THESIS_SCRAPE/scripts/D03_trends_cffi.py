"""D03: Google Trends (US, weekly) via the public explore/widgetdata JSON endpoints the trends page itself calls,
using curl_cffi (Chrome TLS) because pytrends gets 429/SSL errors. Pulls one term per request so each series is
self-normalized (compare a term only with itself y/y).
Rerun: python THESIS_SCRAPE\\scripts\\D03_trends_cffi.py
Output: THESIS_SCRAPE\\raw\\D03_trends_weekly.csv, D03_trends_summary.csv
"""
import json, time, urllib.parse, sys
import pandas as pd
from curl_cffi import requests as cr

TERMS = ["soccer cleats", "baseball bat", "football cleats", "running shoes", "pickleball paddle", "golf clubs",
         "flag football", "volleyball shoes", "basketball shoes", "winter jacket", "workout clothes", "youth soccer"]
TF = "2023-10-01 2026-10-06"
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D03_trends_weekly.csv"
SUM = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D03_trends_summary.csv"


def strip(t):
    return json.loads(t[t.find("{"):])


def fetch(s, term):
    req = {"comparisonItem": [{"keyword": term, "geo": "US", "time": TF}], "category": 0, "property": ""}
    u = "https://trends.google.com/trends/api/explore?hl=en-US&tz=300&req=" + urllib.parse.quote(json.dumps(req))
    r = s.get(u, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"explore {r.status_code}")
    w = [x for x in strip(r.text)["widgets"] if x["id"] == "TIMESERIES"][0]
    u2 = ("https://trends.google.com/trends/api/widgetdata/multiline?hl=en-US&tz=300&req="
          + urllib.parse.quote(json.dumps(w["request"])) + "&token=" + w["token"])
    r2 = s.get(u2, timeout=30)
    if r2.status_code != 200:
        raise RuntimeError(f"multiline {r2.status_code}")
    pts = strip(r2.text)["default"]["timelineData"]
    return pd.Series({pd.to_datetime(int(p["time"]), unit="s"): p["value"][0] for p in pts}, name=term)


def main():
    s = cr.Session(impersonate="chrome")
    s.get("https://trends.google.com/trends/explore?geo=US", timeout=30)
    out = []
    for t in TERMS:
        for a in range(3):
            try:
                out.append(fetch(s, t)); print("ok", t, flush=True); break
            except Exception as e:
                print("err", t, e, flush=True); time.sleep(20 * (a + 1))
        time.sleep(6)
    if not out:
        sys.exit("no data")
    df = pd.concat(out, axis=1); df.to_csv(RAW)
    W = {"Q3TD_Aug2_Oct4": ("08-02", "10-04"), "Q2_May4_Aug1": ("05-04", "08-01"), "Q1_Feb2_May3": ("02-02", "05-03")}
    rows = []
    for t in df.columns:
        r = {"term": t}
        for w, (a, z) in W.items():
            v25 = df.loc[f"2025-{a}":f"2025-{z}", t].mean(); v26 = df.loc[f"2026-{a}":f"2026-{z}", t].mean()
            r[w + "_yoy%"] = round((v26 / v25 - 1) * 100, 1) if v25 else None
        rows.append(r)
    sm = pd.DataFrame(rows); sm.to_csv(SUM, index=False); print(sm.to_string())


if __name__ == "__main__":
    main()
