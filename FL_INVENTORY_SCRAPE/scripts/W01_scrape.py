# Full footlocker.com catalog pagination by productType slice; saves raw product JSON per page.
import json, os, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
import W01_fetch as F, random
def enc(q):
    # random percent-encoding of letters to defeat CDN cache key that ignores currentPage
    out=[]
    for ch in q:
        if ch==":": out.append(random.choice(["%3A","%3a"]))
        elif ch.isalpha() and random.random()<0.5: out.append("%%%02X"%ord(ch) if random.random()<0.5 else "%%%02x"%ord(ch))
        elif ch=="'": out.append("%27")
        elif ch==" ": out.append("%20")
        else: out.append(ch)
    return "".join(out)
OUT = "/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W01/pages"
os.makedirs(OUT, exist_ok=True)
slices = sys.argv[1:] or ["Shoes", "Clothing", "Accessories"]
for pt in slices:
    q = ":relevance:productType:" + pt
    page = 0; total_pages = None
    while True:
        fn = f"{OUT}/{pt}_{page:03d}.json"
        if os.path.exists(fn):
            d = json.load(open(fn))
        else:
            url = "https://www.footlocker.com/search?query=" + enc(q) + f"&currentPage={page}"
            h = F.get_html(url)
            st = F.hydration(h) if h else None
            s = st.get('search') if st else None
            if s and s.get('pagination',{}).get('currentPage') != page:
                print("mismatch-retry", pt, page, flush=True)
                h = F.get_html("https://www.footlocker.com/search?query=" + enc(q) + f"&currentPage={page}")
                st = F.hydration(h) if h else None
                s = st.get('search') if st else None
                if s and s['pagination']['currentPage'] != page: s = None
            if not s or 'pagination' not in s:
                print("fail", pt, page, flush=True); time.sleep(10); continue
            d = {"pagination": s['pagination'], "products": s['products'], "fetched": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
            if page == 0: d["facets"] = s.get('facets')
            json.dump(d, open(fn, "w"))
            time.sleep(1.0)
        total_pages = d['pagination']['totalPages']
        if d['pagination']['currentPage'] != page:
            print("page mismatch", pt, page, d['pagination']['currentPage'], flush=True)
        print(pt, page, total_pages, len(d['products']), flush=True)
        page += 1
        if page >= total_pages or not d['products']: break
