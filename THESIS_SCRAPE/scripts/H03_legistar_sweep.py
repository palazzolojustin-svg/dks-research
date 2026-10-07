"""H03: sweep many Legistar clients for matters mentioning House of Sport / Dick's Sporting Goods / Field House (2023+).
Rerun: python H03_legistar_sweep.py   -> writes raw/H03_legistar_sweep.csv (client, matterId, file, date, title)
Client slugs are guesses; invalid slugs just return an error and are skipped.
"""
import requests, time, csv, os
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
CLIENTS = """arlington arlingtontx dallascityhall sanantonio houston fortworthgov fortworth plano frisco mckinney roundrock lubbock sugarland pearland
katy elpaso mesa chandler tempe phoenix tucson glendale-az gilbert peoria-az scottsdale denver coloradosprings auroragov lakewood westminster thornton
okc oklahomacity tulsa kansascity kcmo wichita omaha desmoines minneapolis stpaul bloomington rochester madison milwaukee chicago schaumburg naperville
rockford peoria columbus cincinnati cleveland toledo akron dayton detroit grandrapids annarbor lansing novi indianapolis fortwayne louisville lexington
nashville knoxville memphis chattanooga atlanta sandysprings alpharetta gwinnettcounty charlotte charlottenc raleigh durham greensboro columbia charleston
jacksonville tampa stpete orlando miamidade broward fortlauderdale tallahassee richmond virginiabeach norfolk alexandria fairfaxcounty montgomerycountymd
baltimore annapolis phila pittsburgh harrisburg allentown newark jerseycity boston worcester providence hartford newhaven buffalo syracuse sacramento
fresno sanjose oakland sfgov lacity longbeach anaheim costamesa irvine riverside sandiego chulavista portland seattle tacoma bellevue spokane boise
slc reno albuquerque cerritos brea mentor strongsville frederickcountymd frederick palmbeachgardens braintree burlington natick framingham
sioux-falls siouxfalls cedarrapids iowacity fargo lincoln springfield stlouis stlouiscounty overlandpark olathe lenexa leawood independence
murfreesboro franklin brentwood hoover huntsville birmingham mobile montgomery baton-rouge brla shreveport lafayette jackson littlerock fayetteville
lasvegas henderson clarkcounty sparks provo orem ogden sandy westjordan saltlakecounty meridian nampa eugene salem vancouver everett kent renton
lynnwood federalway alameda hayward fremont santaclara sunnyvale roseville elkgrove stockton modesto visalia bakersfield ontario rancho fontana
temecula murrieta corona torrance carson pasadena glendale burbank thousandoaks ventura oxnard santabarbara slo santamaria santarosa vacaville
""".split()
TERMS = ["House of Sport", "Dick's Sporting", "Dicks Sporting", "DICK'S", "Field House"]
out = open(os.path.join(RAW, "H03_legistar_sweep.csv"), "w", newline="", encoding="utf-8")
w = csv.writer(out); w.writerow(["client", "term", "matterId", "file", "introDate", "title"])
valid = 0
for c in CLIENTS:
    ok = False
    for t in TERMS:
        tt = t.replace("'", "''")
        params = {"$filter": f"substringof('{tt}',MatterTitle) and MatterIntroDate ge datetime'2023-01-01'", "$top": "200"}
        r = None
        for attempt in range(2):
            try:
                r = requests.get(f"https://webapi.legistar.com/v1/{c}/matters", params=params, timeout=20)
                break
            except Exception as e:
                print("  ", c, t, "ERR", type(e).__name__, flush=True)
                time.sleep(3); r = None
        if r is None or r.status_code != 200:
            break
        try:
            js = r.json()
        except Exception:
            break
        if not isinstance(js, list):
            break
        ok = True
        for m in js:
            title = (m.get("MatterTitle") or m.get("MatterName") or "").replace("\n", " ")
            w.writerow([c, t, m["MatterId"], m.get("MatterFile"), (m.get("MatterIntroDate") or "")[:10], title[:500]])
            print(c, t, m["MatterId"], (m.get("MatterIntroDate") or "")[:10], title[:200], flush=True)
        time.sleep(1.2)
    print("client done:", c, "valid" if ok else "invalid", flush=True)
    if ok:
        valid += 1
    out.flush()
    time.sleep(1)
print("valid clients:", valid)
