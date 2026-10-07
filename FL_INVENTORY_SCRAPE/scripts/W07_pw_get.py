# usage: W07_pw_get.py URL OUT [wait_ms]
import asyncio, sys
from playwright.async_api import async_playwright
async def main(url, out, wait):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox','--disable-blink-features=AutomationControlled'])
        ctx = await b.new_context(locale='en-US', viewport={'width':1300,'height':900}, user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36')
        pg = await ctx.new_page()
        await pg.goto(url, timeout=90000)
        await pg.wait_for_timeout(wait)
        html = await pg.content()
        open('/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W07/'+out,'w').write(html)
        t = await pg.inner_text('body')
        print(pg.url); print(t[:3000])
        await b.close()
asyncio.run(main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv)>3 else 5000))
