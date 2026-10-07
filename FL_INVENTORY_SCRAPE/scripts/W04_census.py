"""W04 live catalog census of Foot Locker international sites via the server-rendered search page facets.
Usage: python3 W04_census.py <outdir> [domains...]
For each domain: queries all / sale / new / new+sale / shoes / clothing / per-brand, saves parsed facets+pagination+page-0 products as JSON.
"""
import sys, os, json, time, urllib.parse, gzip
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from W04_parse import extract_state, find_search, facets, products
from curl_cffi import requests as r

SITES = {"footlocker.co.uk":"en","footlocker.de":"de","footlocker.fr":"fr","footlocker.it":"it","footlocker.nl":"nl","footlocker.es":"es",
         "footlocker.be":"fr","footlocker.at":"de","footlocker.pl":"pl","footlocker.ie":"en","footlocker.pt":"pt","footlocker.cz":"cs",
         "footlocker.hu":"hu","footlocker.lu":"fr","footlocker.com.au":"en","footlocker.co.nz":"en","footlocker.ca":"en","footlocker.com":"en"}
BRANDS = ["nike","jordan","adidas","new balance","asics","on","hoka","salomon","puma","ugg","the north face","crocs","timberland","converse","vans","mizuno","saucony","under armour","lacoste","reebok"]

def get(s, dom, lang, q):
    u = f"https://www.{dom}/{lang}/search?query=" + urllib.parse.quote(q)
    for attempt in range(3):
        try:
            h = s.get(u, timeout=90)
            st = extract_state(h.text)
            sr = find_search(st) if st else None
            if sr: return u, sr
        except Exception as e:
            pass
        time.sleep(5)
    return u, None

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    doms = sys.argv[2:] or list(SITES)
    s = r.Session(impersonate="chrome")
    for dom in doms:
        lang = SITES[dom]; fn = os.path.join(out, dom + ".json.gz")
        if os.path.exists(fn): continue
        res = {}
        base = ":relevance:group_id:all"
        qs = {"all": base, "sale": base+":saleProduct:True", "new": base+":newProduct:True",
              "new_sale": base+":newProduct:True:saleProduct:True", "shoes": base+":productTypes:Shoes",
              "clothing": base+":productTypes:Clothing", "flonly": base+":footLockerOnly:True"}
        for k, q in qs.items():
            u, sr = get(s, dom, lang, q)
            res[k] = {"url": u, "pagination": sr and sr.get("pagination"), "facets": sr and facets(sr), "products": sr and products(sr)}
            time.sleep(1.0)
        bf = (res["all"]["facets"] or {}).get("brand", {})
        for b in BRANDS:
            name = next((n for n in bf if n.lower() == b), None)
            if not name: continue
            u, sr = get(s, dom, lang, base + ":brand:" + name)
            res["brand:" + name] = {"url": u, "pagination": sr and sr.get("pagination"), "facets": sr and facets(sr), "products": sr and products(sr)}
            time.sleep(1.0)
        res["_fetched"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with gzip.open(fn, "wt") as f: json.dump(res, f)
        print(dom, "done", res["all"]["pagination"], flush=True)

if __name__ == "__main__":
    main()
