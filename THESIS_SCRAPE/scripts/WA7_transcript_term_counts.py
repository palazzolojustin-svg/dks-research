"""WA7: term-frequency and analyst-question series across raw DKS management transcripts.

Rerun:  python THESIS_SCRAPE\\scripts\\WA7_transcript_term_counts.py
Reads:  SOURCE\\02_DKS_TRANSCRIPTS\\earnings_calls\\*.md, conferences\\*.md
Writes: THESIS_SCRAPE\\raw\\WA7_transcript_term_counts.csv (one row per transcript)
        THESIS_SCRAPE\\raw\\WA7_analyst_questions_cost.txt (analyst questions touching SG&A / flow-through / labor)
Method: management-speech term counts (all text minus analyst question blocks is not separated; counts are whole-transcript,
        boilerplate disclaimer stripped), plus analyst question blocks (text following an 'Analyst, ...' header line up to the
        next '.....' separator) classified by keyword.
"""
import re, csv, pathlib

ROOT = pathlib.Path(r"C:\Users\palaz\Downloads\DKS_RESEARCH")
SRC = ROOT / "SOURCE" / "02_DKS_TRANSCRIPTS"
OUT = ROOT / "THESIS_SCRAPE" / "raw"

TERMS = {
    "sga": r"SG&A",
    "leverage_word": r"\b(de)?leverag",
    "productivity": r"productiv",
    "efficien": r"efficien",
    "labor_payroll": r"\blabor\b|payroll|staffing|scheduling(?! purposes)",
    "teammate": r"teammate",
    "invest": r"\binvest",
    "healthcare": r"health ?care",
    "house_of_sport": r"House of Sport",
}
COST_Q = re.compile(r"SG&A|flow[- ]?through|leverage|\blabor\b|payroll|expense|cost structure|margin", re.I)
LABOR_Q = re.compile(r"\blabor\b|payroll|staff|teammate|store model|operating model|headcount|wage", re.I)

def date_of(name):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", name)
    return m.group(1) if m else ""

rows, qlog = [], []
for sub in ("earnings_calls", "conferences"):
    for f in sorted((SRC / sub).glob("*.md")):
        txt = f.read_text(encoding="utf-8", errors="ignore")
        cut = txt.find("Disclaimer")
        if cut > 0:
            txt = txt[:cut]
        row = {"date": date_of(f.name), "type": sub, "file": f.name}
        for k, pat in TERMS.items():
            row[k] = len(re.findall(pat, txt, flags=re.I))
        # analyst question blocks
        lines = txt.splitlines()
        blocks, i = [], 0
        while i < len(lines):
            if re.match(r"^Analyst,", lines[i].strip()):
                j, buf = i + 1, []
                while j < len(lines) and not lines[j].strip().startswith("....."):
                    buf.append(lines[j]); j += 1
                blocks.append(" ".join(buf)); i = j
            else:
                i += 1
        row["analyst_q_blocks"] = len(blocks)
        row["q_cost_margin"] = sum(1 for b in blocks if COST_Q.search(b))
        row["q_labor"] = sum(1 for b in blocks if LABOR_Q.search(b))
        for b in blocks:
            if COST_Q.search(b) or LABOR_Q.search(b):
                qlog.append(f"{row['date']} | {f.name} | labor={bool(LABOR_Q.search(b))} | {re.sub(r'\s+', ' ', b)[:600]}")
        rows.append(row)

rows.sort(key=lambda r: r["date"])
OUT.mkdir(parents=True, exist_ok=True)
with open(OUT / "WA7_transcript_term_counts.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
(OUT / "WA7_analyst_questions_cost.txt").write_text("\n".join(qlog), encoding="utf-8")
for r in rows:
    print({k: r[k] for k in r if k != "file"}, r["file"][:40])

