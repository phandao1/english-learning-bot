"""
RSS Feed Crawler Module.
Fetches and parses articles from configured RSS feeds.
"""
import logging
import random
import re
from datetime import datetime, timedelta
from typing import Optional

import feedparser
import requests
from bs4 import BeautifulSoup

try:
    import trafilatura
    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False

from config import GARMENT_FEEDS, GENERAL_ENGLISH_FEEDS, ARTICLES_PER_CATEGORY

logger = logging.getLogger(__name__)

# Timeout for HTTP requests (seconds)
REQUEST_TIMEOUT = 15

# User agent to avoid being blocked
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Number of candidates to fetch full text for before final selection
_CANDIDATES_PER_CATEGORY = 8


def calculate_article_score(article: 'Article') -> float:
    """
    Evaluate and score an article based on:
    1. Content quality: Reject junk/promotional articles
    2. Vocabulary Difficulty: Prefer B1-B2 level (intermediate)
    3. Relevance: Reward garment/textile keywords if category is garment
    4. Date: Reward newer articles
    5. Full text quality: Reward articles with substantial readable content
    """
    score = 0.0
    # Use full_text for scoring when available, fall back to summary
    full = getattr(article, 'full_text', '') or ''
    text = f"{article.title} {article.summary} {full}".lower()
    words = re.findall(r"\b[a-z]{2,}\b", text)

    if not words:
        return -1000.0

    # 0. Content Quality Filter - reject junk articles
    junk_patterns = [
        r"lessons?\.com", r"free.*materials", r"eslholiday",
        r"famouspeople", r"click here", r"subscribe",
        r"buy now", r"sign up", r"download free",
        r"thousands of free", r"all my si",
        r"cookie", r"privacy policy", r"terms of service",
    ]
    for pattern in junk_patterns:
        if re.search(pattern, text):
            return -1000.0

    # Reject very short content (likely broken scrape or paywall)
    content_len = len(full) if full else len(article.summary)
    if content_len < 60:
        score -= 50

    # 1. Date Score (Max 10 points)
    if article.published:
        pub_date = article.published.replace(tzinfo=None)
        days_old = (datetime.now().replace(tzinfo=None) - pub_date).days
        date_score = max(0, 10 - max(0, days_old))
        score += date_score

    # 2. Relevance Score
    if article.category == "garment_industry":
        core_keywords = [
            "textile", "apparel", "garment", "fabric", "cotton", "yarn",
            "sewing", "clothing", "manufacturing", "supply chain",
            "sustainability", "woven", "knit", "denim", "factory",
            "thread", "stitching", "production", "quality control",
            "pattern", "cutting", "dyeing", "finishing", "export",
            "import", "order", "buyer", "supplier", "sample",
            "inspection", "compliance", "worker", "labor",
            "material", "polyester", "nylon", "silk", "wool",
        ]
        relevance = sum(1 for kw in core_keywords if kw in text)
        score += relevance * 3
    else:
        general_keywords = [
            "speak", "learn", "study", "everyday", "life", "world",
            "people", "news", "health", "work", "practice", "read",
            "listen", "conversation", "communicate", "understand",
            "environment", "community", "technology", "science",
        ]
        relevance = sum(1 for kw in general_keywords if kw in text)
        score += relevance * 2

    # 3. Vocabulary Difficulty (CRITICAL)
    long_words = [w for w in words if len(w) >= 9]
    long_word_ratio = len(long_words) / len(words)

    if long_word_ratio > 0.30:
        score -= 30  # Too academic
    elif long_word_ratio > 0.20:
        score -= 10
    elif long_word_ratio < 0.03:
        score -= 5   # Too simple
    else:
        score += 25  # B1-B2 sweet spot

    # 4. Content richness - reward articles with good full text
    if full:
        word_count = len(full.split())
        if 200 <= word_count <= 1500:
            score += 20  # Ideal reading length
        elif word_count > 1500:
            score += 10  # Long but still OK
        elif word_count < 100:
            score -= 15  # Scrape probably failed / paywall
    else:
        score -= 10  # No full text available

    return score


