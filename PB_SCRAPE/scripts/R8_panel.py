"""R8: build the union supplier panel for DKS's import entity (consignee DICK'S MERCHANDISING & SUPPLY CHAIN) and tag each
supplier owned / national / ambiguous, using (1) DKS's own published vertical-brand factory lists (X14: raw/X14_factory_list_combined.csv,
Transparency-Pledge exports 2023-01, 2023-07, 2024-07) as the PRIMARY key, then (2) BOL product text / X04 manual classes for the rest.

Panels merged (latest observation wins for overlapping quarters, except pre-2025-07 quarters where the larger kg is kept,
because ImportYeti later revised history):
  raw/X04_wayback_dmsc_20250906_rsc.txt          (Wayback snapshot of the DMSC page, 2025-09-06)
  raw/X04_iy_company_dick-s-merchandising-and-supply-cha.txt  (live, 2026-10-07, X04)
  raw/R8_iy_company_dick-s-merchandising-and-supply-cha.txt   (live refresh by R8, if present)
  raw/R8_wayback_dmsc_*_rsc.txt                  (any other Wayback snapshots R8 retrieved)
Outputs: raw/R8_supplier_panel.csv (supplier x quarter, with class) and raw/R8_supplier_classes.csv
Rerun: python R8_panel.py   (after refreshing the live page with R8_iy_fetch.py)
"""
import re, json, csv, os, glob
from collections import defaultdict
import pandas as pd

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")


def vt(p):
    big = open(p, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'\{"shipments_12m":(\d+),"vendor_name":"([^"]*)".*?"country":"([^"]*)".*?"url":"/supplier/([^"]*)".*?"product_descriptions":"([^"]*)","vendor_time_series":(\{.*?\}\}),(.*?)"uflpa"', big):
        ch = re.search(r'"hs_code_chapters":(\[.*?\]),$', m.group(7))
        chs = {}
        if ch:
            try:
                L = json.loads(ch.group(1)); tot = sum(c["weight"] for c in L) or 1
                chs = {(c["chapter"] or "other"): c["weight"] / tot for c in L}
            except Exception:
                pass
        out[m.group(4)] = dict(name=m.group(2), country=m.group(3), desc=m.group(5), ts=json.loads(m.group(6)), chapters=chs)
    return out


def qkey(k):
    return f"{k[6:]}-{k[3:5]}"


PANELS = []
for p in sorted(glob.glob(os.path.join(RAW, "R8_wayback_dmsc_*_rsc.txt"))) + [os.path.join(RAW, "X04_wayback_dmsc_20250906_rsc.txt"),
                                                                               os.path.join(RAW, "X04_iy_company_dick-s-merchandising-and-supply-cha.txt"),
                                                                               os.path.join(RAW, "R8_iy_company_dick-s-merchandising-and-supply-cha.txt")]:
    if os.path.exists(p):
        d = vt(p)
        if d:
            PANELS.append((os.path.basename(p), d))

# ---------- factory-list key (X14) ----------
STOP = {'co', 'ltd', 'limited', 'company', 'inc', 'corp', 'joint', 'stock', 'the', 'int', 'l', 'intl', 'international', 'hk', 'group',
        'industrial', 'industry', 'mfg', 'manufacturing', 'trading', 'trade', 'sa', 'de', 'cv', 'sporting', 'goods', 'sports', 'garment', 'garments',
        'vietnam', 'viet', 'nam', 'cambodia', 'china', 'branch', 'factory', 'pt', 'jsc', 'llc', 'and', 'export', 'c', 'products', 'enterprise',
        'manufacturi', 'technology', 'tech', 'global', 'hong', 'kong'}


def toks(s):
    return {t for t in re.sub(r'[^a-z0-9 ]', ' ', str(s).lower()).split() if t not in STOP and len(t) > 2}


fl = pd.read_csv(os.path.join(RAW, "X14_factory_list_combined.csv"))
FLN = []
for _, r in fl.drop_duplicates(['Factory Name', 'Vendor Name']).iterrows():
    FLN.append((toks(r['Factory Name']), r['Factory Name'], r['Factory Type']))
    FLN.append((toks(r['Vendor Name']), str(r['Vendor Name']) + ' [vendor]', r['Factory Type']))


