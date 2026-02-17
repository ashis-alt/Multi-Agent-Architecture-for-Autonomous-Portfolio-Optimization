from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.state import AgentState
from termcolor import colored
import os
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# --- CONFIGURATION ---
# Now that you have billing enabled, this model will fly! 🚀
MODEL_NAME = "gemini-2.0-flash" 

if not api_key:
    print(colored("CRITICAL ERROR: GOOGLE_API_KEY not found", "red"))

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME, 
    temperature=0,
    google_api_key=api_key
)

def fundamental_analyst(state: AgentState) -> AgentState:
    """
    Node 2: Fundamental Analyst
    Evaluates the company's intrinsic value.
    """
    ticker = state.get('ticker', 'Unknown')
    print(colored(f"--- [Node 2] Fundamental Analyst Working on {ticker} ---", "blue"))
    
    price = state.get('data', {}).get('price', 0.0)
    
    msg = f"""
    You are a Senior Fundamental Analyst at a top hedge fund.
    Analyze {ticker} at the current price of ${price:.2f}.
    
    1. Is this company fundamentally strong?
    2. What are the key growth drivers?
    3. Provide a 'Valuation Score' from 0-100.
    
    Keep your answer concise (under 100 words).
    """
    
    try:
        response = llm.invoke([HumanMessage(content=msg)])
        result = response.content
    except Exception as e:
        print(colored(f"Error in Fundamental Analyst: {e}", "red"))
        result = f"Error: {str(e)}"
    
    return {
        "fundamental_analysis": result
    }

def technical_analyst(state: AgentState) -> AgentState:
    """
    Node 3: Technical Analyst
    Evaluates chart patterns (RSI, MACD).
    """
    ticker = state.get('ticker', 'Unknown')
    print(colored(f"--- [Node 3] Technical Analyst Working on {ticker} ---", "yellow"))
    
    data = state.get('data', {})
    price = data.get('price', 0.0)
    rsi = data.get('rsi', 0.0)
    macd = data.get('macd', 0.0)
    
    msg = f"""
    You are a Technical Trading Expert. Analyze these indicators for {ticker}:
    - Price: ${price:.2f}
    - RSI: {rsi:.2f} (Over 70=Overbought, Under 30=Oversold)
    - MACD: {macd:.2f}
    
    Give a clear signal: BUY, SELL, or WAIT based purely on these numbers.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=msg)])
        result = response.content
    except Exception as e:
        print(colored(f"Error in Technical Analyst: {e}", "red"))
        result = f"Error: {str(e)}"
    
    return {
        "technical_analysis": result
    }