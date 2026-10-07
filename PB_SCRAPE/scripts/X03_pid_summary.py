"""X03: summarise product-ID census files (raw/X03_pid_<brand>.txt, plus raw/X03_cdx_p_calia.txt).
Extracts the PID (last path segment of /p/<slug>/<PID>), its 2-digit year code, and the first capture
timestamp. Outputs raw/X03_pid_by_year.csv (brand x PID-year counts) and raw/X03_pid_first_seen.csv
(brand x first-seen-year counts).
Usage: python X03_pid_summary.py
"""
import os, re, glob, csv, collections

RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
OWNED = {"calia", "vrst", "dsg", "maxfli", "walter-hagen", "alpine-design", "ethos", "fitness-gear", "nishiki", "quest", "top-flite", "tommy-armour"}
PID_RX = re.compile(r"/p/([^/?#]+)/([0-9]{2}[a-z0-9]+)", re.I)


def load(brand):
    files = glob.glob(os.path.join(RAW, f"X03_pid_{brand}.txt*"))
    if brand == "calia":
        files.append(os.path.join(RAW, "X03_cdx_p_calia.txt"))
    pids = {}
    for fn in files:
        for line in open(fn, encoding="utf-8", errors="replace"):
            p = line.split()
            if len(p) < 2 or not p[0][:1].isdigit():
                continue
            ts, url = p[0], p[1]
            m = PID_RX.search(url)
            if not m:
                continue
            slug, pid = m.group(1).lower(), m.group(2).lower()
            if not slug.startswith(brand + "-"):
                continue
            # guard against e.g. "on-" matching "on-the-go" (only used for benchmark 'on')
            if pid not in pids or ts < pids[pid][0]:
                pids[pid] = (ts, slug)
    return pids


def main():
    brands = sorted({os.path.basename(f)[8:].split(".txt")[0] for f in glob.glob(os.path.join(RAW, "X03_pid_*.txt*"))
                     if "census" not in f and "by_year" not in f and "first_seen" not in f} | {"calia"})
    by_year = {}
    first = {}
    for b in brands:
        pids = load(b)
        y = collections.Counter("20" + pid[:2] for pid in pids)
        f = collections.Counter(ts[:4] for ts, _ in pids.values())
        by_year[b] = y
        first[b] = f
        print(b, len(pids), dict(sorted(y.items())))
    years = [str(x) for x in range(2014, 2027)]
    for name, d in (("by_year", by_year), ("first_seen", first)):
        with open(os.path.join(RAW, f"X03_pid_{name}.csv"), "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["brand", "owned"] + years + ["total"])
            for b in brands:
                w.writerow([b, int(b in OWNED)] + [d[b].get(yy, 0) for yy in years] + [sum(d[b].values())])


if __name__ == "__main__":
    main()
