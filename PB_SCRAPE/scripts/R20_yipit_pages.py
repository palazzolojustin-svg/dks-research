"""R20_yipit_pages.py - fetch YipitData resource pages and print the public article/teaser body (between the page title
and 'Share this page'/'Your next decision'), flagging DKS / private-label / owned-brand mentions.
Usage: python R20_yipit_pages.py <url> [<url> ...]     (or no args = default list of sporting/apparel pages)
"""
import sys, re
sys.path.insert(0, __file__.rsplit("\\", 1)[0])
from R20_fetch import fetch, text_of
DEFAULT = """july-2026-apparel-monthly-recap-category-shifts-and-brand-movement
corporate-athleisure-apparel-market-trends-2026-report
corporate-girls-apparel-market-trends-private-label-growth
corporate-may-2026-apparel-monthly-recap
june-2026-apparel-market-recap-footwear-athletic-wear-fashion-trends
investor-webcast-20240304-4q-sports-goods-retailer-webcast
corporate-super-bowl-apparel-report
corporate-category-quick-hits-toys-electronics-footwear
corporate-footwear-market-trends-channel-share-consumer-spend
corporate-footwear-report
corporate-clothing-and-footwear-report
workwear-market-report-apparel-and-footwear-sales-data-by-brand-and-retailer
adidas-world-cup-2026-soccer-apparel-sales-trends-article
corporate-footwear-market-trends-running-growth
3trends-revolutionizing-retail
investor-webcast-20240626-lulu""".split()
FLAG = re.compile(r"Dick'?s|DICK'?S|Academy|private[- ]label|owned brand|exclusive|CALIA|VRST|DSG|Golf Galaxy", re.I)
urls = sys.argv[1:] or ["https://www.yipitdata.com/resources/" + s for s in DEFAULT]
import time
for u in urls:
    r = None
    for k in range(4):
        try:
            r = fetch(u); break
        except Exception as e:
            print("retry", k, u, e); time.sleep(10 * (k + 1))
    if r is None:
        continue
    time.sleep(3)
    t = text_of(r.text)
    # body = after the last "Investor Corporations Terms of Service Privacy Policy" nav block
    i = t.rfind("Privacy Policy", 0, t.find("Share this page") if "Share this page" in t else len(t))
    j = t.find("Your next decision", i)
    body = t[i + 14:j if j > 0 else i + 5000]
    hits = sorted({m.group(0) for m in FLAG.finditer(body)})
    print("=" * 100); print(r.status_code, u); print("FLAGS:", hits); print(body[:3500])
