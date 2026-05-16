import hashlib
import requests
import json
from datetime import datetime, timezone
import time
from typing import List, Dict, Tuple, Any
from ledger_manager import load_ledger, save_ledger

ITUNES_BASE_URL = "https://itunes.apple.com"

TARGET_ARTISTS = [
    "Eminem", "Kendrick Lamar", "2Pac", "The Notorious B.I.G.",
    "Jay-Z", "Nas", "Dr. Dre", "Snoop Dogg", "50 Cent", "NF", "J. Cole", "Tech N9ne"
]

def get_previous_hash(ledger: List[Dict[str, Any]]) -> str:
    if not ledger:
        return "0000000000000000000000000000000000000000000000000000000000000000"
    return ledger[0]["hash"]

def create_block(
    artist: str, album: str, release_date: str, image_url: str,
    tracks: List[Dict[str, str]], prev_hash: str,
) -> Dict[str, Any]:
    timestamp = datetime.now(timezone.utc).isoformat()
    # Create deterministic string of track names for the hash
    tracks_str = "||".join([t["name"] for t in tracks])
    
    payload = f"{timestamp}|{artist}|{album}|{release_date}|{image_url}|{tracks_str}|{prev_hash}"
    block_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    return {
        "timestamp": timestamp,
        "artist": artist,
        "album": album,
        "release_date": release_date,
        "image_url": image_url,
        "tracks": tracks, # Now storing a dictionary with name and preview URL
        "prev_hash": prev_hash,
        "hash": block_hash,
    }

def fetch_artist_id(artist_name: str) -> str:
    url = f"{ITUNES_BASE_URL}/search?term={artist_name}&entity=musicArtist&limit=1"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("resultCount", 0) > 0:
            return str(data["results"][0]["artistId"])
    except Exception as e:
        print(f"⚠️ Error fetching ID for {artist_name}: {e}")
    return ""

def fetch_artist_albums(artist_id: str) -> List[Dict[str, Any]]:
    url = f"{ITUNES_BASE_URL}/lookup?id={artist_id}&entity=album"
    albums, seen_names = [], set()
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        for item in data.get("results", []):
            if item.get("wrapperType") == "collection":
                raw_name = item.get("collectionName", "")
                clean_name = raw_name.lower().replace(" (deluxe)", "").replace(" (explicit)", "").replace(" (clean)", "").strip()
                if clean_name not in seen_names:
                    seen_names.add(clean_name)
                    img_url = item.get("artworkUrl100", "").replace("100x100bb", "600x600bb")
                    albums.append({
                        "id": str(item["collectionId"]),
                        "artist": item.get("artistName", "Unknown"),
                        "album": raw_name,
                        "release_date": item.get("releaseDate", ""),
                        "image_url": img_url
                    })
    except Exception:
        pass
    return albums

def fetch_tracks_for_albums(album_ids: List[str]) -> Dict[str, List[Dict[str, str]]]:
    if not album_ids: return {}
    ids_str = ",".join(album_ids)
    url = f"{ITUNES_BASE_URL}/lookup?id={ids_str}&entity=song"
    track_map: Dict[str, List[Dict[str, str]]] = {aid: [] for aid in album_ids}
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        for item in data.get("results", []):
            if item.get("wrapperType") == "track":
                col_id = str(item.get("collectionId", ""))
                track_name = item.get("trackName", "")
                preview_url = item.get("previewUrl", "") # <--- GRABBING AUDIO URL
                if col_id in track_map and track_name:
                    track_map[col_id].append({"name": track_name, "preview": preview_url})
    except Exception:
        pass
    return track_map

def build_discography_ledger() -> None:
    print("🚀 Starting Discography Ledger Engine...")
    ledger = load_ledger()
    existing_records = { f"{b['artist'].lower()}||{b['album'].lower()}" for b in ledger }
    added_count = 0

    for artist in TARGET_ARTISTS:
        print(f"\n🔍 Processing Artist: {artist}")
        artist_id = fetch_artist_id(artist)
        if not artist_id: continue
            
        albums = fetch_artist_albums(artist_id)
        albums.sort(key=lambda x: x["release_date"])
        
        batch_size = 30
        for i in range(0, len(albums), batch_size):
            batch = albums[i:i+batch_size]
            batch_ids = [a["id"] for a in batch]
            track_data = fetch_tracks_for_albums(batch_ids)
            time.sleep(2) 
            
            for album_info in batch:
                record_key = f"{album_info['artist'].lower()}||{album_info['album'].lower()}"
                if record_key in existing_records: continue
                    
                tracks = track_data.get(album_info["id"], [])
                if not tracks: continue 
                    
                prev_hash = get_previous_hash(ledger)
                block = create_block(
                    artist=album_info["artist"], album=album_info["album"], release_date=album_info["release_date"],
                    image_url=album_info["image_url"], tracks=tracks, prev_hash=prev_hash
                )
                ledger.insert(0, block)
                existing_records.add(record_key)
                added_count += 1
                
        print(f"✅ Finished {artist}")

    if added_count > 0:
        print(f"\n💾 Saving {added_count} new albums to ledger...")
        save_ledger(ledger)
    else:
        print("\n📭 No new albums found. Ledger is up to date.")

if __name__ == "__main__":
    build_discography_ledger()