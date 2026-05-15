import requests
import nltk  # type: ignore[import-untyped]
from typing import List, Tuple

def fetch_wikipedia_facts(title: str, topic: str, headers: dict[str, str]) -> Tuple[List[str], str, str, str]:
    url: str = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts|pageimages&explaintext=1&titles={title}&pithumbsize=800&format=json"
    source_url: str = f"https://en.wikipedia.org/wiki/{title}"
    facts: List[str] = []
    image_url: str = ""

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        if not pages:
            return facts, "Wikipedia", image_url, source_url

        page_data = list(pages.values())[0]
        text = page_data.get("extract", "")
        image_url = page_data.get("thumbnail", {}).get("source", "")

        if not text:
            return facts, "Wikipedia", image_url, source_url

        sentences: List[str] = nltk.tokenize.sent_tokenize(text)
        keywords = [
            "million", "billion", "certified", "Grammy", "Billboard",
            "released", "sold", "record", "platinum", "debut",
            "born", "track", "rhyme", "song",
        ]

        for sentence in sentences:
            if 40 <= len(sentence) <= 220 and any(kw in sentence for kw in keywords):
                clean_fact = sentence.replace("\n", " ").strip()
                facts.append(clean_fact)
                if len(facts) >= 15:
                    break
    except Exception as e:
        print(f"â ï¸ Error fetching Wikipedia ({title}): {e}")

    return facts, "Wikipedia", image_url, source_url