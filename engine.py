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
MEDIA_FOLDER = "media"
MAX_FILE_BYTES = 100 * 1024 * 1024  # 100 MB cap per file
REPO_WARN_BYTES = 950 * 1024 * 1024  # Zip folder when near 950 MB
ZIP_PREFIX = "media_archive"
MIN_VIDEO_BYTES = 40 * 1024  # Reject corrupt files < 40 KB
MIN_SCORE = 10  # Minimum upvotes for validation
os.makedirs(MEDIA_FOLDER, exist_ok=True)

# Reddit targets
REDDIT_SUBS = [
    "UFOs", "UAP", "Aliens", "UFObelievers", "UFOdocumentaries",
    "UFOscience", "Mufon", "Experiencers", "TheUAPReport", "Skies_Above",
    "ufo", "NHI", "DisclosureFiles", "Paranormal", "conspiracy",
    "StrangeEarth", "UnexplainedPhenomena"
]

# CURRENT WORKING REDLIB INSTANCES (June 2026) - from official list
REDLIB_INSTANCES = [
    "https://redlib.catsarch.com",
    "https://redlib.perennialte.ch",
    "https://redlib.r4fo.com",
    "https://red.artemislena.eu",
    "https://redlib.cow.rip",
    "https://redlib.privacyredirect.com",
    "https://redlib.nadeko.net",
    "https://redlib.orangenet.cc",
    "https://redlib.privadency.com",
    "https://safereddit.com",  # Still commonly referenced
    "https://redlib.zaggy.nl",
]

# Lemmy
LEMMY_INSTANCES = ["https://lemmy.world", "https://lemmy.ml"]
LEMMY_COMMUNITIES = ["ufos", "aliens", "uap", "strangeearth", "paranormal", "conspiracy"]

# 4chan
FOURCHAN_BOARD = "x"
POSITIVE_KEYWORDS = [
    "ufo", "uap", "orb", "saucer", "tic tac", "tic-tac", "triangle",
    "sighting", "craft", "phenomenon", "footage", "video", "nhi",
    "unidentified", "aerial", "anomalous", "encounter", "lights in the sky"
]
NEGATIVE_KEYWORDS = [
    "furry", "meme", "cgi", "vfx", "blender", "movie", "game", "art",
    "drawing", "tattoo", "fiction", "joke", "animation", "render",
    "satire", "deepfake", "photoshop", "minecraft"
]

# Expanded realistic User-Agent + browser fingerprint pool
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
]

def get_random_headers(referer: Optional[str] = None) -> Dict[str, str]:
    """Generate highly randomized realistic browser headers."""
    ua = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8", "en-CA,en;q=0.9"]),
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Site": random.choice(["none", "same-origin"]),
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Not-A.Brand";v="99", "Chromium";v="126"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
    }
    if referer:
        headers["Referer"] = referer
    return headers

# ─────────────────────────────────────────────────────────────────────────────
# DOWNLOAD HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _download(url: str, dest: str, max_bytes: int = MAX_FILE_BYTES, referer: Optional[str] = None) -> bool:
    """Stream-download with retries, jitter, and randomized headers."""
    headers = get_random_headers(referer)
    for attempt in range(4):
        try:
            r = requests.get(url, stream=True, timeout=30, headers=headers)
            if r.status_code == 200:
                written = 0
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(16384):
                        f.write(chunk)
                        written += len(chunk)
                        if written > max_bytes:
                            print(f" ✗ File too large, aborting.")
                            return False
                return True
            elif r.status_code in (403, 429, 503):
                wait = random.uniform(10, 25) * (attempt + 1)
                print(f" ✗ Rate-limited ({r.status_code}) — backing off {wait:.1f}s")
                time.sleep(wait)
                continue
            else:
                print(f" ✗ HTTP {r.status_code} — {url[:80]}")
                return False
        except Exception as e:
            print(f" ✗ Download error attempt {attempt+1}: {e}")
        time.sleep(random.uniform(4, 12))
    return False

def _valid(path: str) -> bool:
    return os.path.exists(path) and os.path.getsize(path) >= MIN_VIDEO_BYTES

def _reddit_audio_url(video_url: str) -> str:
    base = video_url.split("?")[0]
    return re.sub(r"/DASH_[^/]+\.mp4$", "/DASH_audio.mp4", base)

