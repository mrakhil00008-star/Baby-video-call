from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler, ContextTypes
)
import os

# --- CONFIG ---
ADMIN_ID = 8310700441  # अपना admin ID रखो
TOKEN = os.getenv("BOT_TOKEN")  # Railway में environment variable सेट करो

QR_FILE_ID = "AgACAgUAAxkBAAIBXmpR9KfCaoBPQGCf6__yKGftuAQPAAIcF2sb4VyRVjreUTcE5T58AQADAgADeQADPAQ"
VOICE_START_ID = "AwACAgUAAxkBAAIBYGpR9PWgrbo_7hDMtosZqAolfeJKAAJzIQAC4CD4VJ0O2PDKNJc6PAQ"
VOICE_MENU_ID = "AwACAgUAAxkBAAIBYGpR9PWgrbo_7hDMtosZqAolfeJKAAJzIQAC4CD4VJ0O2PDKNJc6PAQ"

MAIN_MENU, PLAN_SELECTION, PAYMENT_SENDING = range(3)

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📞 Video Call", callback_data='video_call')]]

    await update.message.reply_voice(voice=VOICE_START_ID)
    await update.message.reply_text(
        "Welcome! Click below to see plans:\n\nFull open enjoy 💋",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU

# --- MENU ---
async def video_call_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📞 Demo - ₹20", callback_data='pay_20')],
        [InlineKeyboardButton("📞 5 Min - ₹50", callback_data='pay_50')],
        [InlineKeyboardButton("📞 10 Min - ₹100", callback_data='pay_100')],
        [InlineKeyboardButton("📞 20 Min - ₹200", callback_data='pay_200')],
        [InlineKeyboardButton("📞 30 Min - ₹300", callback_data='pay_300')],
        [InlineKeyboardButton("⬅ Back", callback_data='back')]
    ]

    await query.message.reply_voice(voice=VOICE_MENU_ID)
    await query.edit_message_text(
        "📞 Select your Video Call Plan:\n\nFull open enjoy 💋",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PLAN_SELECTION

# --- BACK ---
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("📞 Video Call", callback_data='video_call')]]

    await query.edit_message_text(
        "Welcome back!\n\nSelect option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU

# --- QR ---
async def show_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_photo(
        photo=QR_FILE_ID,
        caption="💳 Scan & Pay\n\nPayment ke baad screenshot bhejo."
    )
    return PAYMENT_SENDING

# --- PAYMENT ---
async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    keyboard = [[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{update.message.chat_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{update.message.chat_id}")
    ]]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"New Payment from {update.message.from_user.first_name}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return PAYMENT_SENDING

# --- ADMIN RESPONSE ---
async def admin_response(update:
