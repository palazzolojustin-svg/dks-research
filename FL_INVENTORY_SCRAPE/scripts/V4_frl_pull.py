import requests,time,json
A='https://arctic-shift.photon-reddit.com/api'
def pull(kind,sub,after,fields):
    out=[];cur=after
    while True:
        for i in range(6):
            try:
                j=requests.get(f'{A}/{kind}/search',params=dict(subreddit=sub,after=cur,limit=100,sort='asc',fields=fields),timeout=90).json()
                if j.get('error'): raise RuntimeError(j['error'])
                d=j['data'];break
            except Exception: time.sleep(3*(i+1)); d=None
        if not d: break
        out+=d; cur=d[-1]['created_utc']
        if len(d)<100 or len(out)>40000: break
    return out
p=pull('posts','footlocker','2024-01-01','created_utc,title,selftext,score,num_comments')
json.dump(p,open('raw/V4/frl_posts.json','w'));print('posts',len(p))
c=pull('comments','footlocker','2024-01-01','created_utc,body,score')
json.dump(c,open('raw/V4/frl_comments.json','w'));print('comments',len(c))
