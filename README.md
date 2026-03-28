# ATS Resume Analyzer Bot 🤖

An AI-powered ATS (Applicant Tracking System) Resume Analyzer Bot built with **Google Gemini**, available across multiple platforms:

- 🤖 **Telegram Bot** — Upload your resume + JD and get instant ATS analysis
- 💬 **Discord Bot** — Analyze resumes directly in your Discord server
- 📱 **WhatsApp Bot** — Resume analysis via WhatsApp (Flask + Twilio)

---

## Features

- 📄 Upload resume (PDF) and job description (PDF or text)
- 📊 ATS compatibility score with match percentage
- ✅ Missing keywords detection
- 💡 AI-powered resume improvement suggestions
- 📝 Generates an optimized resume document (`.docx`)
- 🚀 Powered by **Google Gemini 2.5 Flash**

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/surendramahla/ats-resume-analyzer-bot.git
cd ats-resume-analyzer-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API keys

#### Telegram Bot (`bot.py`)
```python
TELEGRAM_TOKEN = "Your Telegram Bot Token"
GEMINI_KEY = "Your Gemini API Key"
```

#### Discord Bot (`discord_bot.py`)
Update the token and Gemini key inside `discord_bot.py`.

#### WhatsApp Bot (`whatsapp_bot.py`)
```python
genai.configure(api_key="Your Gemini API Key")
```

### 4. Run the bot

```bash
# Telegram
python bot.py

# Discord
python discord_bot.py

# WhatsApp (Flask server)
python whatsapp_bot.py
```

---

## Requirements

- Python 3.9+
- `google-generativeai`
- `python-telegram-bot`
- `discord.py`
- `flask`
- `PyPDF2` or `pdfplumber`
- `python-docx`

---

## Deployment

The bots can be deployed on platforms like **Render**, **Railway**, or **Heroku**.

---

## License

MIT License
