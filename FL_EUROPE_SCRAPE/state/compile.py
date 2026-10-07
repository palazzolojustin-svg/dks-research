import json, glob, os, re, collections
root = r"C:\Users\palaz\Downloads\DKS_RESEARCH\FL_EUROPE_SCRAPE"
items = []
for f in sorted(glob.glob(os.path.join(root, "confirmed", "*.jsonl"))):
    for line in open(f, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("_complete") or not d.get("claim"):
            continue
        d["_file"] = os.path.basename(f)
        items.append(d)

# dedupe on normalized source_url + first 80 chars of claim
seen, out = set(), []
for d in items:
    k = (str(d.get("source_url", "")).strip().lower(), re.sub(r"\W+", " ", str(d.get("claim", "")).lower())[:80])
    if k in seen:
        continue
    seen.add(k)
    out.append(d)

prev_path = os.path.join(root, "state", "all_items.json")
prev = {}
if os.path.exists(prev_path):
    for p in json.load(open(prev_path, encoding="utf-8")):
        prev[(str(p.get("source_url", "")).strip().lower(), re.sub(r"\W+", " ", str(p.get("claim", "")).lower())[:80])] = p["id"]
nxt = max([int(v[1:]) for v in prev.values()] or [0]) + 1
for d in out:
    k = (str(d.get("source_url", "")).strip().lower(), re.sub(r"\W+", " ", str(d.get("claim", "")).lower())[:80])
    if k in prev:
        d["id"] = prev[k]; d["_new"] = False
    else:
        d["id"] = f"E{nxt:03d}"; nxt += 1; d["_new"] = True
out.sort(key=lambda d: d["id"])
print("new items", sum(d["_new"] for d in out))

print("raw", len(items), "deduped", len(out))
print("by tier", collections.Counter(d.get("final_tier") for d in out))
print("by thesis", collections.Counter(d.get("thesis") for d in out))
print("by status", collections.Counter(d.get("status") for d in out))
print("by cluster", collections.Counter(d.get("cluster") for d in out))
print("by country", collections.Counter(d.get("country") for d in out).most_common(30))

json.dump(out, open(os.path.join(root, "state", "all_items.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# compact view for reading
with open(os.path.join(root, "state", "compact.md"), "w", encoding="utf-8") as f:
    for d in out:
        f.write(f"{d['id']} | {d.get('cluster')}/{d.get('avenue')} | T{d.get('final_tier')} {d.get('status')} | {d.get('thesis')} | {d.get('country')} | {d.get('evidence_date')}\n")
        f.write(f"  CLAIM: {d.get('claim')}\n")
        if d.get("data_point"):
            f.write(f"  DATA: {d.get('data_point')}\n")
        q = d.get("english_translation") or d.get("original_quote") or ""
        if q:
            f.write(f"  QUOTE: {str(q)[:300]}\n")
        f.write(f"  SRC: {d.get('source_name')} {d.get('source_url')}\n")
        vn = str(d.get("verifier_note") or "")
        if vn:
            f.write(f"  VNOTE: {vn[:250]}\n")
print("compact size", os.path.getsize(os.path.join(root, "state", "compact.md")))
