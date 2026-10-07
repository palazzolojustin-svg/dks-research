"""X11 step 6: realized price gap & new-SKU share, Aug+Sep 2025 vs Aug+Sep 2026 (appends to X11_yoy_summary.txt).
Rerun: python X11_cc_gap.py"""
import json,os,statistics as st,collections,datetime
CC=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","raw","X11_cc"); RAW=os.path.join(CC,"..")
def f(x):
    try: return float(x)
    except: return None
def owned(r): return bool(r.get("vb")) and "Vertical Brand" in r["vb"]
def onsale(r): return bool(f(r["list"]) and f(r["offer"]) is not None and f(r["offer"])<f(r["list"])-0.005)
def prods(cids):
    out={}
    for c in cids:
        for l in open(os.path.join(CC,c+"_products.jsonl"),encoding="utf-8"):
            r=json.loads(l)
            if r["pp"] and r["pp"] not in out and f(r["list"]): out[r["pp"]]=r
    return out
A=prods(["CC-MAIN-2025-33","CC-MAIN-2025-38"]); B=prods(["CC-MAIN-2026-34","CC-MAIN-2026-39"])
lines=["","=== (e) realized price gap by product type: median OFFER owned vs national (Aug+Sep pooled)"]
TYPES=[("Pants","Women's"),("Pants","Men's"),("Shorts","Women's"),("Shorts","Men's"),("Shirts","Women's"),("Shirts","Men's"),("Sweatshirts","Women's"),("Sweatshirts","Men's"),("Jackets","Women's"),("Jackets","Men's"),("Sports Bras","Women's"),("Golf Balls",None)]
for t,g in TYPES:
    row=[]
    for lab,D in (("2025",A),("2026",B)):
        sel=[r for r in D.values() if r.get("ptype") and t in r["ptype"] and (g is None or (r.get("gender") and g in r["gender"]))]
        o=[f(r["offer"]) for r in sel if owned(r) and f(r["offer"])]; n=[f(r["offer"]) for r in sel if not owned(r) and f(r["offer"])]
        ol=[f(r["list"]) for r in sel if owned(r)]; nl=[f(r["list"]) for r in sel if not owned(r)]
        if len(o)>=8 and len(n)>=8:
            row.append(f"{lab}: owned med offer ${st.median(o):.2f} (list ${st.median(ol):.2f}, n={len(o)}) vs nat ${st.median(n):.2f} (list ${st.median(nl):.2f}, n={len(n)}) -> owned/nat {st.median(o)/st.median(n):.0%}")
        else: row.append(f"{lab}: n too small ({len(o)},{len(n)})")
    lines.append(f"{t} {g or 'all'} | "+" | ".join(row))
lines.append("")
lines.append("=== (f) new-SKU share: products whose dsgProductSortDate falls in the 6 months before the crawl window")
for lab,D,lo,hi in (("2025",A,"2025-02","2025-09"),("2026",B,"2026-02","2026-09")):
    o=n=0
    for r in D.values():
        sd=r.get("sortdate") or ""
        if len(sd)==10:
            ym=sd[6:10]+"-"+sd[0:2]
            if lo<=ym<hi:
                if owned(r): o+=1
                else: n+=1
    tot_o=sum(map(owned,D.values())); tot=len(D)
    lines.append(f"{lab}: new SKUs (sortdate {lo}..{hi} excl) owned={o} national={n} owned share of new={o/(o+n):.1%}; owned share of all sampled={tot_o/tot:.1%}; new as % of owned sampled={o/tot_o:.1%} vs national {n/(tot-tot_o):.1%}")
txt="\n".join(lines); print(txt)
open(os.path.join(RAW,"X11_yoy_summary.txt"),"a",encoding="utf-8").write(txt+"\n")
