from dotenv import load_dotenv
from src.state import AgentState
from src.agents.data_collector import data_collection_node
from src.agents.analysts import fundamental_analyst, technical_analyst
from src.agents.portfolio_manager import portfolio_manager
from src.agents.risk_manager import risk_management_node
from src.agents.execution import execute_trade_node
from src.agents.reflector import reflector_node  # <--- New Import
from src.data.storage import init_db, log_trade
import sys
from termcolor import colored

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print(colored("--- 🚀 Starting Hedge Fund System (Sprint 6 Complete) ---", "cyan"))
    
    # 0. Initialize Database
    init_db()
    
    # 1. Initialize State
    # Use 'MU' since you just bought it, so we can reflect on it!
    # Or change back to 'AAPL' or any other ticker.
    state: AgentState = {
        "ticker": "MU", 
        "data": {},
        "metadata": {},
        "fundamental_analysis": "",
        "technical_analysis": "",
        "sentiment_analysis": "",
        "portfolio_decision": "",
        "risk_score": 0,
        "risk_analysis": "",
        "trade_approved": False,
        "execution_status": "",
        "revision_count": 0
    }

    # 2. Run Data Collection
    print(f"--- 1. Fetching Data for {state['ticker']} ---")
    node1_result = data_collection_node(state)
    state.update(node1_result)
    
    if "error" in state["metadata"] or not state["data"]:
        print(colored(f"❌ System Halted: {state['metadata'].get('error_msg', 'No Data')}", "red"))
        sys.exit(1)

    # 3. Run Analysts
    state.update(fundamental_analyst(state))
    state.update(technical_analyst(state))

    # 4. Run Portfolio Manager
    state.update(portfolio_manager(state))
    print(colored(f"\n👨‍💼 PM PROPOSAL: {state['portfolio_decision']}", "magenta"))

    # 5. Run Risk Veto Board
    state.update(risk_management_node(state))
    print("\n" + "="*50)
    print(f"🛡️ RISK BOARD VERDICT")
    print(state["risk_analysis"])
    print("="*50)

    # 6. Run Execution Agent
    node6_result = execute_trade_node(state)
    state.update(node6_result)

    # 7. LOGGING
    exec_status = state.get('execution_status', '')
    if "Filled" in exec_status:
        try:
            parts = exec_status.split(" ")
            action = parts[1]
            qty = float(parts[2])
            ticker = parts[3]
            price = state['data']['price']
            log_trade(ticker, action, qty, price, state['portfolio_decision'])
        except Exception as e:
            print(colored(f"⚠️ Error logging: {e}", "yellow"))

    # 8. REFLECTOR AGENT (The Learning Step)
    # It looks at the LAST trade (which might be the one we just did) and comments on it.
    reflector_node(state)

    # --- FINAL REPORT ---
    print("\n" + "="*50)
    print(f"📜 FINAL EXECUTION LOG")
    print("="*50)
    
    if "Filled" in exec_status:
        print(colored(f"SUCCESS: {exec_status}", "green", attrs=['bold']))
    else:
        print(exec_status)
        
    print("="*50)