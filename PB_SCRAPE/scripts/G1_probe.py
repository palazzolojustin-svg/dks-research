"""G1 probe: print raw BV review/product fields for given product ids (to look for OriginalProductName etc.).
python G1_probe.py <client> <product_id> [...]"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from X01_bv_reviews import session_for, get
client = sys.argv[1]
s = session_for(client)
for pid in sys.argv[2:]:
    pr = get(s, client, "products", [("Filter", f"Id:eq:{pid}"), ("Stats", "Reviews")])
    for x in pr.get("Results", []):
        print("PRODUCT", pid, {k: x.get(k) for k in ["Name", "Brand", "FamilyIds", "ProductPageUrl", "Active", "CategoryId", "UPCs", "EANs", "ModelNumbers", "ManufacturerPartNumbers", "Attributes"]})
        print("  stats", (x.get("ReviewStatistics") or {}).get("TotalReviewCount"), (x.get("ReviewStatistics") or {}).get("FirstSubmissionTime"))
    r = get(s, client, "reviews", [("Filter", f"ProductId:eq:{pid}"), ("Sort", "SubmissionTime:asc"), ("Limit", "3")])
    print("  total", r.get("TotalResults"))
    for x in r.get("Results", [])[:3]:
        print("  REVIEW keys", sorted(x.keys()))
        print("   ", x.get("SubmissionTime"), x.get("OriginalProductName"), x.get("ProductId"), x.get("SourceClient"), x.get("IsSyndicated"), (x.get("Title") or "")[:60])
