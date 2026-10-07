"""S1 Google News RSS helper with link decoding: python S1_gnews.py "query" [n_decode]"""
import requests, sys
from bs4 import BeautifulSoup
from googlenewsdecoder import gnewsdecoder
q=sys.argv[1]; nd=int(sys.argv[2]) if len(sys.argv)>2 else 0
r=requests.get('https://news.google.com/rss/search',params={'q':q,'hl':'en-US','gl':'US','ceid':'US:en'},headers={'User-Agent':'Mozilla/5.0'},timeout=20)
s=BeautifulSoup(r.text,'xml')
for i,it in enumerate(s.find_all('item')[:20]):
    u=it.link.text
    if i<nd:
        try: u=gnewsdecoder(u,interval=0.5).get('decoded_url',u)
        except Exception as e: pass
    print(it.pubDate.text[5:16],'|',it.title.text[:140],'|',u[:200])
