"""Build CORE_NOTES/00_CORE_INDEX.md and WORKING_NOTES/00_WORKING_INDEX.md from the `## SRC` headers in each notes file."""
import os, re, glob

ROOT = os.path.join(os.path.expanduser(r"~\Downloads"), "DKS_RESEARCH")

def build(folder, title, intro):
    files = sorted(f for f in glob.glob(os.path.join(ROOT, folder, "*.md")) if not os.path.basename(f).startswith("00_"))
    out = [f"# {title}", intro, "",
           "| file | chars | ~tokens | sources |", "|---|---|---|---|"]
    detail = []
    total = 0
    for f in files:
        txt = open(f, encoding="utf-8", errors="replace").read()
        total += len(txt)
        srcs = re.findall(r"^## SRC (.+?)(?:\s\|.*)?$", txt, flags=re.M)
        name = os.path.basename(f)
        out.append(f"| {name} | {len(txt):,} | {len(txt)//3.5:,.0f} | {len(srcs)} |")
        detail.append(f"\n## {name}")
        for line in re.findall(r"^## SRC .+$", txt, flags=re.M):
            detail.append("- " + line[7:].strip())
    out.append(f"| **TOTAL** | {total:,} | {total//3.5:,.0f} | |")
    with open(os.path.join(ROOT, folder, "00_" + ("CORE" if folder == "CORE_NOTES" else "WORKING") + "_INDEX.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out + detail) + "\n")
    print(folder, len(files), "files", f"{total:,} chars ~{total/3.5:,.0f} tokens")

build("CORE_NOTES", "CORE NOTES INDEX",
      "Every core-notes file and the source documents (SOURCE/ paths) each one covers, with one line per source: path | date | type/firm | period. Raw CSVs are in CORE_NOTES/data/.")
build("WORKING_NOTES", "WORKING NOTES INDEX",
      "Every working-notes file and the source documents (SOURCE/ paths) each one covers. Use this to pick which files the sweep agents read for a question. Prefixes: W0x = DKS SEC filings; P_ = peers (NKE, DECK, ONON, ASO, FL, Adidas/Puma); W20 = sector/macro/credit; W21 = peer Bloomberg consensus + peer market data.")
