import json
import hashlib
import requests
import feedparser
from bs4 import BeautifulSoup
import nltk
from datetime import datetime, timezone
import os

# Download NLTK tokenizer models (handled in workflow, but good fallback)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

LEDGER_FILE = "ledger.json"

def get_previous_hash(ledger):
    if not ledger:
        return "0000000000000000000000000000000000000000000000000000000000000000" # Genesis block
    return ledger[0]['hash'] # Top of the list is the most recent

def create_block(fact_text, source, topic, prev_hash):
    timestamp = datetime.now(timezone.utc).isoformat()
    # Create the data payload to be hashed
    payload = f"{timestamp}|{source}|{topic}|{fact_text}|{prev_hash}"
    block_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    
    return {
        "timestamp": timestamp,
        "source": source,
        "topic": topic,
        "fact": fact_text,
        "prev_hash": prev_hash,
        "hash": block_hash
    }

def fetch_wikipedia_facts(title, topic):
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&titles={title}&format=json"
    response = requests.get(url).json()
    pages = response['query']['pages']
    text = list(pages.values())[0].get('extract', '')
    
    sentences = nltk.tokenize.sent_tokenize(text)
    facts = []
    # NLP Filter: Only keep sentences containing verifiable metrics/keywords
    keywords = ['million', 'billion', 'certified', 'Grammy', 'Billboard', 'released', 'sold', 'record']
    
    for sentence in sentences:
        if len(sentence) < 40 or len(sentence) > 200:
            continue # Skip too short or too long sentences
        if any(kw in sentence for kw in keywords):
            facts.append(sentence.strip())
            if len(facts) >= 20: # Limit per source
                break
    return facts, "Wikipedia"

def generate_ledger():
    # Load existing ledger
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, 'r') as f:
            ledger = json.load(f)
    else:
        ledger = []

    new_facts = []
    
    # 1. Scrape Wikipedia (Eminem & Hip Hop)
    wiki_targets = [("Eminem", "Eminem"), ("Hip_hop_music", "Hip Hop History")]
    for title, topic in wiki_targets:
        facts, source = fetch_wikipedia_facts(title, topic)
        for fact in facts:
            new_facts.append({"fact": fact, "source": source, "topic": topic})

    # 2. Scrape RSS Feeds (e.g., HipHopDX or general music news)
    # Using a generic music/hiphop feed example
    rss_url = "https://hiphopdx.com/rss/news"
    feed = feedparser.parse(rss_url)
    for entry in feed.entries[:10]:
        title = entry.title
        if 'eminem' in title.lower() or 'rap' in title.lower():
            new_facts.append({"fact": title, "source": "HipHopDX RSS", "topic": "Trending"})

    # Filter out duplicates against existing ledger
    existing_facts = set(block['fact'] for block in ledger)
    
    # Seal new facts into the ledger
    added = 0
    for item in new_facts:
        if item['fact'] not in existing_facts:
            prev_hash = get_previous_hash(ledger)
            block = create_block(item['fact'], item['source'], item['topic'], prev_hash)
            ledger.insert(0, block) # Insert at the beginning (newest first)
            existing_facts.add(item['fact'])
            added += 1

    # Keep only top 500 facts to prevent file bloat on GitHub pages
    ledger = ledger[:500]

    with open(LEDGER_FILE, 'w') as f:
        json.dump(ledger, f, indent=2)

    print(f"Axiom Engine Run Complete. Added {added} new verified blocks.")

if __name__ == "__main__":
    generate_ledger()
