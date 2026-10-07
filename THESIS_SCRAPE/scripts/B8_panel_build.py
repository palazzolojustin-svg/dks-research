"""B8 wave3: store-level DICK'S sales panel from CMBS filings (values transcribed from cached EDGAR docs, verified with B8_ctx.py),
same-store growth by fiscal year vs DKS reported comp, and level distribution vs DKS's $13.9M national average.
Rerun: python B8_panel_build.py -> raw/B8_cmbs_store_panel.csv, raw/B8_panel_growth.csv, stdout summary.
Fiscal mapping: CY20xx sales ~ DKS FY20xx (FY ends ~Jan 31 following year); TTM periods mapped to the FY they mostly overlap and flagged.
"""
import csv, os, statistics as st
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
E = "https://www.sec.gov/Archives/edgar/data/"
# store, location, venue type, SF, format, [(period_label, fy, sales_$ or None, psf or None, exact_fy_flag)], occ cost, url, filing date, note
P = [
 ("Empire Mall", "Sioux Falls SD", "regional mall (Simon)", 50300, "legacy DSG (HoS relocation 2026)",
  [("FY21", 2021, 10.7e6, 213, 1), ("FY22", 2022, 10.7e6, 213, 1), ("FY23", 2023, 11.7e6, 233, 1), ("FY24 lease yr Feb24-Jan25", 2024, 12.2e6, 243, 1)],
  "8.1%", E + "1258361/000153949725003123/n5481_x5-424h.htm", "2025-12-03", "HoS 100,709 SF lease from Sep-2026"),
 ("Cape Cod Mall", "Hyannis MA", "regional mall (Simon)", 45264, "legacy DSG",
  [("CY21", 2021, None, 233.01, 1), ("CY22", 2022, None, 298.80, 1), ("CY23", 2023, None, 337.98, 1), ("CY24", 2024, None, 340.80, 1), ("TTM 2/28/2025", 2024.5, None, 341.92, 0)],
  "6.5%", E + "1861132/000153949725001400/n5051_x9-424h.htm", "2025-05-15", "2019-20 NAV: store likely opened 2020-21 (ramp)"),
 ("Shops at Mission Viejo", "Mission Viejo CA", "regional mall (Simon)", 80000, "legacy DSG",
  [("CY22", 2022, 17.566e6, None, 1), ("CY23", 2023, 17.398683e6, None, 1), ("TTM 9/30/2024", 2024, 19.1e6, 239, 0)],
  "9.9%", E + "1541480/000153949725000119/n4723_x5-424h.htm", "2025-01-21", ""),
 ("Hamburg Pavilion", "Lexington KY", "open-air power/lifestyle center", 48000, "legacy DSG",
  [("2021 [sic $31/sf]", 2021, None, 31, 1), ("2022", 2022, None, 274, 1), ("2023", 2023, None, 265, 1), ("T-12 (~mid/late 2024)", 2024, None, 295, 0)],
  "3.4%", E + "1004158/000153949724002633/n4654_x5-424h.htm", "2024-12-12", "2021 $31 = partial year or typo"),
 ("Washington Square", "Portland OR", "A mall (Macerich)", 90000, "legacy DSG (HoS relocation fall-2027)",
  [("2019", 2019, 13.372103e6, None, 1), ("2022", 2022, 18.668948e6, None, 1), ("2023", 2023, 18.569941e6, None, 1)],
  "16.3%", E + "1004158/000153949725002080/n5230_x5-424h.htm", "2025-08-11", "2024 NAV; MTM lease"),
 ("St. Johns Town Center", "Jacksonville FL", "A open-air (Simon)", 66000, "legacy DSG",
  [("2019", 2019, 17.5e6, None, 1), ("2021", 2021, 20.1e6, None, 1), ("2022", 2022, 20.1e6, None, 1), ("2023", 2023, 20.1e6, 305, 1)],
  "7.0%", E + "2023106/000153949724001142/n4265_x2-premktts.htm", "2024-06-03", "Simon ESTIMATE (flat 2021-23): excluded from growth stats"),
 ("Brandon Mall (Westfield Brandon)", "Brandon FL", "regional mall", 45000, "legacy DSG",
  [("2020", 2020, None, 246, 1), ("2021", 2021, None, 350, 1), ("2022", 2022, None, 318, 1), ("TTM 2/28/2023", 2022.5, None, 318, 0)],
  "6.8%", E + "1547361/000153949723001134/n3498_x4-424h.htm", "2023-06-20", ""),
 ("Oxford Galleria II", "Oxford MS (open-air)", "community center", 35000, "legacy DSG",
  [("2021", 2021, 6.425688e6, 184, 1), ("2022", 2022, 6.216591e6, 178, 1)],
  "8.3%", E + "1541480/000153949723001750/n3791-x7_424h.htm", "2023-10-16", "pays 7% pct rent over $5.8M"),
 ("The Court at Oxford Valley", "Langhorne PA", "power center", 49381, "legacy DSG",
  [("2018", 2018, None, 298, 1), ("2019", 2019, None, 292, 1), ("2020", 2020, 12.751682e6, 258, 1)],
  "6.5%", E + "1005007/000153949721001412/n2711_x5-424h.htm", "2021-09-20", ""),
 ("Plaza on Richmond (Golf Galaxy)", "Houston TX", "anchored strip", 15078, "Golf Galaxy",
  [("2018", 2018, None, 319, 1), ("2019", 2019, None, 311, 1), ("2020", 2020, None, 306, 1), ("2021", 2021, None, 415, 1)],
  "10.0%", E + "1937096/000153949722001294/n3204_x2-prets.htm", "2022-07-28", ""),
 ("Concord Mills", "Concord NC", "outlet/value mall (Simon)", 53677, "legacy DSG (opened Feb-2021)",
  [("2021", 2021, None, 190, 1), ("TTM Aug-2022", 2022, 10.195946e6, 190, 0)],
  "8.9%", E + "1547361/000153949722001847/n3327_x9-424b2.htm", "2022-11-22", "store opened Feb-2021"),
 ("Crossgates Mall", "Albany NY", "super-regional mall", 80000, "legacy DSG",
  [("TTM 5/31/2025", 2025, 21.071582e6, 263, 0)], "8.1%", E + "1861132/000153949726001685/n5939_x5-424h.htm", "2026-06-08", "single point"),
 ("Westroads Mall", "Omaha NE", "regional mall", 84000, "legacy DSG",
  [("CY2025", 2025, 10.0e6, 119, 1)], "", E + "2136440/000153949726001656/n5926_x2-premrktts.htm", "2026-06-04", "single point; lease exp 1/31/2029, no renewal options"),
 ("Mall of Victor Valley", "Victorville CA", "regional mall (Macerich)", 49965, "legacy DSG",
  [("TTM 6/2024", 2024, 11.608518e6, 232.33, 0)], "8.5%", E + "1541480/000153949724002274/n4543-x6_424h.htm", "2024-10-28", "single point"),
 ("Galleria at Sunset", "Henderson NV", "regional mall", 81312, "legacy DSG (owned box)",
  [("TTM 1/31/2024 (=FY23)", 2023, 14.322628e6, 176, 1)], "", E + "1861132/000153949724000876/n4188-x7_424h.htm", "2024-04-19", "single point"),
 ("Green Acres", "Valley Stream NY", "regional mall", 70714, "legacy DSG",
  [("~2022", 2022, None, 173, 1)], "29.4%", E + "1005007/000153949723000147/n3430-x5_424h.htm", "2023-02-06", "rent $34.65/sf"),
 ("Scottsdale Fashion Square", "Scottsdale AZ", "A++ mall (Macerich)", 50646, "legacy DSG",
  [("2022", 2022, None, 363, 1)], "8.6%", E + "1970781/000153949723000828/n3566_x5-ts.htm", "2023-05-03", ""),
 ("Shoppes at River Crossing", "Macon GA", "lifestyle center", 50000, "legacy DSG",
  [("~2022", 2022, None, 360, 1)], "2.9%", E + "1967945/000153949723000419/n3489_x1-premktts.htm", "2023-03-13", ""),
 ("Shoppes at Blackstone Valley", "Millbury MA", "open-air center", 54159, "legacy DSG",
  [("FY18 (as of 1/31/2019)", 2018, 9.378102e6, 173, 1)], "7.7%", E + "1013454/000153949719002285/n1886-x16_424b2.htm", "2019-12-12", ""),
 ("Broadcasting Square", "Wyomissing PA", "open-air center", 45101, "legacy DSG",
  [("CY2018", 2018, None, 296, 1)], "4.0%", E + "1013454/000153949719001986/n1886_x4-424h.htm", "2019-11-12", ""),
 ("Cumberland Mall", "Atlanta GA", "regional mall", 70984, "legacy DSG",
  [("~TTM Jan-2023 (lender Q&A)", 2022, 24.0e6, None, 0)], "", E + "1984246/000153949723001301/n3688-x10_fwp.htm", "2023-07-25", "'Dick's sales are at $24mn' (FWP investor Q&A; rounded)"),
 ("Ridgedale Center", "Minnetonka MN", "A mall", 115262, "HOUSE OF SPORT (B9 domain)",
  [("CY2024", 2024, 31.197485e6, 271, 1)], "", E + "1005007/000153949725002024/n5210_x6-424h.htm", "2025-08-05", "HoS opened 2022; excluded from legacy stats"),
]
COMP = {2019: 3.0, 2020: 9.9, 2021: 11.3, 2022: -2.0, 2023: 2.6, 2024: 5.2, 2025: 4.5}  # FY19-22 = outside knowledge (DKS 10-Ks); FY23-25 in WORKING_NOTES W01/W05
rows = []
for s in P:
    name, loc, venue, sf, fmt, obs, occ, url, fd, note = s
    for lab, fy, sales, psf, exact in obs:
        if sales is None and psf is not None: sales_d = psf * sf; est = "psf x SF"
        else: sales_d = sales; est = "reported"
        rows.append(dict(store=name, location=loc, venue=venue, sf=sf, format=fmt, period=lab, fy=fy, sales=round(sales_d) if sales_d else "", psf=psf if psf else (round(sales / sf) if sales else ""), sales_basis=est, exact_fy=exact, occ_cost=occ, url=url, filing_date=fd, note=note))