# ─────────────────────────────────────────────────────────────────────────────
# VIDEO MERGING
# ─────────────────────────────────────────────────────────────────────────────
def merge_reddit_video(video_url: str, audio_url: str, final_path: str) -> bool:
    v_tmp = final_path + ".v.tmp"
    a_tmp = final_path + ".a.tmp"
    ok = False
    try:
        print(f" ↓ video track …")
        if not _download(video_url, v_tmp, referer=video_url) or not _valid(v_tmp):
            return False
        print(f" ↓ audio track …")
        has_audio = _download(audio_url, a_tmp, referer=video_url) and _valid(a_tmp)
        if has_audio:
            vc = VideoFileClip(v_tmp)
            ac = AudioFileClip(a_tmp)
            print(f" ⚙ merging A/V …")
            vc.with_audio(ac).write_videofile(
                final_path, fps=30, codec="libx264", audio_codec="aac",
                audio_bitrate="192k", logger=None
            )
            vc.close(); ac.close()
        else:
            shutil.copy(v_tmp, final_path)
        ok = _valid(final_path)
    except Exception as e:
        print(f" ✗ Merge error: {e}")
    finally:
        for p in (v_tmp, a_tmp):
            if os.path.exists(p):
                try: os.remove(p)
                except: pass
    return ok

# ─────────────────────────────────────────────────────────────────────────────
# SCRAPERS
# ─────────────────────────────────────────────────────────────────────────────
def _passes_filter(title: str, body: str, score: int = MIN_SCORE) -> bool:
    combined = (title + " " + body).lower()
    if not any(kw in combined for kw in POSITIVE_KEYWORDS):
        return False
    if any(kw in combined for kw in NEGATIVE_KEYWORDS):
        return False
    return score >= MIN_SCORE

def _extract_reddit_videos(data: dict, label: str) -> List[Dict]:
    results = []
    for post in data.get("data", {}).get("children", []):
        p = post.get("data", {})
        title = p.get("title", "")
        body = p.get("selftext", "")
        score = p.get("score", 0)
        if not _passes_filter(title, body, score):
            continue

        if p.get("is_video") and p.get("media", {}).get("reddit_video"):
            rv = p["media"]["reddit_video"]
            raw_url = rv.get("fallback_url", "").split("?")[0]
            if not raw_url:
                continue
            results.append({
                "source": label,
                "author": p.get("author", "Anonymous"),
                "title": title,
                "description": body,
                "media_url": raw_url,
                "thumbnail_url": p.get("thumbnail", ""),
                "media_type": "video",
                "audio_url": _reddit_audio_url(raw_url),
                "source_url": f"https://reddit.com{p['permalink']}",
                "score": score,
                "platform": "reddit_native"
            })
            continue

        # Preview MP4
        preview = p.get("preview", {})
        if preview.get("images"):
            img = preview["images"][0]
            if "variants" in img and "mp4" in img["variants"]:
                mp4_url = img["variants"]["mp4"]["source"]["url"]
                res = img.get("resolutions", [])
                thumb = res[-1]["url"] if res else img["source"]["url"]
                results.append({
                    "source": label,
                    "author": p.get("author", "Anonymous"),
                    "title": title,
                    "description": body,
                    "media_url": mp4_url,
                    "thumbnail_url": thumb,
                    "media_type": "video",
                    "audio_url": "",
                    "source_url": f"https://reddit.com{p['permalink']}",
                    "score": score,
                    "platform": "reddit_preview"
                })
    return results

def fetch_reddit_sources() -> List[Dict]:
    """Robust Redlib scraping with heavy randomization and fallbacks."""
    results = []
    subs = REDDIT_SUBS.copy()
    random.shuffle(subs)

    for sub in subs[:3]:  # Reduced to 3 subs per run for stealth
        success = False
        instances = REDLIB_INSTANCES.copy()
        random.shuffle(instances)

        for instance in instances:
            sort = random.choice(["hot", "new", "rising", "top"])
            url = f"{instance}/r/{sub}/{sort}.json?limit=12&t=month"
            print(f" 📡 Trying {instance} → /r/{sub}/{sort}")

            headers = get_random_headers(referer=instance.rstrip('/'))
            try:
                time.sleep(random.uniform(2.0, 5.5))  # Human-like pause
                r = requests.get(url, headers=headers, timeout=20)

                if r.status_code == 200:
                    try:
                        data = r.json()
                        extracted = _extract_reddit_videos(data, f"Reddit /r/{sub}")
                        if extracted:
                            results.extend(extracted)
                            success = True
                            print(f" ✅ Pulled {len(extracted)} items from {instance}")
                            break
                    except json.JSONDecodeError:
                        print(f" ✗ Invalid JSON from {instance} (likely HTML error page)")
                        continue
                elif r.status_code in (403, 429):
                    print(f" ✗ Blocked ({r.status_code}) on {instance} — rotating")
                    time.sleep(random.uniform(8, 20))
                    continue
                else:
                    print(f" ✗ HTTP {r.status_code} on {instance}")
            except Exception as e:
                print(f" ✗ Error on {instance}: {e}")
                continue

        if not success:
            print(f" 📡 /r/{sub} exhausted all Redlib instances this cycle")

    return results

