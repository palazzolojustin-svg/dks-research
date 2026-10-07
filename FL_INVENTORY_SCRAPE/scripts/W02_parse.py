import json, re, sys
def extract_state(html):
    i = html.find('STATE_FROM_SERVER:')
    if i < 0: return None
    j = html.index('{', i)
    dec = json.JSONDecoder()
    obj, end = dec.raw_decode(html[j:])
    return obj
def find_search(obj):
    # locate dict containing 'pagination' and 'products'
    stack=[obj]
    while stack:
        o=stack.pop()
        if isinstance(o,dict):
            if 'pagination' in o and 'products' in o: return o
            stack.extend(o.values())
        elif isinstance(o,list): stack.extend(o)
if __name__=='__main__':
    s=open(sys.argv[1]).read()
    st=extract_state(s); r=find_search(st)
    print(r['pagination'], len(r['products']))
    print([ (f.get('code'), f.get('name')) for f in r.get('facets',[])])
