"""Summarize W04 live census JSONs into CSVs: country-level and brand-level sale share & discount depth."""
import sys, os, json, gzip, glob, csv
MID = {"60% and above":65, "50% - 60%":55, "40% - 50%":45, "30% - 40%":35, "20% - 30%":25, "Up to 20%":10}

def depth(f):
    po = (f or {}).get("percentOffListPrice", {}) or {}
    # map labels by position of numbers since languages differ
    n = 0; w = 0
    for lab, c in po.items():
        key = None
        digits = [int(x) for x in __import__("re").findall(r"\d+", lab)]
        if len(digits) >= 2: key = (digits[0]+digits[1])/2
        elif digits and digits[0] == 60: key = 65
        elif digits and digits[0] == 20: key = 10
        elif digits: key = digits[0]
        if key is None: continue
        n += c; w += c*key
    return n, (w/n if n else None), po

def misc(f, word_list):
    m = (f or {}).get("miscellaneous", {}) or {}
    return m

def main(d, outprefix):
    rows = []; brows = []
    for fn in sorted(glob.glob(os.path.join(d, "*.json.gz"))):
        dom = os.path.basename(fn).replace(".json.gz", "")
        R = json.load(gzip.open(fn, "rt"))
        def tot(k): 
            p = (R.get(k) or {}).get("pagination") or {}
            return p.get("totalResults")
        A = R["all"]["facets"]
        n_po, avg_disc, po = depth(A)
        rec = dict(site=dom, fetched=R.get("_fetched"), total=tot("all"), sale=tot("sale"), sale_share=None, n_pctoff=n_po, avg_disc_of_sale=avg_disc,
                   deep40plus=sum(c for l,c in po.items() if any(x in l for x in ["40","50","60"]) and not l.startswith("30")),
                   new=tot("new"), new_sale=tot("new_sale"), shoes=tot("shoes"), clothing=tot("clothing"), flonly=tot("flonly"))
        if rec["total"] and rec["sale"] is not None: rec["sale_share"] = rec["sale"]/rec["total"]
        for k in ["shoes","clothing","new","flonly"]:
            f = (R.get(k) or {}).get("facets")
            n, a, _ = depth(f)
            rec[k+"_pctoff_n"] = n; rec[k+"_avgdisc"] = a
        rec["deep40plus_share_of_sale"] = rec["deep40plus"]/n_po if n_po else None
        rows.append(rec)
        bf = A.get("brand", {})
        for k, v in R.items():
            if not k.startswith("brand:"): continue
            b = k[6:]; f = v.get("facets"); n, a, _ = depth(f)
            t = (v.get("pagination") or {}).get("totalResults")
            brows.append(dict(site=dom, brand=b, total=t, share_of_catalog=(t/rec["total"] if t and rec["total"] else None), on_sale_pctoff=n, sale_share=(n/t if t else None), avg_disc_of_sale=a))
    with open(outprefix+"_country.csv","w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with open(outprefix+"_brand.csv","w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(brows[0].keys())); w.writeheader(); w.writerows(brows)
    return rows, brows

if __name__ == "__main__":
    rows, brows = main(sys.argv[1], sys.argv[2])
    for r in rows: print({k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items()})
