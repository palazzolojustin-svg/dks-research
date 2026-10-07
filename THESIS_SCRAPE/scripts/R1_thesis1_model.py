"""R1 (wave 4): copy of B7_thesis1_model.py with ONLY the inputs changed (scenario parameters, increment-evidence rows,
output file prefix). Engine, calendar, store paths and consensus are identical to B7.
Input changes vs B7 (see wave4\\R1.md): hos_inc bear/base/bull 10/16/22 -> 7/12/20 plus a 'low' scenario (base params, $7M);
s_new_hos 30/35/38 -> 26/30/35 (QCEW net-new recalibrated + Live Oak tax); s_mature 33 -> 31 base (Ridgedale CY2024 $31.2M).
Rerun:  python THESIS_SCRAPE\\scripts\\R1_thesis1_model.py      (from C:\\Users\\palaz\\Downloads\\DKS_RESEARCH)
Writes: THESIS_SCRAPE\\raw\\R1_opening_schedule.csv, R1_increment_evidence.csv, R1_backtest.csv,
        R1_quarterly_model.csv, R1_variance_summary.csv, R1_variance_grid.csv, R1_relo_sensitivity.csv ; prints all tables.

ORIGINAL B7 DOCSTRING:
B7 (wave 2): THESIS #1 definitive variance model (House of Sport / Field House comp floor vs consensus).

WHAT IT DOES (every output is INFERENCE from a model; inputs are sourced below)
1. Monthly cohort engine. Each House of Sport (HoS) / Field House (FH) opening is dated to a fiscal month.
   A RELOCATED store is in the comp base at once (Gupta 2024-11-26), so for its first 12 months it adds
   (new-format sales - replaced-store sales) = "increment" to comp; weights 0.5 (opening month) / 1.0 x 11 / 0.5
   (month 13). A NEW (non-relocation) store is outside comp for ~14 months but CANNIBALISES nearby comp stores;
   a cannibalisation charge per HoS opening (all HoS) is applied for 12 months.
   Mature HoS (open >12 months) comp at legacy comp + "mature differential".
   GameChanger adds 0.3pt/qtr (Wells Fargo). FY26 one-offs (World Cup, GGG clearance of FL stock) are lapped in FY27.
2. Two store paths: (a) CONSENSUS quarterly store path (Bloomberg setA/setB, printed 2026-10-04, C05 l.144-411);
   (b) EVIDENCE path from the H02 census + H06 hiring + H03 municipal dates (store by store, below).
3. Implied legacy comp INSIDE consensus = consensus comp - format increment + cannibalisation - GC - laps
   - (mature HoS weight x mature differential), computed on the consensus path.
4. Evidence model comp = legacy comp scenario + format terms on the evidence path. Variance vs consensus in
   pts -> $M revenue (x prior-year quarterly DKS-segment sales) + non-comp new-store revenue difference
   -> EPS at a stated flow-through (x (1-27.46%) / 89.09M shares).
"""
import csv, os, itertools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
TAX, SH = 0.2746, 89.09

