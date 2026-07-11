from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler, ContextTypes
)
import os

ADMIN_ID = 8310700441
TOKEN = os.getenv("BOT_TOKEN")

MAIN_MENU, PLAN_SELECTION, PAYMENT_SENDING = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📞 Video Call", callback_data='video_call')]]
    await update.message.reply_text(
        "Welcome! Click below to see plans:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU

async def video_call_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("₹20 Demo", callback_data='pay_20')],
        [InlineKeyboardButton("₹50 - 5 Min", callback_data='pay_50')],
        [InlineKeyboardButton("⬅ Back", callback_data='back')]
    ]

    await query.edit_message_text(
        "Select Plan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PLAN_SELECTION

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("📞 Video Call", callback_data='video_call')]]

    await query.edit_message_text(
        "Welcome back!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU

async def show_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text("Payment karo aur screenshot bhejo.")
    return PAYMENT_SENDING

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Payment received from {update.message.from_user.first_name}"
    )

    return PAYMENT_SENDING

async def admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [CallbackQueryHandler(video_call_menu, pattern='video_call')],
            PLAN_SELECTION: [
                CallbackQueryHandler(show_qr, pattern='pay_'),
                CallbackQueryHandler(back_to_main, pattern='back')
            ],
            PAYMENT_SENDING: [MessageHandler(filters.ALL, handle_payment)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(conv)

    print("Bot running...")
    app.run_polling()
