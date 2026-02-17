from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.state import AgentState
from termcolor import colored
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Setup Alpaca & Gemini
ALPACA_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
HEADERS = {
    "APCA-API-KEY-ID": ALPACA_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET,
    "Content-Type": "application/json"
}

api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0, google_api_key=api_key)

def get_alpaca_portfolio():
    """Fetches REAL account data from Alpaca."""
    try:
        # 1. Get Account Info (Cash, Buying Power)
        acct_response = requests.get(f"{BASE_URL}/v2/account", headers=HEADERS)
        acct_data = acct_response.json()
        
        # 2. Get Open Positions (What stocks we own)
        pos_response = requests.get(f"{BASE_URL}/v2/positions", headers=HEADERS)
        pos_data = pos_response.json()
        
        # Format for the LLM
        portfolio = {
            "buying_power": float(acct_data.get('buying_power', 0)),
            "cash": float(acct_data.get('cash', 0)),
            "equity": float(acct_data.get('equity', 0)),
            "positions": [
                {
                    "symbol": p['symbol'],
                    "qty": int(p['qty']),
                    "market_value": float(p['market_value']),
                    "profit_loss_pct": float(p['unrealized_plpc']) * 100
                }
                for p in pos_data
            ]
        }
        return portfolio
    except Exception as e:
        print(colored(f"⚠️ Failed to fetch Alpaca Portfolio: {e}", "yellow"))
        return {"error": str(e), "positions": []}

def risk_management_node(state: AgentState) -> AgentState:
    """
    Node 4: Risk Veto Board
    Reviews the trade against the REAL portfolio.
    """
    ticker = state['ticker']
    decision = state['portfolio_decision']
    
    print(colored(f"--- [Node 4] Risk Veto Board Reviewing: {ticker} ---", "red"))

    # Skip checks if holding
    if "HOLD" in decision.upper():
        return {
            "risk_score": 0,
            "risk_analysis": "No trade proposed. Risk checks skipped.",
            "trade_approved": True 
        }

    # --- REAL DATA FETCH ---
    current_portfolio = get_alpaca_portfolio()
    
    msg = f"""
    You are the Chief Risk Officer.
    
    PROPOSAL: {decision}
    ASSET: {ticker}
    CURRENT PRICE: ${state['data']['price']:.2f}
    
    REAL-TIME PORTFOLIO STATS:
    - Cash Available: ${current_portfolio.get('cash', 0):.2f}
    - Existing Holdings: {current_portfolio.get('positions')}
    
    RISK CHECKS:
    1. Liquidity Check: Do we have enough cash?
    2. Concentration Check: Do we already hold this asset? (If yes, is exposure > 20%?)
    3. Market Check: Is RSI ({state['data']['rsi']:.2f}) extreme?
    
    OUTPUT FORMAT:
    Risk Score: [0-100]
    Verdict: [APPROVED/REJECTED]
    Reason: [Explanation based on portfolio data]
    """

    try:
        response = llm.invoke([HumanMessage(content=msg)])
        analysis = response.content
        approved = "APPROVED" in analysis.upper()
    except Exception as e:
        print(colored(f"Risk Logic Failed: {e}", "red"))
        analysis = "Error in Risk Node. Defaulting to REJECT."
        approved = False

    return {
        "risk_analysis": analysis,
        "trade_approved": approved
    }