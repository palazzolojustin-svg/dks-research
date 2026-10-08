import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
    pg = b.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")
    for u in ["https://www.dickssportinggoods.com/f/mens-clothing", "https://www.dickssportinggoods.com/f/nike-shoes"]:
        try:
            r = pg.goto(u, timeout=45000); html = pg.content()
            print(u[-20:], r.status, len(html), "dcsg-ngx-plp-server-state" in html)
        except Exception as e: print("err", str(e)[:100])
        time.sleep(3)
    b.close()
