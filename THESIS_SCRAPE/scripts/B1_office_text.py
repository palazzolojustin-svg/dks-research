"""B1: download a .pptx/.docx/.doc(x) attachment and dump its text (zip XML parse; no extra packages).
Rerun: python B1_office_text.py URL out_name   -> raw/B1_docs/<out_name>.<ext> and .txt
"""
import sys, os, re, zipfile, requests, io
D = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B1_docs'
os.makedirs(D, exist_ok=True)
url, name = sys.argv[1], sys.argv[2]
ext = url.split('?')[0].rsplit('.', 1)[-1].lower()
b = None
for a in range(4):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=120)
        if r.status_code == 200:
            b = r.content; break
    except Exception as e:
        pass
    import time; time.sleep(5 * (a + 1))
if b is None:
    print('FAILED'); sys.exit()
open(os.path.join(D, f'{name}.{ext}'), 'wb').write(b)
out = []
try:
    z = zipfile.ZipFile(io.BytesIO(b))
    names = sorted(z.namelist(), key=lambda n: [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', n)])
    for n in names:
        if re.match(r'(ppt/slides/slide\d+\.xml|word/document\.xml|ppt/notesSlides/notesSlide\d+\.xml)$', n):
            x = z.read(n).decode('utf8', 'ignore')
            x = re.sub(r'</a:p>|</w:p>', '\n', x)
            t = re.sub(r'<[^>]+>', '', x)
            out.append(f'=== {n}\n{t.strip()}')
except zipfile.BadZipFile:
    out.append(re.sub(r'[^\x20-\x7e\n]+', ' ', b.decode('latin1')))
txt = '\n'.join(out)
open(os.path.join(D, f'{name}.txt'), 'w', encoding='utf-8').write(txt)
print(len(b), 'bytes;', len(txt), 'chars')
print(txt[:12000])
