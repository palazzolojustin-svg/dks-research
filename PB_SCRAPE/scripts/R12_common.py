"""R12 shared helpers: parse archived dicks.com / golfgalaxy.com product-listing pages (PLPs) of ANY era.

parse_plp(html) -> dict or None
  Handles BOTH page layouts seen in archives:
   - 2023-Mar-2024 "React" layout: `window.__STATE__ = {...}` -> ...productApiData {totalCount, productVOs, facetVOs}
     (X02's parser missed this layout; it only looked for the 2025+ Angular transfer-state blob)
   - 2025-26 "ngx" Angular layout: <script> transfer-state JSON whose entry holds {totalCount, searchVO, productVOs, facetVOs}
  Returns: layout, totalCount, sort, storeId, pageSize, brands {brand: count} (X_BRAND facet, complete list),
           products [(rank, brand, is_vertical_flag, partnumber)] for the first page, sale facet count.
  The owned flag is DKS's own attribute 6025 = "Vertical Brand" inside each productVO's attributes.

wb_get(url, params) : polite Wayback GET shared with X03 via raw/X03_last_request.txt (cross-process gap),
  long exponential back-off on refusals/429 (Internet Archive throttles this IP heavily when many agents run).
"""
import json, os, re, time
import requests

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RAW = os.path.join(ROOT, "raw")
STAMP = os.path.join(RAW, "X03_last_request.txt")  # shared with X03 scripts on purpose
UA = {"User-Agent": "Mozilla/5.0 (research; DKS owned-brand study R12; polite)"}
GAP = float(os.environ.get("R12_GAP", "6"))


def _wait():
    try:
        last = float(open(STAMP).read().strip())
    except Exception:
        last = 0
    d = time.time() - last
    if d < GAP:
        time.sleep(GAP - d)
    try:
        open(STAMP, "w").write(str(time.time()))
    except Exception:
        pass


def wb_get(url, params=None, timeout=150, tries=10, log=print):
    back = 60
    for a in range(tries):
        _wait()
        try:
            r = requests.get(url, params=params, headers=UA, timeout=timeout)
            if r.status_code == 200:
                return r
            if r.status_code in (403, 404, 451):
                return r
            log(f"  [wb] HTTP {r.status_code}; sleep {back}s")
        except requests.exceptions.ConnectionError:
            log(f"  [wb] refused/reset; sleep {back}s")
        except Exception as e:
            log(f"  [wb] err {str(e)[:80]}; sleep {back}s")
        time.sleep(back)
        back = min(back * 2, int(os.environ.get("R12_MAXBACK", "300")))
    return None


def _walk_find(o, pred):
    st = [o]
    while st:
        x = st.pop()
        if isinstance(x, dict):
            if pred(x):
                return x
            st.extend(x.values())
        elif isinstance(x, list):
            st.extend(x)
    return None


def _from_state(t):
    i = t.find("window.__STATE__")
    if i < 0:
        return None, None
    j = t.find("{", i)
    try:
        o, _ = json.JSONDecoder(strict=False).raw_decode(t[j:])
    except Exception:
        return None, None
    holder = _walk_find(o, lambda x: "productApiData" in x and isinstance(x.get("productApiData"), dict))
    if not holder:
        return None, None
    return holder["productApiData"], holder.get("input") or {}


def _from_ngx(t):
    for m in re.finditer(r"<script[^>]*>(.*?)</script>", t, re.S):
        s = m.group(1)
        if '"productVOs"' not in s:
            continue
        try:
            j = json.loads(s, strict=False)
        except Exception:
            continue
        R = _walk_find(j, lambda x: "productVOs" in x and "totalCount" in x)
        if R is None:
            # some captures store the body as a JSON string
            sub = _walk_find(j, lambda x: any(isinstance(v, str) and '"productVOs"' in v for v in x.values()))
            if sub:
                for v in sub.values():
                    if isinstance(v, str) and '"productVOs"' in v:
                        try:
                            R = _walk_find(json.loads(v, strict=False), lambda x: "productVOs" in x and "totalCount" in x)
                        except Exception:
                            pass
        if R is not None:
            return R, R.get("searchVO") or {}
    return None, None


def parse_plp(t):
    if not t:
        return None
    R, inp = _from_ngx(t)
    layout = "ngx"
    if R is None:
        R, inp = _from_state(t)
        layout = "state"
    if R is None:
        return None
    brands, sale = {}, None
    for f in R.get("facetVOs") or []:
        aid = f.get("attrIdentifier")
        vals = f.get("values")
        if not vals and f.get("valueList"):
            vals = {v.get("value"): v.get("count") for v in f["valueList"]}
        if aid == "X_BRAND":
            brands = {k: int(v) for k, v in (vals or {}).items() if v is not None}
        if aid == "5004" or (f.get("attrName") or "").lower() == "sale":
            try:
                sale = sum(int(v) for v in (vals or {}).values())
            except Exception:
                pass
    prods = []
    for k, p in enumerate(R.get("productVOs") or [], 1):
        a = p.get("attributes")
        a = a if isinstance(a, str) else json.dumps(a)
        prods.append((k, p.get("mfName") or p.get("brand") or "", int("Vertical Brand" in a),
                      p.get("parentPartnumber") or p.get("partnumber") or ""))
    return {"layout": layout, "total": R.get("totalCount"), "sort": (inp or {}).get("selectedSort"),
            "store": (inp or {}).get("storeId") or (inp or {}).get("selectedStore"),
            "pagesize": (inp or {}).get("pageSize"), "brands": brands, "sale": sale, "products": prods}


# brands DKS flags with attribute 6025 "Vertical Brand" (union of the 2026-10-07 live census + archived pages;
# extended at run time by R12 scripts from any flagged product seen)
OWNED_BASE = {"DSG", "CALIA", "VRST", "Maxfli", "MAXFLI", "Walter Hagen", "Top Flite", "Top-Flite", "Tommy Armour",
              "Tommy Armour Golf", "Alpine Design", "ETHOS", "Fitness Gear", "Nishiki", "Quest", "PRIMED", "Tour Trek",
              "TourTrek", "DICK'S Sporting Goods", "Lady Hagen", "CALIA by Carrie Underwood"}
