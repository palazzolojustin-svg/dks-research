"""B1: count yellow target-market stars on slide 18 ("Our goal is to open 75-100 stores ... by 2027") of the Braintree DKS deck.
Rerun: python B1_starcount.py  (needs raw/B1_braintree/16382.pdf). Renders page 18 at 300 dpi, thresholds yellow, labels blobs,
estimates star count = sum(round(blob_area / median_single_star_area)).
"""
import pymupdf, numpy as np
from scipy import ndimage
p = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B1_braintree\16382.pdf'
doc = pymupdf.open(p)
pg = doc[17]
pix = pg.get_pixmap(dpi=300)
a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3].astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
yel = (r > 200) & (g > 150) & (b < 90)
# exclude bottom banner / title area
h = yel.shape[0]
yel[: int(h * 0.30)] = False
yel[int(h * 0.92):] = False
lab, n = ndimage.label(yel)
areas = ndimage.sum(yel, lab, range(1, n + 1))
areas = areas[areas > 50]
med = np.median(np.sort(areas)[: max(1, len(areas) // 2)])  # small blobs ~ single stars
est = sum(max(1, round(x / med)) for x in areas)
print('blobs', len(areas), 'single-star area (median of smaller half)', med, 'estimated stars', est)
print('blob size multiples:', sorted([round(x / med, 1) for x in areas], reverse=True)[:30])
