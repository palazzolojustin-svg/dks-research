"""H03: query Texas TDLR TABS project registry (the public search page's own DataTables endpoint) for
Dick's House of Sport / Field House / Dick's Sporting Goods projects; then pull each project's print page
(estimated cost, sq ft, dates, scope, owner, tenant-funded flag).
Rerun: python H03_tabs.py  -> raw/H03_tabs_projects.csv
"""
import requests, re, csv, os, time
from bs4 import BeautifulSoup
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
UA = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}
S = requests.Session()
page = S.get("https://www.tdlr.texas.gov/TABS/Search", headers=UA, timeout=60)
soup = BeautifulSoup(page.text, "html.parser")
el = soup.find(id="project-search-url")
url = el["data-request-url"]
if url.startswith("/"):
    url = "https://www.tdlr.texas.gov" + url
print("endpoint", url)


def search(**flt):
    data = {"draw": 1, "start": 0, "length": 500, "search[value]": "", "search[regex]": "false"}
    data.update(flt)
    r = S.post(url, data=data, headers=UA, timeout=90)
    js = r.json()
    return js.get("data", []), js.get("recordsFiltered")


rows = {}
for fld, val in [("ProjectName", "House of Sport"), ("FacilityName", "House of Sport"), ("ProjectName", "Dick's"),
                 ("ProjectName", "Dicks"), ("FacilityName", "Dick's"), ("ProjectName", "DICK'S"), ("ProjectName", "Field House"),
                 ("ProjectName", "DSG"), ("ProjectName", "Dick"), ("FacilityName", "Dick"),
                 ("OwnerName", "Dick's Sporting"), ("OwnerName", "Dicks Sporting"), ("OwnerName", "DICK'S"),
                 ("ProjectName", "Golf Galaxy"), ("ProjectName", "Public Lands"), ("ProjectName", "Going Going Gone")]:
    try:
        d, n = search(**{fld: val})
    except Exception as e:
        print("ERR", fld, val, e); continue
    print(fld, val, "->", n)
    for x in d:
        rec = x if isinstance(x, dict) else {"raw": x}
        key = rec.get("projectNumber") or rec.get("ProjectNumber") or str(rec)[:60]
        rows[key] = rec
    time.sleep(1)
print("unique projects", len(rows))
out = []
for k, rec in rows.items():
    name = str(rec.get("projectName") or rec.get("ProjectName") or "")
    fac = str(rec.get("facilityName") or rec.get("FacilityName") or "")
    blob = (name + " " + fac).lower()
    own = str(rec.get("ownerName") or rec.get("OwnerName") or "").lower()
    if not (any(s in blob for s in ["house of sport", "dick", "dsg", "golf galaxy", "public lands", "going going gone"]) or "dick" in own):
        continue
    pn = re.sub(r"<[^>]+>", "", str(k))
    try:
        t = BeautifulSoup(S.get(f"https://www.tdlr.texas.gov/TABS/Search/Print/{pn}", headers=UA, timeout=60).text, "html.parser").get_text("\n")
    except Exception as e:
        t = ""
    lines = [l.strip() for l in t.splitlines() if l.strip()]

    def after(lbl):
        for i, l in enumerate(lines):
            if l.startswith(lbl):
                return lines[i + 1] if i + 1 < len(lines) else ""
        return ""
    row = dict(project=pn, name=name, facility=fac, address=after("Location Address:") + " " + (lines[lines.index(after("Location Address:")) + 1] if after("Location Address:") in lines else ""),
               county=after("Location County:"), start=after("Start Date:"), completion=after("Completion Date:"), cost=after("Estimated Cost:"),
               worktype=after("Type of Work:"), sqft=after("Square Footage:"), tenant_funded=after("Are the private funds provided by the tenant?"),
               status=after("Current Status:"), owner=after("Owner Name:"), scope=after("Scope of Work:")[:300])
    out.append(row); print(row)
    time.sleep(0.7)
with open(os.path.join(RAW, "H03_tabs_projects.csv"), "w", newline="", encoding="utf-8") as f:
    if out:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
