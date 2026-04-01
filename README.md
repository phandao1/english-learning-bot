# 📚 Daily English Learning Email System

Hệ thống tự động gửi bài học Tiếng Anh qua email hàng ngày, phục vụ người làm **ngành may mặc** đang học tiếng Anh:
- 🧵 **Tiếng Anh chuyên ngành may** (ESP - English for Specific Purposes)
- 💬 **Tiếng Anh giao tiếp tổng quát** (General English)

## ✨ Tính năng

- 📡 Tự động crawl bài viết từ RSS feeds (chỉ bài báo text, không audio/video)
- 📖 Trích xuất từ vựng quan trọng với **phiên âm IPA** + **nghĩa Tiếng Việt** (offline, không cần API)
- 🎯 Chọn bài thông minh: lọc bài rác, ưu tiên từ vựng cấp B1-B2, phù hợp người mới học
- 📧 Email HTML đẹp mắt, dark-theme hiện đại — đọc trực tiếp trong email, không cần mở file
- 🔊 Tạo file audio MP3 (gTTS) đính kèm để luyện nghe
- ⏰ Lập lịch gửi tự động: sáng (giao tiếp) + tối (chuyên ngành)
- 🐳 Đóng gói Docker, chạy 24/7

## 🚀 Cài đặt nhanh

### 1. Cấu hình Gmail

1. Bật **2-Step Verification** trong tài khoản Google
2. Tạo **App Password**: https://myaccount.google.com/apppasswords
3. Tạo file `.env`:

```env
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient1@gmail.com,recipient2@gmail.com

# Tùy chỉnh giờ gửi (mặc định: 7:30 sáng, 19:30 tối)
MORNING_SEND_HOUR=7
MORNING_SEND_MINUTE=30
EVENING_SEND_HOUR=19
EVENING_SEND_MINUTE=30
TIMEZONE=Asia/Ho_Chi_Minh
```

### 2. Chạy trực tiếp

```bash
pip install -r requirements.txt

# Xem preview email
python main.py --test

# Gửi email ngay
python main.py --send-now

# Chạy scheduler (chạy nền 24/7)
python main.py
```

### 3. Chạy với Docker

```bash
docker-compose up -d        # Build và chạy
docker-compose logs -f       # Xem logs
docker-compose down          # Dừng
```

## 📋 Lệnh CLI

| Lệnh | Mô tả |
|-------|--------|
| `python main.py` | Chạy scheduler tự động |
| `python main.py --send-now` | Gửi email tổng hợp ngay |
| `python main.py --morning` | Gửi email giao tiếp (sáng) |
| `python main.py --evening` | Gửi email chuyên ngành (tối) |
| `python main.py --test` | Tạo file preview HTML |

## 📡 Nguồn dữ liệu

### 🧵 Chuyên ngành may (ESP)
| Nguồn | Mô tả |
|-------|--------|
| Apparel Resources | Kỹ thuật, sản xuất ngành may |
| Textile World | Công nghệ dệt may |
| Sourcing Journal | Chuỗi cung ứng, xuất nhập khẩu |
| Fashion Dive | Tin tức kinh doanh thời trang |

### 💬 Giao tiếp (General)
| Nguồn | Mô tả |
|-------|--------|
| Simple English News | Bài viết tiếng Anh đơn giản |
| News In Levels | Tin tức chia 3 cấp độ |
| Positive News | Tin tích cực, ngôn ngữ dễ hiểu |
| Good News Network | Tin tức tích cực toàn cầu |

## 📅 Lịch học đề xuất

| Thời gian | Nội dung | Mục tiêu |
|-----------|----------|----------|
| ☀️ 7:30 sáng | 3 bài Giao tiếp | Đọc nhẹ cùng cafe, từ vựng đời thường |
| 🌙 7:30 tối | 3 bài Chuyên ngành | Thuật ngữ kỹ thuật may mặc |

## 🧠 Cách hệ thống chọn bài

Mỗi ngày hệ thống crawl ~50-80 bài từ tất cả nguồn, rồi **chấm điểm** để chọn 3 bài tốt nhất/danh mục:

1. **Lọc bài rác**: Bỏ bài promotional, link chết, nội dung quá ngắn
2. **Độ khó từ vựng**: Ưu tiên bài cấp B1-B2 (tỷ lệ từ dài vừa phải, không quá học thuật)
3. **Độ liên quan**: Bài chuyên ngành may được thưởng điểm nếu chứa keyword ngành (textile, garment, fabric, production...)
4. **Độ mới**: Bài mới hơn được ưu tiên

## 📁 Cấu trúc dự án

```
crawl_data/
├── main.py              # Entry point + scheduler
├── config.py            # Cấu hình RSS feeds & settings
├── crawler.py           # RSS crawler + article scoring
├── ai_processor.py      # Trích xuất từ vựng (IPA + dịch Việt)
├── email_sender.py      # Email composer & sender
├── tts_generator.py     # Tạo audio MP3 bằng gTTS
├── pdf_generator.py     # (Không sử dụng) Tạo PDF
├── templates/
│   └── email_template.html  # HTML email template
├── fonts/               # Font cho PDF
├── output/              # File MP3 tạm
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env                 # Gmail credentials (tự tạo)
```

## 💡 Đề xuất cải tiến

### Ưu tiên cao
- **Lưu lịch sử bài đã gửi** (SQLite/JSON): tránh gửi trùng bài, theo dõi từ vựng đã học
- **Scrape full text tốt hơn**: Dùng newspaper3k hoặc trafilatura thay vì BeautifulSoup thủ công — nhiều trang hiện tại scrape không lấy được nội dung đầy đủ
- **Rate limit cho feed**: Thêm delay giữa các request để tránh bị block (Positive News trả 403 ở request đầu)

### Ưu tiên trung bình
- **Spaced Repetition**: Lặp lại từ vựng cũ theo lịch (1 ngày, 3 ngày, 7 ngày) — kiểu Anki nhưng trong email
- **Phân cấp độ bài rõ hơn**: Gắn tag A2/B1/B2 cho mỗi bài dựa trên phân tích readability (Flesch-Kincaid)
- **Template email responsive hơn**: Một số email client (Outlook) không render CSS gradient, nên cần fallback

### Ưu tiên thấp (nice-to-have)
- **Dashboard web đơn giản**: Xem thống kê bài đã gửi, từ vựng đã học
- **Telegram bot song song**: Gửi bài qua Telegram ngoài email
- **Quiz nhỏ cuối email**: 2-3 câu trắc nghiệm từ vựng từ bài hôm trước