# ---------------------------------------------------------------- calendar
FYS = ["FY23", "FY24", "FY25", "FY26", "FY27"]          # fiscal year = Feb..Jan
QL = [f"{fy}Q{q}" for fy in FYS for q in (1, 2, 3, 4)]  # quarter index 0..19
NM = len(QL) * 3                                         # month index 0 = Feb-2023
MONTH_NAMES = ["Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]
def m_of(fy, mon):            # fiscal month index for e.g. ("FY26","Aug")
    return FYS.index(fy) * 12 + MONTH_NAMES.index(mon)

# DKS-segment (DICK'S Business) net sales $M. Actuals: C01B PR bridges / F2 script. FY26 3Q/4Q and FY27: consensus
# = Bloomberg Revenue - Foot Locker contribution (C05 setA l.144-145; setB l.373-374).
SALES = {"FY22Q1": 2732.0, "FY22Q2": 3111.0, "FY22Q3": 2965.0, "FY22Q4": 3536.0,   # FY22 approx (only used for FY23 rows, not reported)
         "FY23Q1": 2842.2, "FY23Q2": 3223.6, "FY23Q3": 3042.4, "FY23Q4": 3705.9,
         "FY24Q1": 3018.4, "FY24Q2": 3473.6, "FY24Q3": 3057.2, "FY24Q4": 3893.6,
         "FY25Q1": 3174.68, "FY25Q2": 3646.62, "FY25Q3": 3236.86, "FY25Q4": 4050.79,
         "FY26Q1": 3377.44, "FY26Q2": 3849.89, "FY26Q3": 5072.52 - 1738.14, "FY26Q4": 6262.29 - 2139.45,
         "FY27Q1": 5250.72 - 1749.00, "FY27Q2": 5726.00 - 1725.35, "FY27Q3": 5214.94 - 1733.89, "FY27Q4": 6452.44 - 2174.61}
def py(ql):
    return f"FY{int(ql[2:4]) - 1}{ql[4:]}"
QSEAS = [3174.68, 3646.62, 3236.86, 4050.79]
QSEAS = [x / sum(QSEAS) for x in QSEAS]                       # FY25 quarterly mix 22.5/25.8/22.9/28.7%
INTRA = {0: [1/3]*3, 1: [1/3]*3, 2: [1/3]*3, 3: [0.28, 0.44, 0.28]}
MSHARE = [QSEAS[(m % 12) // 3] * INTRA[(m % 12) // 3][m % 3] for m in range(12)]   # share of annual sales by fiscal month

ACTUAL_COMP = {"FY24Q1": 5.3, "FY24Q2": 4.5, "FY24Q3": 4.3, "FY24Q4": 6.4, "FY25Q1": 4.5, "FY25Q2": 5.0,
               "FY25Q3": 5.7, "FY25Q4": 3.1, "FY26Q1": 6.0, "FY26Q2": 4.9}
CONS_COMP = {"FY26Q3": 1.69, "FY26Q4": 1.59, "FY27Q1": 2.41, "FY27Q2": 2.24, "FY27Q3": 3.19, "FY27Q4": 3.23}
GC = 0.3                                                     # GameChanger pts of comp (WF 8/10/26)

# ---------------------------------------------------------------- openings
# (label, fy, month or None=spread across quarter q, quarter, fmt, n, relocation fraction, source)
HIST = [
    # FY23: HoS 3 -> 12 (C01A 10-Q store tables: Q2FY23 10, Q3FY23 12); FH ~12 opened in FY23 (assumed even)
    ("FY23 HoS cohort", "FY23", None, 1, "H", 3, 0.8, "10-Q counts; split assumed"),
    ("FY23 HoS cohort", "FY23", None, 2, "H", 4, 0.8, "10-Q counts"),
    ("FY23 HoS cohort", "FY23", None, 3, "H", 2, 0.8, "10-Q counts"),
    *[("FY23 FH cohort", "FY23", None, q, "F", 3, 0.75, "FH ~12 at FYE23 (F4), split assumed") for q in (1, 2, 3, 4)],
    # FY24: HoS 12->19 = 2/0/3/2 (F2); 6 of 7 relocations; FH 3/4/4/4, 11 of 15 relocations (DKS primer)
    ("FY24 HoS", "FY24", None, 1, "H", 2, 6/7, "F2 / DKS primer"), ("FY24 HoS", "FY24", None, 3, "H", 3, 6/7, "F2"),
    ("FY24 HoS", "FY24", None, 4, "H", 2, 6/7, "F2"),
    *[("FY24 FH", "FY24", None, q, "F", n, 11/15, "F2") for q, n in ((1, 3), (2, 4), (3, 4), (4, 4))],
    # FY25: HoS 19->35 = 2/1/13/0, 13 of 16 relocations (FY25 10-K); Q3 cohort dated Aug-Oct 2025 (H05/H07: Dallas 9/10,
    # Jersey City 9/18, Live Oak 10/15, Polaris Aug, Leawood Sep ...) -> 3 Aug / 5 Sep / 5 Oct
    ("FY25 HoS", "FY25", None, 1, "H", 2, 13/16, "10-K"), ("FY25 HoS", "FY25", None, 2, "H", 1, 13/16, "10-K"),
    ("FY25 Q3 HoS cohort", "FY25", "Aug", 3, "H", 3, 13/16, "H05/H07 dates"),
    ("FY25 Q3 HoS cohort", "FY25", "Sep", 3, "H", 5, 13/16, "H05/H07 dates"),
    ("FY25 Q3 HoS cohort", "FY25", "Oct", 3, "H", 5, 13/16, "H05/H07 dates"),
    *[("FY25 FH", "FY25", None, q, "F", n, 13/15, "10-K / F2") for q, n in ((1, 4), (2, 4), (3, 6), (4, 1))],
    # FY26 actual: HoS 35->36->41 ; FH 42->44->52
    ("Amherst NY #1565", "FY26", "Mar", 1, "H", 1, 1.0, "H07: grand opening ~2026-03-13; replaced store unknown (assumed relo)"),
    ("Cedar Rapids IA #1661", "FY26", "Jun", 2, "H", 1, 1.0, "H03: relocation across street, opened 2026-06-03"),
    ("Gaithersburg MD #1634", "FY26", "Jun", 2, "H", 1, 1.0, "H05: in-place conversion"),
    ("Schaumburg IL #1660", "FY26", "Jun", 2, "H", 1, 1.0, "H03 log2: at site of existing DSG"),
    ("Niles OH #1686 (72K)", "FY26", "Jun", 2, "H", 1, 1.0, "H02-5: replaced 52K in same mall, 2026-06-26"),
    ("Arlington TX #1612", "FY26", "Jun", 2, "H", 1, 0.0, "H07: first sale 2026-06-17; net-new to city"),
    ("FY26 FH Q1", "FY26", None, 1, "F", 2, 0.87, "10-Q count"),
    ("FY26 FH Q2", "FY26", None, 2, "F", 8, 0.87, "10-Q count (Ann Arbor, ... )"),
]
# Forward EVIDENCE path (H02 census, H06 hiring, H03 municipal docs). relocation = same-center / <=1.5 mi DSG (H02-2)
EVID = [
    ("Greensburg PA #1617", "FY26", "Aug", 3, "H", 1, 1.0, "H02: opened 2026-08-07; H05 in-place"),
    ("Annapolis MD #1648", "FY26", "Aug", 3, "H", 1, 1.0, "H02: opened 2026-08-14; H05 in-place"),
    ("Thornton CO #1610", "FY26", "Sep", 3, "H", 1, 0.5, "H02: live on locator; ground-up Larkridge (relo status unknown)"),
    ("Raleigh Crabtree #1608", "FY26", "Oct", 3, "H", 1, 0.0, "H02: grand opening 10/9; nearest DSG 6.0 mi (infill)"),
    ("Frisco Stonebriar #1677", "FY26", "Oct", 3, "H", 1, 1.0, "H02/H03: GO 10/23-25; #421 next door (0.1 mi)"),
    ("Cherry Hill NJ #1625", "FY26", "Nov", 4, "H", 1, 1.0, "H02: 'opening in 2026'; relocation confirmed"),
    ("Novi MI #1615", "FY26", "Nov", 4, "H", 1, 1.0, "H06: hourly reqs since 8/17; 0.8 mi"),
    ("Sioux Falls SD #1676", "FY26", "Dec", 4, "H", 1, 1.0, "H06: hourly reqs since 9/16; 0.1 mi"),
    ("San Diego Mission Valley #1643", "FY27", "Apr", 1, "H", 1, 0.0, "H06 'next spring'; 3.8 mi infill"),
    ("Sacramento Arden Fair #1626", "FY27", "Apr", 1, "H", 1, 0.0, "H06 'opening next year'; 10.4 mi"),
    ("Springfield MO #1673", "FY27", "May", 2, "H", 1, 0.0, "H06 ESD 8/13; first-in-market (76 mi)"),
    ("King of Prussia", "FY27", "Jun", 2, "H", 1, 1.0, "H02: 2027; 0.3 mi #1110"),
    ("St Louis Galleria", "FY27", "Jun", 2, "H", 1, 0.0, "H02: construction Apr-26; 5.9 mi"),
    ("Peabody Northshore", "FY27", "Jul", 2, "H", 1, 1.0, "H02: Feb-27 CMBS / fall-27 mall; 0.8 mi Danvers"),
    ("Joliet Rock Run", "FY27", "Aug", 3, "H", 1, 0.5, "H03: back-to-school 2027; old Joliet DSG may become clearance"),
    ("Tysons Corner", "FY27", "Sep", 3, "H", 1, 0.0, "H02: fall 2027; 6.8 mi"),
    ("Tigard Washington Square", "FY27", "Sep", 3, "H", 1, 1.0, "H02: fall 2027; DSG same mall (month-to-month)"),
    ("Rockaway", "FY27", "Sep", 3, "H", 1, 1.0, "H02: FY27 likely; 0.2 mi"),
    ("Sarasota UTC #1629", "FY27", "Oct", 3, "H", 1, 1.0, "H02/H06: FY27 likely; 0.4 mi"),
    ("Poughkeepsie", "FY27", "Oct", 3, "H", 1, 1.0, "H02: FY27 likely; 0.0 mi #16"),
    ("Broomfield Flatiron", "FY27", "Oct", 3, "H", 1, 1.0, "H02: FY27 likely; 0.1 mi #423"),
    ("Hollywood Oakwood Plaza", "FY27", "Aug", 3, "H", 1, 0.0, "H02: FY27 likely; 6.8 mi"),
    ("Braintree South Shore", "FY27", "Oct", 3, "H", 1, 0.0, "H02/H05: placeholder listing; 7.9 mi"),
    ("Austin Barton Creek", "FY27", "Nov", 4, "H", 1, 0.0, "H02: late 2027; 8.5 mi"),
    ("Lubbock South Plains", "FY27", "Nov", 4, "H", 1, 0.0, "H02: FY27 likely; first-in-market (105 mi)"),
    # FH evidence path: FY26 guide ~20 -> 62 at FYE26 (cons 63); FY27 ~18 (cons +18 to 81)
    ("FH 3Q26", "FY26", None, 3, "F", 7, 0.87, "guide ~20 FY26"), ("FH 4Q26", "FY26", None, 4, "F", 3, 0.87, "guide"),
    ("FH 1Q27", "FY27", None, 1, "F", 4, 0.80, "run-rate ~18-20/yr"), ("FH 2Q27", "FY27", None, 2, "F", 5, 0.80, ""),
    ("FH 3Q27", "FY27", None, 3, "F", 6, 0.80, ""), ("FH 4Q27", "FY27", None, 4, "F", 3, 0.80, "Tomball/Bastrop new"),
]
def cons_path(hos_relo_fy27):
    """Bloomberg consensus EOP counts: HoS 41->47/49/53/59/66/69, FH 52->59/63/67/72/78/81."""
    out, hp, fp = [], 41, 52
    for (fy, q), h, f in zip([("FY26", 3), ("FY26", 4), ("FY27", 1), ("FY27", 2), ("FY27", 3), ("FY27", 4)],
                             [47, 49, 53, 59, 66, 69], [59, 63, 67, 72, 78, 81]):
        rh = 0.75 if fy == "FY26" else hos_relo_fy27
        out.append((f"cons HoS {fy}Q{q}", fy, None, q, "H", h - hp, rh, "BBG consensus count"))
        out.append((f"cons FH {fy}Q{q}", fy, None, q, "F", f - fp, 0.87 if fy == "FY26" else 0.80, "BBG consensus count"))
        hp, fp = h, f
    return out

def events_to_months(events):
    """expand to list of (month_index, fmt, n, relo_frac)"""
    out = []
    for lab, fy, mon, q, fmt, n, r, src in events:
        if n == 0:
            continue
        if mon:
            out.append((m_of(fy, mon), fmt, n, r))
        else:
            base = FYS.index(fy) * 12 + (q - 1) * 3
            for k in range(3):
                out.append((base + k, fmt, n / 3, r))
    return out

def hos_count_path(events):
    """HoS end-of-quarter counts implied by FYE22 = 3 plus events"""
    cnt, path = 3, []
    em = events_to_months(events)
    for qi in range(len(QL)):
        cnt_q = 3 + sum(n for (m, f, n, r) in em if f == "H" and m < (qi + 1) * 3)
        path.append(cnt_q)
    return path

def run(events, p):
    """p: dict(hos_inc, fh_inc, cannib, mature_diff, s_mature, s_new_hos, s_new_fh). returns per-quarter dict"""
    em = events_to_months(events)
    inc_m = [0.0] * (NM + 12)
    can_m = [0.0] * (NM + 12)
    new_m = [0.0] * (NM + 12)     # non-comp new-store revenue
    for m, fmt, n, r in em:
        inc = p["hos_inc"] if fmt == "H" else p["fh_inc"]
        snew = p["s_new_hos"] if fmt == "H" else p["s_new_fh"]
        for k in range(13):
            w = 0.5 if k in (0, 12) else 1.0
            mm = m + k
            if mm >= NM:
                break
            share = MSHARE[mm % 12]
            inc_m[mm] += n * r * inc * share * w
            if fmt == "H":
                can_m[mm] += n * p["cannib"] * share * w
        # new stores: revenue outside comp from opening to +14 months
        for k in range(15):
            mm = m + k
            if mm >= NM:
                break
            new_m[mm] += n * (1 - r) * snew * MSHARE[mm % 12] * (0.5 if k == 0 else 1.0)
    hpath = hos_count_path(events)
    res = {}
    for qi, ql in enumerate(QL):
        if py(ql) not in SALES:
            continue
        base = SALES[py(ql)]
        months = range(qi * 3, qi * 3 + 3)
        F = sum(inc_m[m] for m in months) / base * 100
        K = sum(can_m[m] for m in months) / base * 100
        NEW = sum(new_m[m] for m in months)
        n_mat = hpath[qi - 4] if qi >= 4 else 3
        w_m = n_mat * p["s_mature"] * QSEAS[qi % 4] / base
        res[ql] = dict(F=F, K=K, NEW=NEW, w_m=w_m, hos_eop=hpath[qi], base=base)
    return res

# ---------------------------------------------------------------- scenarios (inputs sourced in B7.md table)
# legacy = "evidence" legacy-fleet comp (non-HoS/FH stores, ex one-offs). laps = FY27 lap of FY26 one-offs
# (World Cup in 1H26, GGG clearance of FL inventory; sizes not disclosed -> assumptions).
SCEN = {
    # R1 inputs (reconciled increment; see wave4\R1.md section "Reconciliation"):
    "bear": dict(hos_inc=7.0, fh_inc=0.0, cannib=5.0, mature_diff=-4.0, s_mature=29.0, s_new_hos=26.0, s_new_fh=12.0,
                 legacy=0.5, legacy27=0.5, flow=0.108, laps={"FY27Q1": -0.5, "FY27Q2": -1.5, "FY27Q3": -0.3, "FY27Q4": -0.3},
                 relo27=0.54),
    "low": dict(hos_inc=7.0, fh_inc=2.0, cannib=2.5, mature_diff=0.0, s_mature=31.0, s_new_hos=30.0, s_new_fh=14.0,
                legacy=1.5, legacy27=2.25, flow=0.20, laps={"FY27Q1": -0.3, "FY27Q2": -1.0, "FY27Q3": -0.15, "FY27Q4": -0.15},
                relo27=0.54),
    "base": dict(hos_inc=12.0, fh_inc=2.0, cannib=2.5, mature_diff=0.0, s_mature=31.0, s_new_hos=30.0, s_new_fh=14.0,
                 legacy=1.5, legacy27=2.25, flow=0.20, laps={"FY27Q1": -0.3, "FY27Q2": -1.0, "FY27Q3": -0.15, "FY27Q4": -0.15},
                 relo27=0.54),
    "bull": dict(hos_inc=20.0, fh_inc=3.0, cannib=0.0, mature_diff=2.0, s_mature=35.0, s_new_hos=35.0, s_new_fh=14.0,
                 legacy=None, legacy27=None, flow=0.25, laps={"FY27Q1": 0.0, "FY27Q2": -0.5, "FY27Q3": 0.0, "FY27Q4": 0.0},
                 relo27=0.54),
}
HIST_ONEOFF = {"FY26Q1": 0.3, "FY26Q2": 1.0}   # base-case World Cup/Knicks benefit inside 1H26 actual comps (assumed)
TRAIL, BTLEG = {}, {}
# Evidence on incremental sales per HoS relocation (all sources in THESIS_SCRAPE wave files; see B7.md)
INC_EVID = [
    ["H07 (NY data.ny.gov ny73-2j3u)", "Victor NY (2021, relocation)", "measured", "county sporting-goods taxable sales excess vs control",
     "+$28.1M yr1 / +$26.2M yr2; robustness +$19-25M", 24.0, "net (in-county; lower bound for DKS)", "government tax data"],
    ["H07", "Johnson City NY (2023, relocation 47K->140K)", "measured", "Broome excess", "+$8.6M yr1 / +$4.7M yr2", 8.6, "net", "government tax data"],
    ["H07", "Latham NY (2023)", "measured", "Albany excess", "-$4.9M yr1 / +$4.4M yr2", 0.0, "net", "government tax data"],
    ["H05 (Google reviews, Apify)", "9 in-place conversions", "measured proxy", "review velocity vs own pre-period", "median 2.02x", 15.0,
     "gross", "(2.0-1) x ~$15M replaced store"],
    ["H03 (Corpus Christi Legistar 26-1417)", "Corpus Christi TX (2028, relocation)", "DKS projection", "revenue $20M -> $40M; visits 626K -> 2M+",
     "+$20M", 20.0, "gross", "company number in council memo"],
    ["Company Nov-25 deck + UBS 2026-03-02", "average HoS", "company/broker", "$35M yr-1 vs ~$15M replaced", "+$20M", 20.0,
     "gross ('before any expected cannibalization')", "unit economics"],
    ["H07 (TX data.texas.gov 7z4d-yf2c)", "Live Oak TX (2025, NET-NEW)", "measured", "city retail taxable sales excess", "~$25-30M/yr in-store -> $31-37M omni",
     None, "n/a (new store total, not an increment)", "validates ~$35M total"],
    ["H03 (Norman OK staff)", "Sooner Mall (new market, proposed)", "city projection", "taxable sales", "~$26M/yr", None, "n/a", "new store total"],
    ["H05", "25 mature HoS", "measured proxy", "review velocity vs legacy", "1.72x (2025) -> 1.54x (2026)", None, "n/a", "mature fade (bear mature diff)"],
    ["H05", "8 legacy stores 10-35 km from new HoS", "measured proxy", "relative review growth", "-18% vs other legacy", None, "cannibalisation",
     "bear cannib ~$5M/HoS"],
    ["H07-4 (TX permits)", "Baybrook, Polaris, Katy", "structure", "2-into-1 consolidations", ">=3 of 41 HoS", None, "lowers increment", "qualitative"],
    ["B2 interim (Placer Infogram)", "12 HoS vs DSG", "measured", "visits per location", "3.2-4.2x (Jul-23 to Feb-24)", None, "n/a",
     "visits >> sales multiple"],
    # --- added after coordinator message (wave1 H04, CMBS / landlord data) ---
    ["H04 (BBCMS 2025-5C38 CMBS term sheet, SEC)", "Tampa International Plaza HoS (opened Oct-2024)", "measured (landlord)",
     "gross sales first 3 months", "$12.3M -> ~$40-44M annualised (incl. holiday + opening lift)", 24.0,
     "gross", "INFERENCE: ~$38M run-rate after opening-lift haircut minus $13.9M DKS avg store = ~+$24M if a relocation"],
    ["H04 (Macerich Q2-26 call, 8-K decks)", "Freehold Raceway HoS (opened Oct-2025)", "measured (landlord, visits)",
     ">800K customers in ~9 months = ~1.07M/yr vs ~935K HoS avg (Placer FY24)", "+14% visits vs avg HoS -> ~$40M if sales track visits",
     25.0, "gross", "INFERENCE: $40M - ~$15M; NB H05 review proxy for Freehold was only 2.02x its own prior listing"],
    ["H04 (BANK 2025-BNK50 etc. CMBS)", "Washington Square OR (FY27 relocation)", "landlord projection + actual legacy",
     "legacy DKS $18.6M (2023) vs DKS national avg $13.9M; sponsor est. HoS $35M", "+$16.4M", 16.4, "gross",
     "A-mall relocations replace above-average stores"],
    ["H04 (Benchmark 2025-V19 / WFCM 2025-5C7 CMBS)", "Empire Mall Sioux Falls (4Q26 relocation)", "actual legacy + model",
     "legacy DKS $10.7M (2021) -> $12.2M (lease-yr 2024); HoS at company $35M", "+$22.8M", 22.8, "gross", "small-metro relocation of a below-average store"],
    ["H04 (CMBS)", "St Johns Town Center (legacy, not HoS)", "actual legacy", "2023 sales $20.1M (Simon est.)", "n/a", None, "n/a",
     "A-mall legacy stores run $18-21M (WS, St Johns, Mission Viejo $19.1M TTM)"],
    ["H04 (CMBS, DKS-supplied)", "DKS national average store", "company figure", "$13.9M sales per store (2023)", "n/a", None, "n/a",
     "confirms UBS ~$15M replaced-store base"],
    # --- R1 additions (wave 2/3 results) ---
    ["B11-3 (MN DOR gross, controls)", "Minnetonka/Ridgedale (2022, relocation)", "measured", "city 459 gross excess", "+$7-22M, central ~$12M", 12.0, "net", "government tax data"],
    ["B11-2 (VA taxable)", "Chesapeake (2023, 2-into-1)", "measured", "city 451 excess", "+$3-7M", 5.0, "net (understates comp: F&S recapture)", "government tax data"],
    ["B11-1 (VA taxable)", "Charlottesville (2025, 2-into-1)", "measured", "Albemarle 451 excess, 3 qtrs", "+$2-5M", 3.2, "net", "government tax data"],
    ["B9-1 + B11-3", "Ridgedale CMBS $31.2M CY2024", "measured (landlord)", "store sales minus ~$19M implied replaced", "~+$12M store", 14.4, "store->omni x1.18", "SEC 424H"],
    ["B5-1 recalibrated (R1)", "11 relocation/conversion QCEW events", "measured (jobs)", "116 excess jobs x $120K paired $/job x1.18",
     "B5 said $21-25M at $210-220K/job", 16.4, "net", "R1_reconcile.py: DKS paired $/job median $103K, pooled $120K"],
    ["R1 SUMMARY", "hard-sales relocation reads (tax x omni 1.18 + Ridgedale)", "INFERENCE", "weights 1/1/1/0.5/0.5/0.5",
     "mean $12.0M; raw tax median $6M / mean $8.5M; all-evidence weighted mean $14.9M", 12.0, "omni, comp basis", "R1 base"],
    ["SUMMARY", "n-weighted measured (3 county + 9 review + Tampa + Freehold = 14)", "INFERENCE",
     "(24 + 8.6 + 0 + 9 x 15 + 24 + 25)/14", "~$15.5M", 15.5, "mixed",
     "projections (CC 20, WS 16.4, Empire 22.8, company 20) avg ~$19.8M -> bear $10M / base $16M / bull $22M"],
]
FWD = ["FY26Q3", "FY26Q4", "FY27Q1", "FY27Q2", "FY27Q3", "FY27Q4"]
BT = ["FY24Q1", "FY24Q2", "FY24Q3", "FY24Q4", "FY25Q1", "FY25Q2", "FY25Q3", "FY25Q4", "FY26Q1", "FY26Q2"]

def implied_legacy(C, r, p, lap):
    und = C - r["F"] + r["K"] - GC - lap
    return und - r["w_m"] * p["mature_diff"]

def main():
    out_bt, out_q, out_sum = [], [], []
    print("=" * 110)
    print("BACK-TEST: implied legacy-fleet comp on ACTUAL quarters (same engine, actual store path)")
    trailing = {}
    for name, p in SCEN.items():
        r = run(HIST, p)
        vals = []
        for ql in BT:
            lg = implied_legacy(ACTUAL_COMP[ql], r[ql], p, HIST_ONEOFF.get(ql, 0.0))
            vals.append(lg)
            out_bt.append([name, ql, ACTUAL_COMP[ql], round(r[ql]["F"], 2), round(r[ql]["K"], 2), round(r[ql]["w_m"], 3),
                           round(lg, 2)])
        trailing[name] = sum(vals[-8:]) / 8
        BTLEG[name] = dict(zip(BT, vals))
        print(f"{name:5s} legacy " + " | ".join(f"{q[2:]} {v:+.2f}" for q, v in zip(BT, vals)) +
              f" | 8Q avg (24Q3-26Q2) {trailing[name]:+.2f} | min {min(vals[-8:]):+.2f}")
        print(f"{'':5s} format " + " | ".join(f"{q[2:]} {r[q]['F']-r[q]['K']:+.2f}" for q in BT) +
              f" | FY25 avg {sum(r[q]['F']-r[q]['K'] for q in BT if q.startswith('FY25'))/4:.2f}")
    SCEN["bull"]["legacy"] = round(trailing["bull"], 2); SCEN["bull"]["legacy27"] = round(trailing["bull"], 2)
    TRAIL.update(trailing)

    print("=" * 110)
    hdr = ["scenario", "quarter", "cons_comp", "cons_path_format_pts", "cons_path_cannib_pts", "laps_pts",
           "IMPLIED_legacy_in_consensus", "evidence_legacy", "evid_path_format_pts", "evid_path_cannib_pts",
           "model_comp", "variance_pts", "py_sales_$M", "comp_rev_var_$M", "noncomp_rev_var_$M", "total_rev_var_$M",
           "eps_var_at_scen_flow", "eps_var_at_20pct", "hos_eop_cons", "hos_eop_evid"]
    for name, p in SCEN.items():
        rc = run(HIST + cons_path(p["relo27"]), p)
        re_ = run(HIST + EVID, p)
        for ql in FWD:
            lap = p["laps"].get(ql, 0.0)
            C = CONS_COMP[ql]
            il = implied_legacy(C, rc[ql], p, lap)
            ev_leg = p["legacy"] if ql.startswith("FY26") else p["legacy27"]
            mc = ev_leg + re_[ql]["w_m"] * p["mature_diff"] + re_[ql]["F"] - re_[ql]["K"] + GC + lap
            vp = mc - C
            base = rc[ql]["base"]
            crev = vp / 100 * base
            nrev = re_[ql]["NEW"] - rc[ql]["NEW"]
            trev = crev + nrev
            eps_s = trev * p["flow"] * (1 - TAX) / SH
            eps_20 = trev * 0.20 * (1 - TAX) / SH
            out_q.append([name, ql, C, round(rc[ql]["F"], 2), round(rc[ql]["K"], 2), lap, round(il, 2), ev_leg,
                          round(re_[ql]["F"], 2), round(re_[ql]["K"], 2), round(mc, 2), round(vp, 2), round(base, 1),
                          round(crev, 1), round(nrev, 1), round(trev, 1), round(eps_s, 3), round(eps_20, 3),
                          round(rc[ql]["hos_eop"]), round(re_[ql]["hos_eop"])])
    print("QUARTERLY MODEL (pts unless noted)")
    print(" | ".join(hdr))
    for row in out_q:
        print(" | ".join(str(x) for x in row))

    # period summaries
    print("=" * 110)
    print("PERIOD SUMMARY")
    for name in SCEN:
        rows = [r for r in out_q if r[0] == name]
        for per, qs in (("2H FY26", ["FY26Q3", "FY26Q4"]), ("FY27", ["FY27Q1", "FY27Q2", "FY27Q3", "FY27Q4"])):
            rr = [r for r in rows if r[1] in qs]
            wsum = sum(r[12] for r in rr)
            cons = sum(r[2] * r[12] for r in rr) / wsum
            il = sum(r[6] * r[12] for r in rr) / wsum
            fmt_c = sum((r[3] - r[4]) * r[12] for r in rr) / wsum
            fmt_e = sum((r[8] - r[9]) * r[12] for r in rr) / wsum
            mc = sum(r[10] * r[12] for r in rr) / wsum
            trev = sum(r[15] for r in rr)
            eps_s = sum(r[16] for r in rr)
            eps20 = sum(r[17] for r in rr)
            rev_bps = trev / (15203.0 if per == "FY27" else 7457.2) * 1e4    # 2H26E cons DKS seg rev 3,334.4 + 4,122.8
            evl = SCEN[name]["legacy"] if per != "FY27" else SCEN[name]["legacy27"]
            gap = TRAIL[name] - il
            out_sum.append([name, per, round(cons, 2), round(fmt_c, 2), round(il, 2), round(TRAIL[name], 2), round(gap, 2),
                            evl, round(fmt_e, 2), round(mc, 2), round(mc - cons, 2), round(trev, 1), round(rev_bps),
                            SCEN[name]["flow"], round(eps_s, 2), round(eps20, 2)])
            print(f"{name:5s} {per:8s} cons comp {cons:.2f} | cons-path net format {fmt_c:.2f} | IMPLIED legacy {il:+.2f} "
                  f"(trailing {TRAIL[name]:+.2f}, decel {gap:.2f}pt) | evidence legacy {evl:+.2f} | evid-path net format {fmt_e:.2f} | "
                  f"model comp {mc:.2f} | var {mc-cons:+.2f}pt | rev {trev:+.0f}M ({rev_bps:+.0f}bp) | "
                  f"EPS {eps_s:+.2f} @ {SCEN[name]['flow']:.1%} / {eps20:+.2f} @20%")
        # 2-year stacked legacy comp implied by consensus vs history
        st = []
        for q27, q26, q25, q24 in (("FY27Q1", "FY26Q1", "FY25Q1", "FY24Q1"), ("FY27Q2", "FY26Q2", "FY25Q2", "FY24Q2"),
                                   ("FY27Q3", "FY26Q3", "FY25Q3", "FY24Q3"), ("FY27Q4", "FY26Q4", "FY25Q4", "FY24Q4")):
            il27 = [r[6] for r in rows if r[1] == q27][0]
            l26 = BTLEG[name].get(q26, [r[6] for r in rows if r[1] == q26][0] if q26 in FWD else None)
            hist = BTLEG[name][q25] + BTLEG[name][q24]
            st.append(f"{q27[2:]}: cons 2yr legacy stack {l26 + il27:+.1f} vs FY24+FY25 stack {hist:+.1f}")
        print(f"{'':14s}" + " | ".join(st))

    # grid: format parameter set x legacy comp, FY27, base laps, flow 20%
    print("=" * 110)
    print("GRID FY27: EPS variance at 20% flow-through (rows = format/cannibalisation parameter set; cols = legacy comp)")
    grid = []
    legs = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    for name, p0 in SCEN.items():
        p = dict(p0)
        rc = run(HIST + cons_path(p["relo27"]), p)
        re_ = run(HIST + EVID, p)
        line = []
        for lg in legs:
            tr = 0.0
            for ql in FWD[2:]:
                lap = SCEN["base"]["laps"].get(ql, 0.0)
                mc = lg + re_[ql]["w_m"] * p["mature_diff"] + re_[ql]["F"] - re_[ql]["K"] + GC + lap
                tr += (mc - CONS_COMP[ql]) / 100 * rc[ql]["base"] + re_[ql]["NEW"] - rc[ql]["NEW"]
            e = tr * 0.20 * (1 - TAX) / SH
            line.append(round(e, 2))
            grid.append([name, lg, round(tr, 1), round(e, 2)])
        print(f"{name:5s} params: " + " | ".join(f"leg {l:.1f}%: {e:+.2f}" for l, e in zip(legs, line)))

    # relocation-share sensitivity of the consensus-implied legacy comp (base params)
    print("=" * 110)
    print("SENSITIVITY: consensus-implied FY27 legacy comp vs FY27 HoS relocation share and HoS increment (base cannib/mature)")
    sens = []
    for relo in (0.44, 0.54, 0.80):
        for inc in (6.0, 8.0, 12.0, 16.0, 20.0):
            p = dict(SCEN["base"]); p["hos_inc"] = inc
            rc = run(HIST + cons_path(relo), p)
            qs = FWD[2:]
            wsum = sum(rc[q]["base"] for q in qs)
            il = sum(implied_legacy(CONS_COMP[q], rc[q], p, p["laps"].get(q, 0.0)) * rc[q]["base"] for q in qs) / wsum
            il_h2 = sum(implied_legacy(CONS_COMP[q], rc[q], p, 0.0) * rc[q]["base"] for q in FWD[:2]) / sum(rc[q]["base"] for q in FWD[:2])
            sens.append([relo, inc, round(il_h2, 2), round(il, 2)])
            print(f"FY27 relo share {relo:.0%}, HoS increment ${inc:.0f}M: implied legacy 2H26 {il_h2:+.2f}% | FY27 {il:+.2f}%")

    # write files
    def w(fn, header, rows):
        with open(os.path.join(RAW, fn), "w", newline="") as f:
            c = csv.writer(f); c.writerow(header); c.writerows(rows)
    w("R1_backtest.csv", ["scenario", "quarter", "actual_comp", "format_pts", "cannib_pts", "mature_weight", "implied_legacy_comp"], out_bt)
    w("R1_quarterly_model.csv", hdr, out_q)
    w("R1_increment_evidence.csv", ["source", "store", "type", "metric", "value", "increment_$M_per_yr_used",
                                    "gross_or_net_of_cannibalisation", "basis"], INC_EVID)
    w("R1_variance_summary.csv", ["scenario", "period", "cons_comp", "cons_path_net_format", "implied_legacy_in_cons",
                                  "trailing_8Q_legacy", "implied_deceleration_pts", "evidence_legacy", "evid_path_net_format", "model_comp", "variance_pts", "rev_var_$M",
                                  "rev_var_bps", "flow_through", "eps_var_at_flow", "eps_var_at_20pct"], out_sum)
    w("R1_variance_grid.csv", ["format_param_set", "legacy_comp", "FY27_rev_var_$M", "FY27_eps_var_20pct"], grid)
    w("R1_relo_sensitivity.csv", ["fy27_hos_relo_share", "hos_increment_$M", "implied_legacy_2H26", "implied_legacy_FY27"], sens)
    FIRST = ("Springfield MO", "Lubbock")
    def kind(lab, fmt, r):
        if any(f in lab for f in FIRST): return "first-in-market (no DSG within 65+ mi)"
        if r >= 0.99: return "relocation/conversion"
        if r <= 0.01: return "new (infill, in trade area of a comp DSG)"
        return "mixed/unknown"
    sched = []
    for lab, fy, mon, q, fmt, n, r, src in HIST + EVID:
        sched.append(["actual/evidence", lab, fy, q, mon or "spread", fmt, n, round(r, 2), kind(lab, fmt, r), src])
    for lab, fy, mon, q, fmt, n, r, src in cons_path(0.54):
        sched.append(["consensus", lab, fy, q, "spread", fmt, n, round(r, 2), "share", src])
    w("R1_opening_schedule.csv", ["path", "label", "fiscal_year", "quarter", "month", "format", "n", "relocation_fraction",
                                  "type", "source"], sched)
    print("=" * 110)
    print("OPENING SCHEDULE BY QUARTER (HoS openings: total / relocation-equivalent; FH openings)")
    for fy in ("FY25", "FY26", "FY27"):
        for q in (1, 2, 3, 4):
            ev = [e for e in HIST + EVID if e[1] == fy and e[3] == q]
            cs = [e for e in cons_path(0.54) if e[1] == fy and e[3] == q]
            eh = sum(e[5] for e in ev if e[4] == "H"); er = sum(e[5] * e[6] for e in ev if e[4] == "H")
            ef = sum(e[5] for e in ev if e[4] == "F")
            ch = sum(e[5] for e in cs if e[4] == "H"); cf = sum(e[5] for e in cs if e[4] == "F")
            line = f"{fy}Q{q}: actual/evidence HoS {eh:g} (relo-eq {er:.1f}) FH {ef:g}"
            if cs:
                line += f" | consensus HoS {ch:g} FH {cf:g}"
            print(line)

if __name__ == "__main__":
    main()
