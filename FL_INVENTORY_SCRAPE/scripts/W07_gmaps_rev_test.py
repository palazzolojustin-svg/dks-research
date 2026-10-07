import asyncio
from playwright.async_api import async_playwright
fid='0x89c259ab291f3beb:0x1a6dc1656d45fd51'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox','--disable-blink-features=AutomationControlled'])
        ctx = await b.new_context(locale='en-US', viewport={'width':1300,'height':900}, user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36')
        pg = await ctx.new_page()
        reqs=[]
        pg.on('request', lambda r: reqs.append(r.url) if 'rpc' in r.url or 'review' in r.url else None)
        await pg.goto('https://www.google.com/maps/place/Foot+Locker/@40.7551817,-73.9863723,17z/data=!3m1!4b1!4m6!3m5!1s'+fid+'!8m2!3d40.7551817!4d-73.9863723?hl=en', timeout=90000)
        await pg.wait_for_timeout(5000)
        t = await pg.inner_text('body')
        print('reviews' in t.lower(), t[:600])
        for sel in ['button[aria-label*="Reviews"]','button:has-text("Reviews")','text=Reviews']:
            try:
                await pg.click(sel, timeout=4000); print('clicked',sel); break
            except Exception as e: print('no',sel)
        await pg.wait_for_timeout(4000)
        t = await pg.inner_text('body'); print(t[:2000])
        u=f"https://www.google.com/maps/rpc/listugcposts?authuser=0&hl=en&gl=us&pb=!1m6!1s{fid}!6m4!4m1!1e1!4m1!1e3!2m2!1i20!2s!5m2!1sx!7e81!8m9!2b1!3b1!5b1!7b1!12m4!1b1!2b1!4m1!1e1!11m0!13m1!1e2"
        r = await pg.evaluate("async u => { const r = await fetch(u); return r.status + ' ' + (await r.text()).slice(0,800); }", u)
        print('FETCH', r)
        print(reqs[:10])
        await b.close()
asyncio.run(main())
