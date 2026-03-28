from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import os

# --- CONFIG ---
genai.configure(api_key="Insert Gemini Api Key")
model = genai.GenerativeModel('gemini-2.5-flash')
app = Flask(__name__)

# User Memory (Stores if they sent Resume or JD)
user_state = {}

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '')
    sender = request.values.get('From')
    
    resp = MessagingResponse()
    msg = resp.message()

    if sender not in user_state:
        user_state[sender] = {"step": "resume"}
        msg.body("👔 *AI Resume Architect*\nPlease paste your **Resume text** to start.")
    
    elif user_state[sender]["step"] == "resume":
        user_state[sender]["resume"] = incoming_msg
        user_state[sender]["step"] = "jd"
        msg.body("✅ Resume saved! Now paste the **Job Description (JD)** text.")
        
    elif user_state[sender]["step"] == "jd":
        # AI Analysis
        prompt = f"Analyze Resume: {user_state[sender]['resume']} vs JD: {incoming_msg}. Give Score % and 3 tips."
        ai_res = model.generate_content(prompt).text
        
        msg.body(f"📊 *ATS Analysis:*\n\n{ai_res}\n\n*Type anything to restart or 'Done' to exit.*")
        del user_state[sender] # Clear session

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)