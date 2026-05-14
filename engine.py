import json
import hashlib
import requests
import feedparser
from bs4 import BeautifulSoup
import nltk
from datetime import datetime, timezone
import os

# Download NLTK tokenizer models
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

LEDGER_FILE = "ledger.json"

HEADERS = {
    "User-Agent": "AxiomEngineBot/1.0 (https://github.com/; axiom-engine@example.com) python-requests/2.x"
}

def get_previous_hash(ledger):
    if not ledger:
        return "0000000000000000000000000000000000000000000000000000000000000000"
    return ledger[0]['hash']

def create_block(fact_text, source, topic, prev_hash, image_url=""):
    timestamp = datetime.now(timezone.utc).isoformat()
    payload = f"{timestamp}|{source}|{topic}|{fact_text}|{image_url}|{prev_hash}"
    block_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    
    return {
        "timestamp": timestamp,
        "source": source,
        "topic": topic,
        "fact": fact_text,
        "image_url": image_url,
        "prev_hash": prev_hash,
        "hash": block_hash
    }

def fetch_wikipedia_facts(title, topic):
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts|pageimages&explaintext=1&titles={title}&pithumbsize=800&format=json"
    facts = []
    image_url = ""
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get('query', {}).get('pages', {})
        if not pages:
            return facts, "Wikipedia", image_url
            
        page_data = list(pages.values())[0]
        text = page_data.get('extract', '')
        
        image_url = page_data.get('thumbnail', {}).get('source', '')
        
        if not text:
            return facts, "Wikipedia", image_url
        
        sentences = nltk.tokenize.sent_tokenize(text)
        keywords = ['million', 'billion', 'certified', 'Grammy', 'Billboard', 'released', 'sold', 'record']
        
        for sentence in sentences:
            if len(sentence) < 40 or len(sentence) > 200:
                continue
            if any(kw in sentence for kw in keywords):
                clean_fact = sentence.replace('\n', ' ').strip()
                facts.append(clean_fact)
                if len(facts) >= 20:
                    break
                    
    except Exception as e:
        print(f"⚠️ Error fetching Wikipedia ({title}): {e}")
        
    return facts, "Wikipedia", image_url

def generate_ledger():
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, 'r') as f:
                ledger = json.load(f)
        except json.JSONDecodeError:
            ledger = []
    else:
        ledger = []

    new_facts = []
    
    print("Scraping Wikipedia...")
    wiki_targets = [("Eminem", "Eminem"), ("Hip_hop_music", "Hip Hop History")]
    for title, topic in wiki_targets:
        facts, source, img_url = fetch_wikipedia_facts(title, topic)
        for fact in facts:
            new_facts.append({"fact": fact, "source": source, "topic": topic, "image_url": img_url})

    print("Scraping RSS Feeds...")
    try:
        rss_url = "https://hiphopdx.com/rss/news"
        feed = feedparser.parse(rss_url, agent=HEADERS["User-Agent"])
        for entry in feed.entries[:15]:
            title = entry.title
            if 'eminem' in title.lower() or 'rap' in title.lower() or 'hip hop' in title.lower():
                img_url = ""
                if 'media_content' in entry and len(entry.media_content) > 0:
                    img_url = entry.media_content[0]['url']
                elif 'links' in entry:
                    for link in entry.links:
                        if 'image' in link.get('type', ''):
                            img_url = link.href
                            break
                
                new_facts.append({"fact": title, "source": "HipHopDX RSS", "topic": "Trending", "image_url": img_url})
    except Exception as e:
        print(f"⚠️ Error fetching RSS: {e}")

    existing_facts = set(block['fact'] for block in ledger)
    
    added = 0
    for item in reversed(new_facts):
        if item['fact'] not in existing_facts:
            prev_hash = get_previous_hash(ledger)
            block = create_block(item['fact'], item['source'], item['topic'], prev_hash, item.get('image_url', ''))
            ledger.insert(0, block)
            existing_facts.add(item['fact'])
            added += 1

    ledger = ledger[:500]

    with open(LEDGER_FILE, 'w') as f:
        json.dump(ledger, f, indent=2)

    print(f"✅ Axiom Engine Run Complete. Added {added} new verified blocks.")

if __name__ == "__main__":
    generate_ledger()
