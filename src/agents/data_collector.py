import yfinance as yf
from datetime import datetime
from src.state import AgentState
from src.utils.indicators import calculate_technical_indicators
from termcolor import colored

def data_collection_node(state: AgentState) -> AgentState:
    """
    Node 1: Data Collection
    Fetches OHLCV data and adds technical indicators.
    """
    ticker = state["ticker"]
    print(colored(f"--- [Node 1] Data Collector Activated for {ticker} ---", "cyan"))

    try:
        # 1. Fetch Data via yfinance
        stock = yf.Ticker(ticker)
        # Fetch 6 months of data to ensure enough history for indicators
        hist = stock.history(period="6mo")
        
        if hist.empty:
            raise ValueError(f"No data found for {ticker}")

        # 2. Calculate Indicators (pandas-ta)
        hist_processed = calculate_technical_indicators(hist)
        
        # Get the most recent row of data (Today's state)
        latest = hist_processed.iloc[-1]

        # 3. Structure the data for the State
        market_data = {
            "price": latest["Close"],
            "volume": latest["Volume"],
            "rsi": latest["RSI"],
            "macd": latest["MACD_12_26_9"],
            "signal": latest["MACDs_12_26_9"],
            "sma_20": latest["SMA_20"],
            "sma_50": latest["SMA_50"],
            "last_updated": datetime.now().isoformat()
        }

        print(colored(f"Successfully fetched data: Price=${latest['Close']:.2f}, RSI={latest['RSI']:.2f}", "green"))

        # Update State
        return {
            "data": market_data,
            "metadata": {"status": "success"}
        }

    except Exception as e:
        print(colored(f"Error in Data Collection: {str(e)}", "red"))
        # In a real LangGraph, you might route to an 'End' node here
        return {
            "data": {},
            "metadata": {"status": "error", "error_msg": str(e)}
        }