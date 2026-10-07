"""Q2 task 3: owned-brand mix -> DICK'S-segment gross-margin bridge vs Bloomberg consensus (FY27E, FY28E).

ALL OUTPUTS ARE MODEL ARITHMETIC (INFERENCE). Inputs and where they come from:
  REV          Bloomberg DICK'S segment revenue FY26E/27E/28E $14,753 / 15,203 / 15,742M (CORE_NOTES C05 L36; M1).
  CONS_GM      Bloomberg DSG GM ~36.2-36.3%; consensus FY26E->FY27E DSG GM change +7bps (user brief).
  PEN0         FY25 owned penetration of DICK'S non-footwear merchandise 19.05% (band 18.7-19.6; M1-1, 10-K FY25 $1.8B).
  FW0, OTH     FY25 DICK'S footwear share 30.33% (M1, FL 84% footwear strip); non-merch "Other" 3.4% (1H FY26 run-rate, M1-3).
  Consensus baseline = flat penetration, flat footwear, flat Other (i.e. no mix benefit in consensus GM).
  TAX 27.46%, SHARES 89.09M (both years, per brief), cons adj EPS FY27E $13.36 / FY28E $15.03 (C05 via M1).
  PREMIUM      mgmt 700-900bps owned-vs-national GM premium; markdown-adjusted tiers derived below from X11
               (PB_SCRAPE/raw/X11_yoy_summary.txt, Common Crawl dicks.com listing JSON, Aug+Sep 2025 vs 2026).
  EVIDENCE     review route: R1 apparel PIE+ORG Apr-Aug owned share 43.9 -> 46.0 (+4.8% relative) and R1-3 blended index
               y/y Q2 FY26 +4.3%, early Q3 +6.4%; beta 0.29-0.54 (R1-3 back-test vs 10-K, RELATIVE changes).
               listing route: R12 owned share of Common Crawl category listings 5.82 -> 6.76% (+0.94pt), used 1:1 as an upper bound.
RERUN: python Q2_margin_bridge.py   -> Q2_margin_bridge.csv, Q2_markdown_premium.csv, printed tables.
"""
import csv, os, itertools

OUT = os.path.dirname(os.path.abspath(__file__))
REV = {"FY26": 14753.08, "FY27": 15202.95, "FY28": 15741.60}
CONS_EPS = {"FY27": 13.36, "FY28": 15.03}
CONS_GM_CHG_FY27 = 7.0  # bps, FY26E -> FY27E
PEN0, FW0, OTH = 19.05, 30.33, 3.4
TAX, SH = 0.2746, 89.09
YRS = {"FY26": 1, "FY27": 2, "FY28": 3}

# ---------------- markdown-adjusted premium (X11) ----------------
# GM on realized price, cost fixed: m' = 1 - (1-m)/(1+dp) where dp = realized-price change.
def dm(m, dp):
    return (1 - (1 - m) / (1 + dp)) - m

MO, MN = 0.44, 0.36  # illustrative merchandise margins owned / national (800bp apart); results insensitive to +/-5pt levels
md_rows = []
cases = {
    # name: (owned avg disc 2025, 2026, national avg disc 2025, 2026) -> realized/list change
    "pooled avg discount (X11 a)": (0.181, 0.219, 0.073, 0.084),
    "matched-category avg discount (X11 a)": (0.197, 0.249, 0.085, 0.096),
}
for k, (o0, o1, n0, n1) in cases.items():
    dpo, dpn = (1 - o1) / (1 - o0) - 1, (1 - n1) / (1 - n0) - 1
    comp = (dm(MO, dpo) - dm(MN, dpn)) * 1e4
    md_rows.append((k, round(dpo * 100, 2), round(dpn * 100, 2), round(comp)))
