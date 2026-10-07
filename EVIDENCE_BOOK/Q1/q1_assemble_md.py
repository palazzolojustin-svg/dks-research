"""Assemble EVIDENCE_BOOK\\Q1.md = narrative head (EVIDENCE_BOOK\\Q1_narrative_head.tmp) + generated tables (Q1\\out\\tables.md)."""
import os, re
EB = r"C:\Users\palaz\Downloads\DKS_RESEARCH\EVIDENCE_BOOK"
head_p = os.path.join(EB, "Q1_narrative_head.tmp")
h = open(head_p, encoding="utf-8").read()
fix = {
    "and it is exactly the median of pre-COVID Q4s (FY15-FY19 Q4 2-yr stacks: 0.9 / 2.5 / 3.0 / \u22124.2 / 3.1)":
        "and in the 50th percentile of ex-COVID Q4s (median 5.6%). The FY15-FY19 Q4 2-yr stacks were 0.9 / 2.5 / 3.0 / \u22124.2 / 3.1",
    "(+$0.06-0.09 at segment OM). Real, but small against the stock's \u00b1$1-2 consensus EPS swings this year.":
        "(+$0.06-0.08 at segment OM). Real, but small next to the $2.50 FY26 guide cut.",
    "(digest s.3b; C02B l.326)": "(digest s.3b; C02B l.325)",
    "JPM's earlier 1H/2H core split was +4.2% / +2.5% (C06R2 l.451)": "JPM's earlier 1H/2H core split was +4.2% / +2.5% (C06R2 l.451, as cited by B7; not re-read)",
}
for a, b in fix.items():
    assert a in h, a[:60]
    h = h.replace(a, b)
t = open(os.path.join(EB, "Q1", "out", "tables.md"), encoding="utf-8").read()
t = re.sub(r"(?m)^\| (FY\d\dQ4) \| Q4 \|", r"| **\1** | Q4 |", t)
open(os.path.join(EB, "Q1.md"), "w", encoding="utf-8").write(h + "\n" + t)
os.remove(head_p)
print("Q1.md written", len(h + t), "chars")
