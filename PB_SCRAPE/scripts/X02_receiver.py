"""X02 local receiver: tiny HTTP server that saves JSON POSTed from a browser console.

Why: dicks.com / golfgalaxy.com product-listing pages are behind Akamai (plain python requests get 403
"Site Unavailable"), but a normal browser session loads them fine. The census JS (X02_census_browser.js)
runs inside an ordinary dicks.com tab, fetches listing pages same-origin, and POSTs the parsed rows here.

Rerun: python PB_SCRAPE\\scripts\\X02_receiver.py   (listens on http://127.0.0.1:8765)
Then paste X02_census_browser.js into the DevTools console of a dicks.com tab.
Each POST to /save?name=<file> is written to PB_SCRAPE\\raw\\<file>.
"""
import http.server, urllib.parse, os

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"


class H(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        name = os.path.basename(q.get("name", ["X02_dump.json"])[0])
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        with open(os.path.join(RAW, name), "wb") as f:
            f.write(body)
        self.send_response(200); self._cors(); self.end_headers()
        self.wfile.write(f"saved {name} {len(body)}".encode())


if __name__ == "__main__":
    http.server.HTTPServer(("127.0.0.1", 8765), H).serve_forever()