# (fetch_lemmy_sources, fetch_4chan_sources, fetch_all_sources, archival functions remain almost identical to previous version)
# ... [keeping the rest of the file exactly as in the previous upgrade for brevity - only Reddit part heavily improved]

def fetch_lemmy_sources() -> List[Dict]:
    results = []
    for community in LEMMY_COMMUNITIES:
        success = False
        for instance in LEMMY_INSTANCES:
            print(f" 📡 Lemmy c/{community} via {instance}")
            headers = get_random_headers()
            try:
                url = f"{instance}/api/v3/post/list?community_name={community}&sort=New&limit=20"
                time.sleep(random.uniform(1.5, 4))
                r = requests.get(url, headers=headers, timeout=18)
                if r.status_code == 200:
                    data = r.json()
                    # ... (same parsing as before)
                    for item in data.get("posts", []):
                        post_data = item.get("post", {})
                        title = post_data.get("name", "")
                        body = post_data.get("body", "")
                        media_url = post_data.get("url", "")
                        if not media_url or not (media_url.lower().endswith((".mp4", ".webm", ".mov", ".gifv")) or "v.redd.it" in media_url):
                            continue
                        score = item.get("counts", {}).get("score", 0)
                        if not _passes_filter(title, body, score):
                            continue
                        creator = item.get("creator", {})
                        audio_url = ""
                        platform = "lemmy_direct"
                        if "v.redd.it" in media_url:
                            media_url = media_url.split("?")[0]
                            if not media_url.endswith(".mp4"):
                                media_url = f"{media_url}/DASH_720.mp4"
                            audio_url = _reddit_audio_url(media_url)
                            platform = "reddit_native"
                        results.append({
                            "source": f"Lemmy c/{community}",
                            "author": creator.get("name", "Anonymous"),
                            "title": title,
                            "description": body,
                            "media_url": media_url,
                            "thumbnail_url": post_data.get("thumbnail_url") or "",
                            "media_type": "video",
                            "audio_url": audio_url,
                            "source_url": post_data.get("ap_id") or f"{instance}/post/{post_data.get('id')}",
                            "score": max(0, score),
                            "platform": platform
                        })
                    success = True
                    break
            except Exception as e:
                print(f" Lemmy error: {e}")
            time.sleep(random.uniform(2, 5))
    return results

def fetch_4chan_sources() -> List[Dict]:
    # (unchanged from previous - 4chan is stable)
    print(f" 🍀 4chan /{FOURCHAN_BOARD}/ Deep-Thread Scan")
    results = []
    try:
        catalog_url = f"https://a.4cdn.org/{FOURCHAN_BOARD}/catalog.json"
        r = requests.get(catalog_url, headers=get_random_headers(), timeout=12)
        if r.status_code != 200:
            return []
        catalog = r.json()
        target_threads = []
        for page in catalog[:6]:
            for thread in page.get("threads", []):
                comment = re.sub(r"<[^>]+>", " ", thread.get("com", ""))
                title = thread.get("sub", "")
                combined = (title + " " + comment).lower()
                if any(kw in combined for kw in POSITIVE_KEYWORDS) and not any(neg in combined for neg in NEGATIVE_KEYWORDS):
                    target_threads.append(thread.get("no"))
        target_threads = list(set(target_threads))[:5]
        processed = 0
        for thread_no in target_threads:
            try:
                thread_url = f"https://a.4cdn.org/{FOURCHAN_BOARD}/thread/{thread_no}.json"
                tr = requests.get(thread_url, headers=get_random_headers(), timeout=10)
                if tr.status_code != 200:
                    continue
                posts = tr.json().get("posts", [])
                for post in posts:
                    ext = post.get("ext", "")
                    if ext in (".webm", ".mp4"):
                        comment = re.sub(r"<[^>]+>", " ", post.get("com", ""))
                        post_title = post.get("sub") or comment[:80] or f"4chan reply {thread_no}"
                        tid = post["tim"]
                        results.append({
                            "source": f"4chan /{FOURCHAN_BOARD}/",
                            "author": post.get("name", "Anonymous"),
                            "title": post_title,
                            "description": comment,
                            "media_url": f"https://i.4cdn.org/{FOURCHAN_BOARD}/{tid}{ext}",
                            "thumbnail_url": f"https://i.4cdn.org/{FOURCHAN_BOARD}/{tid}s.jpg",
                            "media_type": "video",
                            "audio_url": "",
                            "source_url": f"https://boards.4channel.org/{FOURCHAN_BOARD}/thread/{thread_no}#p{post.get('no')}",
                            "score": 0,
                            "platform": "4chan"
                        })
                        processed += 1
            except:
                continue
            time.sleep(random.uniform(1.2, 3))
        print(f" 4chan scan found {processed} videos")
    except Exception as e:
        print(f" 4chan error: {e}")
    return results

