cd /home/user/dks-research/HOS_SCRAPE
for s in tx ga; do
 for i in 1 2 3 4 5 6; do curl -s -C - --retry 5 -o raw/J02/qwi_$s.csv.gz https://lehd.ces.census.gov/data/qwi/latest_release/$s/qwi_${s}_sa_f_gc_n4_op_u.csv.gz; gzip -t raw/J02/qwi_$s.csv.gz 2>/dev/null && break; done
 python3 -I scripts/J02_qwi_filt.py $s
done
echo DONE
