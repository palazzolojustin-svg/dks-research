"""W08: collect Reddit posts+comments mentioning Foot Locker / Champs via arctic-shift API.
Usage: python3 -I W08_arctic_collect.py <outdir> [subs comma] [terms comma] [after] [before]
Resumable: writes one jsonl per (kind, sub, term), and a .done marker when finished.
"""
import sys, os, json, time, urllib.parse, re
import requests

BASE = "https://arctic-shift.photon-reddit.com/api"
outdir = sys.argv[1]
subs = sys.argv[2].split(",") if len(sys.argv) > 2 else ["Sneakers"]
terms = sys.argv[3].split(",") if len(sys.argv) > 3 else ["foot locker", "footlocker"]
AFTER = sys.argv[4] if len(sys.argv) > 4 else "2024-01-01"
BEFORE = sys.argv[5] if len(sys.argv) > 5 else "2026-10-08"
os.makedirs(outdir, exist_ok=True)
S = requests.Session()
S.headers["User-Agent"] = "research-script/0.1 (W08 FL sentiment)"

POST_FIELDS = "id,subreddit,title,selftext,created_utc,score,num_comments,author,link_flair_text,permalink"
COM_FIELDS = "id,subreddit,body,created_utc,score,author,link_id,parent_id"


def get(url, params):
    for attempt in range(8):
        try:
            r = S.get(url, params=params, timeout=90)
            if r.status_code == 200:
                j = r.json()
                if j.get("error"):
                    raise RuntimeError(j["error"])
                return j.get("data") or []
            raise RuntimeError(f"HTTP {r.status_code} {r.text[:200]}")
        except Exception as e:
            wait = 5 * (attempt + 1)
            print(f"  retry {attempt} after error {e}; sleep {wait}", flush=True)
            time.sleep(wait)
    raise RuntimeError("giving up")


def collect(kind, sub, term):
    slug = re.sub(r"\W+", "_", f"{kind}_{sub}_{term}")
    path = os.path.join(outdir, slug + ".jsonl")
    done = path + ".done"
    if os.path.exists(done):
        print("skip", slug)
        return
    after = AFTER
    seen = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                d = json.loads(line)
                seen.add(d["id"])
                after = max(after, str(d["created_utc"])) if isinstance(after, str) and after.isdigit() else str(d["created_utc"])
    n = 0
    with open(path, "a") as out:
        while True:
            params = {"subreddit": sub, "limit": 100, "sort": "asc", "after": after, "before": BEFORE}
            if kind == "posts":
                params["query"] = term
                params["fields"] = POST_FIELDS
                url = BASE + "/posts/search"
            else:
                params["body"] = term
                params["fields"] = COM_FIELDS
                url = BASE + "/comments/search"
            data = get(url, params)
            new = [d for d in data if d["id"] not in seen]
            for d in new:
                seen.add(d["id"])
                out.write(json.dumps(d) + "\n")
            n += len(new)
            if len(data) < 100 or not new:
                break
            after = str(max(int(d["created_utc"]) for d in data))
            time.sleep(0.7)
    open(done, "w").write(str(n))
    print(f"{slug}: {n} rows", flush=True)


for sub in subs:
    for term in terms:
        for kind in ("posts", "comments"):
            collect(kind, sub, term)
