import pandas as pd
import pandas_ta as ta

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates RSI, MACD, and SMA using pandas-ta.
    Ref: Synopsis Section 4.5 - Technical Architecture
    """
    # 1. RSI (Relative Strength Index)
    df['RSI'] = df.ta.rsi(length=14)

    # 2. MACD (Moving Average Convergence Divergence)
    macd = df.ta.macd(fast=12, slow=26, signal=9)
    df = pd.concat([df, macd], axis=1)

    # 3. SMA (Simple Moving Average)
    df['SMA_20'] = df.ta.sma(length=20)
    df['SMA_50'] = df.ta.sma(length=50)

    # Clean up NaN values created by indicators
    df.fillna(0, inplace=True)
    
    return df