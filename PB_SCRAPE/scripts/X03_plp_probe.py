"""X03: probe a product-listing (/f/ or /s/) Wayback snapshot for result counts and brand facets.
Usage: python X03_plp_probe.py <ts> <url>
"""
import sys, re, os, json
sys.path.insert(0, os.path.dirname(__file__))
from X03_fetch import fetch

t = fetch(sys.argv[1], sys.argv[2])
if not t:
    print("FAIL"); sys.exit(1)
print("len", len(t))
for m in re.findall(r".{0,100}\b[0-9][0-9,]* (?:results|Results|products|Products|items|Items)\b.{0,60}", t)[:10]:
    print("TXT:", m.replace("\n", " ")[:220])
for m in re.findall(r'"(?:totalCount|numFound|productCount|totalResults|recordSetTotal|total|totalProducts|resultCount)"\s*:\s*\d+', t)[:15]:
    print("JSON:", m)
for m in re.findall(r'"(?:X_BRAND|brand|Brand)"[^\]]{0,300}', t)[:5]:
    print("BRAND:", m[:300])
