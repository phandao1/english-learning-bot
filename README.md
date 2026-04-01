# 📚 Daily English Learning Email System

Hệ thống tự động gửi bài học Tiếng Anh qua email hàng ngày, kết hợp:
- 🧵 **Tiếng Anh chuyên ngành may** (ESP - English for Specific Purposes)
- 💬 **Tiếng Anh giao tiếp tổng quát** (General English)

## ✨ Tính năng

- 📡 Tự động crawl bài viết từ RSS feeds uy tín
- 🤖 Tóm tắt AI bằng Gemini (tùy chọn)
- 📖 Từ vựng quan trọng với phiên âm IPA + nghĩa Tiếng Việt
- 📧 Email HTML đẹp mắt, dark-theme hiện đại
- ⏰ Lập lịch gửi tự động: sáng (giao tiếp) + tối (chuyên ngành)
- 🐳 Đóng gói Docker, chạy 24/7

## 🚀 Cài đặt nhanh

### 1. Cấu hình Gmail

1. Bật **2-Step Verification** trong tài khoản Google
2. Tạo **App Password**: https://myaccount.google.com/apppasswords
3. Tạo file `.env`:

```bash
cp .env.example .env
# Sửa file .env với thông tin của bạn
```

### 2. Chạy trực tiếp (không Docker)

```bash
pip install -r requirements.txt

# Xem preview email
python main.py --test

# Gửi email ngay
python main.py --send-now

# Chạy scheduler (chạy nền)
python main.py
```

### 3. Chạy với Docker

```bash
# Build và chạy
docker-compose up -d

# Xem logs
docker-compose logs -f

# Dừng
docker-compose down
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

### Chuyên ngành may (ESP)
| Nguồn | Mô tả |
|-------|--------|
| Apparel Resources | Kỹ thuật, sản xuất ngành may |
| Just Style | Phân tích thị trường dệt may |
| Fashion United | Tin tức kinh doanh thời trang |
| Textile World | Công nghệ dệt may |
| Fibre2Fashion | Chuỗi cung ứng dệt may |

### Giao tiếp (General)
| Nguồn | Mô tả |
|-------|--------|
| BBC Learning English | Bài học theo cấp độ |
| VOA Learning English | Tin tức dễ hiểu |
| Breaking News English | Tin tức chia theo level |
| Simple English News | Bài viết đơn giản |
| News In Levels | Tin tức 3 cấp độ |

## 🤖 Tích hợp Gemini AI (Tùy chọn)

Thêm API key vào `.env` để kích hoạt:
- Tóm tắt bài viết 2 câu
- Trích xuất 3 từ vựng quan trọng + nghĩa Việt
- Gợi ý keyword then chốt

Lấy API key miễn phí: https://aistudio.google.com/apikey

## 📅 Lịch học đề xuất

| Thời gian | Nội dung | Mục tiêu |
|-----------|----------|----------|
| ☀️ 6:30 sáng | 3 bài Giao tiếp | Đọc nhẹ cùng cafe |
| 🌙 5:30 chiều | 3 bài Chuyên ngành | Thuật ngữ kỹ thuật |

## 📁 Cấu trúc dự án

```
crawl_data/
├── main.py              # Entry point + scheduler
├── config.py            # Cấu hình RSS feeds & settings
├── crawler.py           # RSS feed crawler
├── ai_processor.py      # Gemini AI processor
├── email_sender.py      # Email composer & sender
├── templates/
│   └── email_template.html  # HTML email template
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```
