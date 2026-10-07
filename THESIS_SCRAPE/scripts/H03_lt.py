import requests, sys
c = sys.argv[1]
for f in ["substringof('Palmera',MatterTitle) and MatterIntroDate ge datetime'2023-01-01'",
          "substringof('Palmera',MatterTitle)"]:
    r = requests.get(f"https://webapi.legistar.com/v1/{c}/matters", params={"$filter": f, "$top": "5"}, timeout=30)
    print(r.status_code, r.text[:300])
