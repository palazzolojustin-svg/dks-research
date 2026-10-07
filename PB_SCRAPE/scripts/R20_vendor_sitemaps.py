"""R20_vendor_sitemaps.py
Pull each alt-data vendor's public sitemap(s) (robots.txt -> sitemap index -> child sitemaps) and list URLs whose
slug matches DKS / sporting-goods / private-label / owned-brand keywords.
Rerun: python R20_vendor_sitemaps.py   -> PB_SCRAPE/raw/R20_vendor_sitemap_hits.csv (+ R20_vendor_sitemap_status.csv)
No login, no keys. Polite: 0.5 s between requests, max 60 child sitemaps per vendor.
"""
import requests, re, csv, os, time, gzip, io
from urllib.parse import urljoin

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}
VENDORS = {
    "YipitData": "https://www.yipitdata.com", "Earnest": "https://www.earnestanalytics.com",
    "ConsumerEdge": "https://www.consumer-edge.com", "SecondMeasure": "https://secondmeasure.com",
    "Numerator": "https://www.numerator.com", "Circana": "https://www.circana.com", "Placer": "https://www.placer.ai",
    "MScience": "https://mscience.com", "Edison": "https://trends.edison.tech", "Facteus": "https://www.facteus.com",
    "Cardify": "https://www.cardify.ai", "Similarweb": "https://www.similarweb.com", "Profitero": "https://www.profitero.com",
    "DataWeave": "https://dataweave.com", "Stackline": "https://www.stackline.com", "EDITED": "https://edited.com",
    "Trendalytics": "https://www.trendalytics.co", "Klover": "https://www.klover.ai", "MeasurableAI": "https://www.measurable.ai",
    "Bloomberg2M": "https://www.bloomberg.com", "Coresight": "https://coresight.com", "SocialStandards": "https://www.socialstandards.com",
    "Particl": "https://www.particl.com", "Pattern": "https://pattern.com", "Earnest2": "https://earnestanalytics.com",
    "Bobsled": "https://www.bobsled.co", "Quid": "https://www.quid.com", "CivicScience": "https://civicscience.com",
    "Euromonitor": "https://www.euromonitor.com", "Mintel": "https://www.mintel.com", "Wiser": "https://www.wiser.com",
    "Lumi": "https://www.lumi.com", "Salsify": "https://www.salsify.com", "CommerceIQ": "https://www.commerceiq.ai",
    "Momentum": "https://www.momentumcommerce.com", "Grips": "https://gripsintelligence.com", "Thinknum": "https://www.thinknum.com",
    "Superscript": "https://superscript.com", "Attain": "https://www.attaindata.io", "Affinity": "https://www.affinity.solutions",
    "Bain": "https://www.bain.com", "SportsOneSource": "https://www.sportsonesource.com", "SGB": "https://sgbonline.com",
}
KW = re.compile(r"dick|dks|calia|vrst|maxfli|sporting-good|sportinggood|athleisure|activewear|private-label|private_label|"
                r"privatelabel|store-brand|owned-brand|own-brand|house-of-sport|golf-ball|golf|foot-locker|academy-sports|"
                r"athletic-apparel|sportswear|back-to-school", re.I)


def get(url):
    r = requests.get(url, headers=H, timeout=30)
    c = r.content
    if url.endswith(".gz") or c[:2] == b"\x1f\x8b":
        try:
            c = gzip.decompress(c)
        except Exception:
            pass
    return r.status_code, c.decode("utf-8", "ignore")


def sitemaps_for(base):
    sms = []
    try:
        st, txt = get(base + "/robots.txt")
        sms = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", txt)
    except Exception:
        pass
    if not sms:
        sms = [base + "/sitemap.xml", base + "/sitemap_index.xml"]
    return sms


def crawl(vendor, base, maxchild=12):
    seen, urls, todo, status = set(), [], sitemaps_for(base), []
    n = 0
    while todo and n < maxchild:
        sm = todo.pop(0)
        if sm in seen:
            continue
        seen.add(sm); n += 1
        try:
            st, txt = get(sm)
        except Exception as e:
            status.append((vendor, sm, "ERR " + str(e)[:80])); continue
        status.append((vendor, sm, st))
        if st != 200:
            continue
        locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", txt)
        lastmods = re.findall(r"<url>.*?</url>", txt, re.S)
        if "<sitemapindex" in txt:
            # skip obviously irrelevant child sitemaps (products, images, locales) when huge
            kids = [l for l in locs if not re.search(r"/(de|fr|es|ja|it|pt|zh|ko|nl)[-/_]|image|video", l, re.I)]
            # prioritise blog/resources/insights children
            kids.sort(key=lambda l: 0 if re.search(r"blog|post|resource|insight|news|article|press|report|data", l, re.I) else 1)
            todo.extend(kids)
        else:
            for blk in lastmods or []:
                loc = re.search(r"<loc>\s*(.*?)\s*</loc>", blk)
                lm = re.search(r"<lastmod>\s*(.*?)\s*</lastmod>", blk)
                if loc:
                    urls.append((loc.group(1), lm.group(1)[:10] if lm else ""))
            if not lastmods:
                urls += [(l, "") for l in locs]
        time.sleep(0.5)
    return urls, status


if __name__ == "__main__":
    raw = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
    hits, stat = [], []
    import sys
    only = sys.argv[1:] or list(VENDORS)
    for v in only:
        urls, status = crawl(v, VENDORS[v])
        stat += [(v, s, c, len(urls)) for (_, s, c) in status]
        h = [(v, u, lm) for (u, lm) in urls if KW.search(u)]
        hits += h
        print(f"{v:15s} urls={len(urls):6d} hits={len(h):4d} sitemaps={len(status)}")
    with open(os.path.join(raw, "R20_vendor_sitemap_hits.csv"), "a" if len(only) < len(VENDORS) else "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([("vendor", "url", "lastmod")] + hits if len(only) == len(VENDORS) else hits)
    with open(os.path.join(raw, "R20_vendor_sitemap_status.csv"), "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(stat)

