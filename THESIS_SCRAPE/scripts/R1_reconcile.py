"""R1 (wave 4): reconcile the HoS sales increment from QCEW jobs (B5) vs state tax data (H07/B11/B4) vs CMBS (B9).

Rerun:  python THESIS_SCRAPE\\scripts\\R1_reconcile.py   (from C:\\Users\\palaz\\Downloads\\DKS_RESEARCH)
Reads : THESIS_SCRAPE\\raw\\B5_event_summary.csv (per-event QCEW excess jobs, B5 wave 2/3)
Writes: THESIS_SCRAPE\\raw\\R1_paired_stores.csv, R1_jobs_recalibrated.csv, R1_increment_distribution.csv ; prints tables.

Every number below is either copied from a wave file (source in the row) or INFERENCE computed here.
"""
import csv, os, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")

# ------------------------------------------------------------------ 1. stores with BOTH QCEW jobs and tax $
# (store, type, qcew_y1_jobs, qcew_y2_jobs, tax_y1_$M, tax_y2_$M, tax source, note)
B5 = {r["city"]: r for r in csv.DictReader(open(os.path.join(RAW, "B5_event_summary.csv")))}
def j(city, col):
    v = B5[city][col]
    return float(v) if v else None
PAIRS = [
    ("Victor NY", "relocation (DSG only)", j("Victor", "y1_jobs"), j("Victor", "y2_jobs"), 28.1, 26.2, "H07-1 Ontario NY 4511/4591"),
    ("Johnson City NY", "relocation (DSG only, 47K->140K)", j("Johnson City", "y1_jobs"), j("Johnson City", "y2_jobs"), 8.6, 4.7, "H07-2 Broome"),
    ("Latham NY", "unknown / multi-door county", j("Latham", "y1_jobs"), j("Latham", "y2_jobs"), -4.9, 4.4, "H07-2 Albany"),
    ("Chesapeake VA", "2-into-1 in place (DSG+F&S)", j("Chesapeake", "y1_jobs"), j("Chesapeake", "y2_jobs"), 4.3, 7.1, "B11-2 Hampton Roads control"),
    ("Minnetonka MN", "relocation (DSG 'top performer')", j("Minnetonka", "y1_jobs"), j("Minnetonka", "y2_jobs"), 12.0, 12.0, "B11-3 central (annual gross 459; Hennepin QCEW base 2,331 jobs = noisy)"),
    ("Live Oak TX", "NET-NEW", j("Live Oak(San Antonio)", "y1_jobs"), None, 27.5, None, "H07-3 city retail, in-store annualised (Bexar QCEW)"),
    ("Charlottesville VA", "2-into-1 in place (DSG+Public Lands)", j("Charlottesville", "y1_jobs"), None, 3.2, None, "B11-1 (3 qtrs; QCEW 2 qtrs)"),
]
CALIB_B5 = [("Victor NY", 128.5, 28.1), ("Bass Pro Clifton Park (not DKS)", 148.0, 31.1)]

