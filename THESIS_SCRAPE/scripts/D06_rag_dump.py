"""D06: summarise a saved Apify rag-web-browser dataset JSON (from an MCP tool-results file).
Usage: python THESIS_SCRAPE/scripts/D06_rag_dump.py <json-file> [keyword ...]
Prints each result's title/url and paragraphs containing any keyword (default: DICK, Dick).
"""
import sys, json, re
d = json.load(open(sys.argv[1], encoding='utf-8'))
kws = sys.argv[2:] or ['DICK', "Dick's", 'Dick’s']
items = d['items'] if isinstance(d, dict) else d
for it in items:
    sr = it.get('searchResult', {}) or {}
    title = sr.get('title') or it.get('searchResult.title'); url = sr.get('url') or it.get('searchResult.url')
    text = it.get('text') or ''
    print('=====', title, '|', url, '| len', len(text))
    sents = re.split(r'(?<=[.!?])\s+', text)
    hits = [s for s in sents if any(k.lower() in s.lower() for k in kws)]
    for s in hits[:25]:
        print('  -', s[:400])
