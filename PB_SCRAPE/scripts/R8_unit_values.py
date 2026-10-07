"""R8: US import unit values ($ per kg) by HS chapter x origin country, from the UN Comtrade PUBLIC preview API (no key, no login).
Used to convert ImportYeti kg (gross weight) into an estimated customs value, so owned vs national shares can be value-weighted
(a treadmill kg is not an apparel kg) and the IEEPA refund can be reconciled.
Output: raw/R8_us_import_unit_values.csv (reporter USA=842, flow M, years 2024/2025).
Rerun: python R8_unit_values.py   (one request per partner-year, 3s apart)
"""
import os, time, requests, pandas as pd

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
PARTNERS = {"China": 156, "Vietnam": 704, "Cambodia": 116, "Indonesia": 360, "Taiwan": 490, "Thailand": 764, "Bangladesh": 50,
            "Myanmar": 104, "Dominican Republic": 214, "El Salvador": 222, "Mexico": 484, "Israel": 376, "Singapore": 702, "Pakistan": 586,
            "India": 699, "Philippines": 608, "Malaysia": 458, "Sri Lanka": 144, "Jordan": 400}
CHAPTERS = "39,40,42,61,62,63,64,65,73,76,84,87,90,94,95,96,8712,9506,9504,9503,6110,6104,6103,6109,6112,6114,6211,6212"
rows = []
for yr in ["2024", "2025"]:
    for name, code in PARTNERS.items():
        for attempt in range(3):
            try:
                r = requests.get("https://comtradeapi.un.org/public/v1/preview/C/A/HS",
                                 params={"reporterCode": "842", "period": yr, "partnerCode": str(code), "cmdCode": CHAPTERS, "flowCode": "M"}, timeout=90)
                j = r.json()
                for d in j.get("data", []):
                    rows.append(dict(year=yr, country=name, cmd=d["cmdCode"], value=d["primaryValue"], netwgt=d.get("netWgt"), qty=d.get("qty")))
                print(yr, name, len(j.get("data", [])), flush=True)
                break
            except Exception as e:
                print("retry", yr, name, e)
                time.sleep(10)
        time.sleep(3)
df = pd.DataFrame(rows)
df["usd_per_kg_net"] = df.value / df.netwgt
df.to_csv(os.path.join(RAW, "R8_us_import_unit_values.csv"), index=False)
print(df.pivot_table(index=["cmd"], columns=["country"], values="usd_per_kg_net", aggfunc="first").round(1).to_string())
