#!/bin/bash
cd /home/user/dks-research/FL_INVENTORY_SCRAPE/scripts
( python3 -I W02_crawl.py champssports.com mens_shoes ":name-asc:collection_id:all-men-s-shoes"
  python3 -I W02_crawl.py champssports.com kids_shoes ":name-asc:collection_id:kids-shoes"
  python3 -I W02_crawl.py champssports.com clothing ":name-asc:collection_id:all-clothing"
  python3 -I W02_crawl.py champssports.com accessories ":name-asc:collection_id:all-accessories"
  python3 -I W02_crawl.py champssports.com fanshop ":name-asc:collection_id:fan-shop" ) > ../raw/W02/log_champs.txt 2>&1 &
( python3 -I W02_crawl.py kidsfootlocker.com shoes ":name-asc:collection_id:kids-shoes"
  python3 -I W02_crawl.py kidsfootlocker.com clothing ":name-asc:collection_id:kids-clothing"
  python3 -I W02_crawl.py kidsfootlocker.com accessories ":name-asc:collection_id:accessories" ) > ../raw/W02/log_kfl.txt 2>&1 &
wait
