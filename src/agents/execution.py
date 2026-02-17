import os
import requests
import re
import math
from dotenv import load_dotenv
from src.state import AgentState
from termcolor import colored

load_dotenv()

# Load Alpaca Keys
ALPACA_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

HEADERS = {
    "APCA-API-KEY-ID": ALPACA_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET,
    "Content-Type": "application/json"
}

# CONFIG: Position Sizing
# How much money (in USD) do you want to allocate per trade?
POSITION_SIZE_USD = 5000.0 

def execute_trade_node(state: AgentState) -> AgentState:
    """
    Node 5: Execution Agent
    Calculates dynamic quantity based on price and sends order to Alpaca.
    """
    print(colored("--- [Node 5] Execution Agent Activated ---", "cyan"))

    # 1. Check Risk Approval
    if not state.get("trade_approved", False):
        print(colored("❌ Trade NOT Approved. Skipping execution.", "yellow"))
        return {"execution_status": "Skipped (Risk Veto)"}

    # 2. Parse the Decision using Regex
    decision_text = state["portfolio_decision"].upper()
    ticker = state["ticker"]
    
    # Ensure we have a valid price to calculate quantity
    current_price = state.get("data", {}).get("price")
    if not current_price or current_price <= 0:
        print(colored("❌ Error: Invalid price data. Cannot calculate quantity.", "red"))
        return {"execution_status": "Failed (Invalid Price)"}

    # Regex patterns to capture the specific action
    buy_pattern = r"ACTION:\s*BUY"
    sell_pattern = r"ACTION:\s*SELL"

    side = None
    if re.search(buy_pattern, decision_text):
        side = "buy"
    elif re.search(sell_pattern, decision_text):
        side = "sell"
    
    if not side:
        print(colored(f"⚠️ Decision is HOLD or unclear. No order sent.", "yellow"))
        return {"execution_status": "Skipped (Hold)"}

    # 3. Dynamic Sizing Calculation
    # Qty = Target Amount / Current Price (Rounded down)
    qty = math.floor(POSITION_SIZE_USD / current_price)
    
    # Safety: Always buy at least 1 share if price > 0
    if qty < 1:
        qty = 1
        
    print(colored(f"💰 Sizing Calculation: ${POSITION_SIZE_USD} / ${current_price:.2f} = {qty} shares", "cyan"))

    # 4. Construct the Order Payload
    order_data = {
        "symbol": ticker,
        "qty": qty,
        "side": side,
        "type": "market",
        "time_in_force": "day"
    }

    print(colored(f"🚀 Sending Order to Alpaca: {side.upper()} {qty} {ticker}...", "cyan", attrs=['bold']))

    # 5. Send to Alpaca API
    try:
        # We append /v2/orders to the base URL
        api_url = f"{BASE_URL}/v2/orders"
        
        response = requests.post(api_url, json=order_data, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            print(colored(f"✅ ORDER EXECUTED! ID: {data['id']}", "green", attrs=['bold']))
            status = f"Filled: {side} {qty} {ticker}"
        else:
            # Parse error message from Alpaca
            try:
                error_data = response.json()
                error_msg = error_data.get('message', response.text)
            except:
                error_msg = response.text
                
            print(colored(f"❌ Order Failed: {error_msg}", "red"))
            status = f"Failed: {error_msg}"

    except Exception as e:
        print(colored(f"❌ API Connection Error: {str(e)}", "red"))
        status = f"Error: {str(e)}"

    return {
        "execution_status": status
    }