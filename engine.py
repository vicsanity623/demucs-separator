import hashlib
import requests
import json
from datetime import datetime, timezone
import time
from typing import List, Dict, Tuple, Any
from ledger_manager import load_ledger, save_ledger

# We use iTunes API because it is free, unauthenticated, and highly accurate for discography/tracklists.
ITUNES_BASE_URL = "https://itunes.apple.com"

# The artists to build the discography ledger for
TARGET_ARTISTS = [
    "Eminem",
    "Kendrick Lamar",
    "2Pac",
    "The Notorious B.I.G.",
    "Jay-Z",
    "Nas",
    "Dr. Dre",
    "Snoop Dogg",
    "50 Cent",
    "Wu-Tang Clan",
    "J. Cole",
    "Drake"
]


def get_previous_hash(ledger: List[Dict[str, Any]]) -> str:
    if not ledger:
        return "0000000000000000000000000000000000000000000000000000000000000000"
    return ledger[0]["hash"]


def create_block(
    artist: str,
    album: str,
    release_date: str,
    image_url: str,
    tracks: List[str],
    prev_hash: str,
) -> Dict[str, Any]:
    timestamp = datetime.now(timezone.utc).isoformat()
    # Create a deterministic string of tracks for the hash payload
    tracks_str = "||".join(tracks)
    
    payload = f"{timestamp}|{artist}|{album}|{release_date}|{image_url}|{tracks_str}|{prev_hash}"
    block_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    return {
        "timestamp": timestamp,
        "artist": artist,
        "album": album,
        "release_date": release_date,
        "image_url": image_url,
        "tracks": tracks,
        "prev_hash": prev_hash,
        "hash": block_hash,
    }


def fetch_artist_id(artist_name: str) -> str:
    """Fetch the unique iTunes artist ID."""
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
    """Fetch all albums by the artist, handling basic deduplication."""
    url = f"{ITUNES_BASE_URL}/lookup?id={artist_id}&entity=album"
    albums = []
    seen_names = set()
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        for item in data.get("results", []):
            if item.get("wrapperType") == "collection":
                raw_name = item.get("collectionName", "")
                
                # Basic deduplication (ignore explicit/clean duplicates by standardizing names)
                clean_name = raw_name.lower().replace(" (deluxe)", "").replace(" (explicit)", "").replace(" (clean)", "").strip()
                
                if clean_name not in seen_names:
                    seen_names.add(clean_name)
                    # Request 600x600 high res album covers instead of the default 100x100
                    img_url = item.get("artworkUrl100", "").replace("100x100bb", "600x600bb")
                    albums.append({
                        "id": str(item["collectionId"]),
                        "artist": item.get("artistName", "Unknown"),
                        "album": raw_name,
                        "release_date": item.get("releaseDate", ""),
                        "image_url": img_url
                    })
    except Exception as e:
        print(f"⚠️ Error fetching albums for ID {artist_id}: {e}")
        
    return albums


def fetch_tracks_for_albums(album_ids: List[str]) -> Dict[str, List[str]]:
    """
    Fetch tracks for multiple albums at once to save API limits.
    Returns a dict mapping album_id -> list of track names.
    """
    if not album_ids:
        return {}
        
    # iTunes allows multiple IDs separated by commas
    ids_str = ",".join(album_ids)
    url = f"{ITUNES_BASE_URL}/lookup?id={ids_str}&entity=song"
    
    track_map: Dict[str, List[str]] = {aid: [] for aid in album_ids}
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        # iTunes returns both the collections and the tracks in the same flat list
        for item in data.get("results", []):
            if item.get("wrapperType") == "track":
                col_id = str(item.get("collectionId", ""))
                track_name = item.get("trackName", "")
                if col_id in track_map and track_name:
                    track_map[col_id].append(track_name)
    except Exception as e:
        print(f"⚠️ Error fetching tracks: {e}")
        
    return track_map


def build_discography_ledger() -> None:
    print("🚀 Starting Discography Ledger Engine...")
    ledger = load_ledger()
    
    # Create a fast lookup set of "Artist - Album" to avoid duplicate blocks
    existing_records = { f"{b['artist'].lower()}||{b['album'].lower()}" for b in ledger }
    
    added_count = 0

    for artist in TARGET_ARTISTS:
        print(f"\n🔍 Processing Artist: {artist}")
        artist_id = fetch_artist_id(artist)
        
        if not artist_id:
            print(f"❌ Could not find iTunes ID for {artist}. Skipping.")
            continue
            
        albums = fetch_artist_albums(artist_id)
        
        # Sort albums chronologically (oldest first).
        # We process oldest first, inserting them at the beginning of the ledger. 
        # This results in the ledger having the *newest* albums at index 0 (top of the feed).
        albums.sort(key=lambda x: x["release_date"])
        
        # Batch requests to get tracklists (max 30 albums per request)
        batch_size = 30
        for i in range(0, len(albums), batch_size):
            batch = albums[i:i+batch_size]
            batch_ids = [a["id"] for a in batch]
            
            print(f"   Fetching tracklists for {len(batch)} albums...")
            track_data = fetch_tracks_for_albums(batch_ids)
            time.sleep(2) # Respect API rate limits
            
            for album_info in batch:
                record_key = f"{album_info['artist'].lower()}||{album_info['album'].lower()}"
                
                if record_key in existing_records:
                    continue
                    
                tracks = track_data.get(album_info["id"], [])
                if not tracks:
                    continue # Skip albums with empty tracklists
                    
                prev_hash = get_previous_hash(ledger)
                block = create_block(
                    artist=album_info["artist"],
                    album=album_info["album"],
                    release_date=album_info["release_date"],
                    image_url=album_info["image_url"],
                    tracks=tracks,
                    prev_hash=prev_hash
                )
                
                # Insert at the front so newest processed is at top
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