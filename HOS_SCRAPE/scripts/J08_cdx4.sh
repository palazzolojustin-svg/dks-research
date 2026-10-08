q(){ echo "== $1"; curl -s -m 90 -G "https://web.archive.org/cdx/search/cdx" --data-urlencode "url=$1" --data-urlencode "matchType=prefix" --data-urlencode "fl=timestamp,original,statuscode" --data-urlencode "limit=${2:-40}" | head -${2:-40} | cut -c1-200; sleep 1.5; }
q "indeed.com/q-Dick" 30
q "indeed.com/q-House-Of-Sport" 30
q "indeed.com/q-house-of-sport" 30
q "indeed.com/jobs?q=house+of+sport" 20
q "indeed.com/jobs?q=dick" 20
q "ziprecruiter.com/Jobs/Dicks-House-Of-Sport" 20
q "ziprecruiter.com/Jobs/House-Of-Sport" 20
q "ziprecruiter.com/c/Dicks-Sporting-Goods" 20
q "simplyhired.com/search?q=house+of+sport" 20
q "simplyhired.com/search?q=dick" 20
q "glassdoor.com/Job/house-of-sport" 20
q "linkedin.com/jobs/dicks-house-of-sport" 20
q "linkedin.com/jobs/house-of-sport" 20
q "linkedin.com/jobs/search?keywords=House" 20
