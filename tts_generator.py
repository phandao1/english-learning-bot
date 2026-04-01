"""
Text-to-Speech Module.
Uses Microsoft Edge TTS (free, high quality) to generate audio MP3 files
for English articles - helping users practice listening.
"""
import logging
import os
from datetime import datetime
from gtts import gTTS

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

def ensure_output_dir():
    """Ensure output directory exists."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_article_audio(article, index: int, category: str = "garment") -> str | None:
    """Generate audio for a single article using gTTS."""
    ensure_output_dir()
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{category}_article_{index}_{date_str}.mp3"
    filepath = os.path.join(OUTPUT_DIR, filename)

    parts = []
    category_name = "Garment Industry News" if category == "garment" else "General English Practice"
    parts.append(f"Article number {index}. {category_name}.")
    parts.append(f"From {article.source_name}.")
    parts.append(f"Title: {article.title}")
    
    # Use full scraped text if available, else fallback to summary
    content = getattr(article, "full_text", "")
    if not content:
        content = article.ai_summary if getattr(article, "ai_summary", None) else article.summary

    if content:
        parts.append("Content: ")
        parts.append(content)

    if article.vocabulary:
        parts.append("Key Vocabulary:")
        for vocab in article.vocabulary:
            word = vocab.get("word", "")
            meaning_en = vocab.get("meaning_en", "")
            parts.append(f"Word: {word}.")
            if meaning_en:
                parts.append(f"Meaning: {meaning_en}.")

    text = ". ".join(parts)

    try:
        logger.info(f"🔊 Generating audio for article {index} using gTTS...")
        tts = gTTS(text=text, lang='en', tld='us', slow=False)
        tts.save(filepath)
        logger.info(f"✅ Audio saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"❌ Audio generation failed for article {index}: {e}")
        return None

def generate_combined_audio(articles: list, category: str = "garment") -> str | None:
    """Generate a single combined MP3 file for all articles in a category using gTTS."""
    ensure_output_dir()
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{category}_combined_{date_str}.mp3"
    filepath = os.path.join(OUTPUT_DIR, filename)

    parts = []
    if category == "garment":
        parts.append("Welcome to your Daily Garment Industry English Learning.")
    else:
        parts.append("Welcome to your Daily English Communication Practice.")
    parts.append("Let's begin.")

    # Aggregate vocabulary
    all_vocab = []
    
    for i, article in enumerate(articles, 1):
        parts.append(f"Article {i} of {len(articles)}. Source: {article.source_name}.")
        parts.append(f"The title is: {article.title}")
        
        summary = article.ai_summary if article.ai_summary else article.summary
        if summary:
            parts.append(summary)
            
        if article.vocabulary:
            all_vocab.extend(article.vocabulary)
            
        parts.append("Moving on." if i < len(articles) else "Now for the vocabulary section.")

    if all_vocab:
        parts.append("Here is the combined vocabulary list for today's articles.")
        # Deduplicate vocab based on word
        seen_words = set()
        unique_vocab = []
        for v in all_vocab:
            w = v.get("word", "").lower()
            if w not in seen_words:
                seen_words.add(w)
                unique_vocab.append(v)
                
        for vocab in unique_vocab:
            word = vocab.get("word", "")
            parts.append(word)
            # Read twice for practice
            parts.append(word)
            parts.append("...")

    parts.append("That's all for today. Keep practicing!")

    text = ". ".join(parts)

    try:
        logger.info(f"🔊 Generating combined audio for {category} ({len(articles)} articles) using gTTS...")
        tts = gTTS(text=text, lang='en', tld='us', slow=False)
        tts.save(filepath)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        logger.info(f"✅ Combined audio saved: {filepath} ({size_mb:.1f} MB)")
        return filepath
    except Exception as e:
        logger.error(f"❌ Combined audio generation failed: {e}")
        return None
