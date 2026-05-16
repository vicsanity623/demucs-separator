import hashlib
import requests
import json
from datetime import datetime, timezone
import time
import re
import random
from typing import List, Dict, Any
from ledger_manager import load_ledger, save_ledger

REDDIT_SUBS = ["UFOs", "UAP", "Aliens", "UFObelievers", "UFOdocumentaries", "UFOscience", "Mufon", "Experiencers", "TheUAPReport", "Skies_Above"]
FOURCHAN_BOARD = "x"

SEARCH_QUERIES = ["ufo sighting video", "uap footage", "unidentified aerial", "strange lights sky"]

POSITIVE_KEYWORDS = ["ufo", "uap", "orb", "saucer", "tic tac", "tic-tac", "triangle", "sighting", "craft", "phenomenon", "footage", "video"]
NEGATIVE_KEYWORDS = ["furry", "psyop", "meme", "fake", "debunk", "cgi", "vfx", "blender", "movie", "game", "art", "drawing", "tattoo", "fiction", "joke", "project blue beam"]

def get_previous_hash(ledger: List[Dict[str, Any]]) -> str:
    if not ledger:
        return "0000000000000000000000000000000000000000000000000000000000000000"
    return ledger[0]["hash"]

def create_block(source, author, title, description, media_url, thumbnail_url, media_type, source_url, prev_hash, score=0):
    timestamp = datetime.now(timezone.utc).isoformat()
    payload = f"{timestamp}|{source}|{title}|{media_url}|{score}|{prev_hash}"
    block_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return {
        "timestamp": timestamp, "source": source, "author": author, "title": title,
        "description": description[:800], "media_url": media_url, "thumbnail_url": thumbnail_url,
        "media_type": media_type, "source_url": source_url, "prev_hash": prev_hash,
        "hash": block_hash, "score": score
    }

def is_high_quality(title, text):
    content = (title + " " + text).lower()
    return any(kw in content for kw in POSITIVE_KEYWORDS) and not any(kw in content for kw in NEGATIVE_KEYWORDS)

def process_reddit_data(data, source_label):
    results = []
    posts = data.get("data", {}).get("children", [])
    for post in posts:
        p = post["data"]
        title = p.get("title", "")
        
        min_score = 30 if "r/" in source_label else 10
        if p.get("score", 0) < min_score or not is_high_quality(title, p.get("selftext", "")): continue
        
        media_url, thumbnail_url, media_type = "", "", ""

        if p.get("preview") and p["preview"].get("images"):
            img_data = p["preview"]["images"][0]
            
            if "variants" in img_data and "mp4" in img_data["variants"]:
                media_url = img_data["variants"]["mp4"]["source"]["url"]
                media_type = "video"
                res = img_data.get("resolutions", [])
                thumbnail_url = res[2]["url"] if len(res) > 2 else img_data["source"]["url"]
            
            elif not p.get("is_video"):
                media_url = img_data["source"]["url"]
                res = img_data.get("resolutions", [])
                thumbnail_url = res[2]["url"] if len(res) > 2 else media_url
                media_type = "image"

        if not media_url and p.get("is_video") and p.get("media") and p["media"].get("reddit_video"):
            media_url = p["media"]["reddit_video"].get("fallback_url", "")
            thumbnail_url = p.get("thumbnail", "")
            media_type = "video"

        if media_url and (thumbnail_url not in ["self", "default", ""]):
            results.append({
                "source": source_label, "author": p.get("author", "Anonymous"),
                "title": title, "description": p.get("selftext", ""),
                "media_url": media_url, "thumbnail_url": thumbnail_url,
                "media_type": media_type, "source_url": f"https://reddit.com{p.get('permalink', '')}",
                "score": p.get("score", 0)
            })
    return results

def fetch_reddit_sightings():
    results = []
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/114.0 Firefox/114.0"})

    for sub in REDDIT_SUBS:
        for sort in ["hot", "rising"]:
            print(f"Scraping /r/{sub} ({sort})...")
            url = f"https://www.reddit.com/r/{sub}/{sort}.json?limit=15&raw_json=1"
            try:
                res = session.get(url, timeout=15)
                if res.status_code == 200:
                    results.extend(process_reddit_data(res.json(), f"Reddit (/r/{sub})"))
            except: pass
            time.sleep(2)

    for query in SEARCH_QUERIES:
        print(f"Global Discovery Search: '{query}'...")
        url = f"https://www.reddit.com/search.json?q={query}&sort=new&limit=20&raw_json=1"
        try:
            res = session.get(url, timeout=15)
            if res.status_code == 200:
                results.extend(process_reddit_data(res.json(), "Reddit Discovery"))
        except: pass
        time.sleep(2)
        
    return results

def fetch_4chan_sightings():
    results = []
    print("Scraping 4chan /x/...")
    try:
        res = requests.get(f"https://a.4cdn.org/{FOURCHAN_BOARD}/catalog.json", timeout=10)
        for page in res.json():
            for thread in page.get("threads", []):
                comment = re.sub(r'<[^>]+>', ' ', thread.get("com", ""))
                if thread.get("replies", 0) > 10 and is_high_quality(thread.get("sub", ""), comment) and "tim" in thread:
                    results.append({
                        "source": "4chan (/x/)", "author": thread.get("name", "Anonymous"),
                        "title": thread.get("sub") or "UAP Intel", "description": comment,
                        "media_url": f"https://i.4cdn.org/{FOURCHAN_BOARD}/{thread['tim']}{thread['ext']}",
                        "thumbnail_url": f"https://i.4cdn.org/{FOURCHAN_BOARD}/{thread['tim']}s.jpg",
                        "media_type": "video" if thread['ext'] in [".webm", ".mp4"] else "image",
                        "source_url": f"https://boards.4channel.org/{FOURCHAN_BOARD}/thread/{thread['no']}",
                        "score": 0
                    })
    except: pass
    return results

def build_uap_ledger():
    print("🛸 Initializing High-Discovery UAP Tracker...")
    ledger = load_ledger()
    existing_urls = { b["media_url"] for b in ledger }
    new_sightings = fetch_reddit_sightings() + fetch_4chan_sightings()
    added = 0
    for s in new_sightings:
        if s["media_url"] in existing_urls: continue
        block = create_block(s["source"], s["author"], s["title"], s["description"], s["media_url"], s["thumbnail_url"], s["media_type"], s["source_url"], get_previous_hash(ledger), s["score"])
        ledger.insert(0, block)
        existing_urls.add(s["media_url"])
        added += 1
    if added > 0:
        save_ledger(ledger)
        print(f"✅ Sealed {added} new sightings.")
    else:
        print("📭 No new unique sightings found.")

if __name__ == "__main__":
    build_uap_ledger()