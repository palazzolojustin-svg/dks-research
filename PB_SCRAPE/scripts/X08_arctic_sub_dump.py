"""X08 Full dump of one subreddit's posts+comments via the free Arctic Shift API (no key), then count
DKS owned-brand mentions per month normalised by total volume.

Why: Arctic Shift full-text search times out on big subs and PullPush is flaky, but plain subreddit
listings work. For small/medium subs (r/DicksSportingGoods ~35 comments/day) a full dump is cheap.
Rerun:  python X08_arctic_sub_dump.py DicksSportingGoods 2024-01-01 2026-10-08
Output: PB_SCRAPE/raw/X08_arctic_<sub>.jsonl (all items, minimal fields) and X08_arctic_<sub>_monthly.csv
"""
import requests, time, json, sys, os, re, csv, collections, datetime as dt

sub, start, end = sys.argv[1], sys.argv[2], sys.argv[3]
H = {"User-Agent": "dks-research-script/0.1"}
B = "https://arctic-shift.photon-reddit.com/api/"
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
fn = os.path.join(RAW, f"X08_arctic_{sub}.jsonl")

PAT = {
    "calia": r"\bcalia\b", "vrst": r"\bvrst\b",
    "dsg_brand": r"\bdsg\b.{0,30}(legging|jogger|short|pant|hoodie|tee|shirt|jacket|bra|apparel|brand|clothes|clothing|fleece|polo|sock)|(legging|jogger|short|pant|hoodie|tee|shirt|jacket|bra|polo|fleece).{0,15}\bfrom dsg\b|\bdsg brand",
    "maxfli": r"\bmaxfli|\bmaxfly\b", "walter_hagen": r"walter hagen", "alpine_design": r"alpine design",
    "ethos": r"\bethos\b", "fitness_gear": r"fitness gear", "nishiki": r"\bnishiki\b", "quest": r"\bquest (canopy|chair|tent)",
    "top_flite": r"top[- ]?flite", "tommy_armour": r"tommy armour",
    "private_label": r"private label|house brand|store brand|in-house brand|our brands|vertical brand",
    "nike": r"\bnike\b", "lululemon": r"lululemon|\blulu\b", "vuori": r"\bvuori\b",
}


def ts(s):
    return int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp())


def dump(kind):
    after = ts(start)
    endt = ts(end)
    n = 0
    with open(fn, "a", encoding="utf-8") as f:
        while after < endt:
            for att in range(8):
                try:
                    r = requests.get(B + kind + "/search", params={"subreddit": sub, "after": after, "before": endt,
                                                                   "limit": "auto", "sort": "asc"}, headers=H, timeout=120)
                    if r.status_code == 200:
                        d = r.json().get("data") or []
                        break
                except Exception:
                    pass
                time.sleep(5 * (att + 1))
            else:
                print("FAILED at", after, file=sys.stderr); return
            if not d:
                break
            for x in d:
                text = (x.get("title", "") + " || " + x.get("selftext", "")) if kind == "posts" else x.get("body", "")
                f.write(json.dumps({"k": kind, "id": x["id"], "t": int(x["created_utc"]), "a": x.get("author"),
                                    "s": x.get("score"), "text": text[:2000]}) + "\n")
            n += len(d)
            newafter = max(int(x["created_utc"]) for x in d)
            if newafter <= after:
                break
            after = newafter
            print(kind, dt.datetime.fromtimestamp(after, dt.timezone.utc).date(), n, flush=True)
            time.sleep(1)


def summarise():
    seen, agg = set(), collections.defaultdict(collections.Counter)
    for line in open(fn, encoding="utf-8"):
        try:
            x = json.loads(line)
        except Exception:
            continue
        if x["id"] in seen:
            continue
        seen.add(x["id"])
        m = dt.datetime.fromtimestamp(x["t"], dt.timezone.utc).strftime("%Y-%m")
        agg[m]["total"] += 1
        for k, p in PAT.items():
            if re.search(p, x["text"], re.I):
                agg[m][k] += 1
    out = os.path.join(RAW, f"X08_arctic_{sub}_monthly.csv")
    cols = ["total"] + list(PAT)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["month"] + cols)
        for m in sorted(agg):
            w.writerow([m] + [agg[m][c] for c in cols])
            print(m, *[agg[m][c] for c in cols])


if __name__ == "__main__":
    if "--summary-only" not in sys.argv:
        dump("posts"); dump("comments")
    summarise()
