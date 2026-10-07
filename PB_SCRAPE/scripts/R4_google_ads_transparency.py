"""R4: Google Ads Transparency Center creative census for DICK'S Sporting Goods (and related advertisers).

What it does
  1. Pages through ALL creatives that the public Ads Transparency Center (adstransparency.google.com,
     no login) lists for an advertiser ID, region = United States (2840), via the same public RPC the
     web page calls (SearchService/SearchCreatives). Checkpoints every page to CSV (resumable).
  2. One row per creative: advertiser, creative id, format (1=image, 2=text/shopping, 3=video),
     first_shown, last_shown (UTC dates), field-13 (days shown), preview URL / image HTML.

If Google answers HTTP 429 ("unusual traffic" CAPTCHA page) the script does NOT try to solve or evade it;
it sleeps (default 5 min) and retries, up to --max-wait minutes, then exits with what it has.

Rerun weekly:
  python PB_SCRAPE\\scripts\\R4_google_ads_transparency.py DKS_main
  -> PB_SCRAPE\\raw\\R4_gatc_creatives_<NAME>.csv
Then:  python PB_SCRAPE\\scripts\\R4_gatc_classify.py   (product titles for Shopping creatives, owned-brand tags)
       python PB_SCRAPE\\scripts\\R4_gatc_analyze.py    (monthly counts / owned share)
"""
import csv, json, sys, time, datetime as dt, pathlib, requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
ADVERTISERS = {
    "DKS_main": "AR03402856546571386881",   # Dick's Sporting Goods, Inc (10k-20k creatives)
    "DKS_alt": "AR02597527784611905537",    # DICK'S SPORTING GOODS, INC. (17)
    "GolfGalaxy": "AR09212145138371919873", # Golf Galaxy (1)
    "GG_GolfWorks": "AR06240163481916538881", # Golf Galaxy GolfWorks Inc (100-200)
}
URL = "https://adstransparency.google.com/anji/_/rpc/SearchService/SearchCreatives?authuser=0"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
     "Content-Type": "application/x-www-form-urlencoded", "Origin": "https://adstransparency.google.com",
     "Referer": "https://adstransparency.google.com/"}
FIELDS = ["advertiser", "advertiser_id", "creative_id", "format", "first_shown", "last_shown", "days_shown", "preview_url", "img_html"]
MAX_WAIT_MIN = 120
PAGE_SLEEP = 2.5


def ts(d):
    if not d:
        return ""
    return dt.datetime.fromtimestamp(int(d.get("1", 0)), dt.timezone.utc).strftime("%Y-%m-%d")


def post(s, req):
    waited = 0
    while True:
        try:
            r = s.post(URL, data={"f.req": json.dumps(req)}, timeout=60)
            if r.status_code == 200:
                return r.json()
            print("HTTP", r.status_code, "- waiting 300s (total waited %d min)" % waited, flush=True)
        except Exception as e:
            print("err", e, flush=True)
        if waited >= MAX_WAIT_MIN:
            return None
        time.sleep(300); waited += 5


def pull(name, arid, page_size=100, region=2840):
    s = requests.Session(); s.headers.update(H)
    out = RAW / f"R4_gatc_creatives_{name}.csv"
    state = RAW / f"R4_gatc_state_{name}.json"
    token, n = None, 0
    if state.exists():
        st = json.loads(state.read_text()); token, n = st.get("token"), st.get("n", 0)
        if st.get("done"):
            print(name, "already complete; delete", state, "to re-pull"); return
    else:
        with open(out, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()
    while True:
        req = {"2": page_size, "3": {"12": {"1": "", "2": True}, "13": {"1": [arid]}}, "7": {"1": 1, "2": 0, "3": region}}
        if token:
            req["4"] = token
        j = post(s, req)
        if j is None:
            print("gave up (blocked); resumable via", state); return
        rows = []
        for c in j.get("1", []):
            content = c.get("3", {})
            rows.append({"advertiser": name, "advertiser_id": c.get("1"), "creative_id": c.get("2"), "format": c.get("4"),
                         "first_shown": ts(c.get("6")), "last_shown": ts(c.get("7")), "days_shown": c.get("13", ""),
                         "preview_url": content.get("1", {}).get("4", ""), "img_html": content.get("3", {}).get("2", "")})
        with open(out, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writerows(rows)
        n += len(rows)
        token = j.get("2")
        done = not token or not j.get("1")
        state.write_text(json.dumps({"token": token, "n": n, "done": done, "range": [j.get("4"), j.get("5")]}))
        print(name, "rows", n, "range", j.get("4"), j.get("5"), flush=True)
        if done:
            break
        time.sleep(PAGE_SLEEP)
    print(name, "total", n, "->", out)


if __name__ == "__main__":
    names = sys.argv[1:] or list(ADVERTISERS)
    for nm in names:
        pull(nm, ADVERTISERS[nm])
