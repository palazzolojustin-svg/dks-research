"""X09: matched-window share-of-search batches that AVOID the Mar-22..Jun-27-2026 Google Trends artifact.
Each window is queried separately; within a window values are relative, so compare RATIOS (owned / benchmark)
across windows, not raw levels.  Rerun: python X09_run_windows.py   -> raw/X09_gt_win_<window>_<batch>.csv
Daily resolution (windows < 270 days). Pacing 90 s; Google throttles (429 / TLS resets) after ~15-20 rapid calls.
Then analyse with X09_analyze_windows.py.
"""
from X09_gtrends import fetch, RAW
import os, time, requests, sys

WIN = {
    'S25': '2025-07-01 2025-10-05', 'S26': '2026-07-01 2026-10-05',      # post-artifact Jul-Sep(+Oct wk1)
    'P25': '2025-01-01 2025-03-20', 'P26': '2026-01-01 2026-03-20',      # pre-artifact Q1
    'H24': '2024-11-01 2025-01-31', 'H25': '2025-11-01 2026-01-31',      # holiday
}
BAT = {
    'A': ['calia', 'athleta', 'vuori', 'alo yoga', 'fabletics'],
    'G': ['maxfli', 'titleist pro v1', 'srixon', 'vice golf', 'kirkland golf balls'],
    'B': ['vrst', 'rhone', 'ten thousand', 'public rec', 'calia'],
    'D': ['vrst', 'dsg shorts', 'dsg leggings', 'dsg hoodie', 'dsg jacket'],
    'T': ['tommy armour', 'top flite', 'walter hagen golf', 'maxfli', 'wilson golf'],
}
if __name__ == '__main__':
    pause = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    s = requests.Session()
    for b, terms in BAT.items():
        for w, tf in WIN.items():
            out = os.path.join(RAW, f'X09_gt_win_{w}_{b}.csv')
            if os.path.exists(out):
                continue
            try:
                fetch(terms, tf, session=s).to_csv(out); print('saved', out, flush=True)
            except Exception as e:
                print('FAILED', w, b, e, flush=True)
            time.sleep(pause)
