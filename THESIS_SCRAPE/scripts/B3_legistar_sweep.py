"""B3: re-run of H03's Legistar sweep (H03's run wrote 0 rows: connection resets broke it). Searches matter titles
(2023+) for 'Dick' and 'House of Sport' across many client slugs, with retries/backoff.
Rerun: python B3_legistar_sweep.py -> raw/B3_legistar_sweep.csv (client, term, matterId, file, introDate, title)
"""
import requests, time, csv, os
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
CLIENTS = """orlandpark schaumburg joliet corpuscristi corpuschristi maplegrove maplegrovemn arlington arlingtontx dallascityhall sanantonio houston fortworthgov fortworth plano frisco friscotx mckinney roundrock lubbock sugarland pearland
katy elpaso mesa chandler tempe phoenix tucson gilbert peoria-az scottsdale denver coloradosprings auroragov aurora lakewood westminster thornton thorntonco broomfield
okc oklahomacity norman tulsa kansascity kcmo wichita omaha desmoines westdesmoines minneapolis stpaul bloomington rochester madison milwaukee chicago naperville
rockford peoria columbus cincinnati cleveland toledo akron dayton detroit grandrapids annarbor lansing novi troy indianapolis fortwayne louisville lexington
nashville knoxville memphis chattanooga atlanta sandysprings alpharetta gwinnettcounty charlotte charlottenc raleigh durham greensboro columbia charleston
jacksonville tampa stpete orlando miamidade broward fortlauderdale tallahassee pbgfl palmbeachgardens palmbeachcounty boca richmond virginiabeach norfolk alexandria fairfaxcounty montgomerycountymd
baltimore annapolis phila pittsburgh harrisburg allentown newark jerseycity boston worcester providence hartford newhaven buffalo syracuse sacramento
fresno sanjose oakland sfgov lacity longbeach anaheim costamesa irvine riverside sandiego chulavista portland seattle tacoma bellevue spokane boise
slc reno albuquerque cerritos brea mentor strongsville frederick braintree burlington natick peabody
siouxfalls cedar-rapids cedarrapids iowacity fargo lincoln springfield stlouis stlouiscounty overlandpark olathe lenexa leawood independence
murfreesboro franklin brentwood hoover huntsville birmingham mobile montgomery brla shreveport lafayette jackson littlerock fayetteville
lasvegas henderson clarkcounty sparks provo orem ogden sandy westjordan meridian nampa eugene salem vancouver everett kent renton
alameda hayward fremont santaclara sunnyvale roseville elkgrove stockton modesto visalia bakersfield ontario fontana
temecula murrieta corona torrance carson pasadena glendale burbank thousandoaks ventura oxnard santarosa vacaville
cityofmiami miami doral hialeah coralsprings sunrise davie pembrokepines westpalmbeach kissimmee lakeland sarasota naples fortmyers
gainesville ocala daytona pensacola savannah augusta macon athens greenville spartanburg myrtlebeach wilmington cary chesapeake
roanoke lynchburg henrico chesterfield loudoun princewilliam arlingtonva fredericksburg dc dccouncil wilmingtonde dover
elizabeth paterson trenton camden edison woodbridge cherryhill kingofprussia lancaster reading erie scranton
albany rochesterny yonkers longisland nassaucounty suffolkcounty whiteplains newrochelle ithaca
""".split()
TERMS = ["Dick", "House of Sport"]
out = open(os.path.join(RAW, "B3_legistar_sweep.csv"), "w", newline="", encoding="utf-8")
w = csv.writer(out); w.writerow(["client", "term", "matterId", "file", "introDate", "title"])
S = requests.Session()
for c in dict.fromkeys(CLIENTS):
    status = "invalid"
    for t in TERMS:
        params = {"$filter": f"substringof('{t}',MatterTitle) and MatterIntroDate ge datetime'2022-01-01'", "$top": "200"}
        r = None
        for attempt in range(5):
            try:
                r = S.get(f"https://webapi.legistar.com/v1/{c}/matters", params=params, timeout=30)
                break
            except Exception as e:
                time.sleep(4 + 4 * attempt); r = None
        if r is None:
            status = "error"; break
        if r.status_code != 200:
            break
        try:
            js = r.json()
        except Exception:
            break
        if not isinstance(js, list):
            break
        status = "valid"
        for m in js:
            title = (m.get("MatterTitle") or m.get("MatterName") or "").replace("\n", " ")
            if t == "Dick" and not any(k in title.lower() for k in ["dick's", "dicks", "dick’s", "house of sport", "dick s"]):
                continue
            w.writerow([c, t, m["MatterId"], m.get("MatterFile"), (m.get("MatterIntroDate") or "")[:10], title[:500]])
            print(c, t, m["MatterId"], (m.get("MatterIntroDate") or "")[:10], title[:160], flush=True)
        time.sleep(2)
    print("client:", c, status, flush=True)
    out.flush()
    time.sleep(1.5)
