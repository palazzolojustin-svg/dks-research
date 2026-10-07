"""B1: OCR rendered PNG pages with rapidocr_onnxruntime (pip install rapidocr_onnxruntime).
Rerun: python B1_ocr.py <png_dir> <glob_prefix> <out_txt>
e.g. python B1_ocr.py ..\\raw\\B1_braintree 16388_p ..\\raw\\B1_braintree\\16388_ocr.txt
Lines are emitted in reading order (sorted by y then x of box top-left).
"""
import sys, glob, os
from rapidocr_onnxruntime import RapidOCR
eng = RapidOCR()
d, pref, out = sys.argv[1], sys.argv[2], sys.argv[3]
files = sorted(glob.glob(os.path.join(d, pref + '*.png')))
with open(out, 'w', encoding='utf-8') as f:
    for fp in files:
        if os.path.getsize(fp) == 0:
            continue
        res, _ = eng(fp)
        f.write(f'=== {os.path.basename(fp)}\n')
        if not res:
            continue
        rows = sorted(res, key=lambda r: (round(r[0][0][1] / 12), r[0][0][0]))
        line, cy = [], None
        for box, txt, conf in rows:
            y = round(box[0][1] / 12)
            if cy is not None and y != cy:
                f.write(' | '.join(line) + '\n'); line = []
            cy = y; line.append(txt)
        if line:
            f.write(' | '.join(line) + '\n')
        f.flush()
        print(fp, len(res), flush=True)
