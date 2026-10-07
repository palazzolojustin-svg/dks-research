"""X04 ImportYeti scraper (free public pages, no login).

Usage (PowerShell):
    python X04_importyeti.py company dicks-sporting-goods
    python X04_importyeti.py supplier foremost-golf-mfg textiles-opico-de
    python X04_importyeti.py search "calia"

What it does: fetches https://www.importyeti.com/<kind>/<slug>, extracts the Next.js RSC
payload (self.__next_f.push chunks), saves it to PB_SCRAPE/raw/X04_iy_<kind>_<slug>.txt and
prints: header stats, manifest_confidentiality windows, monthly time series (company_time_series /
supplier time series), annual totals, the customer table (for suppliers) with shipments_12m, and
the most recent BOLs with consignee + description. Writes a monthly CSV
PB_SCRAPE/raw/X04_iy_<kind>_<slug>_monthly.csv.

Weekly re-run: run for the same slugs and diff the monthly CSVs. Pages are plain HTML (no Akamai
wall as of 2026-10-07). Be polite: 1 request / few seconds.
"""
import re, sys, json, csv, time, os
from collections import defaultdict
import requests

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
     "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en-US,en;q=0.9"}


def fetch(kind, slug):
    url = f"https://www.importyeti.com/{kind}/{slug}" if kind != "search" else f"https://www.importyeti.com/search?q={requests.utils.quote(slug)}"
    r = requests.get(url, headers=H, timeout=40)
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', r.text, re.S)
    big = "".join(chunks).encode().decode("unicode_escape", errors="ignore")
    try:
        big = big.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
    except Exception:
        pass
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", slug)[:60]
    open(os.path.join(RAW, f"X04_iy_{kind}_{safe}.txt"), "w", encoding="utf-8").write(big)
    return r.status_code, big, safe


def time_series_blocks(big):
    """Return list of (title, dict month->vals) for every '"data":{dd/mm/yyyy...}' block followed by a title."""
    out = []
    for m in re.finditer(r'"data":\{("\d\d/\d\d/\d{4}":\{.*?\})\},"title":"([^"]*)"', big):
        try:
            d = json.loads("{" + m.group(1) + "}")
            out.append((m.group(2), d))
        except Exception:
            pass
    return out


def main():
    kind = sys.argv[1]
    for slug in sys.argv[2:]:
        code, big, safe = fetch(kind, slug)
        print("=" * 100)
        print(kind, slug, "HTTP", code, "payload", len(big))
        for k in ["total_shipments", "shipments_12m", "manifest_confidentiality", "company_date_range", "supplier_date_range"]:
            m = re.search('"' + k + r'":(\[[^\]]*\]|\{[^}]*\}|[\d.]+)', big)
            if m:
                print(" ", k, "=", m.group(1)[:300])
        for title, d in time_series_blocks(big):
            yr = defaultdict(lambda: [0, 0])
            rows = []
            for k, v in d.items():
                dd, mm, yy = k.split("/")
                yr[yy][0] += v.get("shipments", 0)
                yr[yy][1] += v.get("teu", 0)
                rows.append([f"{yy}-{mm}", v.get("shipments", 0), v.get("teu", 0), v.get("weight", 0)])
            rows.sort()
            print("  SERIES:", title)
            print("   annual shipments/teu:", {y: yr[y] for y in sorted(yr)})
            print("   last 24 months:", [(r[0], r[1]) for r in rows if r[0] >= "2024-10"])
            with open(os.path.join(RAW, f"X04_iy_{kind}_{safe}_monthly.csv"), "w", newline="") as f:
                w = csv.writer(f); w.writerow(["month", "shipments", "teu", "weight_kg"]); w.writerows(rows)
            break
        # customers (supplier pages) or suppliers (company pages): name + 12m + total
        for m in re.finditer(r'"(?:company_name|vendor_name|customer_name)":"([^"]{2,80})","(?:shipments_12m)":(\d+),"total_shipments":(\d+)', big):
            pass
        cust = re.findall(r'\{"company_name":"([^"]{2,80})","shipments_12m":(\d+),"total_shipments":(\d+)\}', big)
        if cust:
            seen = {}
            for n, s12, tot in cust:
                seen.setdefault(n, (int(s12), int(tot)))
            print("  customers (name, 12m, total):", sorted(seen.items(), key=lambda x: -x[1][1])[:25])
        # recent BOLs
        bols = re.findall(r'"date":"(\d{4}-\d\d-\d\d)T[^{}]*?"bol":"([^"]*)".{0,600}?"title":"([^"]*)".{0,800}?"description":"([^"]*)"', big)
        seen = set()
        for d, b, who, desc in bols[:60]:
            if b in seen:
                continue
            seen.add(b)
            print("   BOL", d, b, "|", who[:40], "|", desc[:110])
        time.sleep(3)


if __name__ == "__main__":
    main()
