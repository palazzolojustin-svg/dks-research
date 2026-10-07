"""R9 step 2: extract dicks.com / golfgalaxy.com / publiclands.com category-page (/f/) product JSON
from Common Crawl captures, for ANY era (2023-24 'window.__STATE__' layout and 2025-26
'dcsg-ngx-plp-server-state' layout).

Rerun:
  python R9_cc_extract.py <collection> <index_jsonl> <out_tag> [max_pages=900] [workers=10]
  e.g. python R9_cc_extract.py CC-MAIN-2023-40 ../raw/X03_cc/CC-MAIN-2023-40_f.jsonl dks 900 10
       python R9_cc_extract.py CC-MAIN-2026-39 ../raw/R9/idx/CC-MAIN-2026-39_gg_f.jsonl gg 900 10
Output (resumable; already-done URLs skipped):
  raw/R9/cc/<collection>_<tag>_pages.jsonl     one line per page: totalCount, Sale facet, Brand facet,
                                                 Vertical Brand facet (if any), sort, pinned count
  raw/R9/cc/<collection>_<tag>_products.jsonl  one line per product (first 48 listed, in display order):
     pos (1-based rank on page), brand (mfName), vb (attr 6025 'Vertical Brand'), badge
     ('DicksExclusive' etc.), cat, ptype, gender, list/offer (displayed SKU), min/max list/offer,
     ratingCount / ratingValue (Bazaarvoice review count embedded in listing), sortdate, pinned.
Sampling: pages whose URL contains a priority slug are always taken (60%), the rest are a
deterministic random sample (seed 11) to max_pages. Same sampling rule as X11, so results
can be pooled with X11's raw/X11_cc files for 2025-08 → 2026-09.
"""
import json, os, random, re, sys, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R9_cc_common import load_idx, fetch_warc, RAW

OUT = os.path.join(RAW, "R9", "cc")
os.makedirs(OUT, exist_ok=True)
PRIORITY = ["calia", "dsg", "vrst", "maxfli", "walter-hagen", "top-flite", "tommy-armour",
            "alpine-design", "ethos", "fitness-gear", "nishiki", "quest", "nike", "under-armour",
            "adidas", "new-balance", "the-north-face", "columbia", "vuori", "lululemon", "titleist",
            "callaway", "taylormade", "leggings", "joggers", "golf-balls", "hoodies", "fleece",
            "shorts", "t-shirts", "tees"]
NEW_RE = re.compile(r'<script id=["\']?dcsg-ngx-plp-server-state["\']?[^>]*>(.*?)</script>', re.S)
lock = threading.Lock()
DEC = json.JSONDecoder(strict=False)


def parse_state(raw):
    """Return (product-list-api dict, layout tag) or (None, None)."""
    m = NEW_RE.search(raw)
    if m:
        try:
            d = json.loads(m.group(1), strict=False)
        except Exception:
            return None, "new-bad"
        pl = d.get("PRODUCT_LIST_API_RESPONSE") or {}
        if not pl:
            for v in d.values():
                if isinstance(v, dict) and isinstance(v.get("b"), dict) and "productVOs" in v["b"]:
                    pl = v["b"]; break
        return (pl or None), "ngx"
    i = raw.find("window.__STATE__")
    if i >= 0:
        j = raw.find("{", i)
        try:
            d, _ = DEC.raw_decode(raw, j)
            pa = d.get("productApiData")
            if pa:
                pa["_sort"] = (d.get("input") or {}).get("selectedSort")
                pa["_default_sort"] = (d.get("common") or {}).get("defaultSort")
            return pa, "state"
        except Exception:
            return None, "state-bad"
    return None, None


def attrs(vo):
    out = {}
    a = vo.get("attributes")
    try:
        lst = json.loads(a, strict=False) if isinstance(a, str) else (a or [])
        for d in lst:
            for k, v in d.items():
                out.setdefault(k.strip(), []).append(v)
    except Exception:
        pass
    return out


def ff(vo, ident):
    vals = [x.get("value") for x in vo.get("floatFacets") or [] if x.get("identifier") == ident]
    return vals[0] if vals else None


def first(a, k):
    v = a.get(k)
    return v[0] if v else None


