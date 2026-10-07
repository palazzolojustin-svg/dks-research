"""R4: snapshot iSpot.tv public 30-day brand scorecards (Total Creatives, National Airings, Spend Rank,
Airing Rank) for DKS-family brands and comparators. Appends to PB_SCRAPE\\raw\\R4_ispot_brandstats_timeseries.csv
with the snapshot date and iSpot's stated data window, so running it weekly builds a time series.

Run weekly:  python PB_SCRAPE\\scripts\\R4_ispot_brandstats.py
Brand paths can be resolved from any ad page (breadcrumb). Add brands to BRANDS as needed.
"""
import csv, re, time, datetime as dt, pathlib, requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "raw" / "R4_ispot_brandstats_timeseries.csv"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
BRANDS = {  # label: brand path or an ad path to resolve the brand from
    "DICKS_master": "/brands/79N/dicks-sporting-goods", "VRST": "/brands/5S8/vrst", "CALIA": "/brands/nkO/calia",
    "Maxfli": "/brands/IBQ/maxfli", "Golf_Galaxy": "/brands/IGj/golf-galaxy",
    "Academy": "/brands/ImB/academy-sports-outdoors", "Bass_Pro": "/brands/dQh/bass-pro-shops",
    "Vuori": "/ad/qVwH/vuori-beach-vibes",
}
EXTRA = {}


def resolve(s, p):
    if p.startswith("/brands/"):
        return p
    t = s.get("https://www.ispot.tv" + p, timeout=40).text
    crumbs = re.findall(r'"item":\s*"https://www.ispot.tv(/brands/[^"]+)"', t)
    return crumbs[-1] if crumbs else None


def stats(s, bp):
    t = s.get("https://www.ispot.tv" + bp, timeout=40).text
    st = dict(re.findall(r'flex-grow-1">\s*([A-Za-z .]+?)\s*</div>\s*<div class="text-success overview-stat[^"]*">\s*([^<]+?)\s*</div>', t))
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))
    m = re.search(r"Data available through (\d\d/\d\d/\d{4}) (\d\d/\d\d/\d{4}) (\d\d/\d\d/\d{4})", txt)
    return st, (m.groups() if m else ("", "", ""))


def main():
    s = requests.Session(); s.headers.update(H)
    today = dt.date.today().isoformat()
    new = not OUT.exists()
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["snapshot_date", "label", "brand_path", "data_through", "window_start", "window_end",
                        "total_creatives", "national_airings_30d", "spend_rank", "airing_rank"])
        for label, p in {**BRANDS, **EXTRA}.items():
            bp = resolve(s, p); time.sleep(1)
            if not bp:
                print("no brand for", label); continue
            st, win = stats(s, bp); time.sleep(1)
            row = [today, label, bp, *win, st.get("Total Creatives", ""), st.get("National Airings", ""),
                   st.get("Spend Rank", ""), st.get("Airing Rank", "")]
            w.writerow(row); print(row)


if __name__ == "__main__":
    main()
