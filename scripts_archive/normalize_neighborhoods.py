import sqlite3
import os

DB_PATH = "/Users/artartemev/Downloads/Telegram Desktop/ChatExport_2026-08-28/chiangmai_portal/chiangmai_guide.db"

def map_neighborhood(s: str) -> str:
    if not s:
        return "Other"
    
    # 1. Old City — anything starting with Old City /
    if s.startswith("Old City /") or s == "Old City":
        return "Old City"
    
    # 2. Nimman — anything starting with Nimman / or containing Nimman
    if s.startswith("Nimman /") or "Nimman" in s:
        return "Nimman"
    
    # 3. Suthep / CMU — anything starting with Suthep / or containing CMU
    if s.startswith("Suthep /") or "CMU" in s or s == "Suthep":
        return "Suthep / CMU"
    
    # 5. Santitham — Chang Phueak / Santitham, Chang Phueak / Santisuk
    if s in ("Chang Phueak / Santitham", "Chang Phueak / Santisuk", "Santitham"):
        return "Santitham"
    
    # 4. Chang Phueak — anything starting with Chang Phueak / (but NOT Santitham)
    if s.startswith("Chang Phueak /") or s == "Chang Phueak":
        return "Chang Phueak"
    
    # 6. Hang Dong — anything starting with Hang Dong /
    if s.startswith("Hang Dong /") or s == "Hang Dong":
        return "Hang Dong"
    
    # 7. Mae Rim — anything starting with Mae Rim /
    if s.startswith("Mae Rim /") or s == "Mae Rim":
        return "Mae Rim"
    
    # 8. Riverside / Wat Ket — anything starting with Wat Ket / or Wat Ket or containing Ping River or Riverside or Pa Tan
    if (s.startswith("Wat Ket /") or s == "Wat Ket" or 
        "Ping River" in s or "Riverside" in s or "Pa Tan" in s):
        return "Riverside / Wat Ket"
    
    # 9. Night Bazaar / Chang Khlan — anything starting with Chang Khlan / or Pa Daet / or containing Night Bazaar or Chang Moi
    if (s.startswith("Chang Khlan /") or s == "Chang Khlan" or 
        s.startswith("Pa Daet /") or s == "Pa Daet" or 
        "Night Bazaar" in s or "Chang Moi" in s):
        return "Night Bazaar / Chang Khlan"
    
    # 10. Haiya / South Gate — anything starting with Haiya / or containing Wua Lai or South Gate
    if (s.startswith("Haiya /") or s == "Haiya" or 
        "Wua Lai" in s or "South Gate" in s):
        return "Haiya / South Gate"
    
    # 11. Fa Ham / Superhighway — anything starting with Fa Ham /
    if s.startswith("Fa Ham /") or s == "Fa Ham":
        return "Fa Ham / Superhighway"
    
    # 12. San Sai — anything starting with San Sai /
    if s.startswith("San Sai /") or s == "San Sai":
        return "San Sai"
    
    # 13. San Kamphaeng / Doi Saket — anything starting with San Kamphaeng / or Doi Saket / or Ban Thi or Mae On
    if (s.startswith("San Kamphaeng /") or s == "San Kamphaeng" or 
        s.startswith("Doi Saket /") or s == "Doi Saket" or 
        "Ban Thi" in s or "Mae On" in s or "San Kamphaeng" in s):
        return "San Kamphaeng / Doi Saket"
    
    # 14. Mae Taeng / Chiang Dao — anything containing Chiang Dao or Mae Taeng
    if "Chiang Dao" in s or "Mae Taeng" in s:
        return "Mae Taeng / Chiang Dao"
    
    # 15. Doi Inthanon / Chom Thong — anything containing Doi Inthanon or Chom Thong or Op Luang
    if "Doi Inthanon" in s or "Chom Thong" in s or "Op Luang" in s:
        return "Doi Inthanon / Chom Thong"
    
    # 16. Doi Suthep-Pui — Doi Suthep-Pui, Doi Suthep
    if s in ("Doi Suthep-Pui", "Doi Suthep"):
        return "Doi Suthep-Pui"
    
    # 17. Huay Kaew — anything starting with Huay Kaew / or Huay Kaew
    if s.startswith("Huay Kaew /") or s == "Huay Kaew":
        return "Huay Kaew"
    
    # 18. Pai / Mae Hong Son — anything containing Pai or Mae Hong Son or Pang Mapha
    if "Pai" in s or "Mae Hong Son" in s or "Pang Mapha" in s:
        return "Pai / Mae Hong Son"
    
    # 19. Chiang Rai / Golden Triangle — anything containing Chiang Rai or Golden Triangle or Wiang
    if "Chiang Rai" in s or "Golden Triangle" in s or "Wiang" in s:
        return "Chiang Rai / Golden Triangle"
    
    # 20. Nan Province — anything containing Nan Province or Nan 
    if "Nan Province" in s or "Nan " in s:
        return "Nan Province"
    
    # 21. Saraphi / Hot — anything containing Saraphi or Hot District or San Pa Tong or San Klang
    if ("Saraphi" in s or "Hot District" in s or 
        "San Pa Tong" in s or "San Klang" in s):
        return "Saraphi / Hot"
    
    # 22. Mae Hia — Mae Hia, Mae Hia / Canal Rd
    if s in ("Mae Hia", "Mae Hia / Canal Rd"):
        return "Mae Hia"
    
    # 23. Tha Sala — anything starting with Tha Sala
    if s.startswith("Tha Sala"):
        return "Tha Sala"
    
    # 24. Airport Area — anything starting with Airport
    if s.startswith("Airport"):
        return "Airport Area"
    
    # 25. Mueang Chiang Mai — keep as is
    if s == "Mueang Chiang Mai":
        return "Mueang Chiang Mai"
    
    # 26. San Phi Suea — anything starting with San Phi Suea
    if s.startswith("San Phi Suea"):
        return "San Phi Suea"
    
    # 27. Leave Other as Other (and fallback for unclassified like Mae Wang)
    return "Other"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("=" * 60)
    print("BEFORE NORMALIZATION")
    print("=" * 60)
    cur.execute("SELECT neighborhood, COUNT(*) as cnt FROM items GROUP BY neighborhood ORDER BY cnt DESC")
    before_rows = cur.fetchall()
    print(f"Total distinct neighborhoods before: {len(before_rows)}")
    for neigh, cnt in before_rows:
        print(f"  {neigh!r}: {cnt}")
    
    # Build mapping
    distinct_vals = [r[0] for r in before_rows]
    mapping = {}
    for v in distinct_vals:
        canonical = map_neighborhood(v)
        mapping[v] = canonical
    
    print("\n" + "=" * 60)
    print("UPDATING DATABASE")
    print("=" * 60)
    updated_count = 0
    for old_val, new_val in mapping.items():
        if old_val != new_val:
            cur.execute("UPDATE items SET neighborhood = ? WHERE neighborhood = ?", (new_val, old_val))
            updated_count += cur.rowcount
            print(f"  Updated {cur.rowcount:2d} rows: {old_val!r} -> {new_val!r}")
        else:
            print(f"  Kept unchanged: {old_val!r}")
            
    conn.commit()
    print(f"\nTotal rows updated: {updated_count}")
    
    print("\n" + "=" * 60)
    print("AFTER NORMALIZATION")
    print("=" * 60)
    cur.execute("SELECT neighborhood, COUNT(*) as cnt FROM items GROUP BY neighborhood ORDER BY cnt DESC")
    after_rows = cur.fetchall()
    print(f"Total distinct neighborhoods after: {len(after_rows)}")
    total_items = 0
    for neigh, cnt in after_rows:
        print(f"  {neigh!r}: {cnt}")
        total_items += cnt
    print(f"Total items in DB: {total_items}")
    
    conn.close()

if __name__ == "__main__":
    main()
