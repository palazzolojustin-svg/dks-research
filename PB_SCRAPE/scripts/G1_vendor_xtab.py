"""G1: brand x vendor-code cross-tab of DKS style IDs (from R5 catalog) to spot styles carried over from another brand.
DKS item ids = 2-digit season + 3-letter vendor code. A DSG product with vendor code QUE (Quest) or PMD (PRIMED) is a
carried-over style. RERUN: python G1_vendor_xtab.py (needs raw/R5_catalog_brands_<date>.csv)."""
import pandas as pd, glob, os
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400); pd.set_option("display.max_columns", 50)
f = sorted(glob.glob(os.path.join(RAW, "R5_catalog_brands_*.csv")))[-1]
d = pd.read_csv(f, low_memory=False, dtype={"pre": str})
d = d.drop_duplicates("product_id")
print(f, len(d))
print(d.brand_id.value_counts().to_string())
x = pd.crosstab(d.brand_id, d.vendor)
for b in x.index:
    row = x.loc[b]; row = row[row > 0].sort_values(ascending=False)
    print(b, dict(row.head(12)))
