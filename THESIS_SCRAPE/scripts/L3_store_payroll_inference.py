"""L3: INFERENCE of legacy-store leadership payroll before vs after Built to Win, from posted pay bands (base pay zone)
and scenario role counts. Not company data: role counts per store are assumptions stated below; pay = midpoint of posted
"Targeted Pay Range" (base zone: IL/MA/MD/CO/MO/ME/NE), 2025 archived Workday postings (pre) vs 2026-10-07 live census (post).
Rerun: python L3_store_payroll_inference.py -> raw/L3_store_payroll_scenarios.csv
"""
import pandas as pd, os
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
HRS = 38 * 52                      # Team Captain bands are quoted "based on a 38 hour work week"; use same for FT hourly
PAY = {                            # annual, base-zone midpoints of posted bands
    'ASM_old': (50000 + 76000) / 2,          # 2025 DSG ASM Softlines/Hardlines/Ops (IL, OH, WA, NY postings)
    'ASM_new': (60000 + 84000) / 2,          # 2026 DSG ASM Sales/Operations (IL, MO, NY, OH, VA)
    'TC': (49500 + 63500) / 2,               # 2026 Team Captain, 38h/wk, 99-100% full time
    'Lead_old': (18 + 26) / 2 * HRS,         # 2025 DSG hourly Lead (87% FT), identical to 2026 Specialist band
    'Spec': (18 + 26) / 2 * HRS,
    'PT_hr': (15 + 22) / 2,                  # Teammate / associate hourly band midpoint (unchanged 2025->2026)
}
BURDEN_FT, BURDEN_PT = 1.25, 1.10            # payroll tax + benefits (FT incl. self-insured health ~$10K); assumption
STORES = 734                                 # DSG 630 + Field House 52 + GGG 52 (2026-08-01 store base; Built to Win scope = DICK'S + GGG)
TC_PER_STORE = 3200 / STORES                 # ">3,200 new leadership opportunities" (2026-04-14 release) = 4.36 per store
REV27, SH, TAX = 15203e6, 89.09e6, 0.2746
STORE_PAYROLL = 1.7e6                        # assumed legacy-store payroll (DICK'S personnel ~$2.0B FY25 / ~890 stores = $2.25M incl. non-store)

sc = {
 # name: (ASM before, ASM after, TCs filled by ex-ASMs, TCs filled by ex-Leads, note)
 'A promote-up: ASM layer kept (3->3), all TCs ex-Leads': (3, 3, 0, TC_PER_STORE, 'ASM band +$12K midpoint; each Lead->TC +$13K'),
 'B half re-slot: 0.5 ASM/store moves to TC': (3, 2.5, 0.5, TC_PER_STORE - 0.5, ''),
 'C re-slot: 1 ASM/store moves to TC (3->2)': (3, 2, 1, TC_PER_STORE - 1, 'fits Indeed "demoted" snippet and ASM posting freeze'),
 'D de-layer: 1 ASM/store exits (3->2), TCs ex-Leads': (3, 2, 0, TC_PER_STORE, 'ASM exits via severance'),
}
rows = []
for k, (a0, a1, tc_asm, tc_lead, note) in sc.items():
    before = a0 * PAY['ASM_old'] + (tc_asm + tc_lead) * 0  # TCs did not exist
    # people-level deltas
    d_asm_kept = min(a0, a1) * (PAY['ASM_new'] - PAY['ASM_old'])
    d_asm_to_tc = tc_asm * (PAY['TC'] - PAY['ASM_old'])
    d_asm_exit = -(a0 - a1 - tc_asm) * PAY['ASM_old'] if a0 - a1 - tc_asm > 0 else 0
    d_lead_to_tc = tc_lead * (PAY['TC'] - PAY['Lead_old'])
    gross = d_asm_kept + d_asm_to_tc + d_asm_exit + d_lead_to_tc
    burdened = gross * BURDEN_FT
    total = burdened * STORES
    bp = total / REV27 * 1e4
    eps = -total * (1 - TAX) / SH
    be_hours = burdened / (PAY['PT_hr'] * BURDEN_PT)
    rows.append([k, a0, a1, round(tc_asm, 2), round(tc_lead, 2), round(d_asm_kept), round(d_asm_to_tc), round(d_asm_exit), round(d_lead_to_tc),
                 round(gross), round(burdened), round(burdened / STORE_PAYROLL * 100, 1), round(total / 1e6, 1), round(bp, 1), round(eps, 2),
                 round(be_hours), round(be_hours / 52, 1), note])
o = pd.DataFrame(rows, columns=['scenario', 'ASM_before', 'ASM_after', 'TC_from_ASM', 'TC_from_Lead', 'd_ASM_kept_$', 'd_ASM_to_TC_$', 'd_ASM_exit_$',
                                'd_Lead_to_TC_$', 'gross_per_store_$', 'burdened_per_store_$', 'pct_of_store_payroll', 'total_$M_734_stores',
                                'bp_of_FY27E_DSG_rev', 'EPS_impact_$', 'breakeven_PT_hours_per_store_yr', 'breakeven_PT_hours_per_week', 'note'])
o.to_csv(os.path.join(RAW, 'L3_store_payroll_scenarios.csv'), index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 60)
print({k: round(v, 2) for k, v in PAY.items()}, 'TC/store', round(TC_PER_STORE, 2))
print(o.drop(columns=['note']).to_string())
# unit offsets (per store, burdened) and their fleet value
u_ft = PAY['Spec'] * BURDEN_FT
u_pt10 = PAY['PT_hr'] * 10 * 52 * BURDEN_PT
for name, val in [('one FT Lead/Specialist role removed per store', u_ft), ('10 fewer PT Teammate hours per week per store', u_pt10)]:
    tot = val * STORES
    print(f"{name}: ${val:,.0f}/store; fleet ${tot/1e6:,.1f}M = {tot/REV27*1e4:.1f}bp = ${tot*(1-TAX)/SH:.3f}/sh")
print('store payroll assumption', STORE_PAYROLL, '-> weekly hours at $19 avg x1.15 burden:', round(STORE_PAYROLL / (19 * 1.15) / 52))
