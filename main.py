"""
Daily English Learning Email System - Main Entry Point.

This system automatically:
1. Crawls articles from garment industry & English learning RSS feeds
2. Processes content with AI (optional, via Gemini)
3. Sends beautifully formatted HTML emails on schedule

Schedule:
- Morning (6:30 AM): General English communication articles
- Evening (5:30 PM): Garment industry ESP articles

Usage:
    python main.py              # Run with scheduler (keeps running)
    python main.py --send-now   # Send immediately and exit
    python main.py --test       # Generate preview HTML and exit
    python main.py --morning    # Send morning email now
    python main.py --evening    # Send evening email now
"""
import argparse
import logging
import os
import sys
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config import (
    MORNING_SEND_HOUR,
    MORNING_SEND_MINUTE,
    EVENING_SEND_HOUR,
    EVENING_SEND_MINUTE,
    TIMEZONE,
    GMAIL_USER,
)
from crawler import fetch_articles
from ai_processor import process_articles
from email_sender import compose_email, send_email
from tts_generator import generate_article_audio

# ──────────────────────────────────────────────
# Logging Setup
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(
            open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)
        ),
        logging.FileHandler("daily_english.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def send_morning_email():
    """Send morning email with General English articles + PDF + Audio."""
    logger.info("=" * 60)
    logger.info("☀️  MORNING EMAIL - General English Communication")
    logger.info("=" * 60)

    try:
        articles = fetch_articles(category="general")
        if articles.get("general"):
            process_articles(articles["general"])

            # Generate audio attachments
            attachments = []
            for i, article in enumerate(articles["general"], 1):
                audio_path = generate_article_audio(article, i, category="general")
                if audio_path:
                    attachments.append(audio_path)

            subject, html = compose_email(articles, email_type="morning")
            send_email(subject, html, attachments=attachments)
        else:
            logger.warning("⚠️  No general English articles found!")
    except Exception as e:
        logger.error(f"❌ Morning email failed: {e}", exc_info=True)


def send_evening_email():
    """Send evening email with Garment Industry articles + PDF + Audio."""
    logger.info("=" * 60)
    logger.info("🌙 EVENING EMAIL - Garment Industry ESP")
    logger.info("=" * 60)

    try:
        articles = fetch_articles(category="garment")
        if articles.get("garment"):
            process_articles(articles["garment"])

            # Generate audio attachments
            attachments = []
            for i, article in enumerate(articles["garment"], 1):
                audio_path = generate_article_audio(article, i, category="garment")
                if audio_path:
                    attachments.append(audio_path)

            subject, html = compose_email(articles, email_type="evening")
            send_email(subject, html, attachments=attachments)
        else:
            logger.warning("⚠️  No garment industry articles found!")
    except Exception as e:
        logger.error(f"❌ Evening email failed: {e}", exc_info=True)


def send_combined_email():
    """Send a combined email with both categories + PDFs + Audio."""
    logger.info("=" * 60)
    logger.info("📚 COMBINED EMAIL - All Categories")
    logger.info("=" * 60)

    try:
        articles = fetch_articles(category="all")
        all_articles = []
        for cat_articles in articles.values():
            all_articles.extend(cat_articles)

        if all_articles:
            process_articles(all_articles)

            # Generate audio attachments for each category
            attachments = []
            if articles.get("garment"):
                for i, article in enumerate(articles["garment"], 1):
                    audio = generate_article_audio(article, i, category="garment")
                    if audio:
                        attachments.append(audio)

            if articles.get("general"):
                for i, article in enumerate(articles["general"], 1):
                    audio = generate_article_audio(article, i, category="general")
                    if audio:
                        attachments.append(audio)

            subject, html = compose_email(articles, email_type="combined")
            send_email(subject, html, attachments=attachments)
        else:
            logger.warning("⚠️  No articles found from any source!")
    except Exception as e:
        logger.error(f"❌ Combined email failed: {e}", exc_info=True)


def generate_preview():
    """Generate a preview HTML file for testing."""
    logger.info("🔍 Generating preview...")

    articles = fetch_articles(category="all")
    all_articles = []
    for cat_articles in articles.values():
        all_articles.extend(cat_articles)

    if all_articles:
        process_articles(all_articles)

    subject, html = compose_email(articles, email_type="combined")

    preview_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "preview.html"
    )
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"✅ Preview saved to: {preview_path}")
    logger.info(f"📧 Subject: {subject}")
    logger.info(f"📊 Articles: {sum(len(v) for v in articles.values())}")
    return preview_path


def run_scheduler():
    """Run the email scheduler."""
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║   📚 Daily English Learning Email System            ║")
    print("║   ─────────────────────────────────────────────      ║")
    print(f"║   📧 Sending to: {GMAIL_USER:<35}  ║")
    print(f"║   ☀️  Morning:    {MORNING_SEND_HOUR:02d}:{MORNING_SEND_MINUTE:02d} ({TIMEZONE}){' '*(20-len(TIMEZONE))}  ║")
    print(f"║   🌙 Evening:    {EVENING_SEND_HOUR:02d}:{EVENING_SEND_MINUTE:02d} ({TIMEZONE}){' '*(20-len(TIMEZONE))}  ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    scheduler = BlockingScheduler()

    # Morning email - General English
    scheduler.add_job(
        send_morning_email,
        CronTrigger(
            hour=MORNING_SEND_HOUR,
            minute=MORNING_SEND_MINUTE,
            timezone=TIMEZONE,
        ),
        id="morning_email",
        name="Morning General English Email",
        misfire_grace_time=3600,  # 1 hour grace period
    )

    # Evening email - Garment Industry
    scheduler.add_job(
        send_evening_email,
        CronTrigger(
            hour=EVENING_SEND_HOUR,
            minute=EVENING_SEND_MINUTE,
            timezone=TIMEZONE,
        ),
        id="evening_email",
        name="Evening Garment Industry Email",
        misfire_grace_time=3600,
    )

    logger.info("⏰ Scheduler started. Waiting for next send time...")
    logger.info("   Press Ctrl+C to stop.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Scheduler stopped. Goodbye!")


def main():
    parser = argparse.ArgumentParser(
        description="Daily English Learning Email System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                Run scheduler (keeps running)
  python main.py --send-now     Send combined email immediately
  python main.py --morning      Send morning email now
  python main.py --evening      Send evening email now
  python main.py --test         Generate preview HTML file
        """,
    )
    parser.add_argument(
        "--send-now", action="store_true",
        help="Send combined email immediately and exit"
    )
    parser.add_argument(
        "--morning", action="store_true",
        help="Send morning email immediately and exit"
    )
    parser.add_argument(
        "--evening", action="store_true",
        help="Send evening email immediately and exit"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Generate preview HTML file and exit"
    )

    args = parser.parse_args()

    if args.test:
        preview_path = generate_preview()
        print(f"\n🌐 Open in browser: file:///{preview_path}")
    elif args.send_now:
        send_combined_email()
    elif args.morning:
        send_morning_email()
    elif args.evening:
        send_evening_email()
    else:
        run_scheduler()


if __name__ == "__main__":
    main()
