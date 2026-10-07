"""Fetch a page with headless Chromium (playwright) and save rendered text + html. Usage: W11_pw_fetch.py <url> <outname> [wait_s]"""
import sys, os, asyncio
from playwright.async_api import async_playwright
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw', 'W11')
async def main(url, name, wait):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--disable-blink-features=AutomationControlled'])
        c = await b.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36', locale='en-US', viewport={'width':1366,'height':900})
        pg = await c.new_page()
        await pg.goto(url, timeout=90000, wait_until='domcontentloaded')
        await pg.wait_for_timeout(wait*1000)
        html = await pg.content(); txt = await pg.inner_text('body')
        open(os.path.join(RAW, name+'.html'),'w').write(html); open(os.path.join(RAW, name+'.txt'),'w').write(txt)
        print(len(html), txt[:3000])
        await b.close()
asyncio.run(main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv)>3 else 15))
