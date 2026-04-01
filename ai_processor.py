"""
AI Content Processor Module (Optional).
Uses Google Gemini to generate summaries, keywords, and vocabulary explanations.
Falls back to simple extraction if Gemini API is not configured.
"""
import logging
import re
from typing import Optional

try:
    import eng_to_ipa as ipa
    from deep_translator import GoogleTranslator
    HAS_LOCAL_DICT = True
except ImportError:
    HAS_LOCAL_DICT = False

from config import GEMINI_API_KEY, USE_AI_SUMMARY

logger = logging.getLogger(__name__)

# Try to import Gemini
gemini_model = None
if USE_AI_SUMMARY:
    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        logger.info("✅ Gemini AI initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️  Could not initialize Gemini AI: {e}")
        gemini_model = None


def extract_keywords_simple(text: str, count: int = 5) -> list[str]:
    """
    Simple keyword extraction without AI.
    Extracts longer, less common words as potential keywords.
    """
    # Common English stop words to filter out
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "out", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where", "why",
        "how", "all", "both", "each", "few", "more", "most", "other", "some",
        "such", "no", "nor", "not", "only", "own", "same", "so", "than",
        "too", "very", "just", "because", "but", "and", "or", "if", "while",
        "about", "this", "that", "these", "those", "it", "its", "they",
        "them", "their", "we", "our", "you", "your", "he", "she", "him",
        "her", "his", "which", "what", "who", "whom", "said", "also",
        "new", "one", "two", "first", "last", "many", "much", "any",
        "make", "take", "get", "get", "know", "find", "time", "year",
        "people", "way", "day", "thing", "man", "world", "life", "hand",
        "part", "child", "eye", "woman", "place", "work", "week", "case",
        "point", "company", "number", "group", "problem", "fact", "says",
        "like", "good", "well", "down", "up", "even", "now", "see", "come"
    }

    words = re.findall(r"\b[a-zA-Z]{5,}\b", text.lower())
    # Count word frequency
    word_freq = {}
    for word in words:
        if word not in stop_words and len(word) > 4:
            word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency and return top words
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:count]]

def build_local_vocabulary(keywords: list[str]) -> list[dict]:
    """Build vocabulary list with IPA and Vietnamese translation offline."""
    vocab_list = []
    if not HAS_LOCAL_DICT:
        return vocab_list
        
    translator = GoogleTranslator(source='en', target='vi')
    for word in keywords[:7]: # Increase limit to top 7 words instead of 3
        try:
            pronunciation = ipa.convert(word)
            meaning_vi = translator.translate(word)
            # Avoid meaningless translations gracefully
            if len(meaning_vi) > 0 and word.lower() != meaning_vi.lower():
                vocab_list.append({
                    "word": word,
                    "pronunciation": pronunciation,
                    "meaning_en": "",
                    "meaning_vi": meaning_vi,
                    "example": ""
                })
        except Exception:
            pass
    return vocab_list


def process_with_ai(article) -> bool:
    """
    Process a single article with Gemini AI to generate:
    - A concise summary (2 sentences)
    - Key vocabulary with Vietnamese translations
    - Important keywords

    Returns True if AI processing was successful.
    """
    if not gemini_model:
        return False

    category_context = (
        "garment/textile industry (ngành may mặc)"
        if article.category == "garment_industry"
        else "general English communication (giao tiếp tiếng Anh)"
    )

    prompt = f"""You are an English teacher helping a Vietnamese professional in the garment industry learn English.

Analyze this article about {category_context}:

Title: {article.title}
Content: {article.summary}

Please provide:
1. **Summary**: A clear, concise 2-sentence summary in English (suitable for intermediate learners).
2. **Vocabulary** (exactly 3 items): Pick 3 important/difficult words from the article. For each:
   - word: the English word
   - pronunciation: IPA pronunciation
   - meaning_en: brief English definition
   - meaning_vi: Vietnamese translation
   - example: a short example sentence using the word
3. **Keywords** (exactly 5 items): 5 key English terms/phrases from this article.

Format your response EXACTLY like this:
SUMMARY: [your 2-sentence summary]
VOCAB1: [word] | [IPA] | [English meaning] | [Vietnamese meaning] | [example sentence]
VOCAB2: [word] | [IPA] | [English meaning] | [Vietnamese meaning] | [example sentence]
VOCAB3: [word] | [IPA] | [English meaning] | [Vietnamese meaning] | [example sentence]
KEYWORDS: [keyword1], [keyword2], [keyword3], [keyword4], [keyword5]
"""

    try:
        response = gemini_model.generate_content(prompt)
        text = response.text.strip()

        # Parse summary
        summary_match = re.search(r"SUMMARY:\s*(.+?)(?=\nVOCAB|\Z)", text, re.DOTALL)
        if summary_match:
            article.ai_summary = summary_match.group(1).strip()

        # Parse vocabulary
        vocab_list = []
        for i in range(1, 4):
            vocab_match = re.search(rf"VOCAB{i}:\s*(.+)", text)
            if vocab_match:
                parts = [p.strip() for p in vocab_match.group(1).split("|")]
                if len(parts) >= 5:
                    vocab_list.append(
                        {
                            "word": parts[0],
                            "pronunciation": parts[1],
                            "meaning_en": parts[2],
                            "meaning_vi": parts[3],
                            "example": parts[4],
                        }
                    )
        article.vocabulary = vocab_list

        # Parse keywords
        keywords_match = re.search(r"KEYWORDS:\s*(.+)", text)
        if keywords_match:
            article.keywords = [
                k.strip() for k in keywords_match.group(1).split(",")
            ]

        logger.info(f"🤖 AI processed: {article.title[:50]}...")
        return True

    except Exception as e:
        logger.warning(f"⚠️  AI processing failed for '{article.title[:40]}': {e}")
        return False


def process_articles(articles: list) -> list:
    """
    Process a list of articles - with AI if available, otherwise with simple extraction.
    """
    for article in articles:
        if USE_AI_SUMMARY and gemini_model:
            success = process_with_ai(article)
            if not success:
                # Fallback to simple extraction
                article.keywords = extract_keywords_simple(
                    f"{article.title} {article.summary}"
                )
                article.vocabulary = build_local_vocabulary(article.keywords)
        else:
            article.keywords = extract_keywords_simple(
                f"{article.title} {article.summary}"
            )
            article.vocabulary = build_local_vocabulary(article.keywords)

    return articles
