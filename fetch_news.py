import json
import os
import urllib.request
import feedparser

# Final Master Feed List for AI Tech & Automation Hub
RSS_FEEDS = [
    # GitHub Trending Pulse (RSSHub)
    "https://rsshub.app/github/trending/daily",
    "https://rsshub.app/github/trending/weekly",
    
    # Core AI Labs
    "https://openai.com/news/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://blog.google/technology/ai/rss/",
    
    # AI Tools & Open Source
    "https://huggingface.co/blog/feed.xml",
    "https://github.com/openclaw/openclaw/releases.atom",
    
    # AI Coding & Agent Tools
    "https://github.com/openai/codex/releases.atom",
    "https://github.com/anthropics/claude-code/releases.atom",
    "https://github.com/google-gemini/gemini-cli/releases.atom",
    
    # Core Language
    "https://blog.python.org/rss.xml"
]

MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL")

def get_latest_news():
    latest_item = None
    
    for url in RSS_FEEDS:
        print(f"Checking feed: {url}")
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                entry = feed.entries[0]
                title = entry.get("title", "No Title")
                link = entry.get("link", "")
                
                # Handle atom and RSSHub feed link variations safely
                if not link and "links" in entry and entry["links"]:
                    link = entry["links"][0].get("href", "")
                    
                summary = entry.get("summary", entry.get("content", [{"value": ""}])[0].get("value", ""))[:300]
                
                latest_item = {
                    "title": title,
                    "link": link,
                    "description": summary,
                    "source": feed.feed.get("title", url)
                }
                print(f"-> Grabbed item from: {latest_item['source']} | {title}")
                break 
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            continue
            
    return latest_item

def send_to_make(data):
    if not MAKE_WEBHOOK_URL:
        raise ValueError("MAKE_WEBHOOK_URL secret is missing!")
        
    req = urllib.request.Request(
        MAKE_WEBHOOK_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    with urllib.request.urlopen(req) as response:
        print(f"Successfully sent to Make.com! Status: {response.status}")

if __name__ == "__main__":
    news = get_latest_news()
    if news:
        print(f"Sending payload: {news['title']}")
        send_to_make(news)
    else:
        print("No articles found across any feeds.")
