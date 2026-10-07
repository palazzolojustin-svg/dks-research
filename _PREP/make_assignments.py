"""Partition every source file into agent assignments (written to _PREP/assignments.json)."""
import os, glob, json

ROOT = os.path.join(os.path.expanduser(r"~\Downloads"), "DKS_RESEARCH")
SRC = os.path.join(ROOT, "SOURCE")
stats = json.load(open(os.path.join(ROOT, "_PREP", "delta_stats.json"))) + \
        json.load(open(os.path.join(ROOT, "_PREP", "delta_stats_ar.json")))
DELTA = {s["variant"]: s["delta_file"] for s in stats}

def rel(pattern):
    return sorted(os.path.relpath(p, SRC) for p in glob.glob(os.path.join(SRC, pattern)))

def kb(p):
    return os.path.getsize(os.path.join(SRC, p)) / 1024

def item(p):
    d = {"source": "SOURCE/" + p.replace("\\", "/"), "kb": round(kb(p))}
    if p in DELTA:
        d["read_delta"] = DELTA[p]
    return d

def bins(files, n):
    """split date-ordered files into n contiguous bins of roughly equal size"""
    total = sum(kb(f) for f in files)
    out, cur, acc = [], [], 0
    for f in files:
        cur.append(f); acc += kb(f)
        if acc >= total * (len(out) + 1) / n and len(out) < n - 1:
            out.append(cur); cur = []
    out.append(cur)
    return [b for b in out if b]

A = []
def add(aid, tier, out, files, note=""):
    A.append({"id": aid, "tier": tier, "output": out, "note": note, "files": [item(f) for f in files]})

# ---------------- CORE ----------------
syn = rel(r"00_DKS_SYNTHESIS\*.md")
for i, b in enumerate(bins(syn, 2)):
    add(f"C01{'AB'[i]}", "CORE", f"CORE_NOTES/C01_SYNTHESIS_{'AB'[i]}.md", b,
        "Pre-written synthesis/primer files. Keep every distinct fact, figure, derived calc, view and quote; they are dense already, so compress little.")
calls = [r"02_DKS_TRANSCRIPTS\earnings_calls\DKS_Q3-FY2024_Earnings-Call_2024-11-26.md",
         r"02_DKS_TRANSCRIPTS\earnings_calls\DKS_Q1-FY2025_Earnings-Call_2025-05-28.md",
         r"02_DKS_TRANSCRIPTS\earnings_calls\DKS_Q2-FY2025_Earnings-Call_2025-08-28.md",
         r"02_DKS_TRANSCRIPTS\earnings_calls\DKS_Q3-FY2025_Earnings-Call_2025-11-25.md",
         r"02_DKS_TRANSCRIPTS\earnings_calls\DKS_Q4-FY2025_Earnings-Call_2026-03-12.md",
         r"02_DKS_TRANSCRIPTS\earnings_calls\DKS_Q1-FY2026_Earnings-Call_2026-05-27.md",
         r"02_DKS_TRANSCRIPTS\earnings_calls\DKS_Q2-FY2026_Earnings-Call_2026-08-25.md"]
add("C02A", "CORE", "CORE_NOTES/C02_EARNINGS_CALLS_A.md", calls[:4])
add("C02B", "CORE", "CORE_NOTES/C02_EARNINGS_CALLS_B.md", calls[4:])
conf = rel(r"02_DKS_TRANSCRIPTS\conferences\*.md")
conf = sorted(conf, key=lambda p: p.rsplit("_", 1)[-1])
ev = rel(r"02_DKS_TRANSCRIPTS\events\*.md")
add("C03A", "CORE", "CORE_NOTES/C03_CONFERENCES_EVENTS_A.md", conf[:4])
add("C03B", "CORE", "CORE_NOTES/C03_CONFERENCES_EVENTS_B.md", conf[4:] + ev)
add("C04", "CORE", "CORE_NOTES/C04_EXPERT_CALLS.md", rel(r"02_DKS_TRANSCRIPTS\expert_calls_alphasense\*.md"))
add("C05", "CORE", "CORE_NOTES/C05_CONSENSUS_MARKETDATA_ALTDATA_SLIDES_LETTERS.md",
    rel(r"06_BLOOMBERG_FINANCIALS\DKS\*.md") + rel(r"08_MARKET_DATA\*.md") +
    [p for p in rel(r"08_MARKET_DATA\csv\*.csv") if not os.path.basename(p).startswith("peer_")] +
    rel(r"02_DKS_TRANSCRIPTS\slides_text\*.md") +
    [r"02_DKS_TRANSCRIPTS\annual_report_letters\DKS_Shareholder_Letters_and_Highlights_FY2022-FY2025_extracted.md"],
    "CSV files: do NOT transcribe raw rows. The raw CSVs are copied verbatim into CORE_NOTES/data/ (Claude can load them). "
    "Write: what each CSV contains (columns, row count, date range), and every analytically relevant derived fact "
    "(for OHLCV: price on every earnings date and 1-day/5-day reactions, 52w high/low, monthly closes table, drawdowns, volume spikes >2x 50d avg; "
    "for options/holders/insiders/ratings: the full content as compact tables since they are small). Empty CSVs: list as empty.")
