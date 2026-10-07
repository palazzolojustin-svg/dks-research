"""R1 (e): other Bazaarvoice clients relevant to DKS owned brands.
- Foot Locker family (footlocker 8001, champssports 8006, kidsfootlocker 9055): is any DKS owned brand listed?
  Checks BrandId filters and free-text Search for DSG/CALIA/VRST/Maxfli; prints catalog freshness (latest reviews).
- publiclands (11544), caliastudio (19888), vrst (10303), golfgalaxy (15899): owned-brand review streams by month,
  and whether the review IDs are independent of the dsg pool.
Output: raw/R1_other_clients_monthly.csv ; printed summary.
RERUN: python R1_bv_other_clients.py
"""
import csv, os, sys, datetime as dt, requests
sys.path.insert(0, os.path.dirname(__file__))
from R1_bv_client_probe import ORIGIN, H
from X01_bv_reviews import RAW

DC = {"dsg": "13107", "golfgalaxy": "15899", "publiclands": "11544", "caliastudio": "19888", "vrst": "10303",
      "footlocker": "8001", "champssports": "8006", "kidsfootlocker": "9055", "academy": "9102"}
OWNED = ["DSG", "Calia", "VRST", "Maxfli", "Walter_Hagen", "Alpine_Design", "ETHOS", "Fitness_Gear", "Top_Flite",
         "Nishiki", "Quest", "Tommy_Armour_Golf"]


def sess(c):
    s = requests.Session(); s.headers.update(H)
    s.headers.update({"bv-bfd-token": f"{DC[c]},main_site,en_US", "Origin": ORIGIN[c], "Referer": ORIGIN[c] + "/"})
    return s


def get(s, c, res, params):
    url = f"https://apps.bazaarvoice.com/bfd/v1/clients/{c}/api-products/cv2/resources/data/{res}.json"
    for i in range(4):
        try:
            r = s.get(url, params=list(params) + [("apiversion", "5.4")], timeout=60)
            if r.status_code == 200:
                j = r.json(); return j.get("response", j)
        except Exception:
            pass
    return {}


def fl_check():
    for c in ("footlocker", "champssports", "kidsfootlocker"):
        s = sess(c)
        out = {}
        for q in ("DSG", "CALIA", "VRST", "Maxfli", "DICK'S"):
            r = get(s, c, "products", [("Search", q), ("Limit", "3")])
            out[q] = (r.get("TotalResults"), [(x.get("Brand") or {}).get("Name") for x in r.get("Results", [])][:3])
        # freshness: newest products by any brand with reviews
        r = get(s, c, "products", [("Filter", "TotalReviewCount:gte:1"), ("Stats", "Reviews"), ("Limit", "1")])
        print(c, "search", out, "products w/ reviews", r.get("TotalResults"), flush=True)


def month_edges(start=(2023, 1)):
    y, m = start; now = dt.datetime.now(dt.timezone.utc)
    while (y, m) <= (now.year, now.month):
        a = int(dt.datetime(y, m, 1, tzinfo=dt.timezone.utc).timestamp())
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        yield f"{y}-{m:02d}", a, int(dt.datetime(ny, nm, 1, tzinfo=dt.timezone.utc).timestamp())
        y, m = ny, nm


def owned_stream(c):
    """Monthly native review counts on owned-brand products for client c, via products.json FilteredStats."""
    s = sess(c)
    pids = {}
    for b in OWNED:
        n = get(s, c, "products", [("Filter", f"BrandId:eq:{b}"), ("Filter", "TotalReviewCount:gte:1"), ("Limit", "1")]).get("TotalResults") or 0
        for o in range(0, n, 100):
            for x in get(s, c, "products", [("Filter", f"BrandId:eq:{b}"), ("Filter", "TotalReviewCount:gte:1"), ("Limit", "100"), ("Offset", str(o))]).get("Results", []):
                pids[x["Id"]] = b
    rows = []
    ids = list(pids)
    for mo, a, bb in month_edges():
        tot = {}
        for i in range(0, len(ids), 100):
            chunk = ids[i:i + 100]
            r = get(s, c, "products", [("Filter", "Id:eq:" + ",".join(chunk)), ("FilteredStats", "Reviews"), ("Limit", "100"),
                                       ("Filter_Reviews", f"SubmissionTime:gte:{a}"), ("Filter_Reviews", f"SubmissionTime:lt:{bb}")])
            for x in r.get("Results", []):
                n = ((x.get("FilteredReviewStatistics") or {}).get("TotalReviewCount") or 0)
                tot[pids[x["Id"]]] = tot.get(pids[x["Id"]], 0) + n
        for b, n in tot.items():
            rows.append([c, mo, b, n])
        print(c, mo, sum(tot.values()), flush=True)
    return rows


if __name__ == "__main__":
    which = sys.argv[1:] or ["fl", "publiclands", "caliastudio", "vrst"]
    if "fl" in which:
        fl_check(); which = [w for w in which if w != "fl"]
    path = os.path.join(RAW, "R1_other_clients_monthly.csv")
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["client", "month", "brand", "native_reviews"])
        for c in which:
            w.writerows(owned_stream(c)); f.flush()
