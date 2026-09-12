import feedparser
import requests
import os
import json
import logging
import random

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("rss_fetcher.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# --- CONFIGURATION ---
WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

FEED_URLS = [
    "https://news.ycombinator.com/rss",
    "https://www.phoronix.com/rss.php",
    "https://www.theverge.com/rss/index.xml",
    "https://hnrss.org/ai",
    "https://9to5google.com/feed/"
]

KEYWORDS = [
    "linux", "ubuntu", "debian", "windows", 
    "ai model", "llm", "openai", "deepseek", "anthropic", 
    "smartphone", "pixel", "galaxy", "gpu"
]

SEEN_FILE = "seen_articles.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_seen(seen_set):
    try:
        seen_list = list(seen_set)[-1000:]
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(seen_list, f)
    except Exception as e:
        logging.error(f"Failed to save seen cache: {e}")

def match_keywords(text, keywords):
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)

def get_random_local_image():
    """Scans the local images/ directory and returns a raw GitHub URL. Raises an error if none found."""
    images_dir = "images"
    
    if not os.path.exists(images_dir):
        raise FileNotFoundError("Critical Error: Local 'images/' directory does not exist in the workspace!")

    valid_extensions = (".jpg", ".jpeg", ".png", ".webp")
    images = [f for f in os.listdir(images_dir) if f.lower().endswith(valid_extensions)]

    if not images:
        raise ValueError("Critical Error: The 'images/' folder contains no valid image files (.jpg, .png, .webp)!")

    chosen_image = random.choice(images)
    
    # Get repo and branch from GitHub Actions env vars, with fallback defaults
    repo = os.getenv("GITHUB_REPOSITORY", "potaterrr/rss-news")
    branch = os.getenv("GITHUB_REF_NAME", "main")
    
    direct_url = f"https://raw.githubusercontent.com/{repo}/{branch}/images/{chosen_image}"
    logging.info(f"Selected random local repo image: {chosen_image} ({direct_url})")
    return direct_url

def main():
    if not WEBHOOK_URL:
        logging.error("MAKE_WEBHOOK_URL environment variable is not set!")
        return

    logging.info("Starting RSS digest run...")
    seen_articles = load_seen()
    digest_items = []
    newly_seen_ids = set()

    # 1. Gather matching items
    for url in FEED_URLS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                entry_id = getattr(entry, "id", getattr(entry, "link", None))
                if not entry_id or entry_id in seen_articles:
                    continue
                    
                title = getattr(entry, "title", "No Title")
                summary = getattr(entry, "summary", getattr(entry, "description", ""))
                
                if match_keywords(f"{title} {summary}", KEYWORDS):
                    item_text = f"• **{title}**\n  Link: {entry.link}\n  Source: {feed.feed.get('title', url)}"
                    digest_items.append(item_text)
                    newly_seen_ids.add(entry_id)
        except Exception as e:
            logging.error(f"Error parsing feed {url}: {e}")

    # 2. Build digest, pick local random image, and send payload to Make.com
    if digest_items:
        logging.info(f"Found {len(digest_items)} new matching articles. Preparing payload...")
        
        combined_digest = "\n\n".join(digest_items)
        random_banner = get_random_local_image()  # Will throw an error if no images exist
        
        payload_data = {
            "digest_title": f"Tech & AI Digest ({len(digest_items)} items)",
            "total_items": len(digest_items),
            "content": combined_digest,
            "banner_image": random_banner
        }
        
        try:
            response = requests.post(WEBHOOK_URL, json=payload_data, timeout=15)
            if response.status_code in [200, 201, 204]:
                logging.info("Successfully delivered digest and image to Make.com.")
                seen_articles.update(newly_seen_ids)
                save_seen(seen_articles)
            else:
                logging.error(f"Webhook rejected payload. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error: {e}")
    else:
        logging.info("No new matching articles found.")

if __name__ == "__main__":
    main()
