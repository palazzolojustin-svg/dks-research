"""Average HoS jobs gain per store across all sources (old QCEW y1 + new QCEW monthly + Census QWI), with exclusions,
then sales gain at $215K/job and lower sensitivities; plus revenue per additional employee at stores with known sales gains."""
import pandas as pd, statistics as st
b = pd.read_csv('/home/user/dks-research/THESIS_SCRAPE/raw/B5_event_summary.csv')
j3 = pd.read_csv('data/J03_robust.csv').set_index('city')['yoy_FebMar'].to_dict()
qwi = {'Kennesaw': 245, 'Freehold': 158, 'Leawood': 176.5, 'Live Oak(San Antonio)': 94,
       'Dallas(Galleria)': -307, 'Brandon': -62, 'Miami(Kendall)': -105}          # J02 DiD excess jobs
EXCL = {'Tulsa': 'Scheels opened in the same county the same quarter',
        'Harris(Baybrook+Katy)': 'two HoS plus a Field & Stream conversion in one county, same quarter',
        'Dallas(Galleria)': 'large county with unrelated sporting-goods closures; flagged contaminated',
        'Glendale': 'Maricopa County: ~9,000 base jobs, county noise far larger than one store',
        'Charlottesville': 'store sits on the city/county line; jobs likely booked in the adjacent county'}
rows = []
for _, r in b.iterrows():
    c = r['city']; vals = {'QCEW y1': r['y1_jobs']}
    if c in j3: vals['QCEW Feb-Mar'] = j3[c]
    if c in qwi: vals['QWI'] = qwi[c]
    t = r['type']; reloc = 'net-new' not in t
    rows.append(dict(store=c, opened=r['open_q'], kind='net-new' if not reloc else 'conversion/relocation',
                     sources=', '.join(f'{k} {v:+.0f}' for k, v in vals.items()), jobs=st.mean(vals.values()),
                     excluded=EXCL.get(c, '')))
d = pd.DataFrame(rows); d.to_csv('data/X_store_jobs_combined.csv', index=False)
k = d[d.excluded == '']
print(d[['store', 'opened', 'kind', 'sources', 'jobs', 'excluded']].round(0).to_string(index=False))
for lab, g in [('All kept stores', k), ('Conversions/relocations only', k[k.kind != 'net-new']), ('Net-new only', k[k.kind == 'net-new'])]:
    print(f"{lab}: n={len(g)} mean jobs {g.jobs.mean():.1f} median {g.jobs.median():.1f}")
