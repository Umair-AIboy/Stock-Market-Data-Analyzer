import streamlit as st
import plotly.graph_objects as go

from utils import (
    get_stock_data,
    get_stock_info,
    calculate_metrics,
    get_popular_stocks_snapshot
)

from auth import create_user_table, signup_user, login_user

st.set_page_config(page_title="Stock Market Analyzer", layout="wide")

# Create user table
create_user_table()

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None


# -----------------------------
# AUTHENTICATION SECTION
# -----------------------------
def show_auth_page():
    st.title("📈 StockVision")
    st.markdown("### Smart Stock Analysis & Market Insights Dashboard")
    st.subheader("Login / Signup")

    auth_mode = st.radio("Select Option", ["Login", "Sign Up"], horizontal=True)

    if auth_mode == "Sign Up":
        st.markdown("### Create a New Account")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Create Account"):
            if not username or not email or not password or not confirm_password:
                st.warning("Please fill all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = signup_user(username, email, password)
                if success:
                    st.success(message)
                    st.info("Now go to Login and sign in with your account.")
                else:
                    st.error(message)

    else:
        st.markdown("### Login to Your Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            success, result = login_user(email, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user = result
                st.success(f"Welcome, {result['username']}!")
                st.rerun()
            else:
                st.error(result)


# -----------------------------
# STOCK ANALYZER DASHBOARD
# -----------------------------
def show_dashboard():
    user = st.session_state.user

    st.title("📈 StockVision")
    st.markdown("### Smart Stock Analysis & Market Insights")
    st.markdown(f"### Welcome, {user['username']} 👋")

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    st.sidebar.header("Stock Selection")

    ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL").upper()

    timeframe_options = {
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "5 Years": "5y"
    }
    selected_timeframe = st.sidebar.selectbox("Select Timeframe", list(timeframe_options.keys()))
    period = timeframe_options[selected_timeframe]

    show_candlestick = st.sidebar.checkbox("Show Candlestick Chart", value=True)
    show_volume = st.sidebar.checkbox("Show Volume Chart", value=True)
    show_data = st.sidebar.checkbox("Show Raw Data", value=False)

    # Popular Stocks Dashboard
    st.subheader("🔥 Popular Stocks Dashboard")
    popular_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN"]
    popular_data = get_popular_stocks_snapshot(popular_tickers)

    if popular_data:
        cols = st.columns(len(popular_data))
        for i, stock in enumerate(popular_data):
            with cols[i]:
                st.metric(
                    label=stock["Ticker"],
                    value=f"${stock['Price']:.2f}" if stock["Price"] is not None else "N/A",
                    delta=f"{stock['Change']:.2f}%" if stock["Change"] is not None else None
                )
    else:
        st.info("Popular stocks snapshot could not be loaded at the moment.")

    st.markdown("---")
    st.subheader(f"📊 Analysis for {ticker}")

    df = get_stock_data(ticker, period)
    info = get_stock_info(ticker)

    if df is None or df.empty:
        st.error("No stock data found. Please enter a valid stock ticker.")
        return

    # Stock metrics
    if info:
        col1, col2, col3, col4 = st.columns(4)

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        day_high = info.get("dayHigh")
        day_low = info.get("dayLow")
        volume = info.get("volume")
        market_cap = info.get("marketCap")

        with col1:
            st.metric("Current Price", f"${current_price:.2f}" if current_price else "N/A")
        with col2:
            st.metric("Day High", f"${day_high:.2f}" if day_high else "N/A")
        with col3:
            st.metric("Day Low", f"${day_low:.2f}" if day_low else "N/A")
        with col4:
            st.metric("Market Cap", f"${market_cap:,.0f}" if market_cap else "N/A")

    st.markdown("---")

    metrics = calculate_metrics(df)

    # Trend Summary
    st.subheader("📌 Trend Summary")
    trend_color = "green" if metrics["trend"] == "Uptrend" else "red" if metrics["trend"] == "Downtrend" else "gray"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Highest Closing Price", f"${metrics['max_close']:.2f}")
    c2.metric("Lowest Closing Price", f"${metrics['min_close']:.2f}")
    c3.metric("Average Closing Price", f"${metrics['avg_close']:.2f}")
    c4.markdown(f"**Trend:** :{trend_color}[{metrics['trend']}]")

    st.write(metrics["summary"])

    # Closing Price + Moving Averages
    st.subheader("📈 Closing Price with Moving Averages")
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Closing Price"))
    fig_line.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode="lines", name="20-Day MA"))
    fig_line.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode="lines", name="50-Day MA"))
    fig_line.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        height=500
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Candlestick chart
    if show_candlestick:
        st.subheader("🕯️ Candlestick Chart")
        fig_candle = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Candlestick"
        )])
        fig_candle.update_layout(
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_white",
            height=500
        )
        st.plotly_chart(fig_candle, use_container_width=True)

    # Volume chart
    if show_volume:
        st.subheader("📊 Trading Volume")
        fig_volume = go.Figure()
        fig_volume.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume"))
        fig_volume.update_layout(
            xaxis_title="Date",
            yaxis_title="Volume",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig_volume, use_container_width=True)

    # Download CSV
    st.subheader("⬇️ Download Data")
    csv = df.to_csv().encode("utf-8")
    st.download_button(
        label="Download Stock Data as CSV",
        data=csv,
        file_name=f"{ticker}_stock_data.csv",
        mime="text/csv"
    )

    # Raw data
    if show_data:
        st.subheader("📄 Raw Historical Data")
        st.dataframe(df.tail(50))

    st.markdown("---")
    st.caption("Built using Python, Streamlit, Pandas, Plotly, yfinance, and SQLite")


# -----------------------------
# MAIN APP FLOW
# -----------------------------
if st.session_state.logged_in:
    show_dashboard()
else:
    show_auth_page()