import hashlib
import requests
import json
import os
import zipfile
import shutil
from datetime import datetime, timezone
import random
import time
import re
from typing import List, Dict, Any, Optional
from moviepy import VideoFileClip, AudioFileClip
from ledger_manager import load_ledger, save_ledger

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
MEDIA_FOLDER    = "media"
MAX_FILE_BYTES  = 100 * 1024 * 1024   # 100 MB cap per file
REPO_WARN_BYTES = 950 * 1024 * 1024   # Zip folder when near 950 MB
ZIP_PREFIX      = "media_archive"
MIN_VIDEO_BYTES = 40 * 1024            # Reject stubs / corrupt files < 40 KB

os.makedirs(MEDIA_FOLDER, exist_ok=True)

# Sourcing targets from open networks
LEMMY_INSTANCES = ["https://lemmy.world", "https://sh.itjust.works"]
LEMMY_COMMUNITIES = ["ufos", "aliens", "uap", "strangeearth", "paranormal", "conspiracy"]
FOURCHAN_BOARD = "x"

POSITIVE_KEYWORDS = [
    "ufo", "uap", "orb", "saucer", "tic tac", "tic-tac", "triangle",
    "sighting", "craft", "phenomenon", "footage", "video", "nhi",
    "unidentified", "aerial", "anomalous", "encounter",
    "unknown object", "lights in the sky", "hovering"
]
NEGATIVE_KEYWORDS = [
    "furry", "meme", "cgi", "vfx", "blender", "movie", "game", "art",
    "drawing", "tattoo", "fiction", "joke", "animation", "render",
    "skyrim", "minecraft", "parody", "satire", "deepfake", "photoshop"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# ─────────────────────────────────────────────────────────────────────────────
# DOWNLOAD HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _download(url: str, dest: str, max_bytes: int = MAX_FILE_BYTES) -> bool:
    """Stream-download url → dest. Returns True on success."""
    try:
        r = requests.get(url, stream=True, timeout=25, headers=HEADERS)
        if r.status_code != 200:
            print(f"   ✗ HTTP {r.status_code} — {url[:70]}")
            return False
        written = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
                written += len(chunk)
                if written > max_bytes:
                    print(f"   ✗ File too large, aborting.")
                    return False
        return True
    except requests.exceptions.Timeout:
        print(f"   ✗ Timeout: {url[:70]}")
    except Exception as e:
        print(f"   ✗ Download error: {e}")
    return False


def _valid(path: str) -> bool:
    """Return True if file exists and is at least MIN_VIDEO_BYTES."""
    return os.path.exists(path) and os.path.getsize(path) >= MIN_VIDEO_BYTES


def _reddit_audio_url(video_url: str) -> str:
    """Convert a Reddit DASH video URL to its audio track URL."""
    base = video_url.split("?")[0]
    return re.sub(r"/DASH_[^/]+\.mp4$", "/DASH_audio.mp4", base)

# ─────────────────────────────────────────────────────────────────────────────
# VIDEO MERGING
# ─────────────────────────────────────────────────────────────────────────────

def merge_reddit_video(video_url: str, audio_url: str, final_path: str) -> bool:
    """Download + merge Reddit's separated video/audio tracks into one MP4."""
    v_tmp = final_path + ".v.tmp"
    a_tmp = final_path + ".a.tmp"
    ok = False
    try:
        print(f"   ↓ video track …")
        if not _download(video_url, v_tmp) or not _valid(v_tmp):
            return False

        print(f"   ↓ audio track …")
        has_audio = _download(audio_url, a_tmp) and _valid(a_tmp)

        if has_audio:
            vc = VideoFileClip(v_tmp)
            ac = AudioFileClip(a_tmp)
            print(f"   ⚙  merging A/V …")
            vc.with_audio(ac).write_videofile(
                final_path, fps=30,
                codec="libx264", audio_codec="aac",
                audio_bitrate="192k", logger=None
            )
            vc.close(); ac.close()
        else:
            shutil.copy(v_tmp, final_path)

        ok = _valid(final_path)
    except Exception as e:
        print(f"   ✗ Merge error: {e}")
    finally:
        for p in (v_tmp, a_tmp):
            if os.path.exists(p):
                try: os.remove(p)
                except: pass
    return ok

# ─────────────────────────────────────────────────────────────────────────────
# OPEN DATA SCRAPING (Lemmy & 4chan)
# ─────────────────────────────────────────────────────────────────────────────

def _passes_filter(title: str, body: str) -> bool:
    combined = (title + " " + body).lower()
    if not any(kw in combined for kw in POSITIVE_KEYWORDS):
        return False
    if any(kw in combined for kw in NEGATIVE_KEYWORDS):
        return False
    return True


def fetch_lemmy_sources() -> List[Dict]:
    results = []
    # Pick a random instance from the list to spread load
    base_instance = random.choice(LEMMY_INSTANCES)
    
    for community in LEMMY_COMMUNITIES:
        print(f"  📡 Lemmy c/{community} via {base_instance}")
        try:
            url = f"{base_instance}/api/v3/post/list?community_name={community}&sort=New&limit=25"
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"     skip: HTTP {r.status_code}")
                continue
                
            data = r.json()
            posts = data.get("posts", [])
            for item in posts:
                post_data = item.get("post", {})
                title = post_data.get("name", "")
                body = post_data.get("body", "")
                media_url = post_data.get("url", "")
                
                if not media_url:
                    continue
                
                # Check if it targets a video format
                is_video = media_url.lower().endswith((".mp4", ".webm", ".mov", ".gifv")) or "v.redd.it" in media_url
                if not is_video:
                    continue
                    
                if not _passes_filter(title, body):
                    continue
                
                creator_data = item.get("creator", {})
                counts_data = item.get("counts", {})
                score = counts_data.get("score", 0)
                
                audio_url = ""
                platform = "lemmy_direct"
                if "v.redd.it" in media_url:
                    # Resolve native reddit video layouts if shared on Lemmy
                    media_url = media_url.split("?")[0]
                    if not media_url.endswith(".mp4"):
                        media_url = f"{media_url}/DASH_720.mp4"
                    audio_url = _reddit_audio_url(media_url)
                    platform = "reddit_native"

                results.append({
                    "source": f"Lemmy c/{community}",
                    "author": creator_data.get("name", "Anonymous"),
                    "title": title,
                    "description": body,
                    "media_url": media_url,
                    "thumbnail_url": post_data.get("thumbnail_url") or "",
                    "media_type": "video",
                    "audio_url": audio_url,
                    "source_url": post_data.get("ap_id") or f"{base_instance}/post/{post_data.get('id')}",
                    "score": max(0, score),
                    "platform": platform
                })
        except Exception as e:
            print(f"     skip error: {e}")
        time.sleep(random.uniform(1.0, 2.5))
        
    return results


