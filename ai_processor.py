"""
Content Processor Module.
Extracts keywords and builds vocabulary with IPA + Vietnamese translations
using local libraries (eng_to_ipa + deep_translator). No external AI needed.
"""
import logging
import re

try:
    import eng_to_ipa as ipa
    from deep_translator import GoogleTranslator
    HAS_LOCAL_DICT = True
except ImportError:
    HAS_LOCAL_DICT = False

logger = logging.getLogger(__name__)

# Common English stop words to filter out during keyword extraction
_STOP_WORDS = {
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
    "make", "take", "get", "know", "find", "time", "year",
    "people", "way", "day", "thing", "man", "world", "life", "hand",
    "part", "child", "eye", "woman", "place", "work", "week", "case",
    "point", "company", "number", "group", "problem", "fact", "says",
    "like", "good", "well", "down", "up", "even", "now", "see", "come",
    "still", "show", "tell", "talk", "help", "look", "think", "back",
    "give", "long", "great", "going", "start", "right",
}


def extract_keywords_simple(text: str, count: int = 5) -> list[str]:
    """Extract important keywords from text by frequency."""
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    word_freq = {}
    for word in words:
        if word not in _STOP_WORDS:
            word_freq[word] = word_freq.get(word, 0) + 1

    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:count]]


def build_local_vocabulary(keywords: list[str]) -> list[dict]:
    """Build vocabulary list with IPA and Vietnamese translation using local libs."""
    vocab_list = []
    if not HAS_LOCAL_DICT:
        return vocab_list

    translator = GoogleTranslator(source='en', target='vi')
    for word in keywords[:7]:
        try:
            pronunciation = ipa.convert(word)
            meaning_vi = translator.translate(word)
            if meaning_vi and word.lower() != meaning_vi.lower():
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


def process_articles(articles: list) -> list:
    """Process articles: extract keywords + build vocabulary (all local, no AI)."""
    for article in articles:
        source_text = f"{article.title} {article.summary}"
        full_text = getattr(article, "full_text", "")
        if full_text:
            source_text += f" {full_text}"

        article.keywords = extract_keywords_simple(source_text)
        article.vocabulary = build_local_vocabulary(article.keywords)

    return articles