def fl_match(name):
    st = toks(name)
    best = None
    for nt, nm, ty in FLN:
        if st and nt and len(st & nt) / len(st) >= 0.99 and (best is None or len(nt) < len(best[0])):
            best = (nt, nm, ty)
    return (best[1], best[2]) if best else ("", "")


# manual aliases (X14) and X04 BOL-text classes
ALIAS = {'ha-bac-export-garment-joint-stock-c': 'Softline', 'habac-export-garment-joint-stock-c': 'Softline', 'nan-yang-garment': 'Softline',
         'century-miracle-apparel-manufacturi': 'Softline', 'wp-sports-cambodia': 'Hardline', 'century-distribution-systems': 'Softline',
         'century-distribution-systems-ind': 'Softline'}
NAT = {"goleader-industries-zhejiang", "goleader-viet-nam-recreation", "goleader-vietnam-recreation-limit", "dyaco-international",
       "zhejiang-arcana-power-sports-tech", "lifetime-hong-kong", "johnson-health-tech", "intex-development", "sportspower",
       "bestway-hong-kong-international-l-imited", "fugang-technology", "denovo-hk"}
# R8 review of BOL text (2026-10-07): GCI-Outdoor chair names (Bleacherback, Packseat, Kickback Rocker, Comfort Pro, Legz Lounger,
# Zero Gravity Freeform) => national; Shinehome (Quest camp cot), DJM (DSG boots), Hydrodynamic (PFDs) are on DKS's factory list => owned;
# Shen Rui (Maxfli/Top-Flite carts & bags), Her Cheng (golf club sets), Formosa Golf (club sets), APL Logistics Taiwan (golf balls,
# Dicks ball pump), HKD Uni-Tech (CEH tents), Fuzhou Fengxiang (camp pillows), Cortina (DSG skates), Hengfeng Cambodia (coolers) => owned by BOL text.
# Huizhou Double Star (table tennis) is ON the DKS vertical factory list => owned per the primary key (flagged: BOLs also name Prince/Odyssey).
# Tangshan Laiyuan (basketball systems, not on list) stays AMBIGUOUS. Lifetime matches the factory list but BOLs name Lifetime-branded hoops => national.
NAT |= {"pinghu-huayang-outdoor-goods-lt", "lanxi-trueyach-industrial"}
AMB = {"tangshan-laiyuan-household-goods"}
APP = {"century-distribution-systems", "century-distribution-systems-ind", "century-miracle-apparel-manufacturi", "uni-gears",
       "makalot-garments-cambodia", "makalot-garments-vietnam", "ha-bac-export-garment-joint-stock-c", "habac-export-garment-joint-stock-c",
       "celebrity-fashion-vina", "glory-industrial-semarang", "hansae-tn", "leader-garment-vietnam", "top-form-brassiere-maesot",
       "haianhtex-joint-stock", "great-global-international", "nan-yang-garment", "new-wide-apparel", "eins-vina", "twhq-garments",
       "twhq-garments-national-ro", "thuyen-nguyen-trade-import-export", "xiamen-kingland", "king-success", "moha-garments",
       "horizon-outdoor-cambodia", "apl-logistics", "phi-logistics", "decor-su-zhou", "southern-textile-network-s-a"}
CONSOL = {"century-distribution-systems", "century-distribution-systems-ind", "apl-logistics", "phi-logistics"}

