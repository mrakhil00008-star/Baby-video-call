from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler, ContextTypes
)
import os

# --- CONFIG ---
ADMIN_ID = 8310700441
TOKEN = os.getenv("BOT_TOKEN")

QR_FILE_ID = "AgACAgUAAxkBAAIBXmpR9KfCaoBPQGCf6__yKGftuAQPAAIcF2sb4VyRVjreUTcE5T58AQADAgADeQADPAQ"
VOICE_ID = "AwACAgUAAxkBAAIBXGpR9JRt1KKh6KJ120NGB03Mf5tKAAJvIQAC4CD4VPDBIV_k516xPAQ"

PLAN_SELECTION, PAYMENT_SENDING = range(2)

# 🔐 Paid users list
PAID_USERS = set()

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    # अगर already paid है
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

    # Demo → voice
    if data == "pay_20":
        await query.message.reply_voice(voice=VOICE_ID)

    # QR sab ke liye
    await query.message.reply_photo(
        photo=QR_FILE_ID,
        caption="💳 Payment karo aur screenshot bhejo"
    )

    return PAYMENT_SENDING

# --- PAYMENT PROOF ---
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    # Forward admin ko
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

# --- ADMIN RESPONSE ---
async def admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = int(data.split("_")[1])

    if data.startswith("approve"):
        PAID_USERS.add(user_id)

        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Payment verified! nude video call Enjoy 💋"
        )
        await query.edit_message_text("✅ Approved")

    else:
        if user_id in PAID_USERS:
            PAID_USERS.remove(user_id)
        await update.message.reply_text("✅ Welcome back! Access granted.")
        return

    keyboard = [
        [InlineKeyboardButton("📞 Demo - ₹20", callback_data='pay_20')],
        [InlineKeyboardButton("📞 5 Min - ₹50", callback_data='pay_50')],
        [InlineKeyboardButton("📞 10 Min - ₹100", callback_data='pay_100')],
        [InlineKeyboardButton("📞 20 Min - ₹200", callback_data='pay_200')],
        [InlineKeyboardButton("📞 30 Min - ₹300", callback_data='pay_300')],
    ]
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ video call krna hai to sahi se baby 🫦💋 kro na baby ful enjoy milega."
        )
        await context.bot.send_photo(
            chat_id=user_id,
            photo=QR_FILE_ID,
            caption="💳 Dobara payment karo"
        )
        await query.edit_message_text("❌ Rejected")

# --- FORCE PAYMENT ---
async def force_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.chat_id

    # अगर paid नहीं है
    if user_id not in PAID_USERS:
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

    # ⚠️ LAST handler (important)
    app.add_handler(MessageHandler(filters.ALL, force_payment))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
