"""
Email Sender Module.
Composes and sends beautifully formatted HTML emails via Gmail SMTP.
"""
import logging
import os
import random
import smtplib
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

from config import (
    GMAIL_USER,
    GMAIL_APP_PASSWORD,
    RECIPIENT_EMAILS,
    EMAIL_SUBJECT_MORNING,
    EMAIL_SUBJECT_EVENING,
    EMAIL_SUBJECT_COMBINED,
    TIMEZONE,
)

logger = logging.getLogger(__name__)

# Directory containing templates
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# Motivational quotes for email footer
QUOTES = [
    "The limits of my language mean the limits of my world. — Ludwig Wittgenstein",
    "One language sets you in a corridor for life. Two languages open every door along the way. — Frank Smith",
    "To have another language is to possess a second soul. — Charlemagne",
    "Learning is a treasure that will follow its owner everywhere. — Chinese Proverb",
    "The beautiful thing about learning is that no one can take it away from you. — B.B. King",
    "Language is the road map of a culture. — Rita Mae Brown",
    "A different language is a different vision of life. — Federico Fellini",
    "You can never understand one language until you understand at least two. — Geoffrey Willans",
    "If you talk to a man in a language he understands, that goes to his head. If you talk to him in his own language, that goes to his heart. — Nelson Mandela",
    "The more that you read, the more things you will know. — Dr. Seuss",
    "Knowledge of languages is the doorway to wisdom. — Roger Bacon",
    "With languages, you are at home anywhere. — Edmund de Waal",
    "Every new language is a new window that opens to a new world. — Chinese Proverb",
    "Study without desire spoils the memory. — Leonardo da Vinci",
]

# Daily learning tips
DAILY_TIPS = [
    "🎯 <b>Shadowing technique</b>: Nghe và lặp lại ngay lập tức những gì bạn nghe. Đây là phương pháp hiệu quả nhất để cải thiện phát âm!",
    "📝 <b>Spaced Repetition</b>: Ghi lại 5 từ vựng mới hôm nay. Ôn lại sau 1 ngày, 3 ngày, và 7 ngày để nhớ lâu hơn.",
    "🗣️ <b>Think in English</b>: Hãy thử suy nghĩ bằng tiếng Anh thay vì dịch từ tiếng Việt. Bắt đầu với những câu đơn giản!",
    "📖 <b>Context is King</b>: Đừng học từ vựng đơn lẻ. Hãy học cả câu hoặc cụm từ để nhớ lâu và sử dụng tự nhiên hơn.",
    "🎧 <b>Active Listening</b>: Khi nghe podcast tiếng Anh, hãy ghi chú lại những từ/cụm từ mới thay vì chỉ nghe thụ động.",
    "✍️ <b>Write Daily</b>: Viết 3-5 câu tiếng Anh mỗi ngày về bất kỳ chủ đề nào. Consistency is more important than perfection!",
    "🔄 <b>Paraphrase</b>: Thử diễn đạt lại một ý tưởng bằng nhiều cách khác nhau. Điều này giúp bạn linh hoạt hơn khi giao tiếp.",
    "📱 <b>Change your phone language</b>: Đổi ngôn ngữ điện thoại sang tiếng Anh. Bạn sẽ tiếp xúc với tiếng Anh mọi lúc!",
    "🎬 <b>Watch with subtitles</b>: Xem phim có phụ đề tiếng Anh. Tránh xem phụ đề tiếng Việt nếu có thể!",
    "💪 <b>Embrace mistakes</b>: Mỗi sai lầm là một cơ hội học hỏi. Đừng sợ nói sai - hãy sợ không nói!",
    "📚 <b>Read aloud</b>: Đọc to bài viết tiếng Anh giúp cải thiện cả phát âm lẫn khả năng đọc hiểu.",
    "🎯 <b>Set mini goals</b>: Đặt mục tiêu nhỏ mỗi ngày: học 3 từ, đọc 1 bài, viết 5 câu. Tích tiểu thành đại!",
    "🧠 <b>Chunking</b>: Thay vì dịch từng từ, hãy học cả cụm: 'in terms of', 'as a matter of fact', 'on the other hand'.",
    "📊 <b>Track progress</b>: Ghi lại số từ vựng mới và thời gian học mỗi ngày. Nhìn lại sẽ thấy tiến bộ rõ rệt!",
]


