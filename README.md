# 🚀 ATS Resume Analyzer Bot

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![AI Powered](https://img.shields.io/badge/AI-Powered-green)
![Status](https://img.shields.io/badge/Project-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

An AI-powered Resume Analyzer that evaluates resumes against job descriptions, provides ATS scores, suggests improvements, and generates optimized resumes. It also supports WhatsApp and Discord bot integration for easy access.

---

## 🔥 Features

- 📄 Upload Resume (PDF / DOCX / TXT)
- 📑 Upload Job Description
- 📊 ATS Score Calculation (out of 10)
- 🤖 AI-based Resume Suggestions
- 📝 Generate Optimized Resume
- 📥 Download Resume in Multiple Formats
- 💬 WhatsApp Bot Integration
- 🎮 Discord Bot Support

---

## 🛠️ Tech Stack

- Python 🐍
- NLP (Natural Language Processing)
- AI APIs (Gemini / OpenAI)
- Flask (Backend)
- Twilio (WhatsApp API)
- Discord.py

---

## 📂 Project Structure


bot/
│
├── bot.py # Main ATS logic
├── whatsapp_bot.py # WhatsApp integration
├── discord_bot.py # Discord bot
├── template.pdf # Resume template
├── jd_upload.pdf # Sample Job Description
├── AI_Suggestions.docx # AI suggestions output
├── optimized_resume.docx # Generated resume
├── requirements.txt # Dependencies


---

## ⚙️ How It Works

1. Upload your Resume  
2. Upload the Job Description  
3. System analyzes:
   - Keywords match
   - Skills alignment
   - ATS compatibility  
4. Generates:
   - 📊 ATS Score  
   - 🧠 AI Suggestions  
   - 📄 Optimized Resume  

---

## 🔑 API & Token Setup (IMPORTANT)

Before running the project, you must add your API keys and tokens.

### Step 1: Create `.env` file

```bash
touch .env
Step 2: Add the following keys
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
DISCORD_BOT_TOKEN=your_discord_token
Step 3: Load environment variables in Python

Make sure your code includes:

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

⚠️ Never upload your .env file to GitHub.

▶️ Run Locally
git clone https://github.com/yourusername/ats-resume-analyzer-bot.git
cd ats-resume-analyzer-bot

pip install -r requirements.txt
python bot.py
📱 Bot Integration
WhatsApp Bot
python whatsapp_bot.py
Discord Bot
python discord_bot.py
📌 Example Workflow
User sends resume via bot
Bot asks for job description
System processes both files
Returns:
ATS Score
Suggestions
Downloadable optimized resume
🔮 Future Improvements
🌐 Web UI Dashboard
📊 Advanced ATS scoring model
📁 Multiple resume templates
🔍 Real-time job matching
☁️ Deployment (AWS / Vercel / Render)
⚠️ Notes
Keep API keys secure using .env
Avoid uploading sensitive personal data
Clean unnecessary generated files before pushing to GitHub
📄 .gitignore (Recommended)
__pycache__/
.env
*.pyc
*.docx
*.pdf
👨‍💻 Author

Surendra Mahla
BTech (Data Science) Student
Interested in AI, Data Analytics & Development

⭐ Support

If you found this project useful:

⭐ Star this repository
🍴 Fork it
📢 Share with others
📬 Contact

For collaboration or queries, feel free to connect!
