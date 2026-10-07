"""Union all Wayback + live release-calendar snapshots -> launches table + observations table."""
import glob, os, sys, pandas as pd
sys.path.insert(0,os.path.dirname(__file__))
from W13_parse_release import rows
base=sys.argv[1]
obs=[]
for f in sorted(glob.glob(base+'/wb/*.html')):
    site,ts=os.path.basename(f)[:-5].split('_')
    obs+=rows(f,site,ts)
obs+=rows(base+'/footlocker.com_release-dates.html','FL','20261007204800')
obs+=rows(base+'/champssports.com_release-dates.html','CH','20261007204800')
o=pd.DataFrame(obs)
o['dt']=pd.to_datetime(o.launch.str.replace(r' GMT.*','',regex=True),format='%b %d %Y %H:%M:%S',errors='coerce')
o['snap']=pd.to_datetime(o.snapshot.str[:14],format='%Y%m%d%H%M%S')
o['age_days']=(o.snap-o.dt).dt.total_seconds()/86400
o.to_csv(base+'/W13_observations.csv',index=False)
print(len(o), o.groupby('site').snapshot.nunique().to_dict())
