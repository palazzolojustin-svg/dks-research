"""X09: very slow polite loop for when Google Trends is throttling: one request every ~3 min, single try,
cycles over missing window batches (from X09_run_windows.BAT/WIN) until all saved or max passes.
Rerun: python X09_slow_loop.py [gap_seconds] [max_passes]
"""
import os, sys, time, requests
from X09_gtrends import fetch, RAW
from X09_run_windows import WIN, BAT

gap = int(sys.argv[1]) if len(sys.argv) > 1 else 180
passes = int(sys.argv[2]) if len(sys.argv) > 2 else 4
only_b = sys.argv[3].split(',') if len(sys.argv) > 3 else list(BAT)      # e.g. D,G
order = sys.argv[4].split(',') if len(sys.argv) > 4 else ['S25', 'S26', 'P25', 'P26', 'H24', 'H25']
for p in range(passes):
    todo = [(w, b) for b in only_b for w in order if not os.path.exists(os.path.join(RAW, f'X09_gt_win_{w}_{b}.csv'))]
    if not todo:
        break
    for w, b in todo:
        try:
            df = fetch(BAT[b], WIN[w], session=requests.Session(), tries=1)
            df.to_csv(os.path.join(RAW, f'X09_gt_win_{w}_{b}.csv')); print('saved', w, b, flush=True)
        except Exception as e:
            print('fail', w, b, flush=True)
        time.sleep(gap)
print('done', flush=True)