def fetch_4chan_sources() -> List[Dict]:
    print(f"  🍀 4chan /{FOURCHAN_BOARD}/")
    results = []
    try:
        catalog_url = f"https://a.4cdn.org/{FOURCHAN_BOARD}/catalog.json"
        r = requests.get(catalog_url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print(f"  ✗ 4chan catalog failed: HTTP {r.status_code}")
            return []
            
        catalog = r.json()
        processed_threads = 0
        
        # Look across more pages since video frequency on /x/ is sparse
        for page in catalog[:8]:
            for thread in page.get("threads", []):
                thread_no = thread.get("no")
                ext = thread.get("ext", "")
                
                if ext not in (".webm", ".mp4"):
                    continue
                    
                comment = re.sub(r"<[^>]+>", " ", thread.get("com", ""))
                title = thread.get("sub") or comment[:80] or f"UAP Thread {thread_no}"
                
                if not _passes_filter(title, comment):
                    continue
                    
                tid = thread["tim"]
                results.append({
                    "source": f"4chan /{FOURCHAN_BOARD}/",
                    "author": thread.get("name", "Anonymous"),
                    "title": title,
                    "description": comment,
                    "media_url": f"https://i.4cdn.org/{FOURCHAN_BOARD}/{tid}{ext}",
                    "thumbnail_url": f"https://i.4cdn.org/{FOURCHAN_BOARD}/{tid}s.jpg",
                    "media_type": "video",
                    "audio_url": "",
                    "source_url": f"https://boards.4channel.org/{FOURCHAN_BOARD}/thread/{thread_no}",
                    "score": 0,
                    "platform": "4chan"
                })
                processed_threads += 1
                
        print(f"     Found {processed_threads} matching video threads on 4chan.")
    except Exception as e:
        print(f"  ✗ 4chan error: {e}")
        
    return results


def fetch_all_sources() -> List[Dict]:
    results = []
    # Merge findings from open channels
    results.extend(fetch_lemmy_sources())
    results.extend(fetch_4chan_sources())
    random.shuffle(results)
    return results

# ─────────────────────────────────────────────────────────────────────────────
# ARCHIVAL
# ─────────────────────────────────────────────────────────────────────────────

def _zip_media_folder():
    ts  = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = f"{ZIP_PREFIX}_{ts}.zip"
    print(f"🗜  Threshold reached — archiving → {out}")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in os.listdir(MEDIA_FOLDER):
            zf.write(os.path.join(MEDIA_FOLDER, f), arcname=f)
    shutil.rmtree(MEDIA_FOLDER)
    os.makedirs(MEDIA_FOLDER)


def check_and_zip_if_full():
    total = sum(
        os.path.getsize(os.path.join(MEDIA_FOLDER, f))
        for f in os.listdir(MEDIA_FOLDER)
        if os.path.isfile(os.path.join(MEDIA_FOLDER, f))
    )
    if total >= REPO_WARN_BYTES:
        _zip_media_folder()


def build_ledger():
    print("🛸  AXIOM UAP — Open-Network Video Archivist\n")
    ledger   = load_ledger()
    existing = {b["source_url"] for b in ledger}
    new_data = fetch_all_sources()
    added    = 0

    for s in new_data:
        if s["source_url"] in existing:
            continue

        file_id    = hashlib.md5(s["media_url"].encode()).hexdigest()
        final_path = os.path.join(MEDIA_FOLDER, f"{file_id}.mp4")
        local_url  = f"./media/{file_id}.mp4"

        if not os.path.exists(final_path):
            print(f"\n📦  {s['title'][:60]}")
            print(f"    {s['source']} | {s['platform']}")

            if s["platform"] == "reddit_native":
                archived = merge_reddit_video(s["media_url"], s["audio_url"], final_path)
            else:
                archived = _download(s["media_url"], final_path)
                if archived and not _valid(final_path):
                    print(f"   ✗ File too small/corrupt — discarding.")
                    try: os.remove(final_path)
                    except: pass
                    archived = False

            # If local download fails, fall back gracefully to the original CDN url
            if not archived:
                local_url = s["media_url"]

        timestamp = datetime.now(timezone.utc).isoformat()
        payload   = f"{timestamp}|{s['source']}|{s['title']}|{s['media_url']}|{s['score']}"

        ledger.insert(0, {
            "timestamp":     timestamp,
            "source":        s["source"],
            "author":        s["author"],
            "title":         s["title"],
            "description":   s["description"][:800],
            "media_url":     local_url,
            "thumbnail_url": s["thumbnail_url"],
            "media_type":    "video",
            "source_url":    s["source_url"],
            "hash":          hashlib.sha256(payload.encode()).hexdigest(),
            "score":         s["score"],
            "platform":      s.get("platform", "unknown")
        })
        existing.add(s["source_url"])
        added += 1

    save_ledger(ledger) # Save the ledger even if 0 items were added, to maintain integrity
    check_and_zip_if_full()
    print(f"\n✅  Done — {added} new video sightings archived.")


if __name__ == "__main__":
    build_ledger()