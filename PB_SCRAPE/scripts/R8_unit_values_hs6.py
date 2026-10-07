"""R8: US import unit values at HS6 for the product types DKS's import suppliers ship (UN Comtrade public preview API, no key).
Output raw/R8_us_import_unit_values_hs6.csv. Rerun: python R8_unit_values_hs6.py
"""
import os, time, requests, pandas as pd
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
P = {"China": 156, "Vietnam": 704, "Taiwan": 490, "Cambodia": 116, "Indonesia": 360, "Thailand": 764}
CMD = "950632,950631,950691,950662,950699,950651,950659,940179,940171,630622,630629,871200,871680,640299,640192,732111,940490,420292,610462,610463,611030,610910,620342,621210,611241,610520,611710,950669,950670,950640,890399,392690,940370,950300"
rows = []
for yr in ["2024", "2025"]:
    for n, c in P.items():
        for a in range(3):
            try:
                j = requests.get("https://comtradeapi.un.org/public/v1/preview/C/A/HS", params={"reporterCode": "842", "period": yr, "partnerCode": str(c),
                                 "cmdCode": CMD, "flowCode": "M"}, timeout=90).json()
                for d in j.get("data", []):
                    rows.append(dict(year=yr, country=n, cmd=d["cmdCode"], value=d["primaryValue"], netwgt=d.get("netWgt"), qty=d.get("qty"), qtyunit=d.get("qtyUnitAbbr")))
                print(yr, n, len(j.get("data", [])), flush=True); break
            except Exception as e:
                print("retry", e); time.sleep(10)
        time.sleep(3)
df = pd.DataFrame(rows)
df["usd_per_kg_net"] = df.value / df.netwgt.where(df.netwgt > 0)
df["usd_per_unit"] = df.value / df.qty.where(df.qty > 0)
df.to_csv(os.path.join(RAW, "R8_us_import_unit_values_hs6.csv"), index=False)
pd.set_option("display.width", 250)
print(df[df.year == "2025"].pivot_table(index="cmd", columns="country", values="usd_per_kg_net").round(1).to_string())
print(df[(df.cmd == "871200")][["year", "country", "value", "qty", "usd_per_unit"]].to_string())
