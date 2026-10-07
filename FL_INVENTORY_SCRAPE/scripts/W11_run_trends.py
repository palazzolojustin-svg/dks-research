"""W11 batch runner. Skips batches already saved. Run: python3 W11_run_trends.py"""
import time, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import W11_gtrends as G
W = "2024-01-01 2026-10-06"
L = "2019-01-01 2026-10-06"
B = [
 ("us_w_ret2", ["foot locker","dicks sporting goods","academy sports","dtlr","jd sports"], W, "US", 0, ""),
 ("us_w_topics", ["/m/08fhy9","/g/11bc6vf4zn","/m/09_gw6","/m/02pnq74","/m/06fgv_"], W, "US", 0, ""),
 ("us_w_shop", ["foot locker","jd sports","finish line","hibbett","champs sports"], W, "US", 0, "froogle"),
 ("us_w_promo", ["foot locker","foot locker sale","foot locker coupon","foot locker discount code","foot locker clearance"], W, "US", 0, ""),
 ("us_w_nearme", ["foot locker","foot locker near me","jd sports near me","finish line near me","hibbett near me"], W, "US", 0, ""),
 ("us_w_kids", ["foot locker","kids foot locker","champs sports","champs","footlocker"], W, "US", 0, ""),
 ("us_m_long", ["foot locker","jd sports","finish line","hibbett","dicks sporting goods"], L, "US", 0, ""),
 ("us_w_ctrl", ["foot locker","nike","new balance","costco membership","pizza hut"], W, "US", 0, ""),
 ("gb_w", ["foot locker","jd sports","footasylum","schuh","size?"], W, "GB", 0, ""),
 ("de_w", ["foot locker","snipes","jd sports","deichmann","zalando"], W, "DE", 0, ""),
 ("fr_w", ["foot locker","courir","jd sports","snipes","intersport"], W, "FR", 0, ""),
 ("it_w", ["foot locker","jd sports","snipes","aw lab","cisalfa"], W, "IT", 0, ""),
 ("nl_w", ["foot locker","jd sports","snipes","zalando","intersport"], W, "NL", 0, ""),
 ("es_w", ["foot locker","jd sports","snipes","decathlon","sprinter"], W, "ES", 0, ""),
 ("au_w", ["foot locker","jd sports","platypus","hype dc","rebel sport"], W, "AU", 0, ""),
 ("ca_w", ["foot locker","sport chek","jd sports","champs sports","sporting life"], W, "CA", 0, ""),
 ("us_w_fldogs", ["foot locker","foot locker jordans","foot locker new balance","foot locker salomon","foot locker hoka"], W, "US", 0, ""),
 ("us_w_fldogs2", ["foot locker","foot locker ugg","foot locker on cloud","foot locker asics","foot locker crocs"], W, "US", 0, ""),
]
for name, terms, tf, geo, cat, gp in B:
    out = os.path.join(G.RAW, f"gt_{name}.csv")
    if os.path.exists(out): print("skip", name); continue
    try:
        df = G.fetch(terms, tf, geo, cat, gp)
        df.to_csv(out); print("saved", name, len(df), flush=True)
    except Exception as e:
        print("FAIL", name, e, flush=True)
    time.sleep(35)
print("DONE")