# brand attribution by supplier (from BOL text; X04 decoder + R8 reading). Primary brand(s) only.
BRAND = {"foremost-golf-mfg": "MAXFLI/TOP-FLITE (golf balls)", "jiangsu-kangliyuan-sports-tech": "ETHOS (strength)",
         "futurux-global": "NISHIKI (bikes)", "camp-planner-int-l": "QUEST/DSG (camp chairs)", "formosa-golf": "Golf clubs (Walter Hagen/Tommy Armour/Top-Flite sets)",
         "makalot-garments-cambodia": "VRST/DSG apparel", "leader-garment-vietnam": "CALIA/DSG apparel", "celebrity-fashion-vina": "DSG/CALIA seamless",
         "top-form-brassiere-maesot": "CALIA/DSG sports bras", "century-miracle-apparel-manufacturi": "Golf apparel (Walter Hagen, INFERENCE)",
         "glory-industrial-semarang": "DSG/CALIA apparel (Makalot)", "hengfeng-top-leisure-vietnam": "DSG wagons", "uni-gears": "Golf apparel (Walter Hagen, INFERENCE)",
         "century-distribution-systems": "Consolidator: DSG/CALIA apparel + DSG hardgoods", "djm-footwear": "DSG boots"}


GRP = {}
for s in ["foremost-golf-mfg", "formosa-golf", "apl-logistics-taiwan", "dongguan-dongcheng-shen-rui-hand", "dong-guan-her-cheng-sporting-goods",
          "xiamen-progoal-sport-goods", "ye-gin-enterprise"]:
    GRP[s] = "Golf hardgoods (Maxfli/Top-Flite/WH/TA)"
for s in ["century-miracle-apparel-manufacturi", "uni-gears", "southern-textile-network-s-a", "nan-yang-garment"]:
    GRP[s] = "Golf apparel (MGA/WGH codes; INFERENCE Walter Hagen)"
for s in ["makalot-garments-cambodia", "makalot-garments-vietnam", "glory-industrial-semarang", "leader-garment-vietnam", "celebrity-fashion-vina",
          "top-form-brassiere-maesot", "ha-bac-export-garment-joint-stock-c", "habac-export-garment-joint-stock-c", "great-global-international",
          "haianhtex-joint-stock", "eins-vina", "hansae-tn", "xiamen-kingland", "moha-garments", "new-wide-apparel", "twhq-garments",
          "twhq-garments-national-ro", "king-success", "horizon-outdoor-cambodia", "thuyen-nguyen-trade-import-export", "decor-su-zhou"]:
    GRP[s] = "Athletic apparel direct (CALIA/DSG/VRST)"
for s in ["apl-logistics", "phi-logistics", "century-distribution-systems", "century-distribution-systems-ind"]:
    GRP[s] = "Apparel via consolidator (CDS/APL/Phi)"
for s in ["jiangsu-kangliyuan-sports-tech", "xiamen-can-am-health-fitness", "sion-international"]:
    GRP[s] = "Fitness (ETHOS/DSG)"
for s in ["hong-kong-sienna-trade", "camp-planner-int-l", "camp-planner-international", "henan-hengfeng-top-leisure", "hengfeng-top-leisure-vietnam",
          "crown-outdoor-sports-technology", "crown-outdoor-sports-technology-hu-factory", "zhejiang-pride-leisure-products",
          "zhejiang-hengfeng-technology", "zhengtong-technology", "hkd-uni-tech", "fuzhou-fengxiang-outdoor", "shinehome-industrial",
          "hydrodynamic-industrial", "hengfeng-outdoors-cambodia", "wp-sports-cambodia"]:
    GRP[s] = "Outdoor/camp (Quest/Alpine Design/DSG)"
GRP["futurux-global"] = "Bikes (Nishiki)"
for s in ["taiwan-sports-trade", "cheung-shing-global-sky-hk-trade", "global-sky-hk-trade", "yegin-industrial-vietnam", "cortina-global",
          "jiajun-sports-goods", "huizhou-double-star-sports-goods"]:
    GRP[s] = "Team sports/games (DSG)"
GRP["djm-footwear"] = "Footwear (DSG boots)"


def classify(slug, name):
    m, ty = fl_match(name)
    if slug in ALIAS:
        m, ty = (m or "alias"), (ty or ALIAS[slug])
    if slug in NAT:
        cls = "NATIONAL"
    elif slug in AMB:
        cls = "AMBIGUOUS"
    else:
        cls = "OWNED"   # on DKS factory list, or owned-brand BOL text (X04 default 'OWN' + R8 review)
    seg = "Softline" if (ty == "Softline" or slug in APP) else (ty if ty else "")
    return cls, m, ty, seg