def fetch_all_sources() -> List[Dict]:
    results = []
    try:
        results.extend(fetch_reddit_sources())
    except Exception as e:
        print(f"⚠️ Reddit scrape error: {e}")
    try:
        results.extend(fetch_lemmy_sources())
    except Exception as e:
        print(f"⚠️ Lemmy scrape error: {e}")
    try:
        results.extend(fetch_4chan_sources())
    except Exception as e:
        print(f"⚠️ 4chan scrape error: {e}")
    random.shuffle(results)
    return results

# ARCHIVAL FUNCTIONS (unchanged from previous)
def _zip_media_folder():
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = f"{ZIP_PREFIX}_{ts}.zip"
    print(f"🗜 Archiving → {out}")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in os.listdir(MEDIA_FOLDER):
            zf.write(os.path.join(MEDIA_FOLDER, f), arcname=f)
    shutil.rmtree(MEDIA_FOLDER)
    os.makedirs(MEDIA_FOLDER)

def check_and_zip_if_full():
    total = sum(os.path.getsize(os.path.join(MEDIA_FOLDER, f)) for f in os.listdir(MEDIA_FOLDER) if os.path.isfile(os.path.join(MEDIA_FOLDER, f)))
    if total >= REPO_WARN_BYTES:
        _zip_media_folder()

def build_ledger():
    print("🛸 AXIOM UAP — Core Video Archivist\n")
    ledger = load_ledger()
    existing = {b["source_url"] for b in ledger}
    new_data = fetch_all_sources()
    added = 0
    for s in new_data:
        if s["source_url"] in existing:
            continue
        file_id = hashlib.md5(s["media_url"].encode()).hexdigest()
        final_path = os.path.join(MEDIA_FOLDER, f"{file_id}.mp4")
        local_url = f"./media/{file_id}.mp4"
        if not os.path.exists(final_path):
            print(f"\n📦 {s['title'][:60]}")
            print(f" {s['source']} | {s['platform']}")
            if s["platform"] == "reddit_native":
                archived = merge_reddit_video(s["media_url"], s["audio_url"], final_path)
            else:
                archived = _download(s["media_url"], final_path, referer=s.get("source_url"))
                if archived and not _valid(final_path):
                    try: os.remove(final_path)
                    except: pass
                    archived = False
            if not archived:
                local_url = s["media_url"]
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = f"{timestamp}|{s['source']}|{s['title']}|{s['media_url']}|{s['score']}"
        ledger.insert(0, {
            "timestamp": timestamp,
            "source": s["source"],
            "author": s["author"],
            "title": s["title"],
            "description": s["description"][:800],
            "media_url": local_url,
            "thumbnail_url": s["thumbnail_url"],
            "media_type": "video",
            "source_url": s["source_url"],
            "hash": hashlib.sha256(payload.encode()).hexdigest(),
            "score": s["score"],
            "platform": s.get("platform", "unknown")
        })
        existing.add(s["source_url"])
        added += 1
        time.sleep(random.uniform(1.8, 5.5))  # Slow down downloads
    save_ledger(ledger)
    check_and_zip_if_full()
    print(f"\n✅ Done — {added} new video sightings archived.")

if __name__ == "__main__":
    build_ledger()
