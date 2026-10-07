"""W10: dump minimal_bol + notify_party tables from an ImportYeti payload. Usage: python3 -I W10_bols.py <payload.txt> [out.csv]"""
import re, json, sys, csv
def arr(big, key):
    i = big.find(f'"{key}":[')
    if i < 0: return []
    j = i + len(key) + 3; depth = 0
    for k in range(j, len(big)):
        c = big[k]
        if c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0: break
    try: return json.loads(big[j:k+1])
    except Exception as e: print("fail", key, e); return []
big = open(sys.argv[1], encoding="utf-8").read()
np_ = arr(big, "notify_party_table") or []
if not np_:
    m = re.search(r'"(\w*notify\w*)":\[\{"notify_party"', big); 
    if m: np_ = arr(big, m.group(1))
print("notify parties:", len(np_))
for n in np_[:40]: print("  NP", n.get("notify_party"), "|", (n.get("address") or "")[:60], "| tot", n.get("shipments"), "12m", n.get("shipments_12m"), "12-24m", n.get("shipments_12_24m"))
B = arr(big, "minimal_bol")
print("bols:", len(B))
rows = []
for b in B:
    o = b.get("organization") or {}
    rows.append([b["date"][:10], b.get("bol"), o.get("title"), o.get("country"), b.get("weight"), b.get("quantity"), b.get("quantityUnit"), b.get("description")])
    print("  ", b["date"][:10], (o.get("title") or "")[:32], o.get("country"), b.get("weight"), b.get("quantity"), "|", (b.get("description") or "")[:110])
if len(sys.argv) > 2:
    with open(sys.argv[2], "w", newline="") as f:
        w = csv.writer(f); w.writerow(["date", "bol", "shipper", "country", "weight_kg", "qty", "unit", "description"]); w.writerows(rows)