res = rel(r"03_DKS_STREET_RESEARCH\*.md")
for i, b in enumerate(bins(res, 6)):
    add(f"C06R{i+1}", "CORE", f"CORE_NOTES/C06_STREET_RESEARCH_R{i+1}.md", b,
        "Broker research (PDF extractions; tables often garbled one-cell-per-line: rebuild them). Skip disclosure/analyst-certification/ratings-distribution pages after confirming they hold no company-specific content.")

# ---------------- WORKING: DKS ----------------
k10 = rel(r"01_DKS_SEC_FILINGS\10-K\*.md")
add("W01", "WORKING", "WORKING_NOTES/W01_DKS_10K_FY2024-FY2025.md", [k10[3], k10[2]],
    "FY2025 10-K is the full reference (read it all). For FY2024 read its delta file (lines not in FY2025 10-K).")
add("W02", "WORKING", "WORKING_NOTES/W02_DKS_10K_FY2022-FY2023.md", [k10[1], k10[0]],
    "Both are delta-only (FY2023 vs FY2024; FY2022 vs FY2023). Read delta files; open originals for table context.")
q10 = rel(r"01_DKS_SEC_FILINGS\10-Q\*.md")
add("W03", "WORKING", "WORKING_NOTES/W03_DKS_10Q_FY22Q3-FY24Q3.md", q10[:7],
    "First 10-Q has no delta: read in full. Others: delta vs prior 10-Q.")
add("W04", "WORKING", "WORKING_NOTES/W04_DKS_10Q_FY25Q1-FY26Q2.md", q10[7:])
k8 = rel(r"01_DKS_SEC_FILINGS\8-K\*.md") + rel(r"01_DKS_SEC_FILINGS\8-K\exhibits\*.md")
k8 = sorted(k8, key=lambda p: os.path.basename(p).split("_")[2] if os.path.basename(p).count("_") >= 2 else p)
for i, b in enumerate(bins(k8, 3)):
    add(f"W05{'ABC'[i]}", "WORKING", f"WORKING_NOTES/W05_DKS_8K_PRESSRELEASES_{'ABC'[i]}.md", b,
        "8-K covers and exhibits (earnings press releases = full financial statements + non-GAAP bridges + guidance: keep every number).")
add("W06", "WORKING", "WORKING_NOTES/W06_DKS_DEBT_REGISTRATION_DOCS.md", rel(r"01_DKS_SEC_FILINGS\Debt-and-registration-docs\*.md"),
    "424B2_2026-09-22 and S-4_2026-06-05 and FWP are full references; the others are delta-only.")
m = r"01_DKS_SEC_FILINGS\Foot-Locker-merger-docs" + "\\"
ref = m + "DKS_424B3_2025-07-11.md"
n = len(open(os.path.join(SRC, ref), encoding="utf-8", errors="replace").read().splitlines())
half = n // 2
A.append({"id": "W07A", "tier": "WORKING", "output": "WORKING_NOTES/W07_FL_MERGER_PROSPECTUS_A.md",
          "note": f"Read ONLY lines 1-{half} of the final merger prospectus (another agent does the rest).",
          "files": [{"source": "SOURCE/" + ref.replace("\\", "/"), "kb": round(kb(ref)), "line_range": [1, half]}]})
A.append({"id": "W07B", "tier": "WORKING", "output": "WORKING_NOTES/W07_FL_MERGER_PROSPECTUS_B.md",
          "note": f"Read ONLY lines {half+1}-{n} of the final merger prospectus, then the three delta files (S-4/A, S-4, DEFM14A vs the final 424B3) and record what differed in earlier drafts.",
          "files": [{"source": "SOURCE/" + ref.replace("\\", "/"), "kb": round(kb(ref)), "line_range": [half + 1, n]}] +
                   [item(m + f) for f in ["DKS_S-4-A_2025-07-08.md", "DKS_S-4_2025-06-23.md", "FL_DEFM14A_Merger-Proxy-Prospectus_filed-2025-07-11.md"]]})
add("W08", "WORKING", "WORKING_NOTES/W08_DKS_FL_DEAL_COMMUNICATIONS_425.md", rel(r"01_DKS_SEC_FILINGS\Foot-Locker-merger-docs\425-deal-communications\*.md"),
    "All are delta-only vs the DKS 8-K material (processed elsewhere) and earlier 425s.")
add("W09", "WORKING", "WORKING_NOTES/W09_DKS_ANNUAL_REPORTS_TO_SHAREHOLDERS.md", rel(r"02_DKS_TRANSCRIPTS\annual_report_letters\DKS_Annual-Report-to-Shareholders_*.md"),
    "Delta-only vs the same-year 10-K (sentence-level). Many delta segments are table fragments re-split by PDF extraction: keep any number not obviously in the 10-K, plus all letter/highlights/proxy/directors/stock-performance content.")

