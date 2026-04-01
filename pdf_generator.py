"""
PDF Generator Module.
Creates beautiful PDF study materials with vocabulary, pronunciation, and translations.
Two types:
  1. Garment Industry ESP - Technical vocabulary focus
  2. General English Communication - Listening/reading practice focus
"""
import logging
import os
import re
from datetime import datetime

from fpdf import FPDF

logger = logging.getLogger(__name__)

# Font directory
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def ensure_dirs():
    """Ensure output and font directories exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FONT_DIR, exist_ok=True)


def download_font_if_needed():
    """Download DejaVu font for Unicode/IPA support if not present."""
    font_path = os.path.join(FONT_DIR, "DejaVuSans.ttf")
    bold_path = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

    if os.path.exists(font_path) and os.path.exists(bold_path):
        return True

    # On Windows, try to use native Arial font which supports Vietnamese + IPA
    windows_arial = r"C:\Windows\Fonts\arial.ttf"
    windows_arial_bd = r"C:\Windows\Fonts\arialbd.ttf"
    
    if os.path.exists(windows_arial) and os.path.exists(windows_arial_bd):
        import shutil
        try:
            shutil.copy(windows_arial, font_path)
            shutil.copy(windows_arial_bd, bold_path)
            logger.info("✅ Used native Windows Arial fonts for Unicode support.")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Could not copy Arial font: {e}")

    # Fallback to web download if Arial is unavailable
    import requests
    base_url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/"
    fonts = {"DejaVuSans.ttf": font_path, "DejaVuSans-Bold.ttf": bold_path}

    for fname, fpath in fonts.items():
        if not os.path.exists(fpath):
            logger.info(f"📥 Downloading font: {fname}...")
            try:
                resp = requests.get(base_url + fname, timeout=10)
                resp.raise_for_status()
                with open(fpath, "wb") as f:
                    f.write(resp.content)
            except Exception as e:
                logger.error(f"❌ Failed to download {fname}: {e}")
                return False
    return True


class EnglishLearningPDF(FPDF):
    """Custom PDF class for English learning materials."""

    def __init__(self, pdf_type="garment"):
        super().__init__()
        self.pdf_type = pdf_type
        self._header_title = ""
        self._header_date = ""

        font_path = os.path.join(FONT_DIR, "DejaVuSans.ttf")
        bold_path = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

        # Setup fonts
        if download_font_if_needed() and os.path.exists(font_path):
            self.add_font("DejaVu", "", font_path)
            self.add_font("DejaVu", "B", bold_path)
            self.default_font = "DejaVu"
        else:
            self.default_font = "helvetica"

    def header(self):
        """PDF header with gradient-like colored bar."""
        if self.pdf_type == "garment":
            r, g, b = 245, 158, 11  # Amber
            emoji = "GARMENT INDUSTRY"
            subtitle = "Tieng Anh Chuyen Nganh May"
        else:
            r, g, b = 16, 185, 129  # Emerald
            emoji = "GENERAL ENGLISH"
            subtitle = "Tieng Anh Giao Tiep"

        # Header background
        self.set_fill_color(r, g, b)
        self.rect(0, 0, 210, 28, "F")

        # Title
        self.set_font(self.default_font, "B", 16)
        self.set_text_color(30, 30, 30)
        self.set_y(5)
        self.cell(0, 8, f"  {emoji} - ESP Vocabulary", ln=True, align="L")

        # Subtitle
        self.set_font(self.default_font, "", 10)
        self.set_text_color(60, 60, 60)
        self.cell(0, 6, f"  {subtitle} | {self._header_date}", ln=True, align="L")

        self.ln(5)

    def footer(self):
        """PDF footer with page number."""
        self.set_y(-15)
        self.set_font(self.default_font, "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Daily English Learning System | Page {self.page_no()}/{{nb}}", align="C")

    def add_article_section(self, article, index):
        """Add an article section with vocabulary analysis."""
        # Check if we need a new page (at least 80mm needed)
        if self.get_y() > 220:
            self.add_page()

        # Article number + source badge
        if self.pdf_type == "garment":
            self.set_fill_color(245, 158, 11)
        else:
            self.set_fill_color(16, 185, 129)

        # Article divider line
        if index > 1:
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)

        # Article number badge
        y_start = self.get_y()
        self.set_font(self.default_font, "B", 12)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(
            245 if self.pdf_type == "garment" else 16,
            158 if self.pdf_type == "garment" else 185,
            11 if self.pdf_type == "garment" else 129,
        )
        self.cell(10, 8, f" {index} ", fill=True)
        self.set_text_color(100, 100, 100)
        self.set_font(self.default_font, "", 9)
        self.cell(0, 8, f"  {article.source_name}", ln=True)

        # Article title
        self.set_font(self.default_font, "B", 13)
        self.set_text_color(30, 30, 30)
        # Clean title for PDF (remove problematic characters)
        clean_title = self._clean_text(article.title)
        self.multi_cell(0, 7, clean_title)
        self.ln(2)

        # Article link
        self.set_font(self.default_font, "", 8)
        self.set_text_color(70, 130, 180)
        link_text = article.link[:80] + "..." if len(article.link) > 80 else article.link
        self.cell(0, 5, link_text, ln=True, link=article.link)
        self.ln(3)

        # AI Summary
        if article.ai_summary:
            self.set_fill_color(240, 245, 255)
            self.set_draw_color(100, 120, 200)
            y_box = self.get_y()
            self.set_font(self.default_font, "B", 9)
            self.set_text_color(80, 80, 160)
            self.cell(0, 6, "  AI SUMMARY", ln=True)
            self.set_font(self.default_font, "", 10)
            self.set_text_color(50, 50, 50)
            clean_summary = self._clean_text(article.ai_summary)
            self.multi_cell(0, 6, clean_summary)
            self.ln(3)
        elif article.summary:
            self.set_font(self.default_font, "", 10)
            self.set_text_color(70, 70, 70)
            clean_summary = self._clean_text(article.summary)
            self.multi_cell(0, 6, clean_summary)
            self.ln(3)

        # Vocabulary removed from here, combined at the end instead

        # Keywords
        if article.keywords:
            self.set_font(self.default_font, "B", 9)
            self.set_text_color(100, 100, 100)
            self.cell(20, 6, "Keywords: ")
            self.set_font(self.default_font, "", 9)
            self.set_text_color(80, 80, 80)
            keywords_text = " | ".join(article.keywords[:5])
            self.cell(0, 6, self._clean_text(keywords_text), ln=True)

        self.ln(8)

    def add_combined_vocabulary(self, articles):
        """Add combined vocabulary list from all articles in a simple, clean notepad style."""
        # Collect unique vocabularies
        all_vocab = []
        seen = set()
        for article in articles:
            for v in article.vocabulary:
                word = v.get("word", "").lower()
                if word not in seen:
                    seen.add(word)
                    all_vocab.append(v)
                    
        if not all_vocab:
            return
            
        self.add_page()
        self.set_font(self.default_font, "B", 14)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "TONG HOP TU VUNG (Vocabulary Glossary)", ln=True)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

        for vocab in all_vocab:
            if self.get_y() > 270:  # Check page break
                self.add_page()
            
            word = self._clean_text(vocab.get("word", ""))
            ipa = self._clean_text(vocab.get("pronunciation", ""))
            meaning_vi = self._clean_text(vocab.get("meaning_vi", ""))
            
            self.set_font(self.default_font, "B", 11)
            self.set_text_color(220, 38, 38)  # Red color for word
            
            # Combine word and IPA into one fixed-width column
            if ipa:
                if not ipa.startswith("/"): ipa = f"/{ipa}/"
                word_ipa = f"  {word} ({ipa})"
            else:
                word_ipa = f"  {word}"
                
            self.cell(70, 7, word_ipa)
            
            self.set_font(self.default_font, "", 11)
            self.set_text_color(40, 40, 40) # Dark text for meaning
            self.cell(0, 7, f": {meaning_vi}", ln=True)
            
            example = self._clean_text(vocab.get("example", ""))
            if example:
                self.set_font(self.default_font, "", 9)
                self.set_text_color(120, 120, 130)
                self.cell(10, 5, "") # Indent
                self.multi_cell(0, 5, f'Ví dụ: "{example}"')
                self.ln(1)
        self.ln(4)

    def _clean_text(self, text):
        """Clean text for PDF output - handle encoding issues."""
        if not text:
            return ""
        # Replace common problematic Unicode characters
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = text.replace("\u2013", "-").replace("\u2014", "--")
        text = text.replace("\u2026", "...")
        text = text.replace("\u00ae", "(R)").replace("\u2122", "(TM)")
        
        # Replace IPA modifier letters that FPDF struggles with
        text = text.replace("ˈ", "'")  # Primary stress
        text = text.replace("ˌ", ",")  # Secondary stress
        
        # Remove emoji but keep basic text
        text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
        return text.strip()


def generate_pdf(articles, pdf_type="garment"):
    """
    Generate a PDF study material from articles.

    Args:
        articles: List of Article objects (already processed by AI)
        pdf_type: 'garment' or 'general'

    Returns:
        Path to the generated PDF file, or None if failed
    """
    ensure_dirs()

    date_str = datetime.now().strftime("%Y-%m-%d")

    if pdf_type == "garment":
        filename = f"garment_vocabulary_{date_str}.pdf"
        title = "Garment Industry - ESP Vocabulary"
    else:
        filename = f"general_english_{date_str}.pdf"
        title = "General English - Communication Practice"

    filepath = os.path.join(OUTPUT_DIR, filename)

    try:
        pdf = EnglishLearningPDF(pdf_type=pdf_type)
        pdf._header_date = datetime.now().strftime("%A, %B %d, %Y")
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()

        # Introduction section
        pdf.set_font(pdf.default_font, "", 10)
        pdf.set_text_color(80, 80, 80)
        if pdf_type == "garment":
            intro = (
                "Tai lieu hoc tu vung Tieng Anh chuyen nganh may mac. "
                "Moi bai viet duoc AI phan tich va trich xuat tu vung quan trong "
                "kem phien am IPA va nghia Tieng Viet."
            )
        else:
            intro = (
                "Tai lieu luyen doc - nghe Tieng Anh giao tiep. "
                "Cac bai bao duoc AI tom tat va phan tich tu vung "
                "giup ban hoc hieu qua hon."
            )
        pdf.multi_cell(0, 6, intro)
        pdf.ln(5)

        # Add each article
        for i, article in enumerate(articles, 1):
            pdf.add_article_section(article, i)

        # Add combined vocabulary section
        pdf.add_combined_vocabulary(articles)

        # Study tips page
        pdf.add_page()
        pdf.set_font(pdf.default_font, "B", 14)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 10, "STUDY TIPS - Meo hoc Tieng Anh", ln=True)
        pdf.ln(5)

        tips = [
            "1. Doc to thanh tieng (Read aloud) - Giup cai thien phat am",
            "2. Ghi chep tu vung vao so tay rieng",
            "3. Dat cau voi moi tu vung moi",
            "4. On lai sau 1 ngay, 3 ngay, 7 ngay (Spaced Repetition)",
            "5. Nghe audio MP3 dinh kem de luyen nghe",
        ]

        pdf.set_font(pdf.default_font, "", 11)
        pdf.set_text_color(50, 50, 50)
        for tip in tips:
            pdf.multi_cell(0, 7, tip)
            pdf.ln(3)

        pdf.output(filepath)
        logger.info(f"✅ PDF generated: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"❌ PDF generation failed: {e}", exc_info=True)
        return None
