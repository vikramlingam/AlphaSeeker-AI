import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from finance_engine import FinanceEngine
from agent_engine import AgentEngine

# Page Config
st.set_page_config(page_title="AlphaSeeker AI", page_icon="📈", layout="wide")

# Custom CSS for "Clean Professional" feel (Light Theme)
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        background-color: #000000;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #333333;
        color: white;
    }
    h1, h2, h3 {
        color: #000000;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stMetricLabel {
        color: #555555 !important;
    }
    .stMetricValue {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Engines
@st.cache_resource
def get_engines_v4():
    return FinanceEngine(), AgentEngine()

fe, ae = get_engines_v4()

# Session State Initialization
if 'ticker_data' not in st.session_state:
    st.session_state.ticker_data = None
if 'competitors' not in st.session_state:
    st.session_state.competitors = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("AlphaSeeker AI 🧠")
    ticker_input = st.text_input("Enter Ticker Symbol", value="AAPL").upper()
    
    if st.button("Analyze Stock"):
        with st.spinner(f"Analyzing {ticker_input}..."):
            st.status("Fetching Financial Data...", expanded=True)
            data, stock_obj = fe.get_stock_data(ticker_input)
            
            if data:
                st.session_state.ticker_data = data
                st.session_state.stock_obj = stock_obj # Store object for history if needed
                st.session_state.messages = [] # Reset chat
                
                # Clear stale competitor data
                if 'comp_data' in st.session_state:
                    del st.session_state.comp_data
                if 'competitors' in st.session_state:
                    del st.session_state.competitors
                
                st.success("Analysis Complete!")
            else:
                st.error("Ticker not found or data unavailable.")

# Main Content
if st.session_state.ticker_data:
    data = st.session_state.ticker_data
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"{data['longName']} ({data['symbol']})")
        st.markdown(f"**Sector:** {data['sector']} | **Industry:** {data['industry']}")
    with col2:
        st.metric("Current Price", f"${data['currentPrice']}", delta=None)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📈 Technical Analysis", "💰 Deep Dive Valuation", "⚔️ Competitor Matrix", "🏛️ Ownership & Activity"])

    # --- TAB 1: DASHBOARD ---
    with tab1:
        st.subheader("Key Metrics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Market Cap", f"${data['marketCap']:,}" if data['marketCap'] else "N/A")
        m2.metric("P/E Ratio", f"{data['trailingPE']:.2f}" if data['trailingPE'] else "N/A")
        m3.metric("EV/EBITDA", f"{data['evToEbitda']:.2f}" if data['evToEbitda'] else "N/A")
        m4.metric("Profit Margin", f"{data['profitMargins']*100:.2f}%" if data['profitMargins'] else "N/A")
        
        st.subheader("Business Summary")
        st.info(data['longBusinessSummary'])
        
        st.subheader("⚠️ Key Risks (AI Analysis)")
        if st.button("Analyze Risks"):
            with st.spinner("Identifying risks..."):
                risks = ae.analyze_risks(data['symbol'], data['longBusinessSummary'])
                st.warning(risks)

    # --- TAB 2: TECHNICAL ANALYSIS ---
    with tab2:
        st.subheader("Technical Analysis & Chart")
        
        hist = fe.get_price_history(data['symbol'])
        if hist is not None:
            # Candlestick Chart with SMAs
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=hist.index,
                            open=hist['Open'], high=hist['High'],
                            low=hist['Low'], close=hist['Close'], name='Price'))
            
            fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_50'], line=dict(color='orange', width=1), name='SMA 50'))
            fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_200'], line=dict(color='blue', width=1), name='SMA 200'))
            
            fig.update_layout(title=f"{data['symbol']} Price History (1Y)", xaxis_title="Date", yaxis_title="Price", height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # RSI
            current_rsi = hist['RSI'].iloc[-1]
            current_price = hist['Close'].iloc[-1]
            sma_50 = hist['SMA_50'].iloc[-1]
            sma_200 = hist['SMA_200'].iloc[-1]
            
            col_tech_1, col_tech_2 = st.columns([1, 2])
            with col_tech_1:
                st.metric("RSI (14)", f"{current_rsi:.2f}")
                if current_rsi > 70:
                    st.error("Overbought (>70)")
                elif current_rsi < 30:
                    st.success("Oversold (<30)")
                else:
                    st.info("Neutral")
            
            with col_tech_2:
                st.markdown("### 🎓 AI Technical Mentor")
                if st.button("Explain Chart"):
                    with st.spinner("Analyzing chart patterns..."):
                        explanation = ae.explain_technical_analysis(data['symbol'], current_price, sma_50, sma_200, current_rsi)
                        st.info(explanation)
        else:
            st.error("Could not fetch price history.")

    # --- TAB 3: DEEP DIVE VALUATION (Reverse DCF) ---
    with tab3:
        st.subheader("Market Implied Reverse DCF")
        st.markdown("Adjust the sliders to see what the market is 'pricing in' vs. your assumptions.")
        
        col_dcf_1, col_dcf_2 = st.columns([1, 2])
        
        with col_dcf_1:
            st.markdown("### Assumptions")
            discount_rate = st.slider("Discount Rate (%)", 5.0, 15.0, 10.0, 0.5) / 100
            terminal_growth = st.slider("Terminal Growth (%)", 1.0, 5.0, 3.0, 0.1) / 100
            
            # Recalculate on the fly
            fcf = data.get('freeCashflow')
            shares = st.session_state.stock_obj.info.get('sharesOutstanding')
            
            if fcf and shares:
                implied_growth = fe.calculate_reverse_dcf(
                    data['currentPrice'], fcf, discount_rate, terminal_growth, shares
                )
                
                st.markdown("---")
                st.metric("Market Implied Growth (10y)", f"{implied_growth:.2f}%")
                
                hist_growth = fe.get_historical_growth(st.session_state.stock_obj)
                st.metric("Historical 5y Growth", f"{hist_growth:.2f}%" if not pd.isna(hist_growth) else "N/A")
                
                if not pd.isna(hist_growth):
                    if implied_growth < hist_growth:
                        st.success("✅ UNDERVALUED: Market expects LESS growth than historical average.")
                    else:
                        st.warning("⚠️ OVERVALUED: Market expects MORE growth than historical average.")
            else:
                st.error("Insufficient data for DCF (Missing FCF or Shares).")

        with col_dcf_2:
            # Visualization of Cash Flows
            if fcf and shares:
                years = list(range(1, 11))
                # Projected FCF based on IMPLIED growth
                projected_fcf = [fcf * ((1 + implied_growth/100) ** i) for i in years]
                
                fig = px.bar(x=years, y=projected_fcf, title="Implied Future Cash Flows", labels={'x': 'Year', 'y': 'Free Cash Flow'})
                st.plotly_chart(fig, use_container_width=True)

    # --- TAB 4: COMPETITOR MATRIX ---
    with tab4:
        st.subheader("Autonomous Competitor Analysis")
        
        if st.button("Run Competitor Analysis"):
            with st.status("Agent is thinking...", expanded=True) as status:
                status.write("Identifying true competitors via LLM...")
                competitors_json = ae.analyze_competitors(data['symbol'], data['longBusinessSummary'])
                
                try:
                    competitors_list = json.loads(competitors_json)
                    st.session_state.competitors = competitors_list
                    status.write(f"Found: {', '.join(competitors_list)}")
                    
                    status.write("Fetching competitor metrics...")
                    comp_data = []
                    # Add Target Stock
                    comp_data.append({
                        "Ticker": data['symbol'],
                        "RevGrowth": data.get('revenueGrowth', 0) * 100 if data.get('revenueGrowth') else 0,
                        "EVEBITDA": data.get('evToEbitda', 0),
                        "NetMargin": data.get('profitMargins', 0),
                        "Type": "Target"
                    })
                    
                    for comp in competitors_list:
                        c_data, _ = fe.get_stock_data(comp)
                        if c_data:
                            comp_data.append({
                                "Ticker": comp,
                                "RevGrowth": c_data.get('revenueGrowth', 0) * 100 if c_data.get('revenueGrowth') else 0,
                                "EVEBITDA": c_data.get('evToEbitda', 0),
                                "NetMargin": c_data.get('profitMargins', 0),
                                "Type": "Peer"
                            })
                    
                    st.session_state.comp_data = pd.DataFrame(comp_data)
                    status.update(label="Analysis Complete!", state="complete", expanded=False)
                    
                except Exception as e:
                    st.error(f"Error parsing competitors: {e}")

        if 'comp_data' in st.session_state:
            df = st.session_state.comp_data
            
            # Scatter Plot
            # Scatter Plot
            # Handle negative sizes for Plotly
            df['NetMargin'] = df['NetMargin'].fillna(0)
            df['AbsMargin'] = df['NetMargin'].abs()
            # Ensure no zero sizes
            df['AbsMargin'] = df['AbsMargin'].replace(0, 0.01)
            
            fig = px.scatter(
                df, x="RevGrowth", y="EVEBITDA", color="Type", text="Ticker",
                size="AbsMargin", hover_data=["NetMargin"],
                title="Valuation Gap: Growth vs. Multiple",
                color_discrete_map={"Target": "#ff4b4b", "Peer": "#00cc96"}
            )
            fig.update_traces(textposition='top center')
            st.plotly_chart(fig, use_container_width=True)
            
            # Better Alternative Engine
            st.subheader("The 'Better Alternative' Engine")
            
            target_rows = df[df['Ticker'] == data['symbol']].to_dict('records')
            if target_rows:
                target_metrics = target_rows[0]
                peers_metrics = df[df['Ticker'] != data['symbol']].to_dict('records')
                
                with st.spinner("Finding Alpha..."):
                    pitch = ae.find_better_alternatives(data['symbol'], target_metrics, peers_metrics)
                    st.markdown(f"### 💡 Analyst Insight\n\n{pitch}")
            else:
                st.warning("Target metrics not found in competitor data. Please re-run analysis.")

    # --- TAB 5: OWNERSHIP & ACTIVITY ---
    with tab5:
        st.subheader("Insider & Institutional Activity")
        
        stock_obj = st.session_state.stock_obj
        
        col_own_1, col_own_2 = st.columns(2)
        
        with col_own_1:
            st.markdown("### 👔 Insider Trading")
            insider_df = fe.get_insider_trades(stock_obj)
            if insider_df is not None and not insider_df.empty:
                st.dataframe(insider_df, use_container_width=True, height=300)
            else:
                st.info("No recent insider trading data available.")
                
        with col_own_2:
            st.markdown("### 🏦 Institutional Holders")
            inst_df = fe.get_institutional_holders(stock_obj)
            if inst_df is not None and not inst_df.empty:
                st.dataframe(inst_df, use_container_width=True, height=300)
            else:
                st.info("No institutional holder data available.")

        st.markdown("---")
        st.subheader("🤖 AI Summary")
        
        if st.button("Generate Ownership Summary"):
            with st.spinner("Analyzing ownership trends..."):
                summary = ae.summarize_ownership_activity(data['symbol'], insider_df, inst_df)
                st.success(summary)

else:
    st.info("👈 Enter a stock ticker in the sidebar to begin.")
