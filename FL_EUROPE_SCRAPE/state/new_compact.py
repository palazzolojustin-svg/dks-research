import json
r = json.load(open("all_items.json", encoding="utf-8"))
with open("new_compact.md", "w", encoding="utf-8") as f:
    for d in r:
        if not d.get("_new"):
            continue
        f.write(f"{d['id']} | {d['cluster']}/{d.get('avenue')} | T{d.get('final_tier')} {d.get('status')} | {d.get('thesis')} | {d.get('country')} | {d.get('evidence_date')}\n")
        f.write(f"  CLAIM: {d.get('claim')}\n")
        f.write(f"  DATA: {str(d.get('data_point') or '')[:500]}\n")
        f.write(f"  SRC: {d.get('source_url')}\n")
        f.write(f"  VNOTE: {str(d.get('verifier_note') or '')[:200]}\n")
