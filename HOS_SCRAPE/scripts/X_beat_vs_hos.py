"""Correlate DKS core comp beat (and comp level) with LTM House of Sport openings."""
import pandas as pd, numpy as np
c = pd.read_csv('HOS_SCRAPE/data/comp_beat_history.csv', parse_dates=['period_end'])
m = pd.read_csv('HOS_SCRAPE/data/J01_hos_master.csv')
m = m[m.status.str.startswith('open')].copy(); m['d'] = pd.to_datetime(m.open_date, errors='coerce'); m = m.dropna(subset=['d'])
c['ltm_hos'] = [((m.d > e - pd.Timedelta(days=364)) & (m.d <= e)).sum() for e in c.period_end]
c['cum_hos'] = [(m.d <= e).sum() for e in c.period_end]
def r(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float); n = len(x); rr = np.corrcoef(x, y)[0, 1]
    t = rr * np.sqrt((n - 2) / (1 - rr ** 2)); return n, rr, t
b = c.dropna(subset=['beat_pp'])
print(c[['fiscal_q', 'actual_comp', 'consensus_comp', 'beat_pp', 'ltm_hos', 'cum_hos']].to_string(index=False))
print('beat vs LTM HoS: n=%d r=%.2f t=%.2f' % r(b.ltm_hos, b.beat_pp))
k = c[c.fiscal_q >= 'FY23Q1']  # ex-COVID swings
print('comp level vs LTM HoS (FY23Q1+): n=%d r=%.2f t=%.2f' % r(k.ltm_hos, k.actual_comp))
c.to_csv('HOS_SCRAPE/data/comp_beat_vs_hos.csv', index=False)
