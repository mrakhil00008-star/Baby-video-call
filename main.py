import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# Railway Variables
BOT_TOKEN = '8890969566:AAFS7CF97zSRnNDOW_PyggG5_c3oiqF4SPk'
OPENAI_API_KEY =os.getenv('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')

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are Aisha, a fictional AI companion.

Rules:
- You are an AI assistant, not a real human.
- Reply in Hindi/Hinglish.
- Be friendly, warm and playful.
- Keep replies natural and short.
- Do not claim to be a real girlfriend.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hii! Main Aisha hoon, ek AI companion.\n\nKaise ho? 😊"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text

        response = client.responses.create(
            model="gpt-5.5",
            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
        )

        await update.message.reply_text(response.output_text)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )

    print("Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