# ---------------- WORKING: PEERS / SECTOR ----------------
for t, nb in [("NKE", 4), ("DECK", 5), ("ONON", 4)]:
    fs = rel(rf"04_PEERS\{t}\*.md")
    for i, b in enumerate(bins(fs, nb)):
        add(f"P{t}{i+1}", "WORKING", f"WORKING_NOTES/P_{t}_RESEARCH_{i+1}.md", b,
            "Peer research. Skip disclosure pages after confirming no company content. Always record any DKS read-through explicitly.")
add("PMISC", "WORKING", "WORKING_NOTES/P_ADIDAS_PUMA_ASO_FL_RESEARCH.md",
    rel(r"04_PEERS\ADIDAS_PUMA\*.md") + rel(r"04_PEERS\ASO\*.md") + rel(r"04_PEERS\FL\*.md"))
nk = rel(r"04_PEERS\NKE\sec_filings\NKE_10-K_*.md")
add("PNKEK", "WORKING", "WORKING_NOTES/P_NKE_10K.md", [nk[1], nk[0]], "FY2026 10-K full; FY2025 delta-only.")
nq = rel(r"04_PEERS\NKE\sec_filings\NKE_10-Q_*.md")
add("PNKEQA", "WORKING", "WORKING_NOTES/P_NKE_10Q_A.md", nq[:4], "First 10-Q full, rest delta-only.")
add("PNKEQB", "WORKING", "WORKING_NOTES/P_NKE_10Q_B.md", nq[4:])
add("PASOK", "WORKING", "WORKING_NOTES/P_ASO_10K.md", rel(r"04_PEERS\ASO\sec_filings\ASO_10-K_*.md"))
add("PASOQ", "WORKING", "WORKING_NOTES/P_ASO_10Q.md", rel(r"04_PEERS\ASO\sec_filings\ASO_10-Q_*.md"), "First 10-Q full, rest delta-only.")
fk = rel(r"04_PEERS\FL\sec_filings\FL_10-K_*.md")
add("PFLKA", "WORKING", "WORKING_NOTES/P_FL_10K_A.md", [fk[3]], "FY2024 10-K (latest) read in full.")
add("PFLKB", "WORKING", "WORKING_NOTES/P_FL_10K_B.md", [fk[2], fk[1], fk[0]], "Delta-only (each vs the next later 10-K).")
fq = rel(r"04_PEERS\FL\sec_filings\FL_10-Q_*.md")
for i, b in enumerate(bins(fq, 3)):
    add(f"PFLQ{'ABC'[i]}", "WORKING", f"WORKING_NOTES/P_FL_10Q_{'ABC'[i]}.md", b, "Read delta file where given, else full.")
f8 = rel(r"04_PEERS\FL\sec_filings\8-K\*.md")
for i, b in enumerate(bins(f8, 2)):
    add(f"PFL8{'AB'[i]}", "WORKING", f"WORKING_NOTES/P_FL_8K_{'AB'[i]}.md", b, "All delta-only vs DKS 8-K/425 material and earlier FL 8-Ks.")
add("W20", "WORKING", "WORKING_NOTES/W20_SECTOR_MACRO.md", rel(r"05_SECTOR_MACRO\*.md") + rel(r"05_SECTOR_MACRO\credit\*.md"))
add("W21", "WORKING", "WORKING_NOTES/W21_PEER_CONSENSUS_FINANCIALS_AND_PEER_MARKET_DATA.md",
    [p for d in ["DECK", "NKE", "ONON"] for p in rel(rf"06_BLOOMBERG_FINANCIALS\{d}\*.md")] +
    rel(r"08_MARKET_DATA\csv\peer_*.csv"),
    "Bloomberg tables: transcribe every number (compact tables). Peer CSVs: raw files are copied to CORE_NOTES/data/; write columns/coverage plus derived facts (monthly closes per ticker, YTD/1y/3y returns, drawdowns, full valuation snapshot table).")

# coverage check: every source file assigned exactly once
allsrc = {os.path.relpath(p, SRC).replace("\\", "/") for p in glob.glob(os.path.join(SRC, "**", "*.*"), recursive=True)}
assigned = [f["source"][7:] for a in A for f in a["files"]]
missing = sorted(allsrc - set(assigned))
dups = sorted({x for x in assigned if assigned.count(x) > 1})
json.dump(A, open(os.path.join(ROOT, "_PREP", "assignments.json"), "w"), indent=1)
print("assignments:", len(A), "| files assigned:", len(set(assigned)), "/", len(allsrc))
print("missing:", missing)
print("assigned twice:", dups)
for a in A:
    eff = sum(f["kb"] if "read_delta" not in f else os.path.getsize(os.path.join(ROOT, f["read_delta"])) / 1024 for f in a["files"])
    print(f'{a["id"]:8s} {len(a["files"]):3d} files  ~{eff:6.0f} KB to read  -> {a["output"]}')
