# config.py
import os

# Telegram Bot API Token (Populate via environment variables or direct assignment)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "TOKEN(***************)")

# Core Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Structural Timeframe and Interval Mappings from predict(2).py
TIMEFRAME_NAMES = {"1": "1H", "2": "4H", "3": "12H", "4": "24H"}
INTERVAL_MAP = {"1": "5m", "2": "15m", "3": "30m", "4": "1h"}
FUTURE_MAP = {"1": 12, "2": 48, "3": 144, "4": 288}
MODEL_MAP = {
    "1": os.path.join(MODELS_DIR, "xgb_1h.pkl"),
    "2": os.path.join(MODELS_DIR, "xgb_4h.pkl"),
    "3": os.path.join(MODELS_DIR, "xgb_12h.pkl"),
    "4": os.path.join(MODELS_DIR, "xgb_24h.pkl"),
}

# Supported Asset Universe
SYMBOLS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD", "DOGE-USD", "TRX-USD",
    "DOT-USD", "LTC-USD", "BCH-USD", "LINK-USD", "XLM-USD", "ATOM-USD", "ETC-USD", "XMR-USD",
    "HBAR-USD", "ICP-USD", "FIL-USD", "ARB-USD", "OP-USD", "AVAX-USD", "SEI-USD", "NEAR-USD",
    "AAVE-USD", "MKR-USD", "INJ-USD", "RENDER-USD", "FET-USD", "ALGO-USD", "EGLD-USD", "THETA-USD",
    "SAND-USD", "MANA-USD", "AXS-USD", "FLOW-USD", "CHZ-USD", "CRV-USD", "LDO-USD", "SNX-USD",
    "DYDX-USD", "1INCH-USD", "BAT-USD", "ZRX-USD", "ENS-USD", "CAKE-USD", "APE-USD", "SHIB-USD",
    "FLOKI-USD", "BONK-USD", "WIF-USD", "JUP-USD", "PYTH-USD", "TIA-USD", "STRK-USD", "AR-USD",
    "KAS-USD", "RUNE-USD"
]

SYMBOL_MAP = {symbol: idx + 1 for idx, symbol in enumerate(SYMBOLS)}

# Historical Backtest Weak Performance Filters
WEAK_SYMBOLS = {
    "TRX-USD": ["1H"],
    "BNB-USD": ["12H"],
    "SOL-USD": ["12H"]
}

