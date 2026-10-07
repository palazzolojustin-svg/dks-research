"""Copy sources into SOURCE/ and build line-level delta files for near-duplicate documents.

A delta file lists every line of a variant document whose whitespace-normalized text does not
appear anywhere in its reference document(s). Lines that are dropped are verbatim repeats.
"""
import os, re, shutil, glob, json

DL = os.path.expanduser(r"~\Downloads")
ROOT = os.path.join(DL, "DKS_RESEARCH")
SRC = os.path.join(ROOT, "SOURCE")
OUT = os.path.join(ROOT, "_PREP", "deltas")
FOLDERS = ["00_DKS_SYNTHESIS", "01_DKS_SEC_FILINGS", "02_DKS_TRANSCRIPTS", "03_DKS_STREET_RESEARCH",
           "04_PEERS", "05_SECTOR_MACRO", "06_BLOOMBERG_FINANCIALS", "08_MARKET_DATA"]

for f in FOLDERS:
    dst = os.path.join(SRC, f)
    if not os.path.exists(dst):
        shutil.copytree(os.path.join(DL, f), dst)
os.makedirs(OUT, exist_ok=True)

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

def lines(p):
    with open(os.path.join(SRC, p), encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()

def keyset(paths):
    ks = set()
    for p in paths:
        ks.update(norm(l) for l in lines(p))
    return ks

stats = []

def delta(variant, refs):
    ref = keyset(refs)
    vl = lines(variant)
    keep, nonblank = [], 0
    for i, l in enumerate(vl, 1):
        n = norm(l)
        if not n or n.startswith("<!-- page"):
            continue
        nonblank += 1
        if n not in ref:
            keep.append(f"L{i}: {l.rstrip()}")
    name = variant.replace("\\", "__").replace("/", "__").replace(".md", "") + ".delta.md"
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write(f"# DELTA of SOURCE/{variant}\n# Reference(s): " + "; ".join("SOURCE/" + r for r in refs) + "\n")
        fh.write(f"# {len(keep)} of {nonblank} non-blank lines are NOT verbatim present in the reference(s); all other lines are exact repeats.\n")
        fh.write("# Each line is prefixed with its line number in the original (open the original around that line for context).\n\n")
        fh.write("\n".join(keep) + "\n")
    stats.append({"variant": variant, "refs": refs, "nonblank": nonblank, "delta_lines": len(keep),
                  "delta_file": "_PREP/deltas/" + name})

def rel(pattern):
    return sorted(os.path.relpath(p, SRC) for p in glob.glob(os.path.join(SRC, pattern)))

def chain(files):
    """files sorted oldest->newest; newest is the full reference; each older one vs the next newer."""
    for i in range(len(files) - 1):
        delta(files[i], [files[i + 1]])

# DKS 10-K chain and 10-Q chain (each 10-Q vs previously filed 10-Q)
chain(rel(r"01_DKS_SEC_FILINGS\10-K\*.md"))
q = rel(r"01_DKS_SEC_FILINGS\10-Q\*.md")
for i in range(1, len(q)):
    delta(q[i], [q[i - 1]])

# DKS debt docs
d = r"01_DKS_SEC_FILINGS\Debt-and-registration-docs" + "\\"
delta(d + "DKS_424B2_2026-09-23_senior-notes-2036-2056.md", [d + "DKS_424B2_2026-09-22_senior-notes-2036-2056.md"])
delta(d + "DKS_S-4-A_2026-06-16_registered-exchange-offer-4pct-notes-2029.md", [d + "DKS_S-4_2026-06-05_registered-exchange-offer-4pct-notes-2029.md"])
delta(d + "DKS_424B3_2026-06-17_registered-exchange-offer-4pct-notes-2029.md",
      [d + "DKS_S-4_2026-06-05_registered-exchange-offer-4pct-notes-2029.md", d + "DKS_S-4-A_2026-06-16_registered-exchange-offer-4pct-notes-2029.md"])
delta(d + "DKS_S-3ASR_2026-09-21_senior-notes-2036-2056.md", [d + "DKS_424B2_2026-09-22_senior-notes-2036-2056.md"])

# Foot Locker merger docs: 424B3 (final prospectus) is the full reference
m = r"01_DKS_SEC_FILINGS\Foot-Locker-merger-docs" + "\\"
ref = m + "DKS_424B3_2025-07-11.md"
delta(m + "DKS_S-4-A_2025-07-08.md", [ref])
delta(m + "DKS_S-4_2025-06-23.md", [ref, m + "DKS_S-4-A_2025-07-08.md"])
delta(m + "FL_DEFM14A_Merger-Proxy-Prospectus_filed-2025-07-11.md", [ref, m + "DKS_S-4-A_2025-07-08.md", m + "DKS_S-4_2025-06-23.md"])

# 425 deal communications vs all DKS 8-K material (+ earlier 425s)
dks8k = rel(r"01_DKS_SEC_FILINGS\8-K\*.md") + rel(r"01_DKS_SEC_FILINGS\8-K\exhibits\*.md")
c425 = rel(r"01_DKS_SEC_FILINGS\Foot-Locker-merger-docs\425-deal-communications\*.md")
for i, f in enumerate(c425):
    delta(f, dks8k + c425[:i])

# Annual reports to shareholders vs same-year 10-K
ar = r"02_DKS_TRANSCRIPTS\annual_report_letters" + "\\"
k = r"01_DKS_SEC_FILINGS\10-K" + "\\"
for a, kk in [("2023-05-05", "FY2022_filed-2023-03-23"), ("2024-05-02", "FY2023_filed-2024-03-28"),
              ("2025-05-02", "FY2024_filed-2025-03-27"), ("2026-05-01", "FY2025_filed-2026-03-27")]:
    delta(ar + f"DKS_Annual-Report-to-Shareholders_{a}.md", [k + f"DKS_10-K_{kk}.md"])

# Peers: NKE, FL, ASO filings
chain(rel(r"04_PEERS\NKE\sec_filings\NKE_10-K_*.md"))
q = rel(r"04_PEERS\NKE\sec_filings\NKE_10-Q_*.md")
for i in range(1, len(q)):
    delta(q[i], [q[i - 1]])
chain(rel(r"04_PEERS\FL\sec_filings\FL_10-K_*.md"))
q = rel(r"04_PEERS\FL\sec_filings\FL_10-Q_*.md")
for i in range(1, len(q)):
    delta(q[i], [q[i - 1]])
q = rel(r"04_PEERS\ASO\sec_filings\ASO_10-Q_*.md")
for i in range(1, len(q)):
    delta(q[i], [q[i - 1]])
fl8k = rel(r"04_PEERS\FL\sec_filings\8-K\*.md")
for i, f in enumerate(fl8k):
    delta(f, dks8k + c425 + fl8k[:i])

with open(os.path.join(ROOT, "_PREP", "delta_stats.json"), "w") as fh:
    json.dump(stats, fh, indent=1)
for s in stats:
    pct = 100 * s["delta_lines"] / max(s["nonblank"], 1)
    print(f'{pct:5.1f}%  {s["delta_lines"]:6d}/{s["nonblank"]:6d}  {s["variant"]}')
