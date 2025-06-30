import feedparser
from typing import List, Dict

RSS_FEEDS = {
    "reuters": "http://feeds.reuters.com/reuters/worldNews",
    "the_guardian": "https://www.theguardian.com/world/rss",
}

def fetch_news(max_per_source: int = 15) -> List[Dict]:
    """
    Fetches news articles from predefined RSS feeds.

    Args:
        max_per_source: The maximum number of articles to fetch from each source.

    Returns:
        A list of dictionaries, where each dictionary represents an article.
    """
    articles = []
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= max_per_source:
                    break
                
                summary = entry.get("summary", "")
                # Basic cleanup of summary
                if '<' in summary and '>' in summary:
                    from bs4 import BeautifulSoup
                    summary = BeautifulSoup(summary, "html.parser").get_text()

                articles.append({
                    "title": entry.title,
                    "summary": summary,
                    "link": entry.link,
                    "source": source,
                })
                count += 1
        except Exception as e:
            print(f"Could not fetch or parse feed from {source}: {e}")
    return articles

if __name__ == '__main__':
    # For testing purposes
    news_list = fetch_news(2)
    for article in news_list:
        print(f"Title: {article['title']}\nSource: {article['source']}\nSummary: {article['summary'][:100]}...\n")
