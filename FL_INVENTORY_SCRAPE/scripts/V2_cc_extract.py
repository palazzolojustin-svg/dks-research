"""X11 step 2: pull sampled dicks.com category-page captures from Common Crawl and extract
page-level facets and product-level list/offer prices (owned 'Vertical Brand' vs national).

Rerun:  python X11_cc_extract.py <collection> [max_pages=500] [workers=8]
  Needs PB_SCRAPE/raw/X11_ccidx/<collection>.jsonl from X11_cc_index.py.
  Output: PB_SCRAPE/raw/X11_cc/<collection>_pages.jsonl and <collection>_products.jsonl
  (resumable: already-processed URLs are skipped).
Sampling: every captured page whose URL contains an owned-brand or benchmark-brand slug is
always taken; the rest are a deterministic random sample (seed=11) up to max_pages total.
Source data: the SSR JSON <script id=dcsg-ngx-plp-server-state> embedded in every
dicks.com /f/ page (PRODUCT_LIST_API_RESPONSE: totalCount, facetVOs incl. 'Sale' facet and
brand facet, productVOs with mfName, attributes (6025='Vertical Brand'), floatFacets list &
offer price, productDetails min/max list/offer price, dsgPriceIndicators).
"""
import gzip, json, os, random, re, sys, threading
from concurrent.futures import ThreadPoolExecutor
import requests

BASE = os.path.join(os.path.dirname(__file__), "..", "raw", "V2")
IDX = os.path.join(BASE, "ccidx")
OUT = os.path.join(BASE, "cc")
os.makedirs(OUT, exist_ok=True)
PRIORITY = ["calia", "dsg", "vrst", "maxfli", "walter-hagen", "top-flite", "tommy-armour",
            "alpine-design", "ethos", "fitness-gear", "nishiki", "quest", "nike", "under-armour",
            "adidas", "new-balance", "the-north-face", "columbia", "vuori", "lululemon", "titleist",
            "callaway", "taylormade", "leggings", "joggers", "golf-balls", "hoodies", "fleece",
            "shorts", "t-shirts", "tees"]
STATE_RE = re.compile(r'<script id=["\']?dcsg-ngx-plp-server-state["\']? type=["\']?application/json["\']?>(.*?)</script>', re.S)
lock = threading.Lock()
S = requests.Session()


def fetch(rec):
    off, ln = int(rec["offset"]), int(rec["length"])
    for i in range(4):
        try:
            r = S.get("https://data.commoncrawl.org/" + rec["filename"],
                      headers={"Range": f"bytes={off}-{off+ln-1}"}, timeout=120)
            if r.status_code in (200, 206):
                return gzip.decompress(r.content).decode("utf-8", "replace")
        except Exception:
            pass
    return None


def attrs(vo):
    out = {}
    try:
        for d in json.loads(vo.get("attributes") or "[]"):
            for k, v in d.items():
                out.setdefault(k.strip(), []).append(v)
    except Exception:
        pass
    return out


def ff(vo, ident):
    vals = [x.get("value") for x in vo.get("floatFacets") or [] if x.get("identifier") == ident]
    return vals[0] if vals else None


def process(rec, cid, fp, fprod):
    raw = fetch(rec)
    if raw is None:
        return
    m = STATE_RE.search(raw)
    page = {"crawl": cid, "url": rec["url"], "ts": rec["timestamp"], "has_state": bool(m)}
    prods = []
    if m:
        try:
            d = json.loads(m.group(1))
            pl = d.get("PRODUCT_LIST_API_RESPONSE") or {}
            if not pl:  # pre-Jun-2026 format: body stored under a hash key of the /v2/search call
                for v in d.values():
                    if isinstance(v, dict) and isinstance(v.get("b"), dict) and "productVOs" in v["b"]:
                        pl = v["b"]; break
            page["totalCount"] = pl.get("totalCount")
            facets = {}
            for f in pl.get("facetVOs") or []:
                facets[f.get("attrName")] = {"id": f.get("attrIdentifier"),
                                              "vals": {str(v.get("value")): v.get("count") for v in f.get("valueList") or []}}
            page["sale_count"] = (facets.get("Sale") or {}).get("vals", {}).get("Sale")
            page["facets"] = {k: v for k, v in facets.items() if k in ("Brand", "Sale", "Price", "Product Type", "Vertical Brand")
                              or (v["id"] in ("X_BRAND", "6025", "5004"))}
            det = pl.get("productDetails") or {}
            for vo in pl.get("productVOs") or []:
                a = attrs(vo)
                pdx = (det.get(str(vo.get("parentCatentryId"))) or det.get(str(vo.get("catentryId"))) or {}).get("prices") or {}
                prods.append({
                    "crawl": cid, "ts": rec["timestamp"], "page": rec["url"],
                    "pp": vo.get("parentPartnumber"), "name": vo.get("name"), "brand": vo.get("mfName"),
                    "vb": a.get("6025"), "cat": (a.get("PRIMARY_CATEGORY_DSG") or [None])[0],
                    "ptype": a.get("5382"), "gender": a.get("5495"),
                    "list": ff(vo, "dickssportinggoodslistprice"), "offer": ff(vo, "dickssportinggoodsofferprice"),
                    "minlist": pdx.get("minlistprice"), "maxlist": pdx.get("maxlistprice"),
                    "minoffer": pdx.get("minofferprice"), "maxoffer": pdx.get("maxofferprice"),
                    "deals": (vo.get("dsgPriceIndicators") or {}).get("dealsPercentage"),
                    "pi": (vo.get("dsgPriceIndicators") or {}).get("priceIndicator"),
                    "sortdate": vo.get("dsgProductSortDate"), "pinned": vo.get("isPinned")})
        except Exception as e:
            page["err"] = str(e)[:200]
    with lock:
        fp.write(json.dumps(page) + "\n"); fp.flush()
        for p in prods:
            fprod.write(json.dumps(p) + "\n")
        fprod.flush()


def main():
    cid = sys.argv[1]
    maxp = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    recs = []
    for l in open(os.path.join(IDX, cid + ".jsonl"), encoding="utf-8"):
        try:
            recs.append(json.loads(l))
        except Exception:
            pass  # truncated CDX line
    recs = [r for r in recs if r.get("status") == "200" and "?" not in r["url"]]
    seen = {}
    for r in recs:
        seen.setdefault(r["url"].lower(), r)  # one capture per URL
    recs = list(seen.values())
    pri = [r for r in recs if any(("/f/" + s) in r["url"].lower() or ("-" + s) in r["url"].lower() for s in PRIORITY)]
    rest = [r for r in recs if r not in pri]
    random.Random(11).shuffle(pri); random.Random(11).shuffle(rest)
    take = pri[: int(maxp * 0.6)]
    take += rest[: maxp - len(take)]
    pfile = os.path.join(OUT, cid + "_pages.jsonl")
    done = set()
    if os.path.exists(pfile):
        done = {json.loads(l)["url"] for l in open(pfile, encoding="utf-8") if l.strip()}
    take = [r for r in take if r["url"] not in done]
    print(cid, "captures", len(recs), "priority", len(pri), "to fetch", len(take), flush=True)
    with open(pfile, "a", encoding="utf-8") as fp, open(os.path.join(OUT, cid + "_products.jsonl"), "a", encoding="utf-8") as fprod:
        with ThreadPoolExecutor(workers) as ex:
            list(ex.map(lambda r: process(r, cid, fp, fprod), take))
    print(cid, "done", flush=True)


if __name__ == "__main__":
    main()
