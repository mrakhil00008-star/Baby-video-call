from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler, ContextTypes
)
import os, json, time, random

# --- CONFIG ---
ADMIN_ID = 8310700441
TOKEN = os.getenv("BOT_TOKEN")

QR_FILE_ID = "AgACAgUAAxkBAAIBXmpR9KfCaoBPQGCf6__yKGftuAQPAAIcF2sb4VyRVjreUTcE5T58AQADAgADeQADPAQ"

START_VOICE = "AwACAgUAAxkBAAIBXGpR9JRt1KKh6KJ120NGB03Mf5tKAAJvIQAC4CD4VPDBIV_k516xPAQ"
DEMO_VOICE = "AwACAgUAAxkBAAIBYGpR9PWgrbo_7hDMtosZqAolfeJKAAJzIQAC4CD4VJ0O2PDKNJc6PAQ"

PROOF_LINK = "https://t.me/+VI2W3dDjCERmNTM1"
OWNER_USERNAME = "@MSSOFIYA64562"

PLAN_SELECTION, PAYMENT_SENDING = range(2)

# --- USERS ---
try:
    with open("paid_users.json", "r") as f:
        PAID_USERS = set(json.load(f))
except:
    PAID_USERS = set()

def save_users():
    with open("paid_users.json", "w") as f:
        json.dump(list(PAID_USERS), f)

# --- AUTO FLOW STORAGE ---
LAST_ACTIVITY = {}

FOLLOW_MESSAGES = [
    "💋 Baby kaha ho? 😘 Interested ho na?",
    "🔥 Jaldi karo baby limited time hai 😍",
    "😏 Demo dekhoge to maza aa jayega baby",
    "💖 Payment karo aur full enjoy karo 😘",
    "👀 Wait mat karo baby, abhi join karo",
    "💞 Main wait kar rahi hu baby 😘"
]

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    LAST_ACTIVITY[user_id] = time.time()

    if user_id in PAID_USERS:
        await update.message.reply_text("✅ Welcome back! Access granted.")
        return

    keyboard = [
        [InlineKeyboardButton("📞 Video Call", callback_data='open_menu')],
        [InlineKeyboardButton("📂 Video Call Proof", url=PROOF_LINK)]
    ]

    await update.message.reply_voice(voice=START_VOICE)

    await update.message.reply_text(
        "💋 Baby video call ke liye niche click karo",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- OPEN MENU ---
async def open_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.message.chat_id
    LAST_ACTIVITY[user_id] = time.time()

    keyboard = [
        [InlineKeyboardButton("📞 Demo - ₹20", callback_data='pay_20')],
        [InlineKeyboardButton("📞 5 Min - ₹50", callback_data='pay_50')],
        [InlineKeyboardButton("📞 10 Min - ₹100", callback_data='pay_100')],
        [InlineKeyboardButton("📞 20 Min - ₹200", callback_data='pay_200')],
        [InlineKeyboardButton("📞 30 Min - ₹300", callback_data='pay_300')],
    ]

    await query.message.reply_text(
        "📞 Select your Video Call Plan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return PLAN_SELECTION

# --- PLAN CLICK ---
async def show_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.message.chat_id
    LAST_ACTIVITY[user_id] = time.time()

    data = query.data

    if data == "pay_20":
        await query.message.reply_voice(voice=DEMO_VOICE)
    else:
        await query.message.reply_voice(voice=START_VOICE)

    await query.message.reply_photo(
        photo=QR_FILE_ID,
        caption="💳 Payment karo aur screenshot bhejo"
    )

    return PAYMENT_SENDING

# --- PAYMENT ---
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    LAST_ACTIVITY[user_id] = time.time()

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

    await update.message.reply_text("⏳ wait baby main payment check karti hu..")

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
            text=(
                "✅ Payment verified!\n\n"
                "💋 Madam ko message karo aur video call karo 😘\n\n"
                f"👉 Telegram ID: {OWNER_USERNAME}\n\n"
                "🔥 Enjoy karo baby 💕"
            )
        )

        await query.edit_message_text("✅ Approved")

    else:
        if user_id in PAID_USERS:
            PAID_USERS.remove(user_id)
            save_users()

        await context.bot.send_voice(chat_id=user_id, voice=DEMO_VOICE)

        await context.bot.send_photo(
            chat_id=user_id,
            photo=QR_FILE_ID,
            caption="❌ Payment failed.\n\n💳 Dubara payment karo"
        )

        await query.edit_message_text("❌ Rejected")

# --- AUTO FOLLOW SYSTEM ---
async def auto_follow(context: ContextTypes.DEFAULT_TYPE):
    now = time.time()

    for user_id in LAST_ACTIVITY:
        if user_id in PAID_USERS:
            continue

        # 60 sec idle
        if now - LAST_ACTIVITY[user_id] > 60:
            msg = random.choice(FOLLOW_MESSAGES)

            await context.bot.send_message(
                chat_id=user_id,
                text=msg
            )

            LAST_ACTIVITY[user_id] = now  # reset timer

# --- MAIN ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(open_menu, pattern='open_menu')],
        states={
            PLAN_SELECTION: [
                CallbackQueryHandler(show_qr, pattern='^pay_')
            ],
            PAYMENT_SENDING: [
                MessageHandler(filters.ALL, handle_payment)
            ],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(admin_response, pattern='^(approve|reject)_'))

    # 🔥 AUTO FLOW JOB
    app.job_queue.run_repeating(auto_follow, interval=30, first=30)

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
