"""X03: dump anchors of a Wayback snapshot. Usage: python X03_anchors.py <ts> <url> [filter-regex]"""
import sys, re
from bs4 import BeautifulSoup as B
sys.path.insert(0, __import__("os").path.dirname(__file__))
from X03_fetch import fetch


def anchors(html):
    s = B(html, "html.parser")
    for sc in s(["script", "style", "noscript"]):
        sc.decompose()
    out = []
    for a in s.find_all("a"):
        h = a.get("href", "") or ""
        tx = " ".join(a.get_text(" ", strip=True).split())
        al = " | ".join(i.get("alt", "") for i in a.find_all("img"))
        out.append((h, tx, al, a.get("aria-label", "") or ""))
    return out


if __name__ == "__main__":
    t = fetch(sys.argv[1], sys.argv[2])
    if not t:
        print("FAIL"); sys.exit(1)
    rx = re.compile(sys.argv[3], re.I) if len(sys.argv) > 3 else None
    for h, tx, al, ar in anchors(t):
        line = f"{h[:120]} || {tx[:80]} || {al[:60]} || {ar[:50]}"
        if rx is None or rx.search(line):
            print(line.encode("ascii", "replace").decode())
