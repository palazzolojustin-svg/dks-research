"""G1: extract PLP product-card review-count labels ("... based on N reviews") for chosen product titles from the
X03/R12 Common Crawl + Wayback HTML caches, to verify the Maxfli Tour X 57 -> 813 jump and compare competitor balls.
USAGE: python G1_cardlabels.py
"""
import os, re, glob, json
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
pat = re.compile(r'href="(/p/[^"]+)"\s+title="([^"]*(?:Tour X|Pro V1|TP5|Chrome Soft|Chrome Tour|Tour S|Maxfli Tour)[^"]*)"\s+aria-label="([^"]*)"')
files = []
for d in ["X03_cc_cache", "X03_cache", "R12_cache", "R9_cache", "X11_cache", "R12_cc_cache", "R9_cc_cache"]:
    files += glob.glob(os.path.join(RAW, d, "*"))
out = {}
for f in files:
    try:
        t = open(f, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    if "based on" not in t:
        continue
    # capture date from WARC/meta if present
    dm = re.search(r"(20\d\d-\d\d-\d\d)T\d\d:\d\d", t[:3000]) or re.search(r"web\.archive\.org/web/(20\d{6})", t)
    dt = dm.group(1) if dm else "?"
    for href, title, lab in pat.findall(t):
        n = re.search(r"based on ([\d,]+) review", lab)
        out[(os.path.basename(os.path.dirname(f)), os.path.basename(f), href.split("?")[0], title)] = (dt, n.group(1) if n else None, lab[-90:])
rows = sorted(out.items(), key=lambda kv: (kv[0][3], kv[1][0]))
for k, v in rows:
    print(v[0], "|", k[3][:55], "|", k[2][-26:], "|", v[1], "|", k[0], k[1][:12])
print(len(rows), "labels from", len(files), "files")
