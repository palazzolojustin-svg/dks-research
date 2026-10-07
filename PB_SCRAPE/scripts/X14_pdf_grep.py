"""X14: extract text from PDFs and print supply-chain stat lines. Usage: python X14_pdf_grep.py file1.pdf [file2.pdf ...]
Writes <file>.txt next to each pdf."""
import sys, re, os, logging
logging.disable(logging.CRITICAL)
import pypdf
KW = r'(?i)(active factor|factories|countries of operation|vertical brand suppliers|in scope|Tier 1|FACTORIES BY REGION|Asia|Latin America|North America|EMEA|high-risk|manufacturing partners|vendors)'
for f in sys.argv[1:]:
    txt = f[:-4] + '.txt'
    if not os.path.exists(txt):
        r = pypdf.PdfReader(f)
        t = '\n'.join((p.extract_text() or '') for p in r.pages)
        open(txt, 'w', encoding='utf-8').write(t)
    lines = open(txt, encoding='utf-8').read().split('\n')
    print('=====', f, len(lines))
    for i, l in enumerate(lines):
        if re.search(KW, l):
            print(i, ' | '.join(x.strip() for x in lines[max(0, i-2):i+3]))
