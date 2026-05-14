import requests
import feedparser  # type: ignore
import nltk  # type: ignore
from typing import List, Tuple, Dict, Any

def fetch_wikipedia_facts(title: str, topic: str) -> Tuple[List[str], str, str, str]:
    url: str = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts|pageimages&explaintext=1&titles={title}&pithumbsize=800&format=json"
    source_url: str = f"https://en.wikipedia.org/wiki/{title}"
    facts: List[str] = []
    image_url: str = ""
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        if not pages: return facts, "Wikipedia", image_url, source_url
        
        page_data = list(pages.values())[0]
        text = page_data.get("extract", "")
        image_url = page_data.get("thumbnail", {}).get("source", "")
        
        sentences = nltk.tokenize.sent_tokenize(text)
        for sentence in sentences:
            if 40 <= len(sentence) <= 220:
                facts.append(sentence.replace("\n", " ").strip())
                if len(facts) >= 15: break
    except Exception:
        pass
    return facts, "Wikipedia", image_url, source_url

def fetch_rss_feed(rss_url: str, agent: str) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    feed = feedparser.parse(rss_url, agent=agent)
    for entry in feed.entries[:15]:
        results.append({
            "fact": entry.get("title", ""),
            "source_url": entry.get("link", "")
        })
    return results