import hashlib
import requests
import json
from datetime import datetime, timezone
import time
import re
from typing import List, Dict, Any
from ledger_manager import load_ledger, save_ledger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# Target platforms
REDDIT_SUBS = ["UFOs", "aliens", "HighStrangeness", "UAP"]
FOURCHAN_BOARD = "x"

KEYWORDS = ["ufo", "uap", "alien", "extraterrestrial", "area 51", "sighting", "craft", "orb", "saucer"]

def get_previous_hash(ledger: List[Dict[str, Any]]) -> str:
    if not ledger:
        return "0000000000000000000000000000000000000000000000000000000000000000"
    return ledger[0]["hash"]

def create_block(
    source: str, author: str, title: str, description: str,
    media_url: str, media_type: str, source_url: str, prev_hash: str
) -> Dict[str, Any]:
    timestamp = datetime.now(timezone.utc).isoformat()
    # Basic payload to hash
    payload = f"{timestamp}|{source}|{author}|{title}|{media_url}|{prev_hash}"
    block_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    return {
        "timestamp": timestamp,
        "source": source,
        "author": author,
        "title": title,
        "description": description[:1000], # Limit desc to avoid giant blocks
        "media_url": media_url,
        "media_type": media_type, # 'video' or 'image'
        "source_url": source_url,
        "prev_hash": prev_hash,
        "hash": block_hash,
    }

def contains_keywords(text: str) -> bool:
    text = text.lower()
    return any(kw in text for kw in KEYWORDS)

def fetch_reddit_sightings() -> List[Dict[str, Any]]:
    results = []
    for sub in REDDIT_SUBS:
        print(f"Scraping Reddit: /r/{sub}...")
        url = f"https://www.reddit.com/r/{sub}/new.json?limit=50"
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            
            if res.status_code == 429:
                print(f"⚠️ Reddit Rate Limited (429) for /r/{sub}. Sleeping for 5s...")
                time.sleep(5)
                continue
            elif res.status_code != 200:
                print(f"⚠️ Reddit blocked request for /r/{sub} (Status: {res.status_code}).")
                continue

            data = res.json()
            posts = data.get("data", {}).get("children", [])
            
            for post in posts:
                p_data = post["data"]
                title = p_data.get("title", "")
                
                if not contains_keywords(title):
                    continue
                
                media_url = ""
                media_type = ""
                
                if p_data.get("is_video") and "media" in p_data and p_data["media"]:
                    reddit_video = p_data["media"].get("reddit_video", {})
                    media_url = reddit_video.get("fallback_url", "")
                    media_type = "video"
                elif "url_overridden_by_dest" in p_data:
                    url_dest = p_data["url_overridden_by_dest"]
                    if url_dest.endswith((".jpg", ".png", ".jpeg")):
                        media_url = url_dest
                        media_type = "image"
                    elif url_dest.endswith((".gif", ".mp4")):
                        media_url = url_dest
                        media_type = "video"
                        
                if media_url:
                    desc = p_data.get("selftext", "")
                    results.append({
                        "source": f"Reddit (/r/{sub})",
                        "author": p_data.get("author", "Anonymous"),
                        "title": title,
                        "description": desc[:1000] + ("..." if len(desc) > 1000 else ""),
                        "media_url": media_url,
                        "media_type": media_type,
                        "source_url": f"https://reddit.com{p_data.get('permalink', '')}"
                    })
        except Exception as e:
            print(f"⚠️ Error with /r/{sub}: {e}")
        
        time.sleep(6) 
        
    return results

def fetch_4chan_sightings() -> List[Dict[str, Any]]:
    results = []
    print(f"Scraping 4chan: /{FOURCHAN_BOARD}/...")
    catalog_url = f"https://a.4cdn.org/{FOURCHAN_BOARD}/catalog.json"
    
    try:
        res = requests.get(catalog_url, headers=HEADERS, timeout=10)
        catalog = res.json()
        
        for page in catalog:
            for thread in page.get("threads", []):
                title = thread.get("sub", "")
                comment = thread.get("com", "")
                
                # Check keywords in title or comment
                if contains_keywords(title) or contains_keywords(comment):
                    # Check if thread has an image/video attached
                    if "tim" in thread and "ext" in thread:
                        tim = thread["tim"]
                        ext = thread["ext"]
                        media_url = f"https://i.4cdn.org/{FOURCHAN_BOARD}/{tim}{ext}"
                        
                        media_type = "video" if ext in [".webm", ".mp4"] else "image"
                        
                        # Strip HTML tags from 4chan comments
                        clean_desc = re.sub(r'<[^>]+>', ' ', comment)
                        
                        results.append({
                            "source": f"4chan (/{FOURCHAN_BOARD}/)",
                            "author": thread.get("name", "Anonymous"),
                            "title": title if title else "UAP Thread (No Title)",
                            "description": clean_desc,
                            "media_url": media_url,
                            "media_type": media_type,
                            "source_url": f"https://boards.4channel.org/{FOURCHAN_BOARD}/thread/{thread.get('no')}"
                        })
    except Exception as e:
        print(f"⚠️ Error with 4chan: {e}")
        
    return results

def build_uap_ledger() -> None:
    print("🛸 Initializing Axiom UAP Tracker...")
    ledger = load_ledger()
    
    # Fast lookup to prevent duplicate URLs being sealed
    existing_urls = { b["media_url"] for b in ledger }
    added_count = 0

    # Fetch Intel
    new_sightings = fetch_reddit_sightings() + fetch_4chan_sightings()
    
    for sighting in new_sightings:
        if sighting["media_url"] in existing_urls:
            continue
            
        prev_hash = get_previous_hash(ledger)
        block = create_block(
            source=sighting["source"],
            author=sighting["author"],
            title=sighting["title"],
            description=sighting["description"],
            media_url=sighting["media_url"],
            media_type=sighting["media_type"],
            source_url=sighting["source_url"],
            prev_hash=prev_hash
        )
        
        ledger.insert(0, block)
        existing_urls.add(sighting["media_url"])
        added_count += 1

    if added_count > 0:
        print(f"\n💾 Encrypting {added_count} new sightings into ledger...")
        save_ledger(ledger)
    else:
        print("\n📭 No new sightings verified. Ledger is up to date.")

if __name__ == "__main__":
    build_uap_ledger()