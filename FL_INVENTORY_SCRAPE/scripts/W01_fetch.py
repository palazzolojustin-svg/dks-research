import re, json, sys, time, subprocess
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def get_html(url, tries=4):
    for i in range(tries):
        try:
            r = subprocess.run(["curl", "-sS", "-m", "60", "-A", UA, "-H", "Accept-Language: en-US,en;q=0.9",
                                "-w", "\n%{http_code}", url], capture_output=True)
            out = r.stdout.decode("utf8", "replace")
            body, code = out.rsplit("\n", 1)
            if code == "200":
                return body
            print("status", code, url, file=sys.stderr)
        except Exception as e:
            print("err", e, file=sys.stderr)
        time.sleep(3 * (i + 1))
    return None


def hydration(h):
    i = h.find('STATE_FROM_SERVER:')
    if i < 0:
        return None
    j = h.index('{', i)
    obj, end = json.JSONDecoder().raw_decode(h, j)
    return obj


def search(url):
    h = get_html(url)
    if h is None:
        return None
    d = hydration(h)
    return d.get('search') if d else None
