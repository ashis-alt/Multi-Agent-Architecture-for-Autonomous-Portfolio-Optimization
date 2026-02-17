from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.state import AgentState
from termcolor import colored
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.0-flash"

llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0, google_api_key=api_key)

def portfolio_manager(state: AgentState) -> AgentState:
    """
    Node 4: Portfolio Manager (The Boss)
    Synthesizes analyst reports and makes the final trading decision.
    """
    print(colored(f"--- [Node 4] Portfolio Manager Deciding on {state['ticker']} ---", "magenta"))
    
    # Get the data from previous agents
    ticker = state.get('ticker')
    fund_analysis = state.get('fundamental_analysis', 'No Report')
    tech_analysis = state.get('technical_analysis', 'No Report')
    
    # The Prompt: Synthesize everything
    msg = f"""
    You are the Head Portfolio Manager. 
    Make a final decision for {ticker} based on these team reports:

    1. FUNDAMENTAL REPORT: 
    {fund_analysis}

    2. TECHNICAL REPORT:
    {tech_analysis}

    DECISION TASK:
    - Synthesize the conflicting signals.
    - Output a final decision: "ACTION: [BUY/SELL/HOLD]" 
    - Output a conviction score: "CONFIDENCE: [0-100]%"
    - Provide a 1-sentence reasoning.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=msg)])
        decision = response.content
    except Exception as e:
        # Fallback if API fails
        print(colored(f"⚠️ PM Rate Limit. Simulating decision.", "yellow"))
        decision = f"ACTION: HOLD (Simulated)\nCONFIDENCE: 50%\nReason: API Limit reached, staying neutral."

    return {
        "portfolio_decision": decision
    }