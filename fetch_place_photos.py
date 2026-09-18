import sqlite3
import urllib.request
import re
import os
import json
import base64
import time
from PIL import Image
import io

DB_PATH = 'chiangmai_guide.db'
PHOTOS_DIR = 'static/photos/places'
os.makedirs(PHOTOS_DIR, exist_ok=True)

UA_FACEBOOK = 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'
UA_BROWSER = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_photo_url(location_url):
    if not location_url:
        return None
        
    if 't.me/' in location_url:
        try:
            req = urllib.request.Request(location_url, headers={'User-Agent': UA_BROWSER})
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode('utf-8', errors='ignore')
                og = re.findall(r'<meta property="og:image" content="([^"]+)"', body)
                if og:
                    return og[0]
        except Exception as e:
            print(f"Error fetching t.me: {e}")
            return None

    # Check if AF1Qip photo is directly in the URL
    m_direct = re.search(r'https%3A%2F%2F(lh[0-9]\.googleusercontent\.com%2Fp%2F[A-Za-z0-9_-]+)', location_url)
    if m_direct:
        return 'https://' + m_direct.group(1).replace('%2F', '/')

    m_direct2 = re.search(r'(https://lh[0-9]\.googleusercontent\.com/p/[A-Za-z0-9_-]+)', location_url)
    if m_direct2:
        return m_direct2.group(1)

    # Fetch from Google Maps via crawler UA
    try:
        req = urllib.request.Request(location_url, headers={'User-Agent': UA_FACEBOOK})
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            
            # 1. Look for itemprop="image" or property="og:image"
            m = re.search(r'<meta content="([^"]+)" itemprop="image"', body)
            if not m:
                m = re.search(r'itemprop="image" content="([^"]+)"', body)
            if not m:
                m = re.search(r'<meta property="og:image" content="([^"]+)"', body)
                
            if m:
                raw_url = m.group(1)
                # Check if it's a dimg collage with base64 encoded urls
                if 'dimg-pa.googleapis.com' in raw_url:
                    b64_matches = re.findall(r'aHR0cHM[A-Za-z0-9_-]+', raw_url)
                    for b in b64_matches:
                        b_padded = b + '=' * (-len(b) % 4)
                        decoded = base64.b64decode(b_padded).decode('latin1', errors='ignore')
                        if 'googleusercontent.com' in decoded:
                            return decoded
                elif 'googleusercontent.com' in raw_url:
                    return raw_url
                    
            # 2. Search anywhere in body for googleusercontent
            lh = re.findall(r'https://lh[0-9]\.googleusercontent\.com/(?:p|gps-cs-s|grass-cs)/[A-Za-z0-9_-]+', body)
            if lh:
                return lh[0]
                
    except Exception as e:
        print(f"Error fetching Google Maps: {e}")
        return None

    return None

def download_and_save_image(photo_url, dest_path):
    if not photo_url:
        return False
        
    # Adjust size parameter for Google usercontent URLs
    fetch_url = photo_url
    if 'googleusercontent.com' in photo_url:
        # Strip any existing sizing like =w... or =s...
        base_url = re.sub(r'=[swh0-9k-p_]+$', '', photo_url)
        fetch_url = base_url + '=s1200'
        
    try:
        req = urllib.request.Request(fetch_url, headers={'User-Agent': UA_BROWSER})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            
        # Verify valid image
        img = Image.open(io.BytesIO(data))
        if img.size[0] < 100 or img.size[1] < 100 or len(data) < 5000:
            print(f"Image too small: {img.size}, {len(data)} bytes")
            return False
            
        # Convert RGBA/P to RGB if JPEG
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
            
        img.save(dest_path, 'JPEG', quality=88)
        return True
    except Exception as e:
        print(f"Error downloading image from {fetch_url[:60]}: {e}")
        # Try original photo_url without parameter change
        if fetch_url != photo_url:
            try:
                req = urllib.request.Request(photo_url, headers={'User-Agent': UA_BROWSER})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()
                img = Image.open(io.BytesIO(data))
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(dest_path, 'JPEG', quality=88)
                return True
            except Exception as e2:
                print(f"Error downloading original URL: {e2}")
        return False

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Target all items that do not have photos
    c.execute('''
        SELECT id, title, category, location_url, photos_json 
        FROM items 
        WHERE (status="active" OR status IS NULL)
        ORDER BY id
    ''')
    items = c.fetchall()
    
    missing = []
    for it in items:
        pid, title, cat, loc, pjson = it
        local_path = f"static/photos/places/{pid}.jpg"
        event_path = f"static/photos/events/{pid}.jpg"
        
        has_file = (os.path.exists(local_path) and os.path.getsize(local_path) > 3000) or \
                   (os.path.exists(event_path) and os.path.getsize(event_path) > 3000)
                   
        if not has_file:
            missing.append(it)
            
    print(f"Total missing places/items: {len(missing)}")
    
    success_count = 0
    failed_items = []
    
    for idx, (pid, title, cat, loc, pjson) in enumerate(missing, 1):
        print(f"[{idx}/{len(missing)}] Processing #{pid}: {title[:40]}...")
        photo_url = get_photo_url(loc)
        dest_path = f"static/photos/places/{pid}.jpg"
        
        if photo_url and download_and_save_image(photo_url, dest_path):
            # Update DB
            rel_path = f"static/photos/places/{pid}.jpg"
            c.execute('UPDATE items SET photos_json = ? WHERE id = ?', (json.dumps([rel_path]), pid))
            conn.commit()
            print(f"  ✓ Saved to {dest_path} ({os.path.getsize(dest_path)} bytes)")
            success_count += 1
        else:
            print(f"  ✗ Failed to fetch photo")
            failed_items.append((pid, title, loc))
            
        time.sleep(0.3)
        
    conn.close()
    print(f"\nDone! Successfully processed {success_count}/{len(missing)}")
    if failed_items:
        print("Failed:")
        for f in failed_items:
            print(f)

if __name__ == '__main__':
    main()
