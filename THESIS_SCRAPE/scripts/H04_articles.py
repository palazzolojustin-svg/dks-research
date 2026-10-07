"""H04: fetch a list of press/CRE articles about landlord-announced HoS deals; save text; print key sentences.

Rerun: python H04_articles.py   (URL list inline; output raw/H04_art_<n>.txt and stdout)
"""
import re
import time
import requests
from bs4 import BeautifulSoup

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
URLS = [
    "https://shoppingcenterbusiness.com/simon-signs-two-leases-with-dicks-sporting-goods-in-metro-boston/",
    "https://www.nbcphiladelphia.com/entertainment/the-scene/dicks-house-of-sport-king-of-prussia-mall-2027/4297514/?amp=1",
    "https://digital-release.ozarksfirst.com/news/mall-provides-dicks-sporting-goods-opening-detail/amp/",
    "https://digital-release.cbs17.com/news/local-news/wake-county-news/abandoned-sears-at-crabtree-valley-mall-slated-to-become-dicks-house-of-sport/amp/",
    "https://hoodline.com/2026/10/dick-s-house-of-sport-set-to-open-at-crabtree-mall-with-bryce-young-climbing-wall/",
    "https://talkbusiness.net/2026/04/dicks-house-of-sport-to-anchor-37-acre-concord-commons-project-in-lowell/",
    "https://www.foxessellfaster.com/blog/dicks-house-of-sport-is-taking-over-196000-square-feet-at-tysons-corner-center/",
    "https://northernvirginiamag.com/style/shopping/2026/05/18/dicks-plans-to-replace-jcpenney-at-springfield-town-center/",
    "https://archive.triblive.com/local/westmoreland/dicks-to-bring-house-of-sport-concept-to-westmoreland-mall/",
    "https://coloradobiz.com/flatiron-crossing-dicks-house-of-sport-new-retailers/",
    "https://secure.businesswire.com/news/home/20260701843922/en/CBL-Properties-Announces-DICKS-House-of-Sport-to-Join-CoolSprings-Galleria-in-Nashville-Tennessee",
    "https://hoodline.com/2026/07/arlington-s-new-dick-s-house-of-sport-takes-over-old-sears/",
    "https://finance.yahoo.com/sectors/technology/articles/dicks-house-sport-construction-underway-103408364.html",
    "https://www.ffxnow.com/2026/02/25/dicks-house-of-sport-coming-to-tysons-corner-center/",
    "https://shoppingcenterbusiness.com/dicks-house-of-sport-to-anchor-cherry-hill-mall-in-new-jersey/",
    "https://www.costar.com/article/1744599581/mall-owner-macerich-sees-robust-leasing-as-it-looks-for-new-kinds-of-tenants",
    "https://commercialobserver.com/2026/03/us-mall-traffic-growth-february-placerai/",
    "https://www.tradeandindustrydev.com/region/new-jersey/news/nj-dicks-house-sport-open-120000-sq-ft-retail-34455",
    "https://sgbonline.com/dicks-sg-to-open-house-of-sports-in-miami/",
    "https://www.arlingtontx.gov/News-Articles/2023/July/Parks-Mall-at-Arlington-Set-to-Open-Dick's-House-of-Sport-as-Part-of-Multi-Phase-Redevelopment-Plan",
]
KEY = re.compile(r"House of Sport|square|sq\.? ?ft|open|traffic|percent|%|\$|lease|rent|anchor|landlord|Simon|Brookfield|CBL|Macerich|said", re.I)

for i, u in enumerate(URLS):
    try:
        r = requests.get(u, headers=UA, timeout=40)
    except Exception as e:
        print("#####", i, u, "ERR", type(e).__name__)
        continue
    soup = BeautifulSoup(r.text, "html.parser")
    for t in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        t.decompose()
    ps = [p.get_text(" ", strip=True) for p in soup.find_all(["p", "h1", "h2", "li"])]
    ps = [p for p in ps if len(p) > 50]
    open(f"{RAW}\\H04_art_{i:02d}.txt", "w", encoding="utf-8").write(u + "\n" + "\n".join(ps))
    print("#####", i, r.status_code, u)
    for p in ps:
        if re.search(r"House of Sport|Dick", p, re.I) and KEY.search(p):
            print("  -", p[:700])
    time.sleep(1)
