import feedparser

URL = "https://www.indeed.co.in/rss?q=python+developer&l=India"


def main():
    print("Parsing RSS:", URL)
    feed = feedparser.parse(URL)

    print("status:", feed.get("status", "N/A"))
    print("bozo:", getattr(feed, "bozo", False))
    if getattr(feed, "bozo", False):
        print("bozo_exception:", getattr(feed, "bozo_exception", ""))

    print("feed title:", feed.feed.get("title", "(no title)"))
    entries = feed.entries
    print("entries count:", len(entries))

    for i, entry in enumerate(entries[:10], start=1):
        print("--- ENTRY", i, "---")
        print("title:", entry.get("title", ""))
        print("link:", entry.get("link", ""))
        print("author:", entry.get("author", ""))
        print("published:", entry.get("published", ""))
        summary = entry.get("summary", "")
        print("summary (first 200 chars):", summary[:200].replace("\n", " "))


if __name__ == "__main__":
    main()
