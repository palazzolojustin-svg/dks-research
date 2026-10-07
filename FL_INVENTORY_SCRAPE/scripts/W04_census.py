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

def facet_queries(sr):
    """map (code,name)->(query value, expected count) from the facets of a search result"""
    out = {}
    for f in sr.get("facets", []) or []:
        for v in f.get("values", []):
            try: out[(f.get("code"), v["name"])] = (v["query"]["query"]["value"], v.get("count"))
            except Exception: pass
    return out

def get_checked(s, dom, lang, q, expected=None):
    best = None
    for attempt in range(4):
        u, sr = get(s, dom, lang, q)
        if sr is None: continue
        t = (sr.get("pagination") or {}).get("totalResults")
        if expected is None or (t is not None and abs(t - expected) <= max(5, 0.15*expected)):
            return u, sr, True
        best = (u, sr); time.sleep(3)
    return (best[0], best[1], False) if best else (None, None, False)

def pack(u, sr, ok, exp):
    return {"url": u, "ok": ok, "expected": exp, "pagination": sr and sr.get("pagination"), "facets": sr and facets(sr), "products": sr and products(sr)}

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    doms = sys.argv[2:] or list(SITES)
    s = r.Session(impersonate="chrome")
    for dom in doms:
        lang = SITES[dom]; fn = os.path.join(out, dom + ".json.gz")
        if os.path.exists(fn): continue
        res = {}
        base = ":relevance:group_id:all"
        u, sr, ok = get_checked(s, dom, lang, base)
        u2, sr2, ok2 = get_checked(s, dom, lang, base)
        if sr2 and sr and (sr2["pagination"].get("totalResults") or 0) > (sr["pagination"].get("totalResults") or 0): u, sr = u2, sr2
        if not sr: print(dom, "FAIL", flush=True); continue
        res["all"] = pack(u, sr, True, None)
        fq = facet_queries(sr)
        todo = {}
        for (code, name), (qv, cnt) in fq.items():
            if code == "miscellaneous": todo["misc:" + qv.split(":")[-2]] = (qv, cnt)
            elif code in ("productType", "productTypes") and cnt and cnt > 50: todo["ptype:" + name] = (qv, cnt)
            elif code == "gender": todo["gender:" + name] = (qv, cnt)
            elif code == "style" and cnt and cnt >= 150: todo["style:" + name] = (qv, cnt)
            elif code == "brand" and name.lower() in BRANDS: todo["brand:" + name] = (qv, cnt)
        todo["new_sale"] = (base + ":newProduct:True:saleProduct:True", None)
        for k, (qv, cnt) in todo.items():
            u, sr, ok = get_checked(s, dom, lang, qv, cnt)
            res[k] = pack(u, sr, ok, cnt)
            time.sleep(0.8)
        res["_fetched"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with gzip.open(fn, "wt") as f: json.dump(res, f)
        bad = [k for k, v in res.items() if isinstance(v, dict) and v.get("ok") is False]
        print(dom, "done", res["all"]["pagination"].get("totalResults"), "queries", len(todo), "not_ok", bad, flush=True)

if __name__ == "__main__":
    main()
