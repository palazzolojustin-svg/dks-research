"""B3: fuller Texas TDLR TABS extract of DICK'S / House of Sport / Golf Galaxy / Field House projects (2022+).
Extends H03_tabs.py: (1) name/facility/owner searches with many variants, (2) searches by the DESIGN FIRMS that DKS
uses (harvested from print pages of known DKS projects), (3) per-city searches in HoS candidate cities; then fetches
every candidate's print page and keeps those whose name/facility/owner/TENANT/scope mention DKS banners.
Rerun: python B3_tabs_full.py  -> raw/B3_tabs_all.csv (all candidates with parsed fields) and raw/B3_tabs_dks.csv (DKS only)
"""
import requests, re, csv, os, time, json
from bs4 import BeautifulSoup
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
UA = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}
S = requests.Session()
URL = "https://www.tdlr.texas.gov/TABS/Search/SearchProjects"
S.get("https://www.tdlr.texas.gov/TABS/Search", headers=UA, timeout=60)


def search(**flt):
    out = []
    start = 0
    while True:
        data = {"draw": 1, "start": start, "length": 100, "order[0][column]": 3, "order[0][dir]": "desc"}
        data.update(flt)
        for i in range(4):
            try:
                js = S.post(URL, data=data, headers=UA, timeout=90).json(); break
            except Exception:
                time.sleep(5 * (i + 1)); js = {}
        d = js.get("data", []) or []
        out += d
        n = js.get("recordsFiltered") or 0
        start += 100
        if start >= n or not d or start >= 1500:
            return out, n
        time.sleep(0.8)


def pn(rec):
    return re.sub(r"<[^>]+>", "", str(rec.get("ProjectNumber") or rec.get("projectNumber") or ""))


cands = {}


def add(recs, tag):
    for r in recs:
        k = pn(r)
        if k:
            cands.setdefault(k, {"tags": set(), "rec": r})["tags"].add(tag)


Q = []
for v in ["House of Sport", "House of Sports", "Dick's", "Dicks", "DICK'S", "Dick s", "DSG", "Golf Galaxy",
          "Going Going Gone", "Public Lands", "Field & Stream", "Field and Stream"]:
    Q += [("ProjectName", v), ("FacilityName", v)]
Q += [("OwnerName", v) for v in ["Dick's", "Dicks", "DICK'S", "Dick's Sporting", "Dick's Merchandising"]]
for f, v in Q:
    recs, n = search(**{f: v, "RegistrationDateBegin": "01/01/2022"})
    print(f, v, n, flush=True); add(recs, f"{f}={v}"); time.sleep(0.8)

# fetch print pages


def printpage(k):
    for i in range(3):
        try:
            t = BeautifulSoup(S.get(f"https://www.tdlr.texas.gov/TABS/Search/Print/{k}", headers=UA, timeout=60).text, "html.parser").get_text("\n")
            return [l.strip() for l in t.splitlines() if l.strip()]
        except Exception:
            time.sleep(4)
    return []


def parse(lines):
    def after(lbl, n=1):
        for i, l in enumerate(lines):
            if l.startswith(lbl):
                return " ".join(lines[i + 1:i + 1 + n])
        return ""
    return dict(name=after("Project Name:"), facility=after("Facility Name:"), address=after("Location Address:", 2), county=after("Location County:"),
                registered=after("Registration Date:"), start=after("Start Date:"), completion=after("Completion Date:"), cost=after("Estimated Cost:"),
                worktype=after("Type of Work:"), sqft=after("Square Footage:"), tenant_funded=after("Are the private funds provided by the tenant?"),
                status=after("Current Status:"), owner=after("Owner Name:"), tenant=after("Tenant Name:"), design=after("Design Firm Name:"),
                scope=after("Scope of Work:")[:400])


PAT = re.compile(r"dick'?s sport|dicks sport|dick's house|dick's #|house of sport|golf galaxy|\bdsg\b|going going gone|public lands|dick's merchandising|^dick'?s$|dick'?s \(", re.I)
rows = {}


def process(keys):
    for k in keys:
        if k in rows:
            continue
        p = parse(printpage(k)); p["project"] = k; p["tags"] = ";".join(sorted(cands.get(k, {}).get("tags", [])))
        p["dks"] = bool(PAT.search(" ".join([p["name"], p["facility"], p["owner"], p["tenant"], p["scope"]])))
        rows[k] = p
        if p["dks"]:
            print("DKS", k, p["name"][:40], "|", p["address"][:50], "|", p["cost"], p["sqft"], "|", p["completion"], "|", p["design"], "|", p["tenant"][:40], flush=True)
        time.sleep(0.6)


process(list(cands))
designs = {}
for r in rows.values():
    if r["dks"] and r["design"]:
        designs[r["design"]] = designs.get(r["design"], 0) + 1
print("design firms on DKS projects:", designs, flush=True)
# second pass: search by design firm (registered 2022+), keep everything, then fetch print pages and filter by tenant
for dsn in [d for d, c in sorted(designs.items(), key=lambda x: -x[1])][:15]:
    short = re.sub(r",? (inc|llc|pc|pllc)\.?$", "", dsn, flags=re.I)[:30]
    recs, n = search(ArchitectName=short, RegistrationDateBegin="01/01/2022")
    print("ARCH", short, n, flush=True)
    if n and n <= 600:
        add(recs, f"Arch={short}")
process(list(cands))
allrows = list(rows.values())
keys = ["project", "dks", "name", "facility", "address", "county", "registered", "start", "completion", "cost", "worktype", "sqft", "tenant_funded", "status", "owner", "tenant", "design", "scope", "tags"]
with open(os.path.join(RAW, "B3_tabs_all.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(allrows)
with open(os.path.join(RAW, "B3_tabs_dks.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows([r for r in allrows if r["dks"]])
print("total candidates", len(allrows), "dks", sum(r["dks"] for r in allrows))