class Article:
    """Represents a parsed article from an RSS feed."""

    def __init__(
        self,
        title: str,
        link: str,
        summary: str,
        source_name: str,
        source_icon: str,
        category: str,
        published: Optional[datetime] = None,
        image_url: Optional[str] = None,
    ):
        self.title = title
        self.link = link
        self.summary = summary
        self.source_name = source_name
        self.source_icon = source_icon
        self.category = category
        self.published = published or datetime.now()
        self.image_url = image_url
        self.full_text: str = ""
        # These will be filled by AI module (optional)
        self.ai_summary: Optional[str] = None
        self.keywords: list[str] = []
        self.vocabulary: list[dict] = []

    def __repr__(self):
        return f"Article(title='{self.title[:50]}...', source='{self.source_name}')"

def fetch_full_text(url: str) -> str:
    """Scrape the main article text using trafilatura (accurate) or BeautifulSoup (fallback)."""
    try:
        downloaded = requests.get(url, headers=HEADERS, timeout=12)
        downloaded.raise_for_status()
        html = downloaded.text
    except Exception as e:
        logger.warning(f"Could not download {url}: {e}")
        return ""

    # Method 1: trafilatura - much better at extracting article body
    if HAS_TRAFILATURA:
        try:
            text = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=False,
                no_fallback=False,
            )
            if text and len(text) > 200:
                return text
        except Exception:
            pass

    # Method 2: BeautifulSoup fallback
    try:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        paragraphs = [p for p in paragraphs if len(p) > 50]
        full_text = " ".join(paragraphs)
        if len(full_text) > 200:
            return full_text
    except Exception as e:
        logger.warning(f"Could not scrape full text for {url}: {e}")
    return ""


def clean_html(raw_html: str) -> str:
    """Remove HTML tags and clean up text."""
    if not raw_html:
        return ""
    # Avoid BeautifulSoup warning when input doesn't look like HTML
    if "<" not in raw_html:
        return re.sub(r"\s+", " ", raw_html).strip()
    soup = BeautifulSoup(raw_html, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def truncate_text(text: str, max_length: int = 300) -> str:
    """Truncate text to a maximum length, ending at a sentence boundary."""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    # Try to end at a sentence boundary
    last_period = truncated.rfind(".")
    if last_period > max_length * 0.5:
        return truncated[: last_period + 1]
    return truncated + "..."


def extract_image_url(entry) -> Optional[str]:
    """Try to extract an image URL from an RSS entry."""
    # Check media_content
    if hasattr(entry, "media_content") and entry.media_content:
        for media in entry.media_content:
            if media.get("medium") == "image" or "image" in media.get("type", ""):
                return media.get("url")

    # Check media_thumbnail
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url")

    # Check enclosures
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if "image" in enc.get("type", ""):
                return enc.get("href")

    # Try to extract from summary/content HTML
    content = entry.get("summary", "") or entry.get("content", [{}])[0].get("value", "")
    if content:
        soup = BeautifulSoup(content, "lxml")
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]

    return None


def parse_published_date(entry) -> Optional[datetime]:
    """Parse the published date from an RSS entry."""
    date_fields = ["published_parsed", "updated_parsed", "created_parsed"]
    for field in date_fields:
        parsed = getattr(entry, field, None)
        if parsed:
            try:
                return datetime(*parsed[:6])
            except Exception:
                continue
    return None


