import sqlite3
import requests
import re
import urllib.parse
from datetime import datetime

DB_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/chiangmai_guide.db"

SUBDISTRICT_MAP = {
    "chang khlan": "Pa Daet / Chang Khlan",
    "pa daet": "Pa Daet / Chang Khlan",
    "padet": "Pa Daet / Chang Khlan",
    "chang moi": "Old City / Chang Moi",
    "phra sing": "Old City",
    "si phum": "Old City",
    "nimman": "Nimman",
    "suthep": "Chang Phueak / Suthep",
    "chang phueak": "Chang Phueak / Suthep",
    "chang phuak": "Chang Phueak / Suthep",
    "hang dong": "Hang Dong",
    "mae rim": "Mae Rim",
    "mae sa": "Mae Rim",
    "mae on": "Mae On / Mae Kampong",
    "san kamphaeng": "Mae On / Mae Kampong",
    "san sai": "San Sai",
    "doi suthep": "Doi Suthep",
    "pai": "Pai / Chiang Dao",
    "chiang dao": "Pai / Chiang Dao",
    "chiang rai": "Pai / Chiang Dao"
}

def resolve_google_maps_link(short_url):
    if not short_url or "maps.app.goo.gl" not in short_url and "goo.gl/maps" not in short_url:
        return None, None

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    try:
        r = requests.get(short_url, allow_redirects=True, stream=True, headers=headers, timeout=5)
        final_url = r.url

        place_name = ""
        neighborhood = "Other"

        q_match = re.search(r"[?&]q=([^&]+)", final_url)
        p_match = re.search(r"/place/([^/@]+)", final_url)

        query_str = ""
        if q_match:
            query_str = urllib.parse.unquote(q_match.group(1)).replace("+", " ")
        elif p_match:
            query_str = urllib.parse.unquote(p_match.group(1)).replace("+", " ")

        if query_str:
            # Extract venue name before address comma
            parts = [p.strip() for p in query_str.split(",")]
            if parts:
                place_name = parts[0]

            # Match subdistrict from full query string
            q_lower = query_str.lower()
            for sub, neigh in SUBDISTRICT_MAP.items():
                if sub in q_lower:
                    neighborhood = neigh
                    break

        return place_name, neighborhood
    except Exception:
        return None, None

def run_geocoder():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Update OmHome explicitly first
    cursor.execute("""
        UPDATE items 
        SET neighborhood = 'Pa Daet / Chang Khlan',
            location_url = 'https://maps.app.goo.gl/FcH2vP9WtEEJqSM48',
            venue_name = 'OmHome Space'
        WHERE title LIKE '%omhome%' OR title LIKE '%om home%' OR venue_name LIKE '%omhome%' OR venue_name LIKE '%om home%' OR description LIKE '%omhome%' OR description LIKE '%om home%'
    """)

    cursor.execute("SELECT id, title, location_url, neighborhood FROM items WHERE location_url LIKE '%maps%' LIMIT 50")
    items = cursor.fetchall()
    print(f"Resolving Google Maps addresses for {len(items)} sample items...")

    updated_count = 0
    for item in items:
        p_name, neigh = resolve_google_maps_link(item["location_url"])
        if p_name or (neigh and neigh != "Other"):
            cursor.execute("""
                UPDATE items 
                SET neighborhood = CASE WHEN ? != 'Other' THEN ? ELSE neighborhood END,
                    venue_name = CASE WHEN ? != '' THEN ? ELSE venue_name END
                WHERE id = ?
            """, (neigh, neigh, p_name, p_name, item["id"]))
            updated_count += 1
            print(f"ID #{item['id']}: Link='{item['location_url'][:35]}' -> Resolved Venue='{p_name}' | Neigh='{neigh}'")

    conn.commit()
    conn.close()
    print(f"\n✅ Geocoder pass finished! Updated {updated_count} items with exact Google Maps places & subdistricts.")

if __name__ == "__main__":
    run_geocoder()
