"""Shared helpers: region/domain map, page-type rules and product-price parsing
for archived Foot Locker listing pages (Common Crawl WARC records or Wayback raw HTML)."""
import json
import re

# SURT host -> (region, country). Only the main storefront host (www stripped by SURT).
DOMAINS = {
    "com,footlocker": ("NA", "US"),
    "ca,footlocker": ("NA", "CA"),
    "uk,co,footlocker": ("EMEA", "UK"),
    "de,footlocker": ("EMEA", "DE"),
    "fr,footlocker": ("EMEA", "FR"),
    "it,footlocker": ("EMEA", "IT"),
    "es,footlocker": ("EMEA", "ES"),
    "nl,footlocker": ("EMEA", "NL"),
    "be,footlocker": ("EMEA", "BE"),
    "at,footlocker": ("EMEA", "AT"),
    "ie,footlocker": ("EMEA", "IE"),
    "dk,footlocker": ("EMEA", "DK"),
    "se,footlocker": ("EMEA", "SE"),
    "no,footlocker": ("EMEA", "NO"),
    "pl,footlocker": ("EMEA", "PL"),
    "pt,footlocker": ("EMEA", "PT"),
    "cz,footlocker": ("EMEA", "CZ"),
    "lu,footlocker": ("EMEA", "LU"),
    "gr,footlocker": ("EMEA", "GR"),
    "hu,footlocker": ("EMEA", "HU"),
    "ch,footlocker": ("EMEA", "CH"),
    "eu,footlocker": ("EMEA", "EU"),
}
HOST2SURT = {}
for s in DOMAINS:
    h = ".".join(reversed(s.split(",")))
    HOST2SURT[h] = s
    HOST2SURT["www." + h] = s

LISTING_RE = re.compile(r"/(category|buy|search)(/|\?|\.html|$)", re.I)
PRODUCT_RE = re.compile(r"/product/", re.I)


def page_type(url):
    path = re.sub(r"^https?://[^/]+", "", url)
    if LISTING_RE.search(path):
        return "listing"
    if PRODUCT_RE.search(path):
        return "product"
    return "other"


def host_of(url):
    m = re.match(r"^https?://([^/:?#]+)", url, re.I)
    return m.group(1).lower() if m else ""


def region_of(url):
    s = HOST2SURT.get(host_of(url))
    return DOMAINS[s] if s else (None, None)


_NUM = r"(-?[\d.]+|null)"
# Product objects in the embedded React-query state: name ... originalPrice ... price ... sku
PROD_RE = re.compile(
    r'"name":"((?:[^"\\]|\\.){1,200})",'
    r'(?:"[A-Za-z]+":(?:"(?:[^"\\]|\\.)*"|[\d.]+|true|false|null),){0,6}'
    r'"originalPrice":\{"value":' + _NUM + r'[^}]*\},'
    r'"price":\{"value":' + _NUM + r'[^}]*\}'
    r'(?:.{0,400}?"sku":"([^"]{1,40})")?',
    re.S,
)
# Fallback ordering: price before originalPrice
PROD_RE2 = re.compile(
    r'"name":"((?:[^"\\]|\\.){1,200})",'
    r'(?:"[A-Za-z]+":(?:"(?:[^"\\]|\\.)*"|[\d.]+|true|false|null),){0,6}'
    r'"price":\{"value":' + _NUM + r'[^}]*\},'
    r'"originalPrice":\{"value":' + _NUM + r'[^}]*\}'
    r'(?:.{0,400}?"sku":"([^"]{1,40})")?',
    re.S,
)


def _f(x):
    try:
        v = float(x)
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


def _unesc(s):
    try:
        return json.loads('"' + s + '"')
    except Exception:
        return s


def _json_arrays(html, key='"products":['):
    dec = json.JSONDecoder()
    pos = 0
    while True:
        k = html.find(key, pos)
        if k < 0:
            return
        pos = k + len(key)
        try:
            arr, _ = dec.raw_decode(html, k + len(key) - 1)
        except Exception:
            continue
        if isinstance(arr, list) and arr and isinstance(arr[0], dict):
            yield arr


def parse_products(html):
    """Return (fmt, products) for a listing page. products = [{sku,name,brand,orig,price}].
    fmt 'cat'  = Foot Locker category/search grid (originalPrice vs price)
    fmt 'seo'  = /buy/ SEO landing grid (price_range list vs purchase price); when present it is
                 the page's own product set (the cat-style arrays on /buy/ pages are a generic catalog)
    fmt 'rx'   = regex fallback for unparseable embeds."""
    seo, cat, seen_s, seen_c = [], [], set(), set()
    for arr in _json_arrays(html):
        for a in arr:
            pr = a.get("price_range")
            if isinstance(pr, dict):
                orig = _f(pr.get("min_price")) or _f(pr.get("max_price"))
                price = _f(pr.get("min_purchase_price")) or _f(pr.get("max_purchase_price"))
                key = str(a.get("product_id") or a.get("title"))
                if orig and price and key not in seen_s:
                    seen_s.add(key)
                    seo.append({"sku": str(a.get("product_id")), "name": a.get("title"),
                                "brand": a.get("brand"), "orig": orig, "price": price})
                continue
            op, p = a.get("originalPrice"), a.get("price")
            if isinstance(op, dict) and isinstance(p, dict):
                orig, price = _f(op.get("value")), _f(p.get("value"))
                key = a.get("sku") or a.get("name")
                if orig and price and key not in seen_c:
                    seen_c.add(key)
                    cat.append({"sku": a.get("sku"), "name": a.get("name"), "brand": None,
                                "orig": orig, "price": price})
    if seo:
        return "seo", seo
    if cat:
        return "cat", cat
    out, seen = [], set()
    for rx, swap in ((PROD_RE, False), (PROD_RE2, True)):
        for m in rx.finditer(html):
            name, a, b, sku = m.group(1), m.group(2), m.group(3), m.group(4)
            orig, price = (_f(b), _f(a)) if swap else (_f(a), _f(b))
            if orig is None or price is None:
                continue
            key = sku or name
            if key in seen:
                continue
            seen.add(key)
            out.append({"sku": sku, "name": _unesc(name), "brand": None, "orig": orig, "price": price})
        if out:
            break
    return ("rx" if out else "none"), out


def is_nike(name, brand=None):
    n = ((brand or "") + " " + (name or "")).lower().strip()
    return n.startswith("nike") or n.startswith("jordan")