with open(os.path.join(RAW, "B8_cmbs_store_panel.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# growth pairs (consecutive observations, legacy only, excl. estimate/ramp)
EXCL_STORE = {"St. Johns Town Center", "Ridgedale Center"}
g = []
for s in P:
    name = s[0]
    if name in EXCL_STORE: continue
    obs = [(fy, (sal if sal else psf * s[3]), lab, ex) for lab, fy, sal, psf, ex in s[5] if (sal or psf)]
    for a, b in zip(obs, obs[1:]):
        if b[0] - a[0] < 0.75 or b[0] - a[0] > 1.25: continue
        if name == "Hamburg Pavilion" and a[0] == 2021: continue  # $31 sic
        ramp = (name == "Cape Cod Mall" and a[0] <= 2022) or (name == "Concord Mills")
        g.append(dict(store=name, from_=a[2], to=b[2], fy=int(round(b[0])), s0=a[1], s1=b[1], growth=(b[1] / a[1] - 1) * 100, exact=int(a[3] and b[3]), ramp=int(ramp)))
with open(os.path.join(RAW, "B8_panel_growth.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(g[0].keys())); w.writeheader(); w.writerows(g)
print("PAIRS"); [print(f"  FY{x['fy']} {x['store'][:28]:28s} {x['from_']:>22s} -> {x['to']:<24s} {x['growth']:+6.1f}% exact={x['exact']} ramp={x['ramp']}") for x in g]
for fy in sorted({x['fy'] for x in g}):
    for lab, sel in [("all ex-ramp", [x for x in g if x['fy'] == fy and not x['ramp']]), ("exact-FY only ex-ramp", [x for x in g if x['fy'] == fy and not x['ramp'] and x['exact']])]:
        if not sel: continue
        med = st.median([x['growth'] for x in sel]); wt = (sum(x['s1'] for x in sel) / sum(x['s0'] for x in sel) - 1) * 100
        print(f"FY{fy} {lab:22s} n={len(sel)} median {med:+.1f}% weighted {wt:+.1f}% | DKS reported comp {COMP.get(fy)}%")
# levels: latest legacy observation per store (sales $)
lv = []
for s in P:
    if s[0] in EXCL_STORE or "HOUSE" in s[4] or "Golf" in s[4]: continue
    lab, fy, sal, psf, ex = s[5][-1]
    lv.append((s[0], fy, sal if sal else psf * s[3], s[3]))
vals = sorted(v[2] for v in lv)
print("LEVELS n=", len(vals), "median $%.1fM mean $%.1fM min $%.1fM max $%.1fM; above $13.9M: %d" % (st.median(vals) / 1e6, st.mean(vals) / 1e6, vals[0] / 1e6, vals[-1] / 1e6, sum(v > 13.9e6 for v in vals)))
psfs = sorted(v[2] / v[3] for v in lv); print("  median $/sf %.0f" % st.median(psfs))
for v in sorted(lv, key=lambda z: z[2]): print(f"   {v[0][:30]:30s} FY{v[1]} ${v[2]/1e6:5.1f}M  {v[3]:,} SF  ${v[2]/v[3]:.0f}/sf")
