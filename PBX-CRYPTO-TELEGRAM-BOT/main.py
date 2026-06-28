# main.py
import sys
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

# Setup environment path adjustments
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BOT_TOKEN
from handlers.menu import start_command
from handlers.info import handle_info_routes, handle_resume_submenus
from handlers.signal import initiate_signal_workflow, catch_asset, catch_timeframe, catch_capital_and_compute, abort_workflow, GET_ASSET, GET_TIMEFRAME, GET_CAPITAL

def main():
    """Initializes high-level listeners and boots the network interface polling system."""
    if BOT_TOKEN == "**********************":
        print("❌ CRITICAL CONFIG ERROR: Please populate your Telegram Token inside config.py or Environment Variables.")
        return

    # Instantiating the master application agent container
    application = Application.builder().token(BOT_TOKEN).build()

    # Conversation sequence configuration
    signal_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(initiate_signal_workflow, pattern="^menu_signal$")],
        states={
            GET_ASSET: [MessageHandler(filters.TEXT & ~filters.COMMAND, catch_asset)],
            GET_TIMEFRAME: [CallbackQueryHandler(catch_timeframe, pattern="^tf_")],
            GET_CAPITAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, catch_capital_and_compute)]
        },
        fallbacks=[CallbackQueryHandler(abort_workflow, pattern="^abort_signal$")],
        per_message=False
    )

    # Dispatch listener binding trees
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(signal_conv)
    application.add_handler(CallbackQueryHandler(handle_info_routes, pattern="^menu_(dashboard|support|resume)$"))
    application.add_handler(CallbackQueryHandler(handle_resume_submenus, pattern="^resume_"))
    application.add_handler(CallbackQueryHandler(start_command, pattern="^back_to_main$"))

    # Deploy loops
    print("🚀 PBX Algorithmic Telegram Bot Engine Online and Polling live streams...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()