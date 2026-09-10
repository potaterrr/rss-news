import json
import os
import urllib.request
import feedparser

RSS_FEEDS = [
    "https://rsshub.app/github/trending/daily",
    "https://rsshub.app/github/trending/weekly",
    "https://openai.com/news/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://blog.google/technology/ai/rss/",
    "https://huggingface.co/blog/feed.xml",
    "https://github.com/openclaw/openclaw/releases.atom",
    "https://github.com/openai/codex/releases.atom",
    "https://github.com/anthropics/claude-code/releases.atom",
    "https://github.com/google-gemini/gemini-cli/releases.atom",
    "https://blog.python.org/rss.xml"
]

MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL")

def get_all_feeds_news():
    if not MAKE_WEBHOOK_URL:
        print("ERROR: MAKE_WEBHOOK_URL environment variable is missing!")
        return []

    all_news_items = []

    for url in RSS_FEEDS:
        print(f"Checking feed: {url}")
        try:
            feed = feedparser.parse(url)
            if hasattr(feed, 'entries') and len(feed.entries) > 0:
                entry = feed.entries[0]
                title = entry.get("title", "No Title")
                link = entry.get("link", "")
                
                if not link and "links" in entry and entry["links"]:
                    link = entry["links"][0].get("href", "")
                
                summary = entry.get("summary", entry.get("content", [{"value": ""}])[0].get("value", ""))[:300]
                
                item = {
                    "title": title,
                    "link": link,
                    "description": summary,
                    "source": feed.feed.get("title", url)
                }
                all_news_items.append(item)
                print(f"-> Grabbed item from: {item['source']} | {title}")
            else:
                print(f"-> Feed is empty or unrecognized: {url}")
        except Exception as e:
            print(f"WARNING: Error parsing {url}: {e}")
            continue
            
    return all_news_items

def send_to_make(data):
    req = urllib.request.Request(
        MAKE_WEBHOOK_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Successfully sent payload to Make.com! Status: {response.status}")
    except Exception as e:
        print(f"ERROR: Failed to send payload to Make.com: {e}")
        raise e

if __name__ == "__main__":
    news_items = get_all_feeds_news()
    if news_items:
        print(f"Sending {len(news_items)} items to Make.com...")
        send_to_make(news_items)
    else:
        print("Exiting gracefully: No news items found across any of the feeds.")
