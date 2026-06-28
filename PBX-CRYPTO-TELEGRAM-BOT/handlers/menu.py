# handlers/menu.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

def get_main_menu_keyboard():
    """Builds the beautifully colored master matrix keyboard."""
    keyboard = [
        [InlineKeyboardButton("🎯 Get AI Signal", callback_data="menu_signal")],
        [InlineKeyboardButton("📊 Live Dashboard", callback_data="menu_dashboard")],
        [InlineKeyboardButton("📜 Resume & Portfolio", callback_data="menu_resume")],
        [InlineKeyboardButton("📞 Technical Support", callback_data="menu_support")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_to_main_keyboard():
    """Standard returns path routing components."""
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deploys welcome prompt to client."""
    welcome_text = (
        "🤖 *Welcome to PBX-Crypto Forecasting Engine Terminal*\n\n"
        "This system interfaces a quantitative machine learning framework "
        "directly into Telegram, fetching live order books and mapping regularized "
        "XGBoost predictions.\n\n"
        "Select your core action module below:"
    )
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

        