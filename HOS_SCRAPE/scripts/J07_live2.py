import re,time,csv,collections
from curl_cffi import requests as r
from bs4 import BeautifulSoup
old=set(l.split(",")[0] for l in open("data/J07_live_hos_postings_20261008.csv"))
rows={}
for base in ["https://www.dickssportinggoods.jobs/jobs/brand/House-of-Sport/?mypage={}","https://www.dickssportinggoods.jobs/jobs/brand/House-of-Sport/{}/","https://www.dickssportinggoods.jobs/jobs/brand/House-of-Sport/?page={}"]:
    x=r.get(base.format(2),impersonate="chrome",timeout=40)
    s=BeautifulSoup(x.text,"lxml");a=[l.get("href") for l in s.select("a[href*='/job/']")]
    print(base,x.status_code,len(a),a[:1])
