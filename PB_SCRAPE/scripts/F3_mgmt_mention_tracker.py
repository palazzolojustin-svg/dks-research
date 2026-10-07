r"""F3: management "owned-brand mention intensity" tracker for DKS transcripts.

What it does
- Scans every DKS earnings-call / conference / event transcript under SOURCE\02_DKS_TRANSCRIPTS
  (earnings_calls, conferences, events) and counts mentions of DKS owned/vertical brands
  and related terms, normalised per 10,000 words.
- Outputs PB_SCRAPE\raw\F3_mgmt_mentions.csv (one row per transcript, sorted by date).

How to rerun (weekly / after every new call)
- Drop the new FactSet transcript (.md or .txt) into the same SOURCE folder layout, or point
  ROOTS at a folder with new transcripts, then:  python PB_SCRAPE\scripts\F3_mgmt_mention_tracker.py
- A falling count is itself a signal (management stops volunteering the topic); a rising count
  plus quantification ("$", "%", "penetration") is the signal to look for.

Notes
- "ETHOS" is matched case-sensitively (all caps) to avoid the common word "ethos".
- "DSG" is matched as a whole word; it can also be the DKS ticker-like abbreviation in some
  broker text, but in mgmt transcripts it is almost always the DSG brand.
"""
import csv
import os
import re

BASE = r"C:\Users\palaz\Downloads\DKS_RESEARCH"
ROOTS = [os.path.join(BASE, "SOURCE", "02_DKS_TRANSCRIPTS", d) for d in ("earnings_calls", "conferences", "events")]
OUT = os.path.join(BASE, "PB_SCRAPE", "raw", "F3_mgmt_mentions.csv")

TERMS = {
    "vertical_brand": re.compile(r"(?i)\bvertical\b"),
    "private_label_brand": re.compile(r"(?i)\bprivate (label|brand)s?\b"),
    "DSG": re.compile(r"\bDSG\b"),
    "CALIA": re.compile(r"(?i)\bCALIA\b"),
    "VRST": re.compile(r"(?i)\bVRST\b"),
    "Maxfli": re.compile(r"(?i)\bMaxfl[iy]\b"),
    "Walter_Hagen": re.compile(r"(?i)Walter Hagen"),
    "other_owned": re.compile(r"(?i)Top-?Flite|Tommy Armour|Alpine Design|Fitness Gear|Nishiki|\bQuest\b|\bETHOS\b"),
    "margin_premium_bps": re.compile(r"(?i)(600|700)\s*(basis points|bps)\s*(to|-)\s*(800|900)"),
    "emerging_brand_comp": re.compile(r"(?i)Gymshark|Vuori|Free People|FP Movement"),
}
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def main():
    rows = []
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for fn in os.listdir(root):
            if not fn.lower().endswith((".md", ".txt")):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            words = max(1, len(txt.split()))
            m = DATE_RE.search(fn)
            row = {"date": m.group(1) if m else "", "file": fn, "words": words}
            owned_total = 0
            for k, rx in TERMS.items():
                c = len(rx.findall(txt))
                row[k] = c
                if k in ("vertical_brand", "private_label_brand", "DSG", "CALIA", "VRST", "Maxfli", "Walter_Hagen", "other_owned"):
                    owned_total += c
            row["owned_total"] = owned_total
            row["owned_per_10k_words"] = round(owned_total / words * 10000, 2)
            rows.append(row)
    rows.sort(key=lambda r: r["date"])
    cols = ["date", "file", "words"] + list(TERMS) + ["owned_total", "owned_per_10k_words"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r["date"], r["file"][:60].ljust(60), "owned_total=", r["owned_total"], "per10k=", r["owned_per_10k_words"], "emerging=", r["emerging_brand_comp"])


if __name__ == "__main__":
    main()
