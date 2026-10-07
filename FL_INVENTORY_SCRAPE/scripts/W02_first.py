import sys,json
sys.path.insert(0,'/home/user/dks-research/FL_INVENTORY_SCRAPE/scripts')
from W02_parse import *
r=find_search(extract_state(open(sys.argv[1]).read()))
print(r['pagination'], [p['sku'] for p in r['products'][:3]])
