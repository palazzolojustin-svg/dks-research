import json, os
root = r"C:\Users\palaz\Downloads\DKS_RESEARCH\FL_EUROPE_SCRAPE"
tpl = open(os.path.join(root, "artifact", "template.html"), encoding="utf-8").read()
data = json.load(open(os.path.join(root, "state", "items_for_page.json"), encoding="utf-8"))
js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
html = tpl.replace("__DATA__", js)
out = os.path.join(root, "artifact", "FL_Europe_Exit_Evidence.html")
open(out, "w", encoding="utf-8").write(html)
# sanity: every ref id exists
import re
ids = {d["id"] for d in data}
refs = set(re.findall(r'data-id="(E\d{3})"', tpl))
print("bytes", os.path.getsize(out), "missing refs", sorted(refs - ids))
