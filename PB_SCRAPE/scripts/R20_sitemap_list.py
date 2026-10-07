"""R20_sitemap_list.py - list all URLs (with lastmod) from a sitemap or sitemap index, filtered by a slug regex.
Usage: python R20_sitemap_list.py <sitemap_url> <slug_regex> [max_children]
"""
import requests, re, sys, gzip
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}


def get(u):
    c = requests.get(u, headers=H, timeout=40).content
    if c[:2] == b"\x1f\x8b":
        c = gzip.decompress(c)
    return c.decode("utf-8", "ignore")


def walk(u, out, maxc, depth=0):
    x = get(u)
    if "<sitemapindex" in x:
        kids = re.findall(r"<loc>\s*(.*?)\s*</loc>", x)
        print(f"# index {u}: {len(kids)} children", file=sys.stderr)
        for k in kids[:maxc]:
            try:
                walk(k.replace("&amp;", "&"), out, maxc, depth + 1)
            except Exception as e:
                print("# ERR", k, e, file=sys.stderr)
    else:
        for blk in re.findall(r"<url>(.*?)</url>", x, re.S):
            loc = re.search(r"<loc>\s*(.*?)\s*</loc>", blk)
            lm = re.search(r"<lastmod>\s*(.*?)\s*</lastmod>", blk)
            if loc:
                out.append((loc.group(1), lm.group(1)[:10] if lm else ""))


if __name__ == "__main__":
    out = []
    walk(sys.argv[1], out, int(sys.argv[3]) if len(sys.argv) > 3 else 200)
    pat = re.compile(sys.argv[2], re.I)
    print(f"# total urls {len(out)}", file=sys.stderr)
    for u, lm in sorted(out, key=lambda z: z[1], reverse=True):
        if pat.search(u):
            print(lm, u)