# like-for-like products present in both years: realized offer owned -0.3% vs national -2.5% (X11 b)
dpo, dpn = -0.003, -0.025
md_rows.append(("like-for-like realized offer (X11 b)", -0.3, -2.5, round((dm(MO, dpo) - dm(MN, dpn)) * 1e4)))
with open(os.path.join(OUT, "Q2_markdown_premium.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["case", "owned_realized_price_chg_pct", "national_realized_price_chg_pct", "premium_change_bps"]); w.writerows(md_rows)

# Premium tiers used in the bridge (bps): mgmt range, markdown-adjusted central, stress
PREM = {"mgmt-high 900": 900, "mgmt-mid 800": 800, "mgmt-low 700": 700,
        "md-adj central 600": 600,   # 800 less ~200bps (pooled avg-discount compression, X11 a), LFL says ~0
        "md-adj stress 400": 400}    # 700 less ~300bps (matched-category compression, full pass-through)

# ---------------- evidence-implied penetration change per year ----------------
EVID = {}
for lab, rel in (("review Apr-Aug +4.8% rel", 0.048), ("review idx Q2 +4.3%", 0.043), ("review idx early-Q3 +6.4%", 0.064)):
    EVID[lab] = (round(rel * 0.29 * PEN0, 2), round(rel * 0.54 * PEN0, 2))
EVID["listing share +0.94pt (1:1, upper bound)"] = (0.94, 0.94)

PATHS = {"+0.25/yr": 0.25, "+0.50/yr": 0.50, "+0.75/yr": 0.75, "+1.00/yr": 1.00,
         "evid-low +0.25": 0.25, "evid-mid +0.45": 0.45, "evid-high +0.94": 0.94}
FWP = {"fw flat": 0.0, "fw -0.5/yr": -0.5, "fw -1/yr": -1.0, "fw +0.5/yr": 0.5}


def mix(pen, fw):
    return pen * (100 - fw - OTH) / 100  # owned % of DICK'S sales


base_mix = mix(PEN0, FW0)
rows = []
for (pn, dpen), (fn, dfw), (prn, prem) in itertools.product(PATHS.items(), FWP.items(), PREM.items()):
    r = {"pen_path": pn, "fw_path": fn, "premium": prn}
    for fy in ("FY26", "FY27", "FY28"):
        n = YRS[fy]
        mx = mix(PEN0 + dpen * n, FW0 + dfw * n)
        dmix = mx - base_mix                      # pt of DICK'S sales vs consensus flat mix (cumulative from FY25)
        r[f"{fy}_mix"] = round(mx, 3); r[f"{fy}_dmix_pt"] = round(dmix, 3)
        r[f"{fy}_gm_bps_cum"] = round(dmix * prem / 100, 2)
    for fy, prev in (("FY27", "FY26"), ("FY28", "FY27")):
        cum = r[f"{fy}_gm_bps_cum"]; inc = cum - r[f"{prev}_gm_bps_cum"]
        r[f"{fy}_gm_bps_yoy"] = round(inc, 2)
        for tag, bps in (("cum", cum), ("exFY26", r[f"{fy}_gm_bps_cum"] - r["FY26_gm_bps_cum"])):
            gp = bps / 1e4 * REV[fy]
            r[f"{fy}_gp_{tag}"] = round(gp, 1)
            r[f"{fy}_eps_{tag}"] = round(gp * (1 - TAX) / SH, 3)
            r[f"{fy}_eps_pct_{tag}"] = round(100 * gp * (1 - TAX) / SH / CONS_EPS[fy], 2)
        # cushion: bps of margin on national footwear sales (fw share of DICK'S sales) that the mix gain offsets
        fwshare = (FW0 + FWP[fn] * YRS[fy]) / 100
        r[f"{fy}_cushion_fw_bps_cum"] = round(cum / fwshare, 1)
    r["FY27_share_of_cons_+7bps_pct"] = round(100 * r["FY27_gm_bps_yoy"] / CONS_GM_CHG_FY27)
    rows.append(r)
with open(os.path.join(OUT, "Q2_margin_bridge.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, rows[0].keys()); w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    print("baseline owned mix of DICK'S sales (flat pen 19.05, fw 30.33, other 3.4):", round(base_mix, 2))
    print("\n=== markdown-adjusted premium change (bps, + = premium widens)")
    for x in md_rows: print(x)
    print("\n=== evidence-implied penetration change, pt/yr (low, high)")
    for k, v in EVID.items(): print(k, v)
    print("\n=== bridge, fw flat (FY27 / FY28): dmix pt | GM bps cum | GM bps y/y | EPS cum | EPS exFY26 | % of +7bps")
    for r in rows:
        if r["fw_path"] == "fw flat" and r["premium"] in ("mgmt-mid 800", "md-adj central 600", "md-adj stress 400", "mgmt-high 900"):
            print(f"{r['pen_path']:16s} {r['premium']:20s} FY27 {r['FY27_dmix_pt']:+.2f}pt {r['FY27_gm_bps_cum']:+5.1f}bps y/y {r['FY27_gm_bps_yoy']:+4.1f} "
                  f"EPS {r['FY27_eps_cum']:+.3f} (ex26 {r['FY27_eps_exFY26']:+.3f}) {r['FY27_share_of_cons_+7bps_pct']:3d}% | FY28 {r['FY28_dmix_pt']:+.2f}pt "
                  f"{r['FY28_gm_bps_cum']:+5.1f}bps EPS {r['FY28_eps_cum']:+.3f} ({r['FY28_eps_pct_cum']:.2f}%) cushion fw {r['FY28_cushion_fw_bps_cum']}bps")
    print("\n=== footwear drift effect (+0.50/yr pen, 600bps)")
    for r in rows:
        if r["pen_path"] == "+0.50/yr" and r["premium"] == "md-adj central 600":
            print(f"{r['fw_path']:12s} FY27 {r['FY27_dmix_pt']:+.2f}pt {r['FY27_gm_bps_cum']:+.1f}bps y/y {r['FY27_gm_bps_yoy']:+.1f} EPS {r['FY27_eps_cum']:+.3f} | FY28 {r['FY28_gm_bps_cum']:+.1f}bps EPS {r['FY28_eps_cum']:+.3f}")
