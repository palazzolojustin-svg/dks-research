"""R1: probe Bazaarvoice client deployments (bv.js) and the front-door API for other DKS banners / brand sites
and for Foot Locker. Prints HTTP status, displayCode(s) and, if a displayCode is found, owned-brand product counts.
RERUN: python R1_bv_client_probe.py [client ...]
"""
import re, sys, requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129.0 Safari/537.36"}
CLIENTS = ["dsg", "golfgalaxy", "publiclands", "caliastudio", "calia", "vrst", "field-stream", "moosejaw",
           "footlocker", "footlocker-us", "champssports", "champs", "kidsfootlocker", "academy", "academysports",
           "dickssportinggoods", "goinggoinggone", "fastbreak", "houseofsport", "eastbay", "maxfli", "walterhagen"]
OWNED = ["DSG", "Calia", "VRST", "Maxfli", "Walter_Hagen", "Alpine_Design", "ETHOS", "Fitness_Gear", "Top_Flite",
         "Nishiki", "Quest", "Tommy_Armour_Golf"]


def probe(c):
    out = {}
    for env in ("production", "staging"):
        u = f"https://apps.bazaarvoice.com/deployments/{c}/main_site/{env}/en_US/bv.js"
        try:
            r = requests.get(u, headers=H, timeout=30)
            dcs = sorted(set(re.findall(r'displayCode\W{1,4}(\d{3,6})', r.text)))
            out[env] = (r.status_code, len(r.text), dcs)
        except Exception as e:
            out[env] = ("ERR", str(e)[:60], [])
    return out


ORIGIN = {"dsg": "https://www.dickssportinggoods.com", "golfgalaxy": "https://www.golfgalaxy.com",
          "publiclands": "https://www.publiclands.com", "caliastudio": "https://www.calia.com", "vrst": "https://www.vrst.com",
          "field-stream": "https://www.fieldandstreamshop.com", "moosejaw": "https://www.moosejaw.com",
          "footlocker": "https://www.footlocker.com", "champssports": "https://www.champssports.com",
          "kidsfootlocker": "https://www.kidsfootlocker.com", "academy": "https://www.academy.com", "eastbay": "https://www.eastbay.com"}


def products(c, dc):
    s = requests.Session(); s.headers.update(H); s.headers["bv-bfd-token"] = f"{dc},main_site,en_US"
    o = ORIGIN.get(c, f"https://www.{c}.com"); s.headers.update({"Origin": o, "Referer": o + "/"})
    url = f"https://apps.bazaarvoice.com/bfd/v1/clients/{c}/api-products/cv2/resources/data/products.json"
    res = {}
    r = s.get(url, params={"apiversion": "5.4", "Limit": 1}, timeout=60)
    try:
        res["_all"] = r.json().get("response", r.json()).get("TotalResults")
    except Exception:
        res["_all"] = r.status_code
    for b in OWNED:
        try:
            j = s.get(url, params={"apiversion": "5.4", "Limit": 1, "Filter": f"BrandId:eq:{b}"}, timeout=60).json()
            res[b] = j.get("response", j).get("TotalResults")
        except Exception:
            res[b] = None
    return res


if __name__ == "__main__":
    for c in sys.argv[1:] or CLIENTS:
        o = probe(c)
        print(c, o, flush=True)
        dcs = (o.get("production") or (0, 0, []))[2] or (o.get("staging") or (0, 0, []))[2]
        for dc in dcs[:2]:
            print("   products", c, dc, products(c, dc), flush=True)
