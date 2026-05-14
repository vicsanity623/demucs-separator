import json
import hashlib
import requests
import feedparser
import nltk
from datetime import datetime, timezone
import os
import time

# Download NLTK tokenizer models
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

LEDGER_FILE = "ledger.json"
MAX_RUNTIME_SEC = (2 * 60 * 60) + (45 * 60) # Run for 2 hours and 45 minutes

HEADERS = {
    "User-Agent": "AxiomEngineBot/2.0 (https://github.com/; axiom-engine@example.com) python-requests/2.x"
}

# 20 Premium Targets (10 Wiki Hubs, 10 RSS Feeds)
WIKI_TARGETS = [
    ("Eminem", "Eminem"), ("Hip_hop_music", "Hip Hop History"),
    ("Dr._Dre", "Hip Hop History"), ("50_Cent", "Hip Hop History"),
    ("The_Marshall_Mathers_LP", "Eminem"), ("The_Eminem_Show", "Eminem"),
    ("Recovery_(Eminem_album)", "Eminem"), ("Rap_God", "Eminem"),
    ("Lose_Yourself", "Eminem"), ("Tupac_Shakur", "Hip Hop History")
]

RSS_TARGETS = [
    ("HipHopDX", "https://hiphopdx.com/rss/news"),
    ("Billboard Hip-Hop", "https://www.billboard.com/c/music/rb-hip-hop/feed/"),
    ("Rolling Stone", "https://www.rollingstone.com/music/feed/"),
    ("HotNewHipHop", "https://www.hotnewhiphop.com/feed/"),
    ("Uproxx Music", "https://uproxx.com/music/feed/"),
    ("Stereogum", "https://www.stereogum.com/category/music/feed/"),
    ("Consequence", "https://consequence.net/category/music/feed/"),
    ("NME Music", "https://www.nme.com/news/music/feed"),
    ("Pitchfork", "https://pitchfork.com/rss/news/"),
    ("AllHipHop", "https://allhiphop.com/feed/")
]

def get_previous_hash(ledger):
    if not ledger:
        return "0000000000000000000000000000000000000000000000000000000000000000"
    return ledger[0]['hash']

def create_block(fact_text, source, topic, prev_hash, image_url="", source_url=""):
    timestamp = datetime.now(timezone.utc).isoformat()
    payload = f"{timestamp}|{source}|{topic}|{fact_text}|{image_url}|{source_url}|{prev_hash}"
    block_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    
    return {
        "timestamp": timestamp,
        "source": source,
        "topic": topic,
        "fact": fact_text,
        "image_url": image_url,
        "source_url": source_url,
        "prev_hash": prev_hash,
        "hash": block_hash
    }

def fetch_wikipedia_facts(title, topic):
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts|pageimages&explaintext=1&titles={title}&pithumbsize=800&format=json"
    source_url = f"https://en.wikipedia.org/wiki/{title}"
    facts = []
    image_url = ""
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get('query', {}).get('pages', {})
        if not pages:
            return facts, "Wikipedia", image_url, source_url
            
        page_data = list(pages.values())[0]
        text = page_data.get('extract', '')
        image_url = page_data.get('thumbnail', {}).get('source', '')
        
        if not text:
            return facts, "Wikipedia", image_url, source_url
        
        sentences = nltk.tokenize.sent_tokenize(text)
        keywords = ['million', 'billion', 'certified', 'Grammy', 'Billboard', 'released', 'sold', 'record', 'platinum', 'debut']
        
        for sentence in sentences:
            if 40 <= len(sentence) <= 200 and any(kw in sentence for kw in keywords):
                clean_fact = sentence.replace('\n', ' ').strip()
                facts.append(clean_fact)
                if len(facts) >= 20:
                    break
                    
    except Exception as e:
        print(f"⚠️ Error fetching Wikipedia ({title}): {e}")
        
    return facts, "Wikipedia", image_url, source_url

def load_ledger():
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return []

def save_ledger(ledger):
    # Keep ledger optimized to 1000 facts to prevent massive file bloat
    ledger = ledger[:1000]
    with open(LEDGER_FILE, 'w') as f:
        json.dump(ledger, f, indent=2)

def run_engine_cycle(ledger):
    new_facts = []
    
    print("Scraping Wikipedia Hubs...")
    for title, topic in WIKI_TARGETS:
        facts, source, img_url, src_url = fetch_wikipedia_facts(title, topic)
        for fact in facts:
            new_facts.append({"fact": fact, "source": source, "topic": topic, "image_url": img_url, "source_url": src_url})
        time.sleep(1) # Respect Wiki API limit

    print("Scraping RSS Feeds...")
    for source_name, rss_url in RSS_TARGETS:
        try:
            feed = feedparser.parse(rss_url, agent=HEADERS["User-Agent"])
            for entry in feed.entries[:10]:
                title = entry.title
                if 'eminem' in title.lower() or 'rap' in title.lower() or 'hip hop' in title.lower() or 'dre' in title.lower():
                    img_url = ""
                    src_url = entry.link if 'link' in entry else ""
                    
                    if 'media_content' in entry and len(entry.media_content) > 0:
                        img_url = entry.media_content[0]['url']
                    elif 'links' in entry:
                        for link in entry.links:
                            if 'image' in link.get('type', ''):
                                img_url = link.href
                                break
                    
                    new_facts.append({"fact": title, "source": source_name, "topic": "Trending News", "image_url": img_url, "source_url": src_url})
        except Exception as e:
            print(f"⚠️ Error fetching RSS ({source_name}): {e}")
        time.sleep(2) # Respect RSS limits

    existing_facts = set(block['fact'] for block in ledger)
    added = 0
    
    # Insert newest facts at the top
    for item in reversed(new_facts):
        if item['fact'] not in existing_facts:
            prev_hash = get_previous_hash(ledger)
            block = create_block(item['fact'], item['source'], item['topic'], prev_hash, item.get('image_url', ''), item.get('source_url', ''))
            ledger.insert(0, block)
            existing_facts.add(item['fact'])
            added += 1

    return added, ledger

if __name__ == "__main__":
    print(f"🚀 Starting Axiom Engine. Programmed to run for {MAX_RUNTIME_SEC / 60:.1f} minutes...")
    start_time = time.time()
    ledger = load_ledger()
    
    cycle = 1
    while True:
        elapsed = time.time() - start_time
        if elapsed > MAX_RUNTIME_SEC:
            print("🛑 Max runtime reached. Saving final ledger and shutting down.")
            save_ledger(ledger)
            break
            
        print(f"\n--- Starting Cycle {cycle} ---")
        added, ledger = run_engine_cycle(ledger)
        save_ledger(ledger) # Save to disk after every cycle as a failsafe
        
        print(f"✅ Cycle {cycle} Complete. Added {added} new verified blocks.")
        
        # Calculate time left. Sleep for 20 minutes between cycles, unless we are out of time.
        sleep_duration = 20 * 60
        if (time.time() - start_time) + sleep_duration > MAX_RUNTIME_SEC:
            sleep_duration = MAX_RUNTIME_SEC - (time.time() - start_time)
            
        if sleep_duration > 0:
            print(f"💤 Sleeping for {sleep_duration / 60:.1f} minutes before next cycle...")
            time.sleep(sleep_duration)
            
        cycle += 1