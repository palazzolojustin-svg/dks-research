"""B11: search Socrata discovery API for sales-tax datasets on a domain. Usage: python scripts/B11_socrata_search.py <domain> "<query>" """
import sys, requests
dom, q = sys.argv[1], sys.argv[2]
r = requests.get('https://api.us.socrata.com/api/catalog/v1', params={'domains': dom, 'q': q, 'limit': 40}, timeout=60).json()
for x in r.get('results', []):
    res = x['resource']; print(res['id'], '|', res['name'][:100], '|', res.get('data_updated_at', '')[:10], '|', (res.get('description') or '')[:150].replace('\n', ' '))