def fetch_feed(feed_config: dict) -> list[Article]:
    """
    Fetch and parse articles from a single RSS feed.

    Args:
        feed_config: Dictionary with feed name, url, category, icon

    Returns:
        List of Article objects
    """
    url = feed_config["url"]
    name = feed_config["name"]
    category = feed_config["category"]
    icon = feed_config["icon"]

    logger.info(f"📡 Fetching feed: {name} ({url})")

    try:
        # Use requests first to handle timeouts better
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
    except requests.RequestException as e:
        logger.warning(f"⚠️  Failed to fetch {name}: {e}")
        try:
            # Fallback: try feedparser directly
            feed = feedparser.parse(url)
        except Exception as e2:
            logger.error(f"❌ Could not parse {name}: {e2}")
            return []

    if not feed.entries:
        logger.warning(f"⚠️  No entries found in {name}")
        return []

    articles = []
    for entry in feed.entries:
        try:
            title = clean_html(entry.get("title", "No Title"))
            raw_summary = entry.get("summary", "")
            # Also check for content field
            if not raw_summary and entry.get("content"):
                raw_summary = entry["content"][0].get("value", "")
            summary = truncate_text(clean_html(raw_summary))
            link = entry.get("link", "")
            published = parse_published_date(entry)
            image_url = extract_image_url(entry)

            if title and link:
                # Filter out junk/promotional entries
                combined = f"{title} {summary}".lower()
                junk_indicators = [
                    "lessons.com", "eslholiday", "famouspeople",
                    "freeeslmaterials", "click here to",
                    "thousands of free lessons",
                ]
                if any(j in combined for j in junk_indicators):
                    continue

                article = Article(
                    title=title,
                    link=link,
                    summary=summary if summary else "Click to read the full article.",
                    source_name=name,
                    source_icon=icon,
                    category=category,
                    published=published,
                    image_url=image_url,
                )
                articles.append(article)
        except Exception as e:
            logger.warning(f"⚠️  Error parsing entry from {name}: {e}")
            continue

    logger.info(f"✅ Got {len(articles)} articles from {name}")
    return articles


def _select_best_articles(articles: list['Article'], count: int) -> list['Article']:
    """
    Smart article selection:
    1. Quick pre-filter on title+summary (reject obvious junk)
    2. Pick top candidates and fetch their full text
    3. Re-score with full text for accurate ranking
    4. Return the best ones
    """
    if not articles:
        return []

    # Step 1: Quick score on title+summary only → pick top candidates
    articles.sort(key=calculate_article_score, reverse=True)
    candidates = [a for a in articles if calculate_article_score(a) > -500]
    candidates = candidates[:_CANDIDATES_PER_CATEGORY]

    if not candidates:
        return []

    # Step 2: Fetch full text for candidates
    logger.info(f"📥 Fetching full text for {len(candidates)} candidate articles...")
    for a in candidates:
        a.full_text = fetch_full_text(a.link)

    # Step 3: Re-score with full text and pick the best
    candidates.sort(key=calculate_article_score, reverse=True)
    selected = candidates[:count]

    for a in selected:
        logger.info(f"  ✅ Selected: {a.title[:60]}... (score: {calculate_article_score(a):.0f})")

    return selected


def fetch_articles(
    category: str = "all",
    max_per_category: int = ARTICLES_PER_CATEGORY,
) -> dict[str, list[Article]]:
    """
    Fetch articles from all configured feeds.

    Args:
        category: 'garment', 'general', or 'all'
        max_per_category: Maximum number of articles per category

    Returns:
        Dictionary with 'garment' and/or 'general' keys,
        each containing a list of Article objects
    """
    result = {}

    if category in ("garment", "all"):
        garment_articles = []
        for feed_config in GARMENT_FEEDS:
            articles = fetch_feed(feed_config)
            garment_articles.extend(articles)

        result["garment"] = _select_best_articles(garment_articles, max_per_category)

    if category in ("general", "all"):
        general_articles = []
        for feed_config in GENERAL_ENGLISH_FEEDS:
            articles = fetch_feed(feed_config)
            general_articles.extend(articles)

        result["general"] = _select_best_articles(general_articles, max_per_category)

    total = sum(len(v) for v in result.values())
    logger.info(f"📊 Total articles fetched: {total}")
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    articles = fetch_articles("all")
    for cat, arts in articles.items():
        print(f"\n{'='*60}")
        print(f"Category: {cat.upper()}")
        print(f"{'='*60}")
        for i, art in enumerate(arts, 1):
            print(f"\n{i}. {art.source_icon} [{art.source_name}]")
            print(f"   {art.title}")
            print(f"   {art.summary[:100]}...")
            print(f"   🔗 {art.link}")
