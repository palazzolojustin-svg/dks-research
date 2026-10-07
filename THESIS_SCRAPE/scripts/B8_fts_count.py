"""B8: count EDGAR FTS hits for candidate CMBS queries. Rerun: python B8_fts_count.py"""
import requests, time, json
H = {"User-Agent": "IndependentResearch research-script palazzolojustin@gmail.com"}
qs = ['"Dick\'s Sporting Goods" "occupancy cost"', '"Dick\'s" "occupancy cost"', '"Dick\'s" "sales PSF"',
      '"Dick\'s Sporting Goods" "sales per square foot"', '"Golf Galaxy" "occupancy cost"', '"House of Sport" "sales"',
      '"Dick\'s" "Field House"', '"Dick\'s" "TTM" "sales"', '"Dicks Sporting Goods" "occupancy cost"', '"DSG" "occupancy cost"']
for q in qs:
    for (s,e) in [("2019-01-01","2022-12-31"),("2023-01-01","2026-10-07")]:
        r = requests.get("https://efts.sec.gov/LATEST/search-index", params={"q": q, "dateRange": "custom", "startdt": s, "enddt": e, "forms":"FWP,424B2,424H,424B5,424B3"}, headers=H, timeout=60)
        d = r.json()
        print(q, s[:4], e[:4], d.get("hits",{}).get("total",{}).get("value"), flush=True)
        time.sleep(0.3)
