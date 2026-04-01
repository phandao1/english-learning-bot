"""
Configuration for Daily English Learning Email System.
Manages RSS sources, email settings, and scheduling.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Gmail Configuration
# ──────────────────────────────────────────────
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
# Support multiple recipients (comma-separated)
_recipient_raw = os.getenv("RECIPIENT_EMAIL", GMAIL_USER)
RECIPIENT_EMAILS = [e.strip() for e in _recipient_raw.split(",") if e.strip()]

# ──────────────────────────────────────────────
# Schedule Configuration
# ──────────────────────────────────────────────
MORNING_SEND_HOUR = int(os.getenv("MORNING_SEND_HOUR", "7"))
MORNING_SEND_MINUTE = int(os.getenv("MORNING_SEND_MINUTE", "30"))

EVENING_SEND_HOUR = int(os.getenv("EVENING_SEND_HOUR", "19"))
EVENING_SEND_MINUTE = int(os.getenv("EVENING_SEND_MINUTE", "30"))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Ho_Chi_Minh")

# ──────────────────────────────────────────────
# RSS Feed Sources
# ──────────────────────────────────────────────

# Ngành may mặc - Garment/Textile Industry (ESP)
GARMENT_FEEDS = [
    {
        "name": "Apparel Resources",
        "url": "https://apparelresources.com/feed/",
        "category": "garment_industry",
        "icon": "🧵",
    },
    {
        "name": "Textile World",
        "url": "https://www.textileworld.com/feed/",
        "category": "garment_industry",
        "icon": "🏭",
    },
    {
        "name": "Sourcing Journal",
        "url": "https://sourcingjournal.com/feed/",
        "category": "garment_industry",
        "icon": "👔",
    },
    {
        "name": "Fashion Dive",
        "url": "https://www.fashiondive.com/feeds/news/",
        "category": "garment_industry",
        "icon": "👗",
    },
]

# Tiếng Anh giao tiếp - General English Communication (text articles only)
GENERAL_ENGLISH_FEEDS = [
    {
        "name": "Simple English News Daily",
        "url": "https://www.simpleenglishnews.com/feed",
        "category": "general_english",
        "icon": "📖",
    },
    {
        "name": "News In Levels",
        "url": "https://www.newsinlevels.com/feed/",
        "category": "general_english",
        "icon": "📊",
    },
    {
        "name": "Spotlight English",
        "url": "https://spotlightenglish.com/feed/",
        "category": "general_english",
        "icon": "🌍",
    },
    {
        "name": "Good News Network",
        "url": "https://www.goodnewsnetwork.org/feed/",
        "category": "general_english",
        "icon": "😊",
    },
]

# Number of articles per category per email
ARTICLES_PER_CATEGORY = 3

# ──────────────────────────────────────────────
# Email Template Settings
# ──────────────────────────────────────────────
EMAIL_SUBJECT_MORNING = "☀️ Bài Học Tiếng Anh Giao Tiếp - Buổi Sáng | {date}"
EMAIL_SUBJECT_EVENING = "🌙 Bài Học Tiếng Anh Chuyên Ngành May - Buổi Tối | {date}"
EMAIL_SUBJECT_COMBINED = "📚 Bài Học Tiếng Anh Hàng Ngày | {date}"
