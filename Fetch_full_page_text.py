
import pandas as pd
import requests
import time

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"

def fetch_full_wikipedia_text(title: str) -> str:
    """
    Query the MediaWiki API to get the full plain-text extract of the page.
    Returns an empty string if the page doesn’t exist.
    """
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "redirects": True,
        "titles": title,
        "format": "json",
        "exlimit": 1,
    }
    resp = requests.get(WIKI_API_URL, params=params, timeout=10)
    resp.raise_for_status()
    pages = resp.json()["query"]["pages"]
    page = next(iter(pages.values()))
    return page.get("extract", "")

def main():
    # 1. Load your original CSV
    df = pd.read_csv("filtered_nba_players.csv", dtype=str)

    # 2. Fetch full text for each DISPLAY_FIRST_LAST
    texts = []
    for name in df["DISPLAY_FIRST_LAST"]:
        text = fetch_full_wikipedia_text(name)
        texts.append(text)
        time.sleep(0.5)   # be polite to the API

    # 3. Attach to your DataFrame and save
    df["wikipedia_full_text"] = texts
    df.to_csv("nba_players_wiki_full_text.csv", index=False, encoding="utf-8")
    print("✅ Saved nba_players_wiki_full_text.csv")

if __name__ == "__main__":
    main()


