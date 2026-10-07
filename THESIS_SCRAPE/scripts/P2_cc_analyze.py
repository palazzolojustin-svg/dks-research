"""P2_cc_analyze.py: analyze Common Crawl DKS price samples.
  pair <file>   : same-SKU (catentry) like-for-like list & offer price change between the two crawls in a P2_ccpair_*.csv
  xsec <files..>: promo depth per crawl (share of SKUs marked down, avg discount, clearance share, avg list/offer) by category
Rerun: python P2_cc_analyze.py pair ..\\raw\\P2_ccpair_2025-38_2026-39.csv
       python P2_cc_analyze.py xsec ..\\raw\\P2_ccxsec_2026-39.csv ...
Product-level weighting: each product's SKU stats are averaged first, then products are equally weighted (avoids size-run inflation).
"""
import csv, sys, math, statistics as st
from collections import defaultdict

def f(x):
    try:
        return float(x)
    except Exception:
        return None

def load(fp):
    return [r for r in csv.DictReader(open(fp, encoding='utf-8')) if f(r.get('list')) and f(r.get('offer'))]

def pair(fp, verbose=True):
    rows = load(fp)
    crawls = sorted(set(r['crawl'] for r in rows))
    A, B = crawls[0], crawls[-1]
    by = defaultdict(dict)  # product -> crawl -> catentry -> row
    for r in rows:
        by[r['product']].setdefault(r['crawl'], {})[r['catentry']] = r
    res = []
    for p, d in by.items():
        if A not in d or B not in d:
            continue
        common = set(d[A]) & set(d[B])
        if not common:
            continue
        lr, orr, upl, dnl = [], [], 0, 0
        mdA = mdB = 0
        for c in common:
            a, b = d[A][c], d[B][c]
            la, lb, oa, ob = f(a['list']), f(b['list']), f(a['offer']), f(b['offer'])
            lr.append(math.log(lb / la)); orr.append(math.log(ob / oa))
            mdA += oa < la - 0.005; mdB += ob < lb - 0.005
        r0 = next(iter(d[B].values()))
        res.append(dict(product=p, category=r0['category'], brand=r0['brand'], n=len(common), dlist=sum(lr) / len(lr), doffer=sum(orr) / len(orr),
                        mdA=mdA / len(common), mdB=mdB / len(common), listA=statistics_mean([f(d[A][c]['list']) for c in common]),
                        listB=statistics_mean([f(d[B][c]['list']) for c in common]), slug=r0['slug']))
    if verbose:
        print('pair', A, B, 'products with same-SKU matches:', len(res), 'of', len(by))
        summarize(res)
    return res

def statistics_mean(x):
    return sum(x) / len(x) if x else None

def summarize(res, label='ALL'):
    groups = defaultdict(list)
    for r in res:
        groups['ALL'].append(r); groups[r['category']].append(r)
    print('%-10s %5s %8s %8s %8s %7s %7s %7s %8s %8s' % ('group', 'n', 'dList%', 'medList', 'dOffer%', 'up%', 'flat%', 'down%', 'mdA%', 'mdB%'))
    for g, rs in groups.items():
        dl = [r['dlist'] for r in rs]; do = [r['doffer'] for r in rs]
        up = sum(1 for x in dl if x > 0.001) / len(dl); dn = sum(1 for x in dl if x < -0.001) / len(dl)
        print('%-10s %5d %8.2f %8.2f %8.2f %7.1f %7.1f %7.1f %8.1f %8.1f' % (g, len(rs), 100 * (math.exp(st.mean(dl)) - 1), 100 * (math.exp(st.median(dl)) - 1),
              100 * (math.exp(st.mean(do)) - 1), 100 * up, 100 * (1 - up - dn), 100 * dn, 100 * st.mean(r['mdA'] for r in rs), 100 * st.mean(r['mdB'] for r in rs)))

def xsec(files):
    print('%-9s %-10s %5s %8s %8s %8s %8s %8s %9s' % ('crawl', 'group', 'nprod', 'md%', 'disc%', 'discMD%', 'clr%', 'avgList', 'avgOffer'))
    for fp in files:
        rows = load(fp)
        prod = defaultdict(list)
        for r in rows:
            prod[(r['crawl'], r['product'])].append(r)
        groups = defaultdict(list)
        for (c, p), rs in prod.items():
            L = [f(r['list']) for r in rs]; O = [f(r['offer']) for r in rs]
            md = sum(1 for l, o in zip(L, O) if o < l - 0.005) / len(rs)
            disc = st.mean(1 - o / l for l, o in zip(L, O))
            clr = sum(1 for r in rs if r['clearance'] == 'True') / len(rs)
            rec = dict(md=md, disc=disc, clr=clr, L=st.mean(L), O=st.mean(O), cat=rs[0]['category'], crawl=c)
            groups['ALL'].append(rec); groups[rs[0]['category']].append(rec)
        for g, rs in groups.items():
            mdp = [r for r in rs if r['md'] > 0]
            print('%-9s %-10s %5d %8.1f %8.1f %8.1f %8.1f %8.2f %9.2f' % (rs[0]['crawl'][-7:], g, len(rs), 100 * st.mean(r['md'] for r in rs), 100 * st.mean(r['disc'] for r in rs),
                  100 * (st.mean(r['disc'] for r in mdp) if mdp else 0), 100 * st.mean(r['clr'] for r in rs), st.mean(r['L'] for r in rs), st.mean(r['O'] for r in rs)))

if __name__ == '__main__':
    if sys.argv[1] == 'pair':
        res = pair(sys.argv[2])
        if len(sys.argv) > 3:
            with open(sys.argv[3], 'w', newline='', encoding='utf-8') as fo:
                w = csv.DictWriter(fo, fieldnames=list(res[0].keys())); w.writeheader(); w.writerows(res)
    else:
        xsec(sys.argv[2:])
