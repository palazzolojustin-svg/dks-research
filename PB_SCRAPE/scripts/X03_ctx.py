"""X03: print context around a regex in a cached Wayback snapshot. Usage: python X03_ctx.py <ts> <url> <regex> [n=5] [width=300]"""
import sys, re, os
sys.path.insert(0, os.path.dirname(__file__))
from X03_fetch import fetch
t = fetch(sys.argv[1], sys.argv[2])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 5
w = int(sys.argv[5]) if len(sys.argv) > 5 else 300
for i, m in enumerate(re.finditer(sys.argv[3], t)):
    if i >= n:
        break
    print("...", t[max(0, m.start() - w):m.end() + w].replace("\n", " ").encode("ascii", "replace").decode(), "\n")
