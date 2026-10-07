"""X11 step 5: y/y comparisons, Aug/Sep 2025 vs Aug/Sep 2026 Common Crawl captures.
Rerun: python X11_cc_lfl.py
(a) Pooled Aug+Sep 2025 (CC-MAIN-2025-33 + 2025-38) vs Aug+Sep 2026 (CC-MAIN-2026-34 + 2026-39):
    on-sale share and mean discount owned vs national, overall and within matched categories.
(b) Like-for-like products (same parent part number in both periods): change in list price and
    offer price, owned vs national.
(c) Brand-facet panel: same category URL captured in both periods -> owned share of SKU count.
(d) Brand landing pages captured in both periods -> Sale facet share.
Writes PB_SCRAPE/raw/X11_yoy_summary.txt
"""
import json, os, statistics as st, collections, io, contextlib

CC = os.path.join(os.path.dirname(__file__), "..", "raw", "X11_cc")
RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
P25 = ["CC-MAIN-2025-33", "CC-MAIN-2025-38"]
P26 = ["CC-MAIN-2026-34", "CC-MAIN-2026-39"]
OWN_FACET = {"CALIA", "DSG", "VRST", "Maxfli", "Walter Hagen", "Top Flite", "Tommy Armour Golf", "Tommy Armour",
             "Alpine Design", "ETHOS", "Fitness Gear", "Nishiki", "Quest", "P-TEX", "DBX", "Northeast Outfitters",
             "DICK'S Sporting Goods", "PRIMED", "TourTrek", "Jawbone"}


def f(x):
    try:
        return float(x)
    except Exception:
        return None


def owned(r):
    return bool(r.get("vb")) and "Vertical Brand" in r["vb"]


def onsale(r):
    return bool(f(r["list"]) and f(r["offer"]) is not None and f(r["offer"]) < f(r["list"]) - 0.005)


def disc(r):
    return 1 - f(r["offer"]) / f(r["list"]) if onsale(r) else 0.0


def prods(cids):
    out = {}
    for c in cids:
        p = os.path.join(CC, c + "_products.jsonl")
        for l in open(p, encoding="utf-8"):
            r = json.loads(l)
            if r["pp"] and r["pp"] not in out and f(r["list"]):
                out[r["pp"]] = r
    return out


def pages(cids):
    out = {}
    for c in cids:
        for l in open(os.path.join(CC, c + "_pages.jsonl"), encoding="utf-8"):
            g = json.loads(l)
            out.setdefault(g["url"].lower(), g)
    return out


def summ(rs):
    if not rs:
        return "n=0"
    s = sum(map(onsale, rs)) / len(rs)
    d = st.mean(disc(r) for r in rs)
    return f"n={len(rs)} on_sale={s:.1%} avg_disc_all={d:.1%}"


buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    a, b = prods(P25), prods(P26)
    print("=== (a) pooled Aug+Sep 2025 vs Aug+Sep 2026")
    for lab, fn in (("OWNED", owned), ("NATIONAL", lambda r: not owned(r))):
        print(lab, "2025:", summ([r for r in a.values() if fn(r)]), "| 2026:", summ([r for r in b.values() if fn(r)]))
    print("owned share of unique products in sample: 2025 %.1f%% | 2026 %.1f%%" % (
        100 * sum(map(owned, a.values())) / len(a), 100 * sum(map(owned, b.values())) / len(b)))
    # matched categories
    for lab, dset in (("2025", a), ("2026", b)):
        bycat = collections.defaultdict(lambda: [[], []])
        for r in dset.values():
            if r["cat"]:
                bycat[r["cat"]][0 if owned(r) else 1].append(r)
        w = so = sn = do = dn = 0
        for cat, (o, n) in bycat.items():
            if len(o) >= 5 and len(n) >= 5:
                k = len(o); w += k
                so += k * sum(map(onsale, o)) / len(o); sn += k * sum(map(onsale, n)) / len(n)
                do += k * st.mean(map(disc, o)); dn += k * st.mean(map(disc, n))
        print(f"matched-category {lab}: owned-weight={w} owned on_sale={so/w:.1%} nat on_sale={sn/w:.1%} owned avg_disc={do/w:.1%} nat avg_disc={dn/w:.1%}")
    # per brand
    print("--- per brand on-sale share 2025 -> 2026 (n)")
    for br in ["CALIA", "DSG", "VRST", "Maxfli", "Walter Hagen", "Alpine Design", "ETHOS", "Fitness Gear", "Nishiki", "Quest", "Top Flite",
               "Nike", "Under Armour", "adidas", "Jordan", "New Balance", "The North Face", "Columbia", "Titleist", "Callaway", "TaylorMade", "PUMA", "Vuori"]:
        x = [r for r in a.values() if r["brand"] == br]; y = [r for r in b.values() if r["brand"] == br]
        if len(x) >= 15 and len(y) >= 15:
            mo = lambda z: st.median([f(r["offer"]) for r in z if f(r["offer"])])
            print(f"{br:15s} on_sale {sum(map(onsale,x))/len(x):.1%} -> {sum(map(onsale,y))/len(y):.1%} | avg_disc {st.mean(map(disc,x)):.1%} -> {st.mean(map(disc,y)):.1%} | median offer ${mo(x):.2f} -> ${mo(y):.2f} | n {len(x)} -> {len(y)}")
    # (b) like for like
    print("=== (b) like-for-like products present in both periods")
    for lab, fn in (("OWNED", owned), ("NATIONAL", lambda r: not owned(r))):
        common = [k for k in a if k in b and fn(a[k])]
        if not common:
            continue
        lch = [f(b[k]["list"]) / f(a[k]["list"]) - 1 for k in common if f(a[k]["list"]) and f(b[k]["list"])]
        och = [f(b[k]["offer"]) / f(a[k]["offer"]) - 1 for k in common if f(a[k]["offer"]) and f(b[k]["offer"])]
        s25 = sum(onsale(a[k]) for k in common) / len(common); s26 = sum(onsale(b[k]) for k in common) / len(common)
        print(f"{lab}: n={len(common)} mean list chg={st.mean(lch):+.1%} (median {st.median(lch):+.1%}); mean offer chg={st.mean(och):+.1%} (median {st.median(och):+.1%}); on_sale {s25:.1%} -> {s26:.1%}")
    # (c) brand facet panel
    print("=== (c) brand-facet panel: same category URL in both periods")
    pa, pb = pages(P25), pages(P26)
    tot = [0, 0, 0, 0]; n = 0; rows = []
    for u in pa:
        if u in pb:
            fa = ((pa[u].get("facets") or {}).get("Brand") or {}).get("vals"); fb = ((pb[u].get("facets") or {}).get("Brand") or {}).get("vals")
            if fa and fb and len(fa) >= 5 and len(fb) >= 5:
                oa = sum(v for k, v in fa.items() if k in OWN_FACET); ob = sum(v for k, v in fb.items() if k in OWN_FACET)
                ta = sum(fa.values()); tb = sum(fb.values())
                tot[0] += oa; tot[1] += ta; tot[2] += ob; tot[3] += tb; n += 1
                rows.append((u.split("/f/")[-1], oa, ta, ob, tb))
    if n:
        print(f"pages={n} owned SKU share 2025={tot[0]/tot[1]:.2%} ({tot[0]}/{tot[1]}) 2026={tot[2]/tot[3]:.2%} ({tot[2]}/{tot[3]})")
        up = sum(1 for r in rows if r[3] / r[4] > r[1] / r[2] + 0.001); dn = sum(1 for r in rows if r[3] / r[4] < r[1] / r[2] - 0.001)
        print(f"pages where owned share rose={up} fell={dn} flat={n-up-dn}")
        for r in sorted(rows, key=lambda r: -r[4])[:40]:
            print(f"  {r[0][:60]:60s} owned {r[1]}/{r[2]} ({r[1]/r[2]:.1%}) -> {r[3]}/{r[4]} ({r[3]/r[4]:.1%})")
    # (d) sale facet on same URL
    print("=== (d) Sale-facet share, same URL both periods, owned-brand pages vs others")
    for lab, test in (("owned-brand pages", lambda u: any(("/f/" + s) in u for s in ["calia", "dsg-", "vrst", "maxfli", "walter-hagen", "alpine-design", "ethos", "fitness-gear", "nishiki", "top-flite"])),
                      ("nike/ua/adidas pages", lambda u: any(("/f/" + s) in u or ("-" + s + "-") in u for s in ["nike", "under-armour", "adidas"])),
                      ("all matched pages", lambda u: True)):
        sa = ta = sb = tb = k = 0
        for u in pa:
            if u in pb and test(u) and pa[u].get("totalCount") and pb[u].get("totalCount"):
                sa += pa[u].get("sale_count") or 0; ta += pa[u]["totalCount"]; sb += pb[u].get("sale_count") or 0; tb += pb[u]["totalCount"]; k += 1
        if k:
            print(f"{lab}: pages={k} sale share 2025={sa/ta:.1%} ({sa}/{ta}) 2026={sb/tb:.1%} ({sb}/{tb})")
txt = buf.getvalue()
print(txt)
open(os.path.join(RAW, "X11_yoy_summary.txt"), "w", encoding="utf-8").write(txt)
