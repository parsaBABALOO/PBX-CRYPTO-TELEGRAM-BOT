# handlers/info.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.menu import get_back_to_main_keyboard

async def handle_info_routes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Orchestrates query resolution targets for dashboard, support, and main cv."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "menu_dashboard":
        dashboard_text = (
            "📊 *PBX Live Advanced Crypto Interactive Dashboard (Streamlit)*\n\n"
            "👑 *Dear Premium User*, you can audit real-time predictions, market structure metrics, "
            "and our modern 50-cryptocurrency watchlist interactively via our primary dashboard.\n\n"
            "🔗 *Interactive Web Console:* [Access Live Dashboard](https://pbx-crypto.streamlit.app/)\n"
            "🔑 *Temporary Access Panel Token:* PBXvip9045592026"
        )
        await query.message.edit_text(dashboard_text, parse_mode="Markdown", reply_markup=get_back_to_main_keyboard())
        
    elif query.data == "menu_support":
        support_text = (
            "📞 *PBX Engine Core Technical Support*\n\n"
            "If you experience runtime errors, connection exceptions, or wish to deploy custom quantitative "
            "pipelines, communicate directly with our engineering desk:\n\n"
            "👤 *Technical Administrator ID:* @PBXCRYPTO"
        )
        await query.message.edit_text(support_text, parse_mode="Markdown", reply_markup=get_back_to_main_keyboard())
        
    elif query.data == "menu_resume":
        resume_menu = (
            "📜 *PBX Portfolio Repository Directories*\n\n"
            "Please select a sub-classification to review technical metrics or creator profiles:"
        )
        keyboard = [
            [InlineKeyboardButton("🤖 Bot Specifications & Backtest", callback_data="resume_bot")],
            [InlineKeyboardButton("👨‍💻 System Architect CV", callback_data="resume_dev")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
        ]
        await query.message.edit_text(resume_menu, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_resume_submenus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Routes specific inner repository profiles."""
    query = update.callback_query
    await query.answer()
    
    back_to_resume_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Resume Options", callback_data="menu_resume")]])
    
    if query.data == "resume_bot":
        bot_text = (
            "🤖 *PBX Bot Specifications & Core Metrics*\n\n"
            "💻 *Open Source Repository:* [GitHub Repository Link](https://github.com/parsaBABALOO/PBX-Crypto-Forecasting-Engine)\n"
            "📜 *Project Software License:* MIT License\n\n"
            "📊 *Empirical Backtest Metrics (Historical Performance):*\n"
            "• 🎯 *Predictive Win Rate:* 63% - 67%\n"
            "• 📈 *Practice Framework Total Return:* +289% Cumulative Yield\n\n"
            "💡 *Architecture Overview:* This intelligence framework operates utilizing regularized multi-horizon "
            "XGBoost ensemble classifiers calculating 10+ mathematical technical indicators concurrently."
        )
        await query.message.edit_text(bot_text, parse_mode="Markdown", reply_markup=back_to_resume_keyboard)
        
    elif query.data == "resume_dev":
        dev_text = (
            "👨‍💻 *PBX Lead Developer Profile Summary*\n\n"
            "Track engineering backgrounds, architectural designs, and core repository additions via professional channels:\n\n"
            "🔗 *GitHub Web Profile:* [GitHub Profile](https://github.com/parsaBABALOO)\n"
            "💼 *LinkedIn Professional Network:* [LinkedIn Profile](www.linkedin.com/in/parsa-babaloo)\n\n""📬 For algorithmic expansion proposals, contact @PBXCRYPTO."
        )
        await query.message.edit_text(dev_text, parse_mode="Markdown", reply_markup=back_to_resume_keyboard)


