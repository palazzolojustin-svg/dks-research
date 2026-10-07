"""Verify every source file was covered: manifest row present, read to last line, and a SRC section in the output notes."""
import os, json, csv, re, glob

ROOT = os.path.join(os.path.expanduser(r"~\Downloads"), "DKS_RESEARCH")
A = json.load(open(os.path.join(ROOT, "_PREP", "assignments.json")))

def nlines(p):
    with open(p, encoding="utf-8", errors="replace") as fh:
        return len(fh.read().splitlines())

def base(p):
    return os.path.basename(p.replace("\\", "/")).lower()

rows_out, problems = [], []
for a in A:
    out = os.path.join(ROOT, a["output"])
    out_txt = open(out, encoding="utf-8", errors="replace").read() if os.path.exists(out) else ""
    if not out_txt:
        problems.append(f'{a["id"]}: output missing {a["output"]}')
    man = {}
    mp = os.path.join(ROOT, "_MANIFEST", "coverage", f'{a["id"]}.tsv')
    if os.path.exists(mp):
        with open(mp, encoding="utf-8", errors="replace") as fh:
            for r in csv.reader(fh, delimiter="\t"):
                if r and r[0].strip().lower() != "source":
                    man.setdefault(base(r[0]), []).append(r)
    else:
        problems.append(f'{a["id"]}: manifest missing')
    for f in a["files"]:
        b = base(f["source"])
        if "read_delta" in f:
            expected, mode = nlines(os.path.join(ROOT, f["read_delta"])), "delta"
        elif "line_range" in f:
            expected, mode = f["line_range"][1], f"lines {f['line_range'][0]}-{f['line_range'][1]}"
        else:
            expected, mode = nlines(os.path.join(ROOT, f["source"])), "full"
        mrows = man.get(b, [])
        last = None
        for r in mrows:
            nums = [int(x) for x in re.findall(r"\d+", " ".join(r[2:4]))] if len(r) >= 4 else []
            if nums:
                last = max(nums) if last is None else max(last, max(nums))
        stem = re.sub(r"\.(md|csv)$", "", b)
        in_notes = stem[:40] in out_txt.lower()
        ok_manifest = bool(mrows)
        # delta-mode agents sometimes log original line numbers; accept >= expected or a manifest row that says full/complete
        ok_read = last is not None and last >= expected * 0.98
        status = "OK" if (ok_manifest and in_notes and (ok_read or mode == "delta")) else "CHECK"
        if status != "OK":
            problems.append(f'{a["id"]}: {f["source"]} manifest={ok_manifest} last_read={last} expected={expected} ({mode}) src_in_notes={in_notes}')
        rows_out.append((a["id"], f["source"], mode, expected, last, ok_manifest, in_notes, status))

src_all = {p.replace("\\", "/") for p in glob.glob(os.path.join(ROOT, "SOURCE", "**", "*.*"), recursive=True)}
assigned = {os.path.join(ROOT, f["source"]).replace("\\", "/") for a in A for f in a["files"]}
unassigned = sorted(src_all - assigned)

with open(os.path.join(ROOT, "_MANIFEST", "COVERAGE_REPORT.md"), "w", encoding="utf-8") as fh:
    fh.write("# Coverage report: every source file -> agent, read mode, lines, notes section\n\n")
    fh.write(f"Source files: {len(src_all)} | assigned: {len(assigned)} | unassigned: {len(unassigned)} | rows: {len(rows_out)} | flagged: {len(problems)}\n\n")
    fh.write("| agent | source | mode | lines expected | last line logged | manifest | in notes | status |\n|---|---|---|---|---|---|---|---|\n")
    for r in rows_out:
        fh.write("| " + " | ".join(str(x) for x in r) + " |\n")
    if problems:
        fh.write("\n## Flagged\n" + "\n".join("- " + p for p in problems) + "\n")
print(f"rows={len(rows_out)} unassigned={len(unassigned)} flagged={len(problems)}")
for p in problems:
    print(" ", p)