def compose_email(
    articles: dict,
    email_type: str = "combined",
) -> tuple[str, str]:
    """
    Compose an HTML email from articles.

    Args:
        articles: Dictionary with 'garment' and/or 'general' article lists
        email_type: 'morning', 'evening', or 'combined'

    Returns:
        Tuple of (subject, html_body)
    """
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")

    # Select subject based on type
    if email_type == "morning":
        subject = EMAIL_SUBJECT_MORNING.format(date=date_str)
        header_emoji = "☀️"
        header_title = "Bài Học Tiếng Anh Giao Tiếp"
        header_subtitle = "Đọc nhẹ nhàng cùng cafe buổi sáng ☕"
        send_time = "6:30 sáng"
    elif email_type == "evening":
        subject = EMAIL_SUBJECT_EVENING.format(date=date_str)
        header_emoji = "🌙"
        header_title = "Bài Học Tiếng Anh Chuyên Ngành May"
        header_subtitle = "Nâng cao thuật ngữ kỹ thuật ngành may mặc 🧵"
        send_time = "5:30 chiều"
    else:
        subject = EMAIL_SUBJECT_COMBINED.format(date=date_str)
        header_emoji = "📚"
        header_title = "Bài Học Tiếng Anh Hàng Ngày"
        header_subtitle = "Kết hợp chuyên ngành may & giao tiếp tổng quát"
        send_time = "hàng ngày"

    # Load and render template
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("email_template.html")

    html = template.render(
        subject=subject,
        header_emoji=header_emoji,
        header_title=header_title,
        header_subtitle=header_subtitle,
        date_str=date_str,
        garment_articles=articles.get("garment", []),
        general_articles=articles.get("general", []),
        daily_tip=random.choice(DAILY_TIPS),
        quote=random.choice(QUOTES),
        send_time=send_time,
    )

    return subject, html


def send_email(subject: str, html_body: str, attachments: list[str] | None = None) -> bool:
    """
    Send an HTML email via Gmail SMTP to all configured recipients.

    Args:
        subject: Email subject
        html_body: HTML email body
        attachments: Optional list of file paths to attach (PDFs, MP3s, etc.)

    Returns:
        True if sent successfully to at least one recipient
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.error("❌ Gmail credentials not configured! Set GMAIL_USER and GMAIL_APP_PASSWORD in .env")
        return False

    recipients = RECIPIENT_EMAILS if RECIPIENT_EMAILS else [GMAIL_USER]
    logger.info(f"📬 Recipients: {', '.join(recipients)}")

    # Plain text fallback
    plain_text = f"""
Daily English Learning - {datetime.now().strftime('%Y-%m-%d')}

Vui lòng xem email này trong HTML client để có trải nghiệm tốt nhất.

---
Sent by Daily English Learning System
    """

    success_count = 0
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)

            for recipient in recipients:
                try:
                    # Use 'mixed' to support attachments
                    msg = MIMEMultipart("mixed")
                    msg["Subject"] = subject
                    msg["From"] = f"English Learning Bot <{GMAIL_USER}>"
                    msg["To"] = recipient

                    # HTML + plain text alternative part
                    alt_part = MIMEMultipart("alternative")
                    alt_part.attach(MIMEText(plain_text, "plain", "utf-8"))
                    alt_part.attach(MIMEText(html_body, "html", "utf-8"))
                    msg.attach(alt_part)

                    # Attach files (PDFs, MP3s)
                    if attachments:
                        for filepath in attachments:
                            if filepath and os.path.exists(filepath):
                                filename = os.path.basename(filepath)
                                with open(filepath, "rb") as f:
                                    attachment = MIMEApplication(f.read())
                                    attachment.add_header(
                                        "Content-Disposition",
                                        "attachment",
                                        filename=filename,
                                    )
                                    msg.attach(attachment)
                                logger.info(f"📎 Attached: {filename}")

                    server.sendmail(GMAIL_USER, recipient, msg.as_string())
                    logger.info(f"✅ Sent to: {recipient}")
                    success_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to send to {recipient}: {e}")

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "❌ Gmail authentication failed! \n"
            "   Đảm bảo bạn dùng App Password, KHÔNG phải mật khẩu Gmail thường.\n"
            "   Tạo App Password tại: https://myaccount.google.com/apppasswords"
        )
        return False
    except Exception as e:
        logger.error(f"❌ Failed to connect to Gmail: {e}")
        return False

    logger.info(f"📊 Sent successfully to {success_count}/{len(recipients)} recipients")
    return success_count > 0
