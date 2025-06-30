import feedparser

rss_url = "https://apnews.com/apf-worldnews?format=RSS"
feed = feedparser.parse(rss_url)

for entry in feed.entries:
    print(entry.title)
    print(entry.link)
