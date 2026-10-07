"""R8: timing / seasonality of DKS direct imports (entity Dick's Merchandising & Supply Chain) vs controls.
Question: is the Jul-Sep 2026 surge a holiday / spring-2027 pull-forward, a tariff-related restock, or a mix shift?
Uses entity monthly series (X04 or R8 refresh) and control company monthly series raw/*_iy_company_<slug>_monthly.csv.
Outputs raw/R8_timing_seasonality.csv, raw/R8_controls_q3.csv
Rerun: python R8_timing.py
"""
import os, glob
import pandas as pd

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
mfiles = sorted(glob.glob(os.path.join(RAW, "R8_dmsc_monthly_*.csv"))) or [os.path.join(RAW, "X04_dmsc_monthly_2026-10-07.csv")]
m = pd.read_csv(mfiles[-1])
m["y"] = m.month.str[:4].astype(int); m["mo"] = m.month.str[5:7].astype(int)


def season(df, label):
    rows = []
    for y in range(2016, 2027):
        d = df[df.y == y]
        if d.empty:
            continue
        tot = d.weight_kg.sum(); s = d.shipments.sum()
        jun = d[d.mo <= 6].weight_kg.sum()
        rows.append(dict(entity=label, year=y, ship=s, kg=tot,
                         h1_kg=jun, jul_sep_kg=d[d.mo.between(7, 9)].weight_kg.sum(), aug_sep_kg=d[d.mo.between(8, 9)].weight_kg.sum(),
                         oct_dec_kg=d[d.mo >= 10].weight_kg.sum(),
                         aug_sep_ship=d[d.mo.between(8, 9)].shipments.sum(),
                         aug_sep_vs_h1_monthly_avg=(d[d.mo.between(8, 9)].weight_kg.sum() / 2) / (jun / 6) if jun else None,
                         aug_sep_share_of_year=(d[d.mo.between(8, 9)].weight_kg.sum() / tot) if y < 2026 else None,
                         jul_sep_share_of_year=(d[d.mo.between(7, 9)].weight_kg.sum() / tot) if y < 2026 else None))
    return pd.DataFrame(rows)


s = season(m, "DKS_DMSC")
ctrl = []
for f in glob.glob(os.path.join(RAW, "*_iy_company_*_monthly.csv")):
    name = os.path.basename(f).split("_iy_company_")[1].replace("_monthly.csv", "")
    if "dick-s-merchandising" in name:
        continue
    c = pd.read_csv(f); c["y"] = c.month.str[:4].astype(int); c["mo"] = c.month.str[5:7].astype(int)
    ctrl.append(season(c, name))
allx = pd.concat([s] + ctrl)
allx.to_csv(os.path.join(RAW, "R8_timing_seasonality.csv"), index=False, float_format="%.3f")

if __name__ == "__main__":
    pd.set_option("display.width", 250)
    print(allx.round(3).to_string(index=False))
