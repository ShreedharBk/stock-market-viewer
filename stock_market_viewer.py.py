import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# App configuration
st.set_page_config(
    page_title="Stock Data Viewer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile responsiveness
st.markdown("""
    <style>
    .stDateInput, .stSelectbox, .stTextInput {
        width: 100% !important;
    }
    .stDataFrame {
        width: 100%;
    }
    .stButton>button {
        width: 100%;
    }
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def fetch_stock_data(ticker, start_date, end_date, interval):
    """Fetch stock data from Yahoo Finance with error handling."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False
        )
        if data.empty:
            return None, None, "No data available for the selected date range."
        return data, info, None
    except Exception as e:
        return None, None, f"Error fetching data: {str(e)}"

def display_stock_metrics(data):
    """Display key stock metrics in a clean format."""
    if data is None:
        return
    
    latest = data.iloc[-1]
    metrics = {
        "Open": float(latest["Open"]),
        "Close": float(latest["Close"]),
        "High": float(latest["High"]),
        "Low": float(latest["Low"]),
        "Volume": int(latest["Volume"])
    }
    
    cols = st.columns(len(metrics))
    for i, (key, value) in enumerate(metrics.items()):
        cols[i].metric(
            label=key,
            value=f"{value:,.2f}" if key != "Volume" else f"{value:,.0f}"
        )

def get_market_name(info):
    """Extract market name from stock info"""
    if not info:
        return "N/A"
    return info.get('exchangeName', 'N/A')

def main():
    """Main app function."""
    st.title("📊 Worldwide Stock Data Viewer")
    st.markdown("View historical stock data of - US,UK,IN,JAPAN,CHINA Markets etc.")
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'info' not in st.session_state:
        st.session_state.info = None
    
    # Sidebar inputs
    with st.sidebar:
        st.header("Input Parameters")
        
        # Ticker input with validation
        ticker = st.text_input(
            "Stock Ticker (e.g., AAPL, RELIANCE.NS)",
            value="AAPL",
            max_chars=15
        ).strip().upper()
        
        # Date range with sensible defaults
        end_date = st.date_input(
            "End Date",
            value=datetime.now()
        )
        start_date = st.date_input(
            "Start Date",
            value=end_date - timedelta(days=30)
        )
        
        # Interval selection
        interval = st.selectbox(
            "Data Interval",
            options=["1d", "1wk", "1mo"],
            index=0
        )
        
        # Submit button
        submitted = st.button("Get Stock Data")
    
    # Fetch and display data when submitted
    if submitted:
        if start_date >= end_date:
            st.error("End date must be after start date.")
            st.stop()
        
        with st.spinner("Fetching stock data..."):
            data, info, error = fetch_stock_data(ticker, start_date, end_date, interval)
            
            if error:
                st.error(error)
                st.stop()
            
            if data is None:
                st.error("No data available for the selected parameters.")
                st.stop()
            
            st.session_state.data = data
            st.session_state.info = info
            st.success("Data loaded successfully!")
    
    # Display results if data exists
    if st.session_state.data is not None:
        data = st.session_state.data
        info = st.session_state.info
        market_name = get_market_name(info)
        
        st.subheader(f"{ticker} ({market_name}) Stock Data")
        display_stock_metrics(data)
        
        # Display raw data table
        st.dataframe(
            data.sort_index(ascending=False),
            use_container_width=True,
            height=500
        )
        
        # Export to CSV button
        csv = data.to_csv().encode('utf-8')
        st.download_button(
            label="Export to CSV",
            data=csv,
            file_name=f"{ticker}_stock_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()