# ImportYeti renamed these supplier slugs between the Sep-2025 snapshot and Oct-2026 (identical quarterly values in 11-31 quarters):
# without this alias the union panel DOUBLE-COUNTS them in 2016-2025 (X04's union panel did).
SLUG_ALIAS = {"camp-planner-international": "camp-planner-int-l", "crown-outdoor-sports-technology-hu-factory": "crown-outdoor-sports-technology",
              "makalot-garments-vietnam": "makalot-garments-cambodia"}


def build():
    merged = defaultdict(dict)   # slug -> q -> (ship, teu, kg)
    meta = {}
    live = set(PANELS[-1][1])  # slugs present in the most recent live panel
    for fname, d in PANELS:
        snap_q = "2025-07" if "20250906" in fname else None  # quarter that was still in progress when the Wayback snapshot was taken
        for slug0, v in d.items():
            slug = SLUG_ALIAS.get(slug0, slug0)
            meta.setdefault(slug, v)
            meta[slug] = {**meta[slug], "name": v["name"], "country": v["country"],
                          "chapters": v.get("chapters") or meta[slug].get("chapters") or {}}
            for k, x in v["ts"].items():
                q = qkey(k)
                if snap_q and q >= snap_q and slug not in live:
                    continue  # partial quarter in the old snapshot and no live data -> leave to the 'unknown' residual
                new = (x["shipments"], x.get("teu", 0), x["weight"])
                old = merged[slug].get(q)
                if old is None or q >= "2025-07" or new[2] >= old[2]:
                    merged[slug][q] = new
    rows, classes = [], []
    for slug, qs in merged.items():
        cls, m, ty, seg = classify(slug, meta[slug]["name"])
        classes.append(dict(slug=slug, name=meta[slug]["name"], country=meta[slug]["country"], cls=cls, fl_match=m, fl_type=ty, segment=seg,
                            consolidator=slug in CONSOL, brand=BRAND.get(slug, ""), grp=GRP.get(slug, ""),
                            sh_apparel=round(sum(v for k, v in meta[slug]["chapters"].items() if k in ("61", "62")), 3) if meta[slug]["chapters"] else None,
                            sh_footwear=round(meta[slug]["chapters"].get("64", 0), 3) if meta[slug]["chapters"] else None,
                            chapters=json.dumps({k: round(v, 3) for k, v in meta[slug]["chapters"].items() if v >= 0.02}), basis=("factory_list" if (m and m != "alias") else ("alias" if m else "bol_text")),
                            desc=meta[slug].get("desc", "")[:200]))
        for q, (s, t, kg) in qs.items():
            rows.append(dict(slug=slug, q=q, ship=s, teu=t, kg=kg, cls=cls, segment=seg, consolidator=slug in CONSOL, on_list=bool(m),
                             grp=GRP.get(slug, "NATIONAL" if cls == "NATIONAL" else ("AMBIGUOUS" if cls == "AMBIGUOUS" else "Other owned"))))
    pd.DataFrame(rows).sort_values(["slug", "q"]).to_csv(os.path.join(RAW, "R8_supplier_panel.csv"), index=False)
    pd.DataFrame(classes).sort_values("slug").to_csv(os.path.join(RAW, "R8_supplier_classes.csv"), index=False)
    return pd.DataFrame(rows), pd.DataFrame(classes)


if __name__ == "__main__":
    print([p for p, _ in PANELS])
    r, c = build()
    pd.set_option("display.width", 250, "display.max_rows", 200, "display.max_colwidth", 60)
    tot = r[r.q >= "2023-01"].groupby("slug").kg.sum()
    c["kg_2023_26"] = c.slug.map(tot)
    print(c.sort_values("kg_2023_26", ascending=False)[["slug", "country", "cls", "fl_match", "fl_type", "kg_2023_26", "desc"]].to_string())
