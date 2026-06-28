# handlers/signal.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from config import SYMBOLS
from handlers.menu import start_command, get_back_to_main_keyboard
from utils.predictor import PBXForecastingEngine

# State machine indicators
GET_ASSET, GET_TIMEFRAME, GET_CAPITAL = range(3)

async def initiate_signal_workflow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: Solicits target coin ticker choice."""
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        "🎯 *PBX Algorithmic Predictor Channel Engaged.*\n\n"
        "Please type your target cryptocurrency symbol (e.g., BTC-USD, ETH-USD, SOL-USD):",
        parse_mode="Markdown"
    )
    return GET_ASSET

async def catch_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Validates token choice, then maps custom inline keyboard intervals."""
    asset_input = update.message.text.upper().strip()
    if asset_input not in SYMBOLS:
        await update.message.reply_text(
            "❌ *Asset Ticker Not Supported or Missing.* Please supply a valid currency representation (e.g., BTC-USD):",
            parse_mode="Markdown"
        )
        return GET_ASSET
        
    context.user_data['signal_asset'] = asset_input
    
    tf_kb = [
        [InlineKeyboardButton("1 Hour (1H)", callback_data="tf_1"), InlineKeyboardButton("4 Hours (4H)", callback_data="tf_2")],
        [InlineKeyboardButton("12 Hours (12H)", callback_data="tf_3"), InlineKeyboardButton("24 Hours (24H)", callback_data="tf_4")],
        [InlineKeyboardButton("❌ Abort Operational Pipeline", callback_data="abort_signal")]
    ]
    await update.message.reply_text(
        f"📊 *Asset Registered:* {asset_input}\n\nSelect your targeted forecasting timeframe window horizon:",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(tf_kb)
    )
    return GET_TIMEFRAME

async def catch_timeframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes horizon button selection, asks user for account capital."""
    query = update.callback_query
    await query.answer()
    
    choice_mapping = {"tf_1": "1", "tf_2": "2", "tf_3": "3", "tf_4": "4"}
    key = choice_mapping.get(query.data)
    context.user_data['signal_tf_key'] = key
    
    # Check for backtest vulnerability warnings directly from our strategy maps
    symbol = context.user_data['signal_asset']
    warning_msg = PBXForecastingEngine.check_performance_warning(symbol, key)
    
    await query.message.edit_text(
        f"{warning_msg}⏳ *Operational Horizon Stored.*\n\nPlease input your trade portfolio size configuration (Capital in USD, e.g., 5000):",
        parse_mode="Markdown"
    )
    return GET_CAPITAL

async def catch_capital_and_compute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculates forecasting metrics on async loops, displays visual metrics interface."""
    try:
        capital = float(update.message.text.strip())
        if capital <= 0: raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ *Invalid Capital Format.* Please submit a positive numerical valuation:")
        return GET_CAPITAL

    symbol = context.user_data.get('signal_asset')
    choice_key = context.user_data.get('signal_tf_key')
    
    loading_prompt = await update.message.reply_text(
        "⚡ *Request Authenticated.*\n\n"
        "⏳ *Please wait approximately 1 minute.* The XGBoost core forecasting model is retrieving active Binance "
        "historical data matrices and validating feature array calculations...",
        parse_mode="Markdown"
    )
    
    try:
        # Run inference using the modular predictor pipeline
        res = await PBXForecastingEngine.run_inference(symbol, choice_key, capital)
        
        # Build graphical confidence chart representation
        bar_len = int(res['ai_confidence'] / 2)
        visual_bar = '█' * bar_len + '░' * (50 - bar_len)
        
        output_ui = (
            f"===== *PRO TRADING AI EVALUATION* =====\n\n"
            f"🪙 *Target Coin:* {res['symbol']}\n"
            f"💵 *Current Spot Price:* {res['current_price']:.4f}\n"
            f"🔗 *BTC Correlation Factor:* {res['dep']}%\n\n"
            f"📊 *Market Trend State:* {res['trend']}\n"
            f"🟢 *Local Support Layer:* {res['support']:.4f}\n"
            f"🔴 *Local Resistance Layer:* {res['resistance']:.4f}\n\n"
            f"🎯 *Projected Base Value ({res['selected_timeframe']}):* {res['prediction_price']:.4f}\n"
            f"📈 *Estimated Delta Move:* {res['real_percent']:.2f}%\n"
            f"📦 *Volume Node Capacity:* {'HIGH 📈' if res['high_volume'] else 'NORMAL'}\n\n"
            f"⚡ *Core Directive Signal:* {res['signal']}\n\n"
        )
        
        if res['stop_loss']:
            output_ui += (
                f"💰 *Algorithmic Risk Management:*\n"
                f"   • Stop Loss (SL): {res['stop_loss']:.4f} ({res['sl_pct']:.2f}%)\n"
                f"   • Take Profit (TP): {res['take_profit']:.4f} ({res['tp_pct']:.2f}%)\n"
                f"   • Risk/Reward Ratio: {res['risk_reward']:.2f}\n"
                f"   • Position Volume sizing: {res['position_size']:.2f} units (~${res['allocated_cost']:.0f})\n\n"
            )
            
        output_ui += (
            f"📈 *Optimal Accumulation Zone:* {res['support']:.4f} - {res['support']*1.002:.4f}\n"
            f"📉 *Optimal Distribution Zone:* {res['resistance']*0.998:.4f} - {res['resistance']:.4f}\n\n"
            f"🔥 *AI Target Confidence Scale:*\n[{visual_bar}] {res['ai_confidence']}%\n\n"
            f"==================================\n"
            f"📌 *FINAL REVENUE RECOMMENDATION:* {res['signal']}\n"
            f"=================================="
        )
        
        await loading_prompt.delete()
        await update.message.reply_text(output_ui, parse_mode="Markdown", reply_markup=get_back_to_main_keyboard())
        
    except Exception as e:
        await loading_prompt.edit_text(f"❌ *Inference Pipeline Error:* {str(e)}", parse_mode="Markdown", reply_markup=get_back_to_main_keyboard())
        
    return ConversationHandler.END

async def abort_workflow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Graceful breakdown for open conversation handlers."""
    query = update.callback_query
    await query.answer()
    await query.message.edit_text("❌ *Prediction query cancelled.*")
    await start_command(update, context)
    return ConversationHandler.END

