"""X02: assemble census chunks dumped from the browser (tool-result JSON files) into one CSV + facets JSON.
Only needed for the agent workflow; a human analyst uses copy(X02csv()) in DevTools instead.
Usage: python X02_assemble_chunks.py <out_csv> <out_facets_json> <chunkfile1> <chunkfile2> ...
"""
import sys, json

hdr = "cat,sort,rank,pid,brand,vert,excl,badge,d4474,sortdate,minlist,minoffer,maxlist,maxoffer,bvn,bvr"
out_csv, out_fac, files = sys.argv[1], sys.argv[2], sys.argv[3:]
lines, facets = [], None
for fp in files:
    raw = open(fp, encoding="utf-8").read()
    try:
        j = json.loads(raw)
        txt = j[0]["text"] if isinstance(j, list) else raw
    except Exception:
        txt = raw
    if txt.startswith('"'):  # result text is a JSON string literal followed by a "(captured at ...)" note
        end = txt.rfind('"\n')
        txt = json.loads(txt[: end + 1])
    if "X02FACETS\n" in txt:
        txt, fac = txt.split("X02FACETS\n", 1)
        facets = json.loads(fac.strip())
    body = txt.split("\n", 1)[1] if txt.startswith("X02CHUNK") else txt
    lines += [l for l in body.split("\n") if l.strip()]
open(out_csv, "w", encoding="utf-8", newline="").write(hdr + "\n" + "\n".join(lines) + "\n")
if facets:
    json.dump(facets, open(out_fac, "w"), indent=1)
print("rows", len(lines), "facets", len(facets or {}))
