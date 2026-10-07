"""W04 parser for Foot Locker EU/AU listing pages (window.footlocker.STATE_FROM_SERVER)."""
import re, json

def extract_state(html):
    i = html.find('STATE_FROM_SERVER:')
    if i < 0:
        return None
    s = html[i+len('STATE_FROM_SERVER:'):].lstrip()
    try:
        obj, _ = json.JSONDecoder().raw_decode(s)
        return obj
    except Exception:
        return None

def find_search(obj):
    """return dict containing pagination/products/facets"""
    best = None
    def walk(o, depth=0):
        nonlocal best
        if depth > 8: return
        if isinstance(o, dict):
            if 'pagination' in o and 'products' in o and isinstance(o.get('pagination'), dict) and o['pagination'].get('totalResults') is not None:
                if best is None: best = o
            for v in o.values(): walk(v, depth+1)
        elif isinstance(o, list):
            for v in o[:50]: walk(v, depth+1)
    walk(obj)
    return best

def facets(search):
    out = {}
    for f in search.get('facets', []) or []:
        out[f.get('code') or f.get('name')] = {v['name']: v.get('count') for v in f.get('values', [])}
    return out

def products(search):
    rows = []
    for p in search.get('products', []) or []:
        op = (p.get('originalPrice') or {}).get('value')
        pr = (p.get('price') or {}).get('value')
        b = p.get('badges') or {}
        nad = None
        for v in p.get('variantOptions') or []:
            if v.get('sku') == p.get('sku'):
                nad = v.get('newArrivalDate')
        rows.append(dict(sku=p.get('sku'), base=p.get('baseProduct'), name=p.get('name'), orig=op, price=pr,
                         isSale=b.get('isSale'), isNew=b.get('isNewProduct'), newArrivalDate=nad,
                         reviews=(p.get('reviewRatings') or {}).get('reviews'), nvar=len(p.get('variantOptions') or [])))
    return rows
