import json, os, glob
proj = r"C:\Users\palaz\.claude\projects\C--Users-palaz-Downloads-DKS-RESEARCH"
cands = glob.glob(os.path.join(proj, "6c5555e9-c284-4d8a-958d-2282c35d841e*.jsonl"))
out = os.path.dirname(os.path.abspath(__file__))
n = 0
for p in cands:
    for line in open(p, encoding="utf-8"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        msg = d.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for c in content:
            if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Workflow":
                a = c["input"].get("args")
                if isinstance(a, str):
                    a = json.loads(a)
                if a and a.get("cluster"):
                    with open(os.path.join(out, f"args_{a['cluster']}.json"), "w", encoding="utf-8") as f:
                        json.dump(a, f, ensure_ascii=False, indent=1)
                    n += 1
print("candidates", cands, "saved", n)