def main():
    print("=" * 100)
    print("1. SAME-STORE PAIRS: QCEW excess jobs (B5) vs tax-data excess $ (H07/B11)")
    rows = []
    for s, t, j1, j2, d1, d2, src, *_ in [p + ("",) for p in PAIRS]:
        r1 = d1 / j1 * 1000 if j1 and j1 > 20 else None
        r2 = d2 / j2 * 1000 if (j2 and d2 is not None and j2 > 20) else None
        rows.append([s, t, round(j1, 1) if j1 is not None else "", round(j2, 1) if j2 else "", d1, d2 if d2 is not None else "",
                     round(r1) if r1 else "", round(r2) if r2 else "", src])
        print(f"{s:20s} {t:38s} jobs y1 {j1:7.1f} y2 {(j2 or float('nan')):7.1f} | tax $M y1 {d1:6.1f} y2 {d2 if d2 is not None else float('nan'):6.1f} "
              f"| $K/job y1 {r1 if r1 else float('nan'):6.0f} y2 {r2 if r2 else float('nan'):6.0f}")
    # pooled ratio and through-origin OLS on DKS stores with jobs>20 (y1 and y2 observations)
    obs = []
    for s, t, j1, j2, d1, d2, src in PAIRS:
        if j1 and j1 > 20: obs.append((j1, d1, s + " y1"))
        if j2 and d2 is not None and j2 > 20: obs.append((j2, d2, s + " y2"))
    pooled = sum(d for _, d, _ in obs) / sum(x for x, _, _ in obs) * 1000
    ols0 = sum(x * d for x, d, _ in obs) / sum(x * x for x, _, _ in obs) * 1000
    ratios = [d / x * 1000 for x, d, _ in obs]
    med = st.median(ratios)
    # dispersion test: does the jobs number predict $? correlation across stores (y1, relocations only)
    xs = [x for x, _, _ in obs]; ds = [d for _, d, _ in obs]
    mx, md = st.mean(xs), st.mean(ds)
    cov = sum((a - mx) * (b - md) for a, b in zip(xs, ds)); vx = sum((a - mx) ** 2 for a in xs); vd = sum((b - md) ** 2 for b in ds)
    corr = cov / (vx * vd) ** 0.5
    print(f"\nDKS paired obs n={len(obs)}: pooled $/job = ${pooled:.0f}K | through-origin OLS ${ols0:.0f}K | median ratio ${med:.0f}K "
          f"| range ${min(ratios):.0f}-{max(ratios):.0f}K | corr(jobs,$) = {corr:+.2f}")
    print(f"B5 calibration used $210-220K/job from: " + "; ".join(f"{a} {b:.0f} jobs / ${c}M = ${c/b*1000:.0f}K" for a, b, c in CALIB_B5))
    ex_v = [r for r, (_, _, s) in zip(ratios, obs) if not s.startswith("Victor")]
    print(f"Ex-Victor median $/job = ${st.median(ex_v):.0f}K (n={len(ex_v)})")

    # ------------------------------------------------------------------ 2. staffing-template check
    print("=" * 100)
    print("2. STAFFING TEMPLATE: does +100-120 net jobs simply equal planned HoS heads minus replaced-store heads?")
    tmpl = [
        ("Novi MI plan (B1-1, DKS letter 2025-04-14)", 166, None, "HoS heads; replaced-store heads not stated"),
        ("Wells Fargo unit model (KNOWN)", 168, None, "HoS heads"),
        ("Corpus Christi council memo (H03/memo)", 147, 72, "relocation: staff 72 -> 147 for revenue $20M -> $40M"),
        ("Costa Mesa applicant (H03)", None, (34 + 55) / 2, "standard DSG 34-55 heads"),
    ]
    for a, h, l, n in tmpl:
        print(f"  {a:45s} HoS {h} | legacy {l} | {n}")
    for leg in (45, 55, 65, 72):
        print(f"  template delta at 166-168 HoS heads and {leg} legacy heads = +{166 - leg} to +{168 - leg} heads")
    print("  Corpus Christi: +75 heads for +$20M => DKS's own planning ratio = $%.0fK of incremental sales per incremental head" % (20 / 75 * 1000))
    print("  Company average: ($35M - $15M) / (167 - 50) heads = $%.0fK per incremental head" % (20 / 117 * 1000))

    # ------------------------------------------------------------------ 3. recalibrated B5 increments
    print("=" * 100)
    print("3. B5 EVENT-STUDY JOBS CONVERTED AT ALTERNATIVE $/JOB")
    groups = {"relocation/conversion mean (n=11)": 116, "relocation/conversion median": 102, "all clean mean (n=31)": 110,
              "all clean median": 102, "net-new mean (n=4)": 181, "net-new median": 194}
    conv = [("B5 (Victor + Bass Pro)", 215), ("company plan (avg)", round(20 / 117 * 1000)), ("DKS paired pooled", round(pooled)),
            ("DKS paired median", round(med)), ("DKS paired ex-Victor median", round(st.median(ex_v)))]
    out3 = []
    print("  " + " | ".join(f"{c[0]} ${c[1]}K" for c in conv))
    for g, jobs in groups.items():
        vals = [jobs * c[1] / 1000 for c in conv]
        out3.append([g, jobs] + [round(v, 1) for v in vals])
        print(f"  {g:36s} {jobs:4d} jobs -> " + " | ".join(f"${v:5.1f}M" for v in vals))
    with open(os.path.join(RAW, "R1_jobs_recalibrated.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["group", "excess_jobs"] + [f"$M_at_{c[0]}_{c[1]}K" for c in conv]); w.writerows(out3)

    # ------------------------------------------------------------------ 4. reconciled distribution (INFERENCE)
    # basis: comp increment per DSG-only relocation, year 1, OMNI (company basis), net of in-county DKS cannibalisation.
    # Tax/QCEW reads are IN-STORE: gross up x1.18 (store-reported ~80-84% of omni: B9-1; DKS eCom ~16-20%).
    OMNI = 1.18
    ev = [  # (label, value_$M_basis_adjusted, weight, basis note)
        ("Victor tax (H07) mid 23.5 x omni", 23.5 * OMNI, 1.0, "flagship, 2021 boom, single-DKS county"),
        ("Johnson City tax (H07) mid 6.7 x omni", 6.7 * OMNI, 1.0, "shrinking market"),
        ("Minnetonka tax (B11) central 12 x omni", 12.0 * OMNI, 1.0, "gross 459 incl misc retail; replaced a 'top performer'"),
        ("Latham tax (H07) ~0", 0.0, 0.5, "structure unknown; Crossgates DSG same county -> may be net-new less cannibalisation"),
        ("Chesapeake tax (B11) mid 5 x omni", 5.0 * OMNI, 0.5, "2-into-1: market-net understates COMP increment (F&S recapture)"),
        ("Charlottesville tax (B11) mid 2 x omni", 2.0 * OMNI, 0.5, "2-into-1, 3 quarters only"),
        ("QCEW reloc mean 116 jobs x paired $/job x omni", 116 * pooled / 1000 * OMNI, 1.0, "partly circular (calibrated on the tax stores)"),
        ("Google-review conversions 2.02x (H05) -> +15", 15.0, 1.0, "9 in-place conversions; proxy"),
        ("Tampa CMBS (H04/B9) ~38 run-rate - 13.9 avg replaced", 24.0, 0.75, "A+ mall; replaced Westshore sales unknown; opening lift"),
        ("Ridgedale CMBS store 31.2 - ~19 replaced (B9/B11), omni", (31.2 - 19.0) * OMNI, 0.5, "overlaps Minnetonka tax read"),
        ("Company/UBS +20 (gross, before cannibalisation)", 20.0, 0.5, "projection"),
        ("Corpus Christi council memo +20", 20.0, 0.5, "projection for 2028 store"),
    ]
    tw = sum(w for _, _, w, _ in ev)
    mean = sum(v * w for _, v, w, _ in ev) / tw
    # weighted median
    srt = sorted(ev, key=lambda e: e[1]); cum = 0; wmed = None; p25 = p75 = None
    for e in srt:
        cum += e[2]
        if p25 is None and cum >= 0.25 * tw: p25 = e[1]
        if wmed is None and cum >= 0.5 * tw: wmed = e[1]
        if p75 is None and cum >= 0.75 * tw: p75 = e[1]
    meas = [e for e in ev if "Company" not in e[0] and "Corpus" not in e[0]]
    mw = sum(w for _, _, w, _ in meas); mmean = sum(v * w for _, v, w, _ in meas) / mw
    print("=" * 100)
    print("4. RECONCILED RELOCATION INCREMENT (omni, comp basis, $M/yr, INFERENCE)")
    for l, v, w, n in ev:
        print(f"  {l:58s} {v:6.1f}  w={w:.2f}  ({n})")
    print(f"  weighted mean ${mean:.1f}M | weighted median ${wmed:.1f}M | P25 ${p25:.1f}M | P75 ${p75:.1f}M | measured-only mean ${mmean:.1f}M")
    with open(os.path.join(RAW, "R1_increment_distribution.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["evidence", "increment_$M_omni_basis", "weight", "note"])
        w.writerows([[l, round(v, 2), wt, n] for l, v, wt, n in ev])
        w.writerow(["SUMMARY weighted mean / median / P25 / P75 / measured-only mean", f"{mean:.1f}/{wmed:.1f}/{p25:.1f}/{p75:.1f}/{mmean:.1f}", "", ""])
    with open(os.path.join(RAW, "R1_paired_stores.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["store", "type", "qcew_y1_excess_jobs", "qcew_y2_excess_jobs", "tax_y1_excess_$M", "tax_y2_excess_$M",
                    "$K_per_job_y1", "$K_per_job_y2", "tax_source"])
        w.writerows(rows)

if __name__ == "__main__":
    main()
