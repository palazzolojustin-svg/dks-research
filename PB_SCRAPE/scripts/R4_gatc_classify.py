"""R4: classify Google Ads Transparency creatives of DICK'S by product/brand.

For format-2 creatives (text / Shopping), the public preview script (displayads-formats.googleusercontent.com
.../content.js, the same file the Transparency Center page loads) embeds a base64 protobuf 'pla=' parameter
for Shopping (Product Listing) ads: field 2 = product title, field 3 = merchant ("DICK'S Sporting Goods").
Product title starts with the brand -> owned-brand tag.

Sampling: up to K creatives per first-shown month (random, seed 7) to keep requests polite.
Input:  raw\\R4_gatc_creatives_DKS_main.csv (from R4_google_ads_transparency.py)
Output: raw\\R4_gatc_classified_sample.csv (appends; skips creatives already done -> resumable)
Run:    python PB_SCRAPE\\scripts\\R4_gatc_classify.py [K=40] [from=2024-01] [to=2026-10]
"""
import csv, re, sys, time, base64, random, urllib.parse, pathlib, requests
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
SRC = RAW / "R4_gatc_creatives_DKS_main.csv"
OUT = RAW / "R4_gatc_classified_sample.csv"
K = int(sys.argv[1]) if len(sys.argv) > 1 else 40
FROM = sys.argv[2] if len(sys.argv) > 2 else "2024-01"
TO = sys.argv[3] if len(sys.argv) > 3 else "2026-10"
OWN = re.compile(r"^\s*(DSG|CALIA|VRST|Maxfli|Walter Hagen|Alpine Design|ETHOS|Fitness Gear|Nishiki|Quest|Top[- ]?Flite|Tommy Armour|Field & Stream|Field and Stream)\b", re.I)
OWN_ANY = re.compile(r"\b(DSG|CALIA|VRST|Maxfli|Walter Hagen|Alpine Design|ETHOS|Fitness Gear|Nishiki|Top[- ]?Flite|Tommy Armour)\b")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
     "Referer": "https://adstransparency.google.com/"}
FIELDS = ["creative_id", "format", "first_shown", "last_shown", "kind", "title", "merchant", "brand_guess", "owned_brand", "owned_any_text"]


def pb_strings(b):
    """minimal protobuf length-delimited field reader (top level)."""
    i, out = 0, {}
    while i < len(b):
        key = b[i]; i += 1
        fn, wt = key >> 3, key & 7
        if wt != 2:
            break
        ln = 0; shift = 0
        while True:
            x = b[i]; i += 1; ln |= (x & 0x7F) << shift; shift += 7
            if x < 0x80:
                break
        out.setdefault(fn, b[i:i + ln].decode("utf-8", "replace")); i += ln
    return out


def classify(s, url):
    t = s.get(url, timeout=40).text
    m = re.search(r"pla%3D([A-Za-z0-9%_\-]+?)(?:\\\\x26|\\x26|&|')", t)
    if m:
        p = urllib.parse.unquote(urllib.parse.unquote(m.group(1)))
        try:
            d = pb_strings(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4)))
        except Exception:
            d = pb_strings(base64.b64decode(p + "=" * (-len(p) % 4)))
        return "shopping", d.get(2, ""), d.get(3, "")
    # non-shopping text ad: unescape and keep visible-ish strings
    u = t.encode().decode("unicode_escape", "ignore")
    txt = re.sub(r"<[^>]+>", " ", u)
    hits = sorted(set(OWN_ANY.findall(txt)))
    return "text", "|".join(hits), ""


def main():
    rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if r["format"] == "2" and "content.js" in r["preview_url"]]
    done = set()
    if OUT.exists():
        done = {r["creative_id"] for r in csv.DictReader(open(OUT, encoding="utf-8"))}
    else:
        with open(OUT, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()
    bym = defaultdict(list)
    for r in rows:
        mth = r["first_shown"][:7]
        if FROM <= mth <= TO:
            bym[mth].append(r)
    random.seed(7)
    s = requests.Session(); s.headers.update(H)
    for mth in sorted(bym):
        smp = bym[mth] if len(bym[mth]) <= K else random.sample(bym[mth], K)
        n = 0
        for r in smp:
            if r["creative_id"] in done:
                continue
            try:
                kind, title, merch = classify(s, r["preview_url"])
            except Exception as e:
                print("err", e); time.sleep(5); continue
            bg = title.split(" ")[0] if kind == "shopping" else ""
            ob = OWN.match(title).group(1) if (kind == "shopping" and OWN.match(title)) else ""
            with open(OUT, "a", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=FIELDS).writerow({"creative_id": r["creative_id"], "format": r["format"],
                    "first_shown": r["first_shown"], "last_shown": r["last_shown"], "kind": kind, "title": title,
                    "merchant": merch, "brand_guess": bg, "owned_brand": ob, "owned_any_text": title if kind == "text" else ""})
            n += 1
            time.sleep(1.2)
        print(mth, "pool", len(bym[mth]), "classified", n, flush=True)


if __name__ == "__main__":
    main()
