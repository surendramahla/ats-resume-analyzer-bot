import os
import google.generativeai as genai
import fitz  # PyMuPDF
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from docx import Document

# --- CONFIGURATION ---
# Replace with your actual keys
TELEGRAM_TOKEN = "Insert Telegram Token"
GEMINI_KEY = "Insert Gemini Api Key"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- UTILITY FUNCTIONS ---

def extract_text(file_path):
    """Extracts text from PDF or DOCX files."""
    if file_path.endswith('.docx'):
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file_path.endswith('.pdf'):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    return ""

# --- CORE BOT LOGIC ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resets the session and starts the flow."""
    context.user_data.clear()
    await update.message.reply_text(
        "🚀 **AI Resume Architect v3.0 (Industry Edition)**\n\n"
        "I will analyze your resume, give you a match score, and then rewrite it to match the JD perfectly.\n\n"
        "📥 **Step 1:** Please upload your **Resume** (PDF or DOCX)."
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles Resume and JD file uploads."""
    file = await update.message.document.get_file()
    chat_id = update.message.chat_id
    
    if 'resume_text' not in context.user_data:
        # Saving the Resume
        ext = ".pdf" if "pdf" in update.message.document.mime_type else ".docx"
        path = f"res_{chat_id}{ext}"
        await file.download_to_drive(path)
        
        context.user_data['resume_text'] = extract_text(path)
        context.user_data['resume_name'] = update.message.document.file_name
        os.remove(path) # Clean up local storage
        
        await update.message.reply_text("✅ Resume parsed! \n\n📥 **Step 2:** Now upload the **Job Description (JD)** PDF or paste the text.")
    else:
        # Saving the JD
        path = f"jd_{chat_id}.pdf"
        await file.download_to_drive(path)
        context.user_data['jd_text'] = extract_text(path)
        os.remove(path)
        await run_initial_analysis(update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles JD text input or follow-up chat questions."""
    if 'resume_text' in context.user_data and 'jd_text' not in context.user_data:
        # User pasted JD text
        context.user_data['jd_text'] = update.message.text
        await run_initial_analysis(update, context)
    
    elif 'resume_text' in context.user_data and 'jd_text' in context.user_data:
        # User is asking a follow-up question (Chat Mode)
        await chat_with_consultant(update, context)
    else:
        await update.message.reply_text("❌ Please upload your resume first using /start.")

async def run_initial_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Performs the ATS scoring and gap analysis."""
    status_msg = await update.message.reply_text("🔎 **Scanning for Match...**")
    
    prompt = f"""
    You are a Senior Technical Recruiter. Compare this Resume and JD.
    
    1. Calculate a MATCH SCORE (0-100%). Be generous with transferable skills.
    2. Provide a 3-sentence EXECUTIVE SUMMARY of the candidate's fit.
    3. List the top 3 MISSING KEYWORDS.

    Resume: {context.user_data['resume_text'][:2500]}
    JD: {context.user_data['jd_text'][:1500]}
    """
    
    try:
        response = model.generate_content(prompt)
        context.user_data['analysis'] = response.text
        
        # UI Buttons
        keyboard = [
            [InlineKeyboardButton("✨ Rewrite & Download Resume", callback_data='generate')],
            [InlineKeyboardButton("💬 Ask Advice / Questions", callback_data='chat')]
        ]
        
        await status_msg.edit_text(
            f"📊 **ATS Alignment Report**\n\n{response.text}\n\n**What would you like to do next?**",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Analysis Error: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button clicks for Generation or Chat."""
    query = update.callback_query
    # Answer immediately to prevent "Query is too old" error
    await query.answer()

    if query.data == 'generate':
        await query.edit_message_text("🛠️ **Optimizing your Resume...** \nInjecting JD keywords and improving action verbs.")
        
        rewrite_prompt = f"""
        Act as a Resume Writing Expert. Rewrite the Resume to match the JD provided below.
        Goal: Achieve a 95% ATS match score.
        
        - Inject missing keywords naturally into the Skills and Experience sections.
        - Use the STAR method (Situation, Task, Action, Result) for bullets.
        - Ensure the 'Professional Summary' is tailored to the specific role.

        JD: {context.user_data['jd_text']}
        Resume: {context.user_data['resume_text']}
        """
        
        try:
            response = model.generate_content(rewrite_prompt).text
            
            # Generate the File
            doc = Document()
            doc.add_heading('Tailored Professional Resume', 0)
            doc.add_paragraph(response)
            
            out_path = f"Optimized_CV_{update.effective_chat.id}.docx"
            doc.save(out_path)
            
            await context.bot.send_document(
                chat_id=update.effective_chat.id, 
                document=open(out_path, "rb"),
                caption="✅ Your ATS-optimized resume is ready!"
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="You can now ask me questions like: 'Why did you add [Skill]?' or 'How should I prepare for this interview?'"
            )
        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Error generating file: {e}")

    elif query.data == 'chat':
        await query.edit_message_text("💬 **Consultant Mode Active.** \nGo ahead and ask me anything about the job or your resume improvements.")

async def chat_with_consultant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles interactive follow-up questions."""
    user_query = update.message.text
    
    # Maintain context for the AI
    chat_prompt = f"""
    Context: You are helping a candidate apply for a specific JD with their Resume.
    JD: {context.user_data['jd_text'][:500]}
    Candidate Question: {user_query}
    
    Provide a helpful, industry-expert response.
    """
    
    try:
        response = model.generate_content(chat_prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Chat Error: {e}")

# --- MAIN EXECUTION ---

if __name__ == '__main__':
    print("Initializing Industry-Level Bot...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🚀 Bot is LIVE. Press Ctrl+C to stop.")
    app.run_polling()
