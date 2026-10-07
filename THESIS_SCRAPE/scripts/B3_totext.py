"""B3: convert downloaded pdf/docx/pptx/doc files in raw/ to .txt next to them.
Rerun: python B3_totext.py <file> [file ...]   (paths relative to THESIS_SCRAPE or absolute)
"""
import sys, os


def pdf(p):
    import pdfplumber
    out = []
    with pdfplumber.open(p) as d:
        for i, pg in enumerate(d.pages):
            out.append(f"--- page {i+1} ---\n" + (pg.extract_text() or ""))
            for t in pg.extract_tables() or []:
                out.append("TABLE: " + " || ".join(" | ".join(str(c) for c in row) for row in t))
    return "\n".join(out)


def docx(p):
    import docx as D
    d = D.Document(p)
    out = [para.text for para in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            out.append(" | ".join(c.text.strip() for c in row.cells))
    return "\n".join(out)


def pptx(p):
    from pptx import Presentation
    pr = Presentation(p)
    out = []
    for i, s in enumerate(pr.slides):
        out.append(f"--- slide {i+1} ---")
        for sh in s.shapes:
            if sh.has_text_frame:
                out.append(sh.text_frame.text)
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    out.append(" | ".join(c.text for c in row.cells))
            if getattr(sh, "has_chart", False) and sh.has_chart:
                ch = sh.chart
                for pl in ch.plots:
                    cats = list(pl.categories)
                    for se in pl.series:
                        out.append(f"CHART {se.name}: " + ", ".join(f"{c}={v}" for c, v in zip(cats, se.values)))
        if s.has_notes_slide:
            out.append("NOTES: " + s.notes_slide.notes_text_frame.text)
    return "\n".join(out)


for f in sys.argv[1:]:
    ext = os.path.splitext(f)[1].lower()
    try:
        t = {".pdf": pdf, ".docx": docx, ".pptx": pptx}[ext](f)
    except Exception as e:
        t = f"ERR {e}"
    o = os.path.splitext(f)[0] + ".txt"
    open(o, "w", encoding="utf-8").write(t)
    print(o, len(t))