def process(rec, cid, tag, fp, fprod):
    raw = fetch_warc(rec)
    if raw is None:
        return
    pl, layout = parse_state(raw)
    page = {"crawl": cid, "tag": tag, "url": rec["url"], "ts": rec["timestamp"], "layout": layout,
            "has_state": bool(pl)}
    prods = []
    if pl:
        try:
            page["totalCount"] = pl.get("totalCount")
            page["sort"] = pl.get("_sort")
            if page["sort"] is None:
                page["sort"] = (pl.get("searchVO") or {}).get("selectedSort")
            facets = {}
            for f in pl.get("facetVOs") or []:
                facets[f.get("attrName")] = {"id": f.get("attrIdentifier"),
                                              "vals": {str(v.get("value")): v.get("count") for v in f.get("valueList") or []}}
            page["sale_count"] = (facets.get("Sale") or {}).get("vals", {}).get("Sale")
            page["facets"] = {k: v for k, v in facets.items()
                              if k in ("Brand", "Sale", "Price", "Vertical Brand") or v["id"] in ("X_BRAND", "6025", "5004")}
            det = pl.get("productDetails") or {}
            u = rec["url"].lower()
            host = "golfgalaxy" if "golfgalaxy" in u else ("publiclands" if "publiclands" in u else "dickssportinggoods")
            for pos, vo in enumerate(pl.get("productVOs") or [], 1):
                a = attrs(vo)
                pdx = (det.get(str(vo.get("parentCatentryId"))) or det.get(str(vo.get("catentryId"))) or {}).get("prices") or {}
                rc = vo.get("ratingCount")
                if rc is None:
                    rc = first(a, "X_BazaarVoice_count_DSG") or first(a, "X_BazaarVoice_count_ovr_DSG")
                rv = vo.get("ratingValue")
                if rv is None:
                    rv = first(a, "X_BazaarVoice_ratings_DSG")
                prods.append({
                    "crawl": cid, "tag": tag, "ts": rec["timestamp"], "page": rec["url"], "pos": pos,
                    "pp": vo.get("parentPartnumber"), "name": vo.get("name"), "brand": vo.get("mfName") or first(a, "X_BRAND"),
                    "vb": a.get("6025"), "badge": vo.get("badge"), "excl": a.get("4298"),
                    "cat": first(a, "PRIMARY_CATEGORY_DSG"), "ptype": a.get("5382"), "gender": a.get("5495"),
                    "list": ff(vo, host + "listprice"), "offer": ff(vo, host + "offerprice"),
                    "minlist": pdx.get("minlistprice"), "maxlist": pdx.get("maxlistprice"),
                    "minoffer": pdx.get("minofferprice"), "maxoffer": pdx.get("maxofferprice"),
                    "deals": (vo.get("dsgPriceIndicators") or {}).get("dealsPercentage"),
                    "pi": (vo.get("dsgPriceIndicators") or {}).get("priceIndicator"),
                    "rc": rc, "rv": rv,
                    "sortdate": vo.get("dsgProductSortDate"), "pinned": vo.get("isPinned")})
        except Exception as e:
            page["err"] = str(e)[:200]
    page["n_products"] = len(prods)
    with lock:
        fp.write(json.dumps(page) + "\n"); fp.flush()
        for p in prods:
            fprod.write(json.dumps(p) + "\n")
        fprod.flush()


def main():
    cid, idx, tag = sys.argv[1], sys.argv[2], sys.argv[3]
    maxp = int(sys.argv[4]) if len(sys.argv) > 4 else 900
    workers = int(sys.argv[5]) if len(sys.argv) > 5 else 10
    recs = [r for r in load_idx(idx) if r.get("status") == "200" and "?" not in r["url"]
            and "/f/" in r["url"]]
    seen = {}
    for r in recs:
        seen.setdefault(r["url"].lower().rstrip("/"), r)
    recs = list(seen.values())
    pri = [r for r in recs if any(("/f/" + s) in r["url"].lower() or ("-" + s) in r["url"].lower() for s in PRIORITY)]
    pset = {id(r) for r in pri}
    rest = [r for r in recs if id(r) not in pset]
    random.Random(11).shuffle(pri); random.Random(11).shuffle(rest)
    take = pri[: int(maxp * 0.6)]
    take += rest[: maxp - len(take)]
    pfile = os.path.join(OUT, f"{cid}_{tag}_pages.jsonl")
    done = set()
    # skip pages already extracted for this crawl by ANY R9 tag, or by X11 (raw/X11_cc) with valid state
    import glob as _g
    x11 = [] if tag == "panel" else [os.path.join(RAW, "X11_cc", f"{cid}_pages.jsonl")]  # panel wants badges/review counts
    for pf in _g.glob(os.path.join(OUT, f"{cid}_*_pages.jsonl")) + x11:
        if os.path.exists(pf):
            for l in open(pf, encoding="utf-8"):
                try:
                    p = json.loads(l)
                except Exception:
                    continue
                if p.get("has_state") or "X11_cc" not in pf:
                    done.add(p["url"])
    take = [r for r in take if r["url"] not in done]
    print(cid, tag, "captures", len(recs), "priority", len(pri), "to fetch", len(take), flush=True)
    with open(pfile, "a", encoding="utf-8") as fp, \
            open(os.path.join(OUT, f"{cid}_{tag}_products.jsonl"), "a", encoding="utf-8") as fprod:
        with ThreadPoolExecutor(workers) as ex:
            list(ex.map(lambda r: process(r, cid, tag, fp, fprod), take))
    print(cid, tag, "done", flush=True)


if __name__ == "__main__":
    main()
