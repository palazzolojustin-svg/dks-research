"""X04: DKS import-entity supplier census from ImportYeti (free pages, no login).

DKS's direct-import consignee is "DICK'S MERCHANDISING & SUPPLY CHAIN" (ImportYeti slug
company/dick-s-merchandising-and-supply-cha). The DKS-named page (company/dicks-sporting-goods) is
under CBP manifest confidentiality and is NOT usable as a volume series.

Rerun weekly:
    python X04_dmsc_suppliers.py
Outputs (PB_SCRAPE/raw/):
    X04_dmsc_monthly_<date>.csv          monthly shipments/TEU/kg for the DKS entity
    X04_dmsc_vendor_quarterly_<date>.csv supplier x quarter shipments/TEU to DKS (top ~48 suppliers shown free)
    X04_dmsc_supplier_pages_<date>.json  per-supplier: customers (12m/total), recent BOLs to DKS w/ descriptions
Diff the CSVs week to week. Polite: 3s between requests.
"""
import re, json, csv, time, os, datetime
import requests

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
     "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en-US,en;q=0.9"}
TODAY = datetime.date.today().isoformat()


def payload(path):
    r = requests.get("https://www.importyeti.com" + path, headers=H, timeout=40)
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', r.text, re.S)
    big = "".join(chunks).encode().decode("unicode_escape", errors="ignore")
    return r.status_code, big


def company_series(big):
    m = re.search(r'"data":\{("\d\d/\d\d/\d{4}":\{.*?\})\},"title":"[^"]*Total Sea Shipments Over Time"', big)
    d = json.loads("{" + m.group(1) + "}")
    rows = []
    for k, v in d.items():
        dd, mm, yy = k.split("/")
        rows.append([f"{yy}-{mm}", v["shipments"], v["teu"], v["weight"]])
    return sorted(rows)


def vendor_table(big):
    out = []
    for m in re.finditer(r'\{"shipments_12m":(\d+),"vendor_name":"([^"]*)".*?"country":"([^"]*)".*?"url":"(/supplier/[^"]*)".*?"total_shipments_company":(\d+).*?"product_descriptions":"([^"]*)","vendor_time_series":(\{.*?\}\}),', big):
        s12, name, ctry, url, tot, desc, ts = m.groups()
        out.append(dict(name=name, country=ctry, url=url, ship12m=int(s12), total=int(tot), desc=desc, ts=json.loads(ts)))
    return out


def supplier_detail(url):
    code, big = payload(url)
    cust = re.findall(r'\{"company_name":"([^"]{2,80})","shipments_12m":(\d+),"total_shipments":(\d+)\}', big)
    seen = {}
    for n, a, b in cust:
        seen.setdefault(n, (int(a), int(b)))
    bols = []
    sb = set()
    for d, b, who, desc in re.findall(r'"date":"(\d{4}-\d\d-\d\d)T[^{}]*?"bol":"([^"]*)".{0,600}?"title":"([^"]*)".{0,800}?"description":"([^"]*)"', big):
        if b in sb:
            continue
        sb.add(b)
        bols.append(dict(date=d, bol=b, consignee=who, desc=desc))
    ts = None
    m = re.search(r'"data":\{("\d\d/\d\d/\d{4}":\{.*?\})\},"title":"[^"]*Total Sea Shipments Over Time"', big)
    if m:
        ts = json.loads("{" + m.group(1) + "}")
    return dict(http=code, customers=seen, recent_bols=bols, supplier_total_series=ts)


def main():
    code, big = payload("/company/dick-s-merchandising-and-supply-cha")
    rows = company_series(big)
    with open(os.path.join(RAW, f"X04_dmsc_monthly_{TODAY}.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["month", "shipments", "teu", "weight_kg"]); w.writerows(rows)
    vt = vendor_table(big)
    with open(os.path.join(RAW, f"X04_dmsc_vendor_quarterly_{TODAY}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["supplier", "country", "url", "quarter_start", "shipments", "teu", "weight_kg"])
        for v in vt:
            for k, x in sorted(v["ts"].items(), key=lambda kv: (kv[0][6:], kv[0][3:5])):
                w.writerow([v["name"], v["country"], v["url"], f"{k[6:]}-{k[3:5]}", x["shipments"], x["teu"], x["weight"]])
    details = {}
    for v in vt:
        time.sleep(3)
        try:
            details[v["url"]] = dict(name=v["name"], desc=v["desc"], **supplier_detail(v["url"]))
        except Exception as e:
            details[v["url"]] = dict(name=v["name"], error=str(e))
        print(v["name"], "ok")
    json.dump(details, open(os.path.join(RAW, f"X04_dmsc_supplier_pages_{TODAY}.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
