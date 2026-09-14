"""
Enrich items from their Google Maps share links: coordinates, phone, website,
rating, Google category and opening hours. No API key required.

How it works
1. `maps.app.goo.gl/...` 302-redirects to `maps.google.com/?q=<name, address>&ftid=<place id>`.
2. `https://maps.google.com/maps?cid=<place id>&output=embed` returns a small
   HTML page whose init payload contains the matched place: ftid, address,
   [lat, lng], rating, review count, phone, website, category and hours.
3. We accept the result only when its ftid equals the one from the redirect,
   so we never attach a different business's data to an item.

Usage:
    python3 geocode.py            # only items without coordinates
    python3 geocode.py --all      # re-resolve everything (refreshes ratings/hours)
"""
import json
import re
import sys
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import unquote, urlparse, parse_qs

import requests

DB = "chiangmai_guide.db"
UA_REDIRECT = "curl/8.4.0"  # a browser UA gets a JS interstitial instead of the 302
UA_EMBED = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"

RE_FTID = re.compile(r"(0x[0-9a-f]+:0x[0-9a-f]+)")
RE_PLACE_PATH = re.compile(r"/maps/place/(.+?)/data=")
RE_ENTITY = re.compile(r'\["(0x[0-9a-f]+:0x[0-9a-f]+)","([^"]*)",\[(-?\d+\.\d+),(-?\d+\.\d+)\]')
RE_RATING = re.compile(r',(\d(?:\.\d+)?),"([\d,]+) reviews?"')
RE_PHONE = re.compile(r'"(\+?\d[\d \-]{6,14}\d)"')
RE_WEBSITE = re.compile(r'\["(https?://[^"]+)","[^"]+",null,null,"[^"]*"\]|/url\?q=([^"&\\]+)')
RE_HOURS = re.compile(r'\["(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)",\d,\[\d+,\d+,\d+\],\[\["([^"]+)"')

DAY_SHORT = {"Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed", "Thursday": "Thu",
             "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"}
DAY_ORDER = list(DAY_SHORT.values())

LAT_RANGE, LNG_RANGE = (5.0, 21.5), (97.0, 106.0)


def _valid(lat, lng):
    return LAT_RANGE[0] <= lat <= LAT_RANGE[1] and LNG_RANGE[0] <= lng <= LNG_RANGE[1]


def redirect_target(url):
    """Return (query, ftid) from the share-link redirect, or (None, None)."""
    try:
        r = requests.get(url, headers={"User-Agent": UA_REDIRECT}, timeout=20, allow_redirects=False)
    except requests.RequestException:
        return None, None
    loc = unquote(r.headers.get("Location", ""))
    if not loc:
        return None, None
    m = RE_FTID.search(loc)
    ftid = m.group(1) if m else None
    q = parse_qs(urlparse(loc).query).get("q", [""])[0]
    if not q:
        m = RE_PLACE_PATH.search(loc)
        q = m.group(1).replace("+", " ") if m else ""
        q = re.sub(r"^[A-Z0-9]{4}\+[A-Z0-9]{2,3}\s+", "", q)  # drop plus code
    q = re.sub(r",\s*(Таиланд|Thailand)$", "", q).strip()
    return q or None, ftid


