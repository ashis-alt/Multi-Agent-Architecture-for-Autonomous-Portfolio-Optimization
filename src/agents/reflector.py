from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.state import AgentState
from src.data.storage import log_trade
from termcolor import colored
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0, google_api_key=api_key)

DB_PATH = "portfolio.db"

def get_last_trade():
    """Fetches the most recent trade from the DB."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM trades ORDER BY id DESC LIMIT 1')
        trade = cursor.fetchone()
        conn.close()
        return trade
    except Exception:
        return None

def save_lesson(ticker, lesson):
    """Saves a learned lesson to the DB."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO lessons (timestamp, ticker, lesson_text) VALUES (datetime("now"), ?, ?)', (ticker, lesson))
        conn.commit()
        conn.close()
        print(colored(f"🧠 New Lesson Learned: {lesson}", "magenta", attrs=['bold']))
    except Exception as e:
        print(colored(f"Error saving lesson: {e}", "red"))

def reflector_node(state: AgentState) -> AgentState:
    """
    Node 6: Reflector Agent
    Reviews the last trade and extracts a strategic lesson.
    """
    print(colored("--- [Node 6] Reflector Agent Analyzing Past ---", "magenta"))
    
    # 1. Get the last trade we made
    last_trade = get_last_trade()
    if not last_trade:
        print(colored("No past trades to reflect on yet.", "yellow"))
        return {"revision_count": 0}

    # Unpack tuple (id, time, ticker, action, qty, price, pnl, reason)
    # Note: Schema matches what we defined in storage.py
    # id=0, time=1, ticker=2, action=3, qty=4, buy_price=5, pnl=6, reason=7
    past_ticker = last_trade[2]
    buy_price = last_trade[5]
    reasoning = last_trade[7]
    
    # 2. Check Current Price (Hypothetical PnL Check)
    # In a real app, we'd check if we sold it. Here we check "Unrealized PnL".
    current_price = state['data']['price']
    
    # Only reflect if we are looking at the same stock we bought
    if past_ticker != state['ticker']:
        print(colored(f"Skipping reflection (Last trade was {past_ticker}, currently analyzing {state['ticker']})", "yellow"))
        return {"revision_count": 0}

    # Calculate simple PnL
    pnl_percent = ((current_price - buy_price) / buy_price) * 100
    
    outcome = "PROFIT" if pnl_percent > 0 else "LOSS"
    
    print(colored(f"🧐 Reviewing Trade: Bought {past_ticker} at ${buy_price:.2f}. Current: ${current_price:.2f} ({pnl_percent:.2f}%)", "cyan"))

    # 3. Generate Lesson using LLM
    msg = f"""
    You are a Trading Coach.
    We bought {past_ticker} at ${buy_price:.2f} based on this reasoning:
    "{reasoning}"
    
    Current Result: {outcome} ({pnl_percent:.2f}%)
    
    Task:
    Write a ONE-sentence "Trading Rule" to remember for next time.
    If we won, reinforce the good habit.
    If we lost, correct the mistake.
    Start with "LESSON: ..."
    """

    try:
        response = llm.invoke([HumanMessage(content=msg)])
        lesson = response.content.replace("LESSON:", "").strip()
        save_lesson(past_ticker, lesson)
    except Exception as e:
        print(colored(f"Reflector Failed: {e}", "red"))

    return {"revision_count": 0}