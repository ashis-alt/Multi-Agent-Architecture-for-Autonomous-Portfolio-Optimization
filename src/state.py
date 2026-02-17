import operator
from typing import Annotated, List, Dict, Any, TypedDict

class AgentState(TypedDict):
    """
    The Global State Dict passed between all agents.
    Updated for Sprint 4 (Risk & Execution).
    """
    ticker: str
    data: Dict[str, Any]  # Stores price data, indicators, news
    metadata: Dict[str, Any]
    
    # Analyst Outputs
    fundamental_analysis: str
    technical_analysis: str
    sentiment_analysis: str
    
    # Portfolio Manager Output
    portfolio_decision: str  # e.g., "ACTION: BUY | Size: 100"
    
    # Risk Board Outputs (Added for Sprint 4)
    risk_score: int          # 0 = Safe, 100 = Dangerous
    risk_analysis: str       # Explanation from the Veto Board
    trade_approved: bool     # True/False
    
    # Execution Details (Added for Sprint 5)
    execution_status: str
    
    # Loop Control
    revision_count: int  # To track Risk Board rejections