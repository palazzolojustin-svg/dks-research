"""Weekly check for a new Common Crawl crawl of dicks.com; if found, extract and append one row to
data/V2_dks_sale_share.csv using the exact V2/X11 definitions (V2_analyze.py functions).

Usage: python3 scripts/weekly_dks.py
New crawls appear roughly monthly; crawl CC-MAIN-YYYY-WW covers ISO week WW. Prints the y/y comparator month.
"""
import csv, datetime as dt, json, os, subprocess, sys, requests
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
S = os.path.join(R, "scripts"); CSV = os.path.join(R, "data", "V2_dks_sale_share.csv")

src = open(os.path.join(S, "V2_analyze.py")).read().replace("\nmain()\n", "\n")
g = {"__file__": os.path.join(S, "V2_analyze.py")}; exec(compile(src, "V2_analyze", "exec"), g)
load, M, owned, pct, BR = g["load"], g["M"], g["owned"], g["pct"], g["BR"]

rows = list(csv.DictReader(open(CSV))); fields = list(rows[0].keys())
done = {r["crawl"] for r in rows}
cands = ["CC-MAIN-2026-%02d" % w for w in range(40, 54)] + ["CC-MAIN-2027-%02d" % w for w in range(1, 10)]
found = []
for cid in cands:
    if cid in done: continue
    try:
        r = requests.head("https://data.commoncrawl.org/crawl-data/%s/cc-index.paths.gz" % cid, timeout=30)
        if r.status_code == 200: found.append(cid)
    except Exception as e:
        print(cid, "err", str(e)[:60])
print("new crawls:", found or "none")

for cid in found:
    y, w = int(cid[8:12]), int(cid[13:15])
    month = dt.date.fromisocalendar(y, w, 4).strftime("%Y-%m")
    subprocess.run([sys.executable, os.path.join(S, "V2_cc_index2.py"), cid], check=False)
    subprocess.run([sys.executable, os.path.join(S, "V2_cc_extract.py"), cid, "800", "8"], check=False)
    rs = load(cid)
    pages = sum(1 for l in open(os.path.join(R, "raw", "V2", "cc", cid + "_pages.jsonl")) if json.loads(l).get("has_state"))
    nat = [r for r in rs if not owned(r)]; ow = [r for r in rs if owned(r)]
    row = dict(month=month, source="CC", crawl=cid, pages=pages, products=len(rs))
    for nm, grp in [("all", rs), ("nat", nat), ("own", ow)]:
        m = M(grp); row[nm + "_n"] = m["n"]; row[nm + "_on_sale_pct"] = pct(m["on_sale"])
        row[nm + "_depth_when_on_sale_pct"] = pct(m["depth_on_sale"]); row[nm + "_avg_disc_pct"] = pct(m["avg_disc"])
    for b in BR:
        m = M([r for r in nat if r["brand"] == b]); k = b.replace(" ", "_")
        row[k + "_n"] = m["n"]; row[k + "_on_sale_pct"] = pct(m["on_sale"])
    with open(CSV, "a", newline="") as fh:
        csv.DictWriter(fh, fieldnames=fields).writerow({k: row.get(k, "") for k in fields})
    py = "%d-%s" % (y - 1, month[5:])
    prev = [r for r in rows if r["month"] == py and r["source"] == "CC"]
    print(cid, month, "all on sale", row["all_on_sale_pct"], "national", row["nat_on_sale_pct"], "avg disc", row["nat_avg_disc_pct"],
          "| y/y comparator", py, (prev[0]["all_on_sale_pct"], prev[0]["nat_on_sale_pct"], prev[0]["nat_avg_disc_pct"]) if prev else "none")
