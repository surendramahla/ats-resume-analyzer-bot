import discord
from discord.ext import commands
import google.generativeai as genai
import os
import fitz  # PyMuPDF
from docx import Document
import google.api_core.exceptions

# --- CONFIG ---
DISCORD_TOKEN = "Insert Discord Token"
GEMINI_KEY = "Insert Gemini Api Key"

# Switching to 1.5-Flash for HIGH QUOTA (1500 requests/day)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

user_sessions = {}

# --- UI: PERSISTENT END SESSION BUTTON ---

class PersistentView(discord.ui.View):
    def __init__(self, uid):
        super().__init__(timeout=None)
        self.uid = uid

    @discord.ui.button(label="🏁 End Session & Clear Data", style=discord.ButtonStyle.danger)
    async def end_chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.uid:
            return await interaction.response.send_message("This isn't your session!", ephemeral=True)
        
        if self.uid in user_sessions:
            del user_sessions[self.uid]
            await interaction.response.send_message("🔒 **Session Terminated.** All data has been wiped.")
        else:
            await interaction.response.send_message("No active session found.", ephemeral=True)

# --- UTILS ---

def extract_text(file_path):
    try:
        if file_path.endswith('.docx'):
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        elif file_path.endswith('.pdf'):
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text
    except Exception as e:
        print(f"Extraction Error: {e}")
    return ""

async def send_smart_msg(channel, text, uid, extra_view=None):
    """Splits long text and attaches the End Session button."""
    chunks = [text[i:i+1900] for i in range(0, len(text), 1900)]
    view = PersistentView(uid)
    if extra_view:
        for item in extra_view.children:
            view.add_item(item)

    for i, chunk in enumerate(chunks):
        if i == len(chunks) - 1:
            await channel.send(chunk, view=view)
        else:
            await channel.send(chunk)

# --- BOT LOGIC ---

@bot.command()
async def analyze(ctx):
    user_sessions[ctx.author.id] = {
        "chat": model.start_chat(history=[]),
        "resume_text": None,
        "jd_text": None,
        "word_count": 0,
        "state": "WAITING_RESUME"
    }
    await ctx.send("👋 **AI Consultant Online.** Please upload your **Resume (PDF/DOCX)**.", view=PersistentView(ctx.author.id))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    uid = message.author.id
    if uid not in user_sessions:
        await bot.process_commands(message)
        return

    session = user_sessions[uid]

    try:
        # 1. RESUME STEP
        if session["state"] == "WAITING_RESUME" and message.attachments:
            attachment = message.attachments[0]
            path = f"res_{uid}.{attachment.filename.split('.')[-1]}"
            await attachment.save(path)
            session["resume_text"] = extract_text(path)
            session["word_count"] = len(session["resume_text"].split())
            os.remove(path)
            session["state"] = "WAITING_JD"
            await message.channel.send("✅ Resume saved. Now paste/upload the **Job Description (JD)**.", view=PersistentView(uid))
            return

        # 2. JD & ANALYSIS STEP
        elif session["state"] == "WAITING_JD":
            if message.attachments:
                attachment = message.attachments[0]
                path = f"jd_{uid}.pdf"
                await attachment.save(path)
                session["jd_text"] = extract_text(path)
                os.remove(path)
            else:
                session["jd_text"] = message.content

            await message.channel.send("🔎 **Analyzing your fit...**")
            prompt = f"Analyze Resume vs JD. Give Match Score % and 3 key gaps. \nResume: {session['resume_text'][:1500]}\nJD: {session['jd_text'][:1000]}"
            response = session["chat"].send_message(prompt)
            
            # Setup the Rewrite Button
            extra_view = discord.ui.View()
            btn_rewrite = discord.ui.Button(label="✨ Optimize CV", style=discord.ButtonStyle.green)
            
            async def rewrite_cb(interaction):
                if interaction.user.id != uid: return
                await interaction.response.send_message("🛠️ Rebuilding your CV layout...")
                rewrite_prompt = f"Rewrite resume to match JD perfectly. Stay under {session['word_count']} words."
                cv_res = session["chat"].send_message(rewrite_prompt).text
                doc = Document(); doc.add_heading('Tailored CV', 0); doc.add_paragraph(cv_res)
                out = f"CV_{uid}.docx"; doc.save(out)
                await interaction.channel.send(file=discord.File(out))
                os.remove(out)

            btn_rewrite.callback = rewrite_cb
            extra_view.add_item(btn_rewrite)

            session["state"] = "CHAT_MODE"
            await send_smart_msg(message.channel, response.text, uid, extra_view=extra_view)
            return

        # 3. INTERACTIVE CHAT MODE
        elif session["state"] == "CHAT_MODE":
            async with message.channel.typing():
                response = session["chat"].send_message(message.content)
                await send_smart_msg(message.channel, response.text, uid)

    except google.api_core.exceptions.ResourceExhausted:
        await message.channel.send("🚨 **API Quota Limit Reached.** Please wait 60 seconds or use a new key.", view=PersistentView(uid))
    except Exception as e:
        await message.channel.send(f"❌ **Error:** {e}", view=PersistentView(uid))

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)