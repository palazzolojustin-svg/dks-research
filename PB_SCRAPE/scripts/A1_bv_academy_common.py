"""A1: shared helpers for the Academy Sports (academy.com) Bazaarvoice front-door API.

Access: same public front-door as R1/X01 (no login, no passkey):
  https://apps.bazaarvoice.com/bfd/v1/clients/academy/api-products/cv2/resources/data/<products|reviews|categories>.json
  header bv-bfd-token: 9102,main_site,en_US ; Origin https://www.academy.com
Used by A1_bv_academy_*.py scripts.
"""
import time, requests, datetime as dt

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
CLIENT, DC, ORIGIN = "academy", "9102", "https://www.academy.com"


def session():
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
                      "bv-bfd-token": f"{DC},main_site,en_US", "Origin": ORIGIN, "Referer": ORIGIN + "/"})
    return s


def get(s, res, params, tries=5, raw=False):
    url = f"https://apps.bazaarvoice.com/bfd/v1/clients/{CLIENT}/api-products/cv2/resources/data/{res}.json"
    params = list(params) + [("apiversion", "5.4")]
    for i in range(tries):
        try:
            r = s.get(url, params=params, timeout=90)
            if r.status_code == 200:
                j = r.json()
                return j if raw else j.get("response", j)
            time.sleep(2 * (i + 1))
        except Exception:
            time.sleep(2 * (i + 1))
    return {"Results": [], "TotalResults": None, "Errors": ["failed"]}


def months(start=(2023, 1)):
    y, m = start
    now = dt.datetime.now(dt.timezone.utc)
    out = []
    while (y, m) <= (now.year, now.month):
        a = int(dt.datetime(y, m, 1, tzinfo=dt.timezone.utc).timestamp())
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        out.append((f"{y}-{m:02d}", a, int(dt.datetime(ny, nm, 1, tzinfo=dt.timezone.utc).timestamp())))
        y, m = ny, nm
    return out
