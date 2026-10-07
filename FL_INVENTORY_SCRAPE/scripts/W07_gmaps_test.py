import asyncio, sys, os
from playwright.async_api import async_playwright
os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH','/opt/pw-browsers')
async def main(q):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        ctx = await b.new_context(locale='en-US', viewport={'width':1300,'height':900})
        pg = await ctx.new_page()
        await pg.goto('https://www.google.com/maps/search/'+q.replace(' ','+')+'?hl=en', timeout=60000)
        await pg.wait_for_timeout(6000)
        print(pg.url)
        t = await pg.inner_text('body')
        print(t[:2500])
        await pg.screenshot(path='/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W07/gm_test.png')
        await b.close()
asyncio.run(main(sys.argv[1]))