def embed_lookup(query, ftid):
    """Query the embed endpoint and return the entity matching ftid.

    With a known ftid we ask by `cid` (the decimal form of its second half),
    which resolves the exact place; the free-text query is only a fallback.
    """
    params = {"output": "embed", "hl": "en"}
    if ftid:
        params["cid"] = str(int(ftid.split(":")[1], 16))
    else:
        params["q"] = query
    try:
        r = requests.get("https://maps.google.com/maps", params=params,
                         headers={"User-Agent": UA_EMBED}, timeout=20)
    except requests.RequestException:
        return None
    html = r.text
    if "initEmbed(" not in html:
        return None

    entities = list(RE_ENTITY.finditer(html))
    if not entities:
        return None
    chosen = None
    for m in entities:
        if ftid and m.group(1) == ftid:
            chosen = m
            break
    if chosen is None:
        if ftid:  # a different place was matched — don't trust it
            return None
        chosen = entities[0]

    lat, lng = float(chosen.group(3)), float(chosen.group(4))
    if not _valid(lat, lng):
        return None

    # Details for the chosen entity live right after its coordinates block.
    tail = html[chosen.end(): chosen.end() + 6000]
    out = {"lat": round(lat, 6), "lng": round(lng, 6), "address": chosen.group(2),
           "place_id": chosen.group(1)}

    m = RE_RATING.search(tail)
    if m:
        out["rating"] = round(float(m.group(1)), 1)
        out["rating_count"] = int(m.group(2).replace(",", ""))
    m = RE_PHONE.search(tail)
    if m:
        out["phone"] = m.group(1)
    m = RE_WEBSITE.search(tail)
    if m:
        out["website"] = unquote(m.group(1) or m.group(2))
    # Google category: the quoted string immediately before the full address
    addr = re.escape(chosen.group(2).split(",", 1)[1].strip()) if "," in chosen.group(2) else None
    if addr:
        m = re.search(r'"([^"]{3,60})","' + addr + '"', tail)
        if m and not re.search(r"\d{5}", m.group(1)):
            out["gcategory"] = m.group(1)

    hours = {}
    for day, val in RE_HOURS.findall(html):
        hours.setdefault(DAY_SHORT[day], val)
    if hours:
        out["hours"] = {d: hours[d] for d in DAY_ORDER if d in hours}
    return out


def resolve(url):
    q, ftid = redirect_target(url)
    if not q and not ftid:
        return None
    return embed_lookup(q, ftid)


def ensure_columns(conn):
    cols = {r[1] for r in conn.execute("PRAGMA table_info(items)")}
    for name, ddl in [("rating", "REAL"), ("rating_count", "INTEGER"),
                      ("google_category", "TEXT"), ("place_id", "TEXT")]:
        if name not in cols:
            conn.execute(f"ALTER TABLE items ADD COLUMN {name} {ddl}")
    conn.commit()


def main():
    force = "--all" in sys.argv
    conn = sqlite3.connect(DB)
    ensure_columns(conn)
    where = "location_url LIKE '%maps%'" + ("" if force else " AND (latitude IS NULL OR latitude = 0)")
    rows = conn.execute(f"SELECT id, title, location_url, address FROM items WHERE {where}").fetchall()
    print(f"Resolving {len(rows)} links…")

    ok = fail = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=3) as pool:
        futs = {pool.submit(resolve, url): (iid, title, addr) for iid, title, url, addr in rows}
        for fut in as_completed(futs):
            iid, title, addr = futs[fut]
            res = fut.result()
            if not res:
                fail += 1
                print(f"  ✗ {iid} {title}")
                continue
            conn.execute("""UPDATE items SET latitude=?, longitude=?, place_id=?,
                            rating=COALESCE(?, rating), rating_count=COALESCE(?, rating_count),
                            phone_contact=COALESCE(?, phone_contact), website=COALESCE(?, website),
                            google_category=COALESCE(?, google_category),
                            opening_hours=COALESCE(?, opening_hours),
                            address=CASE WHEN address='' OR address IS NULL THEN ? ELSE address END
                            WHERE id=?""",
                         (res["lat"], res["lng"], res["place_id"], res.get("rating"), res.get("rating_count"),
                          res.get("phone"), res.get("website"), res.get("gcategory"),
                          json.dumps(res["hours"], ensure_ascii=False) if res.get("hours") else None,
                          res["address"], iid))
            conn.commit()
            ok += 1
    print(f"Done in {time.time()-t0:.0f}s: {ok} resolved, {fail} failed.")


if __name__ == "__main__":
    main()
