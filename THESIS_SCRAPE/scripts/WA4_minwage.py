"""WA4: DKS-footprint-weighted statutory minimum wage path.

Rerun: python THESIS_SCRAPE\\scripts\\WA4_minwage.py
Inputs:
  - DOL WHD 'State Minimum Wage Laws' page, current (Updated July 1, 2026) + Wayback snapshots
    (Mar-2024, Mar-2025, latest early-2026) -> basic state rate by state.
  - DICK'S Business U.S. store counts by state, 10-K FY2025 Item 2 (as of 2026-01-31), SOURCE\\01_DKS_SEC_FILINGS\\10-K\\DKS_10-K_FY2025_filed-2026-03-27.md l.1052-1080.
  - 2027 scheduled rates: hard-coded dict SCHED_2027 (sources listed in WA4.md), states with no known change carried flat.
Outputs: raw\\WA4_minwage_by_state.csv, raw\\WA4_minwage_weighted.csv
Notes: effective floor = max(state rate, federal 7.25). Multi-rate states use the rate below (NY upstate/downstate blend by store
location is approximated 50/50; OR standard rate). Local (city/county) minimums are ignored (understates CA/WA/CO/IL/MN level).
"""
import re, json, csv, sys, os, requests
from bs4 import BeautifulSoup

BASE = os.path.join(os.path.dirname(__file__), '..', 'raw')
H = {'User-Agent': 'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}
SNAPS = {
    '2024-03': 'http://web.archive.org/web/20240301011506/https://www.dol.gov/agencies/whd/minimum-wage/state',
    '2025-03': 'http://web.archive.org/web/20250303090553/https://www.dol.gov/agencies/whd/minimum-wage/state',
    'current': 'https://www.dol.gov/agencies/whd/minimum-wage/state',
}
STATES = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","District of Columbia","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]
# DICK'S Business stores by state, 10-K FY2025 Item 2 (2026-01-31); total 888
DKS = {"Alabama":15,"Alaska":0,"Arizona":14,"Arkansas":5,"California":65,"Colorado":18,"Connecticut":13,"Delaware":4,"District of Columbia":1,"Florida":59,"Georgia":26,"Hawaii":0,"Idaho":7,"Illinois":39,"Indiana":25,"Iowa":9,"Kansas":11,"Kentucky":13,"Louisiana":8,"Maine":4,"Maryland":22,"Massachusetts":23,"Michigan":26,"Minnesota":17,"Mississippi":7,"Missouri":15,"Montana":0,"Nebraska":5,"Nevada":6,"New Hampshire":7,"New Jersey":28,"New Mexico":4,"New York":49,"North Carolina":42,"North Dakota":1,"Ohio":48,"Oklahoma":10,"Oregon":11,"Pennsylvania":51,"Rhode Island":3,"South Carolina":15,"South Dakota":1,"Tennessee":20,"Texas":63,"Utah":6,"Vermont":2,"Virginia":32,"Washington":14,"West Virginia":6,"Wisconsin":17,"Wyoming":1}


def fetch(label, url):
    path = os.path.join(BASE, f'WA4_dol_state_{label}.html')
    if not os.path.exists(path):
        r = requests.get(url, headers=H, timeout=60)
        r.raise_for_status()
        open(path, 'w', encoding='utf-8').write(r.text)
    return open(path, encoding='utf-8').read()


def parse(html):
    t = BeautifulSoup(html, 'html.parser').get_text('\n', strip=True)
    out = {}
    names = sorted(STATES, key=len, reverse=True)
    lines = t.split('\n')
    cur = None
    for ln in lines:
        if ln in STATES:
            cur = ln
            continue
        if cur and cur not in out:
            m = re.search(r'Basic Minimum Rate \(per hour\):\s*\$([\d.]+)', ln)
            if m:
                out[cur] = float(m.group(1))
            elif 'No state minimum wage law' in ln:
                out[cur] = 7.25
    return out


# Jan-1-2027 scheduled/announced basic state rates (accessed 2026-10-07). Source per state in SRC27.
SCHED_2027 = {
    'California': 17.40, 'Washington': 17.73, 'New Jersey': 16.48, 'Ohio': 11.40, 'Maine': 15.70, 'Colorado': 15.71,
    'Michigan': 15.00, 'Arizona': 15.65, 'Minnesota': 11.87, 'Connecticut': 17.48, 'Virginia': 13.75, 'Rhode Island': 17.00,
    'Florida': 15.00,            # $15 effective 2026-09-30 (Amendment 2 final step); CPI indexing from 2027-09-30
    'New York': 'FROZEN',        # 2027 indexation off-ramp triggered by private job losses: stays $17.00 downstate / $16.00 upstate
    'Nebraska': 15.26,           # INFERENCE: 2025 law capped indexing (1.75%); press: '29 cents less than voters called for'
    'Vermont': 14.85, 'South Dakota': 12.20, 'Montana': 11.20,   # ASSUMED ~+3% CPI indexation (announcements not retrieved); 3 DKS stores total
    'Oregon': 15.55, 'District of Columbia': 18.40, 'Alaska': 14.00,  # July-indexed; carry the July-2026 rate as the Jan-2027 rate
}
SRC27 = {
    'California': 'CA DOF / Gov. Newsom release 2026-07-31 ($16.90 -> $17.40, +2.99%)',
    'Washington': 'WA L&I via Seattle Times/Seattle Weekly 2026-09-30 ($17.13 -> $17.73)',
    'New Jersey': 'NJ DOL via Bergen Record/WRNJ 2026-09-30 ($15.92 -> $16.48)',
    'Ohio': 'Ohio Dept of Commerce 2026-09-30 ($11.00 -> $11.40, +3.5%)',
    'Maine': 'Maine AFL-CIO / Bangor Daily News 2026-09-18 ($15.10 -> $15.70)',
    'Colorado': '9News 2026-08-14 ($15.16 -> $15.71)',
    'Michigan': 'DOL WHD state page (Updated 2026-07-01): $15.00 on 2027-01-01',
    'Arizona': 'KTAR / Capitol Times 2026-09-12/14 ($15.15 -> $15.65)',
    'Minnesota': 'MN DLI via press 2026-08-19 ($11.41 -> $11.87)',
    'Connecticut': 'CT.gov Gov. Lamont release 2026-08-05 ($16.94 -> $17.48)',
    'Virginia': 'doli.virginia.gov homepage (accessed 2026-10-07): $12.77 -> $13.75 on 2027-01-01',
    'Rhode Island': 'dlt.ri.gov minimum wage page: $17.00 commencing 2027-01-01',
    'Florida': 'press 2026-09-28..10-01 (USA Today network, ClickOrlando): $15 on 2026-09-30',
    'New York': 'Newsday/Syracuse.com/Times Union 2026-09-30..10-06: no Jan-2027 increase (job-loss off-ramp)',
    'Nebraska': 'Nebraska Examiner/MSN headline 2026-09-23 (exact rate not retrieved)',
}


