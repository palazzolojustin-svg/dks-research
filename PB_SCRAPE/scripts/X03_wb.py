"""X03: polite, throttled GET for web.archive.org (shared by all X03 scripts).
Wayback refuses connections (WinError 10061) for a few minutes when an IP sends too many requests.
This enforces a minimum gap between requests (cross-process, via a timestamp file) and backs off
for 90-300 s on refusal / 429 / 5xx.
"""
import os, time, requests

UA = {"User-Agent": "Mozilla/5.0 (research; DKS wayback study; polite)"}
GAP = float(os.environ.get("X03_GAP", "4"))
STAMP = os.path.join(os.path.dirname(__file__), "..", "raw", "X03_last_request.txt")


def _wait():
    try:
        last = float(open(STAMP).read().strip())
    except Exception:
        last = 0
    d = time.time() - last
    if d < GAP:
        time.sleep(GAP - d)
    open(STAMP, "w").write(str(time.time()))


def get(url, params=None, timeout=180, tries=8, ok_codes=(200,), final_codes=(403, 404, 451)):
    for a in range(tries):
        _wait()
        try:
            r = requests.get(url, params=params, headers=UA, timeout=timeout)
            if r.status_code in ok_codes:
                return r
            if r.status_code in final_codes:
                return r
            back = 60 if r.status_code == 429 else 20 * (a + 1)
            print(f"  [wb] HTTP {r.status_code}; sleep {back}s", flush=True)
            time.sleep(back)
        except requests.exceptions.ConnectionError as e:
            back = min(90 * (a + 1), 300)
            print(f"  [wb] connection refused/reset; sleep {back}s", flush=True)
            time.sleep(back)
        except Exception as e:
            print(f"  [wb] err {e}; sleep 20s", flush=True)
            time.sleep(20)
    return None
