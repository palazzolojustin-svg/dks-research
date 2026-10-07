# Dump all posts or comments from a subreddit via arctic-shift API (asc pagination)
import sys, json, time, requests
sub, kind, after, before, out = sys.argv[1:6]
base = f"https://arctic-shift.photon-reddit.com/api/{kind}/search"
fields_p = None
n=0
cur = after
with open(out, "w") as f:
    while True:
        params = dict(subreddit=sub, after=cur, before=before, limit=100, sort="asc")
        for attempt in range(5):
            try:
                r = requests.get(base, params=params, timeout=60)
                if r.status_code==200: break
            except Exception as e:
                pass
            time.sleep(5*(attempt+1))
        d = r.json().get("data", [])
        if not d: break
        for x in d:
            keep = {k: x.get(k) for k in ("id","created_utc","author","title","selftext","body","score","num_comments","link_id","parent_id","permalink","link_flair_text","author_flair_text")}
            f.write(json.dumps(keep)+"\n")
        n += len(d)
        last = d[-1]["created_utc"]
        if str(last)==str(cur): break
        cur = int(last)+1 if len(d)==100 else None
        if cur is None: break
        time.sleep(0.6)
print(sub, kind, n)
