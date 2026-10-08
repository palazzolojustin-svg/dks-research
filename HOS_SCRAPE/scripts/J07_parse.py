import re,sys
from bs4 import BeautifulSoup
s=BeautifulSoup(open(sys.argv[1]).read(),"lxml")
t=s.get_text(" ",strip=True)
print(t[:600])
for m in re.finditer(r"(\d[\d,]*)\s+(?:jobs|results|open)",t[:5000],re.I): print(m.group(0))
a=s.select("a[href*='/job/']")
print(len(a))
for x in a[:60]: print(x.get("href"),"|",x.get_text(" ",strip=True)[:120])
pg=[x.get("href") for x in s.select("a[href*='page=']")][:5];print(pg)
