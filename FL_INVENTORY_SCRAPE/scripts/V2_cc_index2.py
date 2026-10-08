"""V2: build the dicks.com /f/ CDX list for a Common Crawl crawl WITHOUT index.commoncrawl.org (which resets
connections through the proxy): binary-search cluster.idx on data.commoncrawl.org, then read the cdx shard blocks.
Output raw/V2/ccidx/<crawl>.jsonl, same format as X11_cc_index.py."""
import gzip, json, os, sys, time, requests
OUT = os.path.join(os.path.dirname(__file__), "..", "raw", "V2", "ccidx"); os.makedirs(OUT, exist_ok=True)
KEY = "com,dickssportinggoods)/f/"
S = requests.Session()
def rng(url, a, b):
    for i in range(6):
        try:
            r = S.get(url, headers={"Range": f"bytes={a}-{b}"}, timeout=90)
            if r.status_code in (200, 206): return r.content
        except Exception: pass
        time.sleep(3 + 3 * i)
    raise RuntimeError("fetch fail " + url)
def run(cid):
    base = f"https://data.commoncrawl.org/cc-index/collections/{cid}/indexes/"
    size = int(S.head(base + "cluster.idx", timeout=60).headers["content-length"])
    def line_at(pos):
        d = rng(base + "cluster.idx", pos, min(size - 1, pos + 3000)).decode("utf-8", "replace")
        if pos: d = d.split("\n", 1)[1]
        return d.split("\n", 1)[0]
    lo, hi = 0, size
    while hi - lo > 4000:  # find first position whose line key >= KEY
        mid = (lo + hi) // 2
        k = line_at(mid).split(" ", 1)[0]
        if k < KEY: lo = mid
        else: hi = mid
    start = max(0, lo - 4000)
    data = rng(base + "cluster.idx", start, min(size - 1, start + 1_500_000)).decode("utf-8", "replace").split("\n")[1:]
    blocks = []
    for i, l in enumerate(data):
        p = l.split("\t")
        if len(p) < 4: continue
        blocks.append((l.split(" ", 1)[0], p[1], int(p[2]), int(p[3])))
    # blocks whose START key <= end-of-prefix; include the block before first key>=KEY
    end = "com,dickssportinggoods)/f0"
    sel = []
    for i, b in enumerate(blocks):
        if b[0] > end: break
        sel.append(b)
    # drop leading blocks that end before KEY (next block start < KEY)
    while len(sel) > 1 and blocks[blocks.index(sel[1])][0] < KEY: sel.pop(0)
    out = []
    for key, fn, off, ln in sel:
        txt = gzip.decompress(rng(base + fn, off, off + ln - 1)).decode("utf-8", "replace")
        for l in txt.splitlines():
            if l.startswith(KEY) and "{" in l:
                j = l[l.index("{"):]
                if '"url": "https://www.dickssportinggoods.com/f/' in j:
                    d = json.loads(j); d["timestamp"] = l.split(" ", 2)[1]; out.append(json.dumps(d))
    open(os.path.join(OUT, cid + ".jsonl"), "w").write("\n".join(out))
    print(cid, "blocks", len(sel), "records", len(out), flush=True)
for c in sys.argv[1:]:
    try: run(c)
    except Exception as e: print(c, "ERR", e, flush=True)
