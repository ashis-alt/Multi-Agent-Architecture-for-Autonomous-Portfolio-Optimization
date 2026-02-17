import streamlit as st
import sqlite3
import pandas as pd
import os
import requests
from dotenv import load_dotenv
import plotly.express as px

# 1. Load Environment Variables
load_dotenv()
ALPACA_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

HEADERS = {
    "APCA-API-KEY-ID": ALPACA_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET,
    "Content-Type": "application/json"
}

# 2. Configure the Page
st.set_page_config(
    page_title="Hedge Fund AI Dashboard",
    page_icon="🦁",
    layout="wide"
)

st.title("🦁 Autonomous AI Hedge Fund")
st.markdown("### Major Project: Multi-Agent Portfolio System")

# 3. Sidebar: Live Account Status (Connects to Alpaca)
st.sidebar.header("📡 Live Market Connection")

try:
    # Fetch Account Data
    acct = requests.get(f"{BASE_URL}/v2/account", headers=HEADERS).json()
    
    # Check if we got valid data
    if 'cash' in acct:
        cash = float(acct['cash'])
        equity = float(acct['equity'])
        buying_power = float(acct['buying_power'])
        
        # Display Metrics
        st.sidebar.metric("💰 Total Equity", f"${equity:,.2f}")
        st.sidebar.metric("💵 Cash Available", f"${cash:,.2f}")
        st.sidebar.metric("⚡ Buying Power", f"${buying_power:,.2f}")
        st.sidebar.success("System Status: ONLINE")
    else:
        st.sidebar.error("Alpaca Error: Check API Keys")
        
except Exception as e:
    st.sidebar.error("System: OFFLINE")
    st.sidebar.warning(f"Connection Error: {e}")

# 4. Main Dashboard Tabs
tab1, tab2, tab3 = st.tabs(["📊 Live Portfolio", "🧠 AI Brain (Reflector)", "📜 Trade Journal"])

# --- TAB 1: CURRENT HOLDINGS ---
with tab1:
    st.subheader("Live Portfolio Holdings")
    
    try:
        # Fetch Positions from Alpaca
        positions = requests.get(f"{BASE_URL}/v2/positions", headers=HEADERS).json()
        
        if positions:
            # Convert to DataFrame for display
            df_pos = pd.DataFrame(positions)
            
            # Select relevant columns
            df_display = pd.DataFrame()
            df_display['Symbol'] = df_pos['symbol']
            df_display['Qty'] = df_pos['qty']
            df_display['Market Value'] = df_pos['market_value'].astype(float).map('${:,.2f}'.format)
            df_display['Profit/Loss'] = df_pos['unrealized_plpc'].astype(float).map('{:.2%}'.format)
            
            # Show Table
            st.table(df_display)
            
            # Show Pie Chart
            fig = px.pie(df_pos, values='market_value', names='symbol', title='Asset Allocation')
            st.plotly_chart(fig)
            
        else:
            st.info("🚫 No open positions. Portfolio is 100% Cash.")
            
    except Exception as e:
        st.error(f"Error fetching holdings: {e}")

# --- TAB 2: AI BRAIN (LESSONS) ---
with tab2:
    st.subheader("🧠 What has the AI learned?")
    st.markdown("The **Reflector Agent** analyzes past trades and saves lessons here.")
    
    try:
        conn = sqlite3.connect("portfolio.db")
        lessons_df = pd.read_sql_query("SELECT * FROM lessons ORDER BY id DESC", conn)
        conn.close()
        
        if not lessons_df.empty:
            for index, row in lessons_df.iterrows():
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(f"**Lesson regarding {row['ticker']}**:")
                    st.info(f"{row['lesson_text']}")
                    st.caption(f"Learned on: {row['timestamp']}")
        else:
            st.write("No lessons learned yet. (Wait for trades to close!)")
    except Exception as e:
        st.error(f"Database Error: {e}")

# --- TAB 3: EXECUTION LOG ---
with tab3:
    st.subheader("📜 Recent Trade Decisions")
    
    try:
        conn = sqlite3.connect("portfolio.db")
        trades_df = pd.read_sql_query("SELECT * FROM trades ORDER BY id DESC", conn)
        conn.close()
        
        if not trades_df.empty:
            st.dataframe(trades_df, use_container_width=True)
        else:
            st.write("No trades recorded in database yet.")
    except Exception as e:
        st.error(f"Database Error: {e}")

# 5. Refresh Button
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()