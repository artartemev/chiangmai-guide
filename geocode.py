"""
Resolve Google Maps short links (maps.app.goo.gl) into coordinates.

Google's share links redirect to a place page whose HTML embeds the map centre
(`center=LAT%2CLNG` in a static-map URL, or `@LAT,LNG` in canonical links).
No API key needed; ~1 request per item.

Usage:
    python3 geocode.py            # only items with latitude == 0
    python3 geocode.py --all      # re-resolve everything
"""
import re
import sys
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import unquote

import requests

DB = "chiangmai_guide.db"
UA = "curl/8.4.0"  # a browser UA triggers a JS interstitial instead of the redirect

RE_CENTER = re.compile(r"center=(-?\d{1,2}\.\d+)%2C(-?\d{1,3}\.\d+)")
RE_AT = re.compile(r"@(-?\d{1,2}\.\d+),(-?\d{1,3}\.\d+)")
RE_Q = re.compile(r"[?&]q=(-?\d{1,2}\.\d+),(-?\d{1,3}\.\d+)")
RE_LL = re.compile(r"[?&]ll=(-?\d{1,2}\.\d+),(-?\d{1,3}\.\d+)")

# Sanity box for northern Thailand + neighbours (rejects garbage matches)
LAT_RANGE = (15.0, 21.0)
LNG_RANGE = (97.0, 102.0)


def _valid(lat, lng):
    return LAT_RANGE[0] <= lat <= LAT_RANGE[1] and LNG_RANGE[0] <= lng <= LNG_RANGE[1]


def resolve(url):
    """Return (lat, lng) or None."""
    try:
        r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "en"}, timeout=20, allow_redirects=True)
    except requests.RequestException:
        return None

    # 1. Coordinates directly in the final URL
    final = unquote(r.url)
    for rx in (RE_Q, RE_LL, RE_AT):
        m = rx.search(final)
        if m:
            lat, lng = float(m.group(1)), float(m.group(2))
            if _valid(lat, lng):
                return lat, lng

    # 2. Coordinates embedded in page HTML
    html = r.text
    m = RE_CENTER.search(html)
    if m:
        lat, lng = float(m.group(1)), float(m.group(2))
        if _valid(lat, lng):
            return lat, lng
    for m in RE_AT.finditer(html):
        lat, lng = float(m.group(1)), float(m.group(2))
        if _valid(lat, lng):
            return lat, lng
    return None


def main():
    force = "--all" in sys.argv
    conn = sqlite3.connect(DB)
    where = "location_url LIKE '%maps%'" + ("" if force else " AND (latitude IS NULL OR latitude = 0)")
    rows = conn.execute(f"SELECT id, title, location_url FROM items WHERE {where}").fetchall()
    print(f"Resolving {len(rows)} links…")

    ok = fail = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(resolve, url): (iid, title) for iid, title, url in rows}
        for fut in as_completed(futs):
            iid, title = futs[fut]
            res = fut.result()
            if res:
                conn.execute("UPDATE items SET latitude=?, longitude=? WHERE id=?", (res[0], res[1], iid))
                conn.commit()
                ok += 1
            else:
                fail += 1
                print(f"  ✗ {iid} {title}")
    print(f"Done in {time.time()-t0:.0f}s: {ok} resolved, {fail} failed.")


if __name__ == "__main__":
    main()
