"""W10: parse an ImportYeti company payload: vendor table (quarterly series), hs chapters, monthly totals, BOLs.
Usage: python3 -I W10_parse.py <payload.txt> [outprefix]"""
import re, json, sys, csv, os
from collections import defaultdict

def vendors(big):
    i = big.find('"vendor_table":[')
    out = []
    if i < 0: return out
    # walk JSON array with bracket matching
    j = i + len('"vendor_table":'); depth = 0; k = j
    for k in range(j, len(big)):
        c = big[k]
        if c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0: break
    try:
        return json.loads(big[j:k+1])
    except Exception as e:
        print("vendor json fail", e); return []

def qlabel(k):
    d, m, y = k.split('/'); return f"{y}Q{(int(m)-1)//3+1}"

if __name__ == "__main__":
    p = sys.argv[1]; pre = sys.argv[2] if len(sys.argv) > 2 else None
    big = open(p, encoding="utf-8").read()
    V = vendors(big)
    print("vendors", len(V))
    rows = []
    for v in V:
        ts = v.get("vendor_time_series") or {}
        yr = defaultdict(int)
        for k, x in ts.items(): yr[k.split('/')[2]] += x.get("shipments", 0)
        chs = v.get("hs_code_chapters") or []
        print(f"{v.get('vendor_name','')[:38]:38} {v.get('country','')[:10]:10} 12m={v.get('shipments_12m')} tot={v.get('total_shipments_company')} | " +
              " ".join(f"{y[2:]}:{yr[y]}" for y in sorted(yr) if y >= '2021') + " | " + (v.get("product_descriptions") or "")[:110])
        for k, x in ts.items():
            rows.append([v.get("vendor_name"), v.get("country"), v.get("url"), qlabel(k), x.get("shipments", 0), x.get("weight", 0), x.get("teu", 0), (v.get("product_descriptions") or "")[:200], ";".join(v.get("hs_codes") or [])])
    if pre:
        with open(pre + "_vendor_quarterly.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["vendor", "country", "url", "quarter", "shipments", "weight_kg", "teu", "product_desc", "hs_codes"]); w.writerows(rows)
