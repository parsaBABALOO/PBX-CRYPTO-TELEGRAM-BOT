# utils/predictor.py
import time
import joblib
import pandas as pd
import asyncio
from config import MODEL_MAP, INTERVAL_MAP, TIMEFRAME_NAMES, SYMBOL_MAP, WEAK_SYMBOLS
from utils.binance_data import get_binance_data
from indicators.indicators import add_indicators
from utils.dependency import get_btc_dependency

class PBXForecastingEngine:
    """Wrapper encapsulating ML weights inference and risk parameters extraction."""
    
    @staticmethod
    def check_performance_warning(symbol: str, choice_key: str) -> str:
        """Evaluates backtest weak configurations."""
        selected_tf = TIMEFRAME_NAMES.get(choice_key, "1H")
        if symbol in WEAK_SYMBOLS and selected_tf in WEAK_SYMBOLS[symbol]:
            return f"⚠️ WARNING: {symbol} on {selected_tf} yielded suboptimal metrics in backtests. Exercise caution.\n\n"
        return ""

    @staticmethod
    async def run_inference(symbol: str, choice_key: str, capital: float) -> dict:
        """Executes full data ingestion, indicator synthesis, and gradient-boosting prediction."""
        # Non-blocking execution of CPU-heavy pipeline using asyncio thread pool
        return await asyncio.to_thread(PBXForecastingEngine._sync_inference, symbol, choice_key, capital)

    @staticmethod
    def _sync_inference(symbol: str, choice_key: str, capital: float) -> dict:
        model_path = MODEL_MAP.get(choice_key)
        interval = INTERVAL_MAP.get(choice_key, "5m")
        selected_timeframe = TIMEFRAME_NAMES.get(choice_key, "1H")
        
        if interval == "5m": period = "7d"
        elif interval == "15m": period = "30d"
        elif interval == "30m": period = "60d"
        else: period = "90d"

        # 1. Fetch market matrix
        df = get_binance_data(symbol=symbol, interval=interval, limit=300, period=period)
        if df.empty:
            raise ValueError("Empty dataset returned from Ingestion API.")

        last_time = int(time.time())

        # 2. Extract quantitative indicators
        df = add_indicators(df)
        df.dropna(inplace=True)
        latest = df.iloc[-1]
        
        # 3. Align high-dimensional feature array
        symbol_id = SYMBOL_MAP.get(symbol, 1)
        features = [[
            symbol_id, latest['close'], latest['volume'], latest['rsi'], latest['macd'],
            latest['macd_signal'], latest['ema_20'], latest['sma_20'], latest['bb_high'],
            latest['bb_low'], latest['high'], latest['low'], latest['atr'], latest['stoch_rsi'], latest['momentum']
        ]]

        # 4. Perform regularized model estimation
        model = joblib.load(model_path)
        pred_percent = float(model.predict(features)[0])
        pred_percent = max(min(pred_percent, 5), -5) # Bound limits

        current_price = latest['close']
        prediction_price = current_price * (1 + pred_percent / 100)
        real_percent = ((prediction_price - current_price) / current_price) * 100

        # 5. Trend and signal distribution checks
        trend = "UP 🟢" if latest['ema_20'] >= latest['sma_20'] else "DOWN 🔴"
        support = df['low'].tail(50).min()
        resistance = df['high'].tail(50).max()
        avg_volume = df['volume'].tail(20).mean()
        high_volume = latest['volume'] > avg_volume

        # Signal assignment rules
        if pred_percent > 0.5 and high_volume: signal = "STRONG BUY 🟢🔥"
        elif pred_percent > 0.1: signal = "BUY 🟢"
        elif pred_percent < -0.5 and high_volume: signal = "STRONG SELL 🔴🔥"
        elif pred_percent < -0.1: signal = "SELL 🔴"
        else: signal = "HOLD 🟡"

        # 6. Risk Management Calculations
        atr = latest['atr']
        if "BUY" in signal:
            stop_loss = current_price - 1.5 * atr
            take_profit = current_price + 2.5 * atr
            risk_reward = (take_profit - current_price) / (current_price - stop_loss)
        elif "SELL" in signal:
            stop_loss = current_price + 1.5 * atr
            take_profit = current_price - 2.5 * atr
            risk_reward = (current_price - take_profit) / (stop_loss - current_price)
        else:
            stop_loss = take_profit = risk_reward = None

        # 7. AI Confidence Matrix Scoring
        trend_score = 40 if trend == "UP 🟢" else 25
        rsi_val = latest['rsi']
        rsi_score = 20 if 40 <= rsi_val <= 60 else (15 if 30 <= rsi_val <= 70 else 10)
        
        macd_diff_ratio = abs(latest['macd'] - latest['macd_signal']) / (latest['atr'] + 0.01)
        macd_score = 25 if macd_diff_ratio > 0.5 else (18 if macd_diff_ratio > 0.2 else 12)
        
        change_abs = abs(real_percent)
        pred_score = 30 if change_abs > 2 else (24 if change_abs > 1 else (18 if change_abs > 0.5 else (12 if change_abs > 0.2 else 8)))
        
        ai_confidence = min(trend_score + rsi_score + macd_score + pred_score, 95)
        
        # Cross-asset dependency coefficient
        dep = get_btc_dependency(symbol)

        # Position sizing details
        position_size = 0
        allocated_cost = 0
        sl_pct = tp_pct = 0
        if stop_loss:
            risk_amount = capital * 0.02
            position_size = risk_amount / abs(current_price - stop_loss)
            allocated_cost = position_size * current_price
            sl_pct = (abs(current_price - stop_loss) / current_price) * 100
            tp_pct = (abs(take_profit - current_price) / current_price) * 100

        return {
            "symbol": symbol, "current_price": current_price, "last_time": last_time, "dep": dep,
            "trend": trend, "support": support, "resistance": resistance, "prediction_price": prediction_price,
            "real_percent": real_percent, "high_volume": high_volume, "signal": signal, "stop_loss": stop_loss,
            "take_profit": take_profit, "risk_reward": risk_reward, "position_size": position_size,
            "allocated_cost": allocated_cost, "sl_pct": sl_pct, "tp_pct": tp_pct, "ai_confidence": round(ai_confidence, 1),
            "selected_timeframe": selected_timeframe
        }