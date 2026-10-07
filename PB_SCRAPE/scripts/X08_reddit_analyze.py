"""X08 Analyse PullPush Reddit hits collected by X08_reddit_mentions.py.

Reads PB_SCRAPE/raw/X08_reddit_raw*.jsonl (lines that are not JSON = fetch-log lines, skipped), dedupes by
(kind,id), applies brand-context filters (removes non-apparel 'Calia' noise, bots, u_ profiles,
deal-bot subs), and prints/saves month x brand counts plus benchmark-normalised share.
Fetch completeness per (month, query, kind) is read from the log lines; months with failed fetches are flagged.
Rerun: python X08_reddit_analyze.py   -> PB_SCRAPE/raw/X08_reddit_monthly.csv
"""
import json, glob, os, re, csv, collections

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
CTX = r"legging|bra\b|jogger|short|pant|top|tank|hoodie|jacket|set|athleisure|activewear|workout|gym|yoga|pilates|golf|dick|dsg|lulu|athleta|vuori|old navy|target|fabric|size|fit|wear|cloth|brand|outfit|swim|denim|polo|underwood"
BOTSUBS = {"dickssportingdeals", "golfgalaxydeals", "wow", "warcraftlore", "enderal", "calscursevictims", "erotichypnosis", "calscurse", "projectrunway", "slovenia", "slovenijafire", "croatia", "ljubljana", "gradimo_obnavljamo", "indianbikes", "classicwow", "wowlore", "warcraft"}
NOISE = r"mistress|hypno|chastity|locktober|calscurse|menethil|warcraft|sylvanas|forsaken|arthas|\bwow\b|enderal|lordaeron|undercity|azeroth"
BRANDS = {
    "calia": lambda t: re.search(r"\bcalia\b", t, re.I) and re.search(CTX, t, re.I) and not re.search(NOISE, t, re.I),
    "vrst": lambda t: re.search(r"\bvrst\b", t, re.I) and re.search(CTX + r"|jogger|limitless|commuter|men", t, re.I) and not re.search(r"\b(je|na|za|ali|ki|pa|ni|tudi|kot|sta|ste|smo)\b", t),
    "dsg_apparel": lambda t: re.search(r"\bdsg\b.{0,40}(legging|jogger|short|pant|hoodie|tee|shirt|jacket|bra|apparel|brand|polo|fleece)|(dick'?s|dicks).{0,60}\bdsg\b(?!.{0,20}(gearbox|transmission|clutch))", t, re.I | re.S) and not re.search(r"gearbox|transmission|clutch|vw|audi|golf r|gti|mk7|mk8", t, re.I),
    "maxfli": lambda t: re.search(r"\bmaxfli", t, re.I),
    "vuori": lambda t: re.search(r"\bvuori\b", t, re.I),
    "athleta": lambda t: re.search(r"\bathleta\b", t, re.I),
}
QMAP = {"calia": "calia", "vrst": "vrst", "maxfli": "maxfli", "vuori": "vuori", "athleta": "athleta"}

seen, cnt, status = set(), collections.defaultdict(collections.Counter), collections.defaultdict(set)
subs = collections.defaultdict(collections.Counter)
for fn in glob.glob(os.path.join(RAW, "X08_reddit_raw*.jsonl")) + glob.glob(os.path.join(RAW, "X08_reddit_fetchlog*.csv")):
    for line in open(fn, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if not line.startswith("{"):
            p = line.split(",")
            if len(p) >= 5 and re.match(r"\d{4}-\d{2}$", p[0]):
                status[(p[0], p[1], p[2])].add(p[4])
            continue
        try:
            x = json.loads(line)
        except Exception:
            continue
        key = (x["kind"], x["id"])
        if key in seen:
            continue
        seen.add(key)
        sub = (x.get("sub") or "").lower()
        if sub in BOTSUBS or sub.startswith("u_") or (x.get("author") or "").lower() in ("automoderator",):
            continue
        import datetime as dt
        m = dt.datetime.fromtimestamp(x["t"], dt.timezone.utc).strftime("%Y-%m")
        for b, f in BRANDS.items():
            if f(x["text"]):
                cnt[m][b] += 1
                subs[b][sub] += 1

months = sorted(cnt)
def ok(m, q):
    s = status.get((m, q, "submission"), set()) | status.get((m, q, "comment"), set())
    return "failed" not in s and bool(s)
out = os.path.join(RAW, "X08_reddit_monthly.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    hdr = ["month"] + list(BRANDS) + ["complete_" + q for q in QMAP]
    w.writerow(hdr); print(*hdr)
    for m in months:
        row = [m] + [cnt[m][b] for b in BRANDS] + [int(ok(m, q)) for q in QMAP]
        w.writerow(row); print(*row)
for b in BRANDS:
    print("top subs", b, subs[b].most_common(10))


