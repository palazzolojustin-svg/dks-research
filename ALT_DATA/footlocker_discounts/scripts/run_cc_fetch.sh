#!/bin/bash
# Fetch each crawl as soon as its index file exists (index step runs in parallel).
cd "$(dirname "$0")/.."
for c in $(python3 -c "import sys;sys.path.insert(0,'scripts');from cc_scrape import CRAWLS;print(' '.join(CRAWLS))"); do
  while [ ! -f data/cdx/$c.jsonl ]; do sleep 20; done
  python3 scripts/cc_scrape.py fetch --crawls $c --workers ${WORKERS:-4}
done
echo ALL_CC_FETCH_DONE