def eff(x):
    return max(x, 7.25)


if __name__ == '__main__':
    rates = {k: parse(fetch(k, u)) for k, u in SNAPS.items()}
    json.dump(rates, open(os.path.join(BASE, 'WA4_dol_rates_parsed.json'), 'w'), indent=1)
    # NY two-tier: blend 50/50 downstate/upstate (DKS NY stores split ~ evenly between NYC metro/LI/Westchester and upstate; INFERENCE)
    ny = {'2024-03': (16.00 + 15.00) / 2, '2025-03': (16.50 + 15.50) / 2, 'current': (17.00 + 16.00) / 2}
    rows = []
    for s in STATES:
        r24 = ny['2024-03'] if s == 'New York' else rates['2024-03'][s]
        r25 = ny['2025-03'] if s == 'New York' else rates['2025-03'][s]
        if s == 'Michigan':
            r25 = 12.48  # MI rate from 2025-02-21 (SB 8); the Mar-2025 DOL snapshot still showed the Jan-2025 $10.56
        r26 = ny['current'] if s == 'New York' else rates['current'][s]
        sch = SCHED_2027.get(s, None)
        r27 = r26 if (sch is None or sch == 'FROZEN') else sch
        rows.append(dict(state=s, dks_stores=DKS[s], jan2024=eff(r24), jan2025=eff(r25), jan2026=eff(r26), jan2027=eff(r27),
                         src2027=SRC27.get(s, 'no scheduled change known -> carried flat' if sch is None else 'assumed index')))
    with open(os.path.join(BASE, 'WA4_minwage_by_state.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    N = sum(r['dks_stores'] for r in rows)
    out = []
    yrs = ['jan2024', 'jan2025', 'jan2026', 'jan2027']
    for i, y in enumerate(yrs):
        avg = sum(r[y] * r['dks_stores'] for r in rows) / N
        d = {'year': y, 'dks_weighted_avg_floor': round(avg, 3)}
        if i:
            p = yrs[i - 1]
            pavg = sum(r[p] * r['dks_stores'] for r in rows) / N
            d['yoy_pct_weighted_avg'] = round((avg / pavg - 1) * 100, 2)
            d['avg_of_store_pct_change'] = round(sum((r[y] / r[p] - 1) * r['dks_stores'] for r in rows) / N * 100, 2)
            d['share_stores_with_increase'] = round(sum(r['dks_stores'] for r in rows if r[y] > r[p] + 1e-9) / N * 100, 1)
            # among stores in states with floor >= $12 (where the floor plausibly binds on entry pay)
            hi = [r for r in rows if r[p] >= 12]
            nh = sum(r['dks_stores'] for r in hi)
            d['stores_floor_ge12'] = nh
            d['pct_change_floor_ge12_states'] = round(sum((r[y] / r[p] - 1) * r['dks_stores'] for r in hi) / nh * 100, 2) if nh else None
        out.append(d)
    with open(os.path.join(BASE, 'WA4_minwage_weighted.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for d in out for k in d}, key=lambda k: (k != 'year', k)))
        w.writeheader(); w.writerows(out)
    print('DKS stores weighted:', N)
    for d in out:
        print(d)
    print('\nTop contributors to Jan-2027 change (stores x $ change):')
    for r in sorted(rows, key=lambda r: -(r['jan2027'] - r['jan2026']) * r['dks_stores'])[:12]:
        print(f"  {r['state']:<15} stores {r['dks_stores']:>3}  {r['jan2026']:.2f} -> {r['jan2027']:.2f}  ({(r['jan2027']/r['jan2026']-1)*100:+.1f}%)")
    print('\nTop contributors to Jan-2026 change:')
    for r in sorted(rows, key=lambda r: -(r['jan2026'] - r['jan2025']) * r['dks_stores'])[:10]:
        print(f"  {r['state']:<15} stores {r['dks_stores']:>3}  {r['jan2025']:.2f} -> {r['jan2026']:.2f}  ({(r['jan2026']/r['jan2025']-1)*100:+.1f}%)")
