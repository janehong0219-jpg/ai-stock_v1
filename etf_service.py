import yfinance as yf
import pandas as pd
import numpy as np

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_stock(symbol):
    if symbol.isdigit():
        symbol = f"{symbol}.TW"
    
    # 這裡加入一點「系統日誌」的感覺
    print(f"[SYSTEM] Initializing Quantitative Analysis for: {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y")
        
        if hist.empty:
            return {"error": "TARGET_NOT_FOUND_OR_DELISTED"}

        # 1. Technical Indicators Calculation
        current_price = hist['Close'].iloc[-1]
        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
        hist['SMA_60'] = hist['Close'].rolling(window=60).mean()
        hist['SMA_120'] = hist['Close'].rolling(window=120).mean()
        hist['RSI'] = calculate_rsi(hist['Close'])
        
        sma_20 = hist['SMA_20'].iloc[-1]
        sma_60 = hist['SMA_60'].iloc[-1]
        sma_120 = hist['SMA_120'].iloc[-1]
        rsi = hist['RSI'].iloc[-1]
        
        if pd.isna(sma_120): sma_120 = current_price

        # 2. Fundamental Data Extraction
        info = ticker.info
        eps = info.get('trailingEps', 0)
        pe_ratio = info.get('trailingPE', 0)
        inst_ownership = info.get('heldPercentInstitutions', 0)
        if inst_ownership: inst_ownership = round(inst_ownership * 100, 1)
        else: inst_ownership = "N/A"
        beta = info.get('beta', 1)
        
        # 3. Generating "Hedge Fund Style" Report
        
        # Why (Valuation Matrix)
        fundamental_advice = ""
        if pe_ratio > 0 and pe_ratio < 15:
            fundamental_advice += "估值處於「低估區間 (Undervalued)」，具備安全邊際。"
        elif pe_ratio > 35:
            fundamental_advice += "估值處於「溢價區間 (Premium)」，需留意修正風險。"
        else:
            fundamental_advice += "估值回歸中位數，市場定價合理。"
            
        # When (Momentum Signal)
        short_signal = "NEUTRAL"
        short_advice = "動能訊號不明確，建議持續監控。"
        if rsi > 75: 
            short_signal, short_advice = "OVERBOUGHT", "RSI 指標呈現「極度超買」，動能過熱，回檔風險激增。"
        elif rsi < 25: 
            short_signal, short_advice = "OVERSOLD", "RSI 指標呈現「極度超賣」，乖離過大，技術性反彈機率高。"
        elif current_price > sma_20: 
            short_signal, short_advice = "BULLISH", "價格站穩月線之上，多頭動能強勁 (Strong Momentum)。"
        else: 
            short_signal, short_advice = "BEARISH", "價格跌破月線支撐，空方控盤 (Weak Momentum)。"

        long_signal = "LONG" if current_price > sma_120 else "SHORT"

        # How (Algorithmic Targets)
        support = sma_20 if current_price > sma_20 else sma_60
        resistance = current_price * 1.15 # 拉大獲利預期，更有野心
        
        # Return Data Package
        result = {
            "symbol": symbol,
            "name": info.get('longName', symbol),
            "price": round(current_price, 2),
            "change_percent": round(((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100, 2),
            "rsi": round(rsi, 1),
            "sma_20": round(sma_20, 2),
            "sma_60": round(sma_60, 2),
            "sma_120": round(sma_120, 2),
            "eps": eps,
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else "N/A",
            "beta": round(beta, 2) if beta else "N/A",
            "inst_ownership": inst_ownership,
            
            # The "Secret" Text
            "fundamental_advice": fundamental_advice,
            "short_term": {"signal": short_signal, "advice": short_advice},
            "long_term":  {"signal": long_signal},
            "buy_target": round(support, 2),
            "sell_target": round(resistance, 2)
        }
        return result

    except Exception as e:
        print(f"[SYSTEM ERROR]: {e}")
        return {"error": "DATA_FETCH_FAILED"}