"""R3: DICK'S Sporting Goods Foundation (EIN 27-4516157) Form 990-PF e-file pull + parse.

How to rerun (annually, after the Foundation files; latest filing appears ~Nov-Jun):
    python PB_SCRAPE/scripts/R3_foundation_990pf.py
1. Reads the object-ID list from ProPublica's org page (projects.propublica.org/nonprofits/organizations/274516157).
2. Downloads each e-file XML from the public GivingTuesday 990 data lake
   (https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/XmlFiles/<object_id>_public.xml) - no login, no key.
3. Parses: tax period, Part I contributions, Schedule B contributors (name, amount, type),
   Part XV grants count/total, and dumps every text node containing DSG/giveback/1%/percent/sales keywords.
Outputs: PB_SCRAPE/raw/R3_990/*.xml, PB_SCRAPE/raw/R3_990pf_contributors.csv, PB_SCRAPE/raw/R3_990pf_summary.csv,
         PB_SCRAPE/raw/R3_990pf_keyword_hits.txt
"""
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET

import requests

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw")
XMLDIR = os.path.join(RAW, "R3_990")
os.makedirs(XMLDIR, exist_ok=True)
H = {"User-Agent": "Mozilla/5.0 (equity research; contact palazzolojustin@gmail.com)"}
EIN = "274516157"
NS = "{http://www.irs.gov/efile}"


def object_ids():
    r = requests.get(f"https://projects.propublica.org/nonprofits/organizations/{EIN}", headers=H, timeout=60)
    ids = sorted(set(re.findall(rf"/{EIN}/(\d{{15,20}})", r.text)))
    return ids


def fetch(oid):
    p = os.path.join(XMLDIR, f"{oid}.xml")
    if os.path.exists(p) and os.path.getsize(p) > 1000:
        return p
    u = f"https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/XmlFiles/{oid}_public.xml"
    r = requests.get(u, headers=H, timeout=120)
    if r.status_code != 200:
        print("FAIL", oid, r.status_code)
        return None
    open(p, "wb").write(r.content)
    return p


def strip(tag):
    return tag.replace(NS, "")


def txt(el, path):
    x = el.find("/".join(NS + t for t in path.split("/")))
    return x.text if x is not None else None


def main():
    ids = sys.argv[1:] or object_ids()
    print("object ids:", ids)
    summ, contribs, hits = [], [], []
    kw = re.compile(r"(?i)\bDSG\b|giveback|give back|gives back|1%|one percent|percent of|% of|sales|Maxfli|CALIA|VRST|round ?up|register|customer")
    for oid in ids:
        p = fetch(oid)
        if not p:
            continue
        root = ET.parse(p).getroot()
        hdr = root.find(NS + "ReturnHeader")
        beg = txt(hdr, "TaxPeriodBeginDt")
        end = txt(hdr, "TaxPeriodEndDt")
        rtype = txt(hdr, "ReturnTypeCd")
        rd = root.find(NS + "ReturnData")
        contri = None
        for e in rd.iter():
            if strip(e.tag) == "ContriRcvdRevAndExpnssAmt":
                contri = e.text
                break
        # Schedule B
        nb = 0
        for sb in rd.iter(NS + "IRS990ScheduleB"):
            for c in sb.iter(NS + "ContributorInformationGrp"):
                nb += 1
                name = " ".join(t.text for t in c.iter() if strip(t.tag) in ("BusinessNameLine1Txt", "BusinessNameLine2Txt", "PersonNm") and t.text)
                amt = None
                for t in c.iter():
                    if strip(t.tag) == "TotalContributionsAmt":
                        amt = t.text
                types = [strip(t.tag) for t in c.iter() if strip(t.tag) in ("PersonContributionInd", "PayrollContributionInd", "NoncashContributionInd")]
                contribs.append({"object_id": oid, "period_begin": beg, "period_end": end, "contributor": name, "amount": amt, "type": "|".join(types)})
        # grants paid (Part XV)
        gpaid = None
        ngrants = 0
        for e in rd.iter():
            t = strip(e.tag)
            if t == "TotalGrantOrContriPdDurYrAmt":
                gpaid = e.text
            if t == "GrantOrContributionPdDurYrGrp":
                ngrants += 1
        summ.append({"object_id": oid, "type": rtype, "period_begin": beg, "period_end": end, "contributions_partI": contri,
                     "schedB_contributors": nb, "grants_paid_total": gpaid, "grants_count": ngrants})
        # keyword hits in every text node (skip grant recipient lists noise by limiting length)
        for e in rd.iter():
            if e.text and kw.search(e.text) and len(e.text.strip()) > 3:
                hits.append(f"{oid}\t{end}\t{strip(e.tag)}\t{e.text.strip()[:600]}")
    with open(os.path.join(RAW, "R3_990pf_summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summ[0].keys()))
        w.writeheader(); w.writerows(summ)
    with open(os.path.join(RAW, "R3_990pf_contributors.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["object_id", "period_begin", "period_end", "contributor", "amount", "type"])
        w.writeheader(); w.writerows(contribs)
    open(os.path.join(RAW, "R3_990pf_keyword_hits.txt"), "w", encoding="utf-8").write("\n".join(hits))
    for s in summ:
        print(s)
    for c in contribs:
        print(c)
    print(len(hits), "keyword hits")


if __name__ == "__main__":
    main()
