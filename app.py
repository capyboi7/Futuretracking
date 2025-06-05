import streamlit as st
import requests
import time
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Cấu hình trang
st.set_page_config(page_title="🚀 Futures Pump Detector", layout="wide")
st.title("🚀 Binance Futures Token Pump (1 min ≥ 1%)")
placeholder = st.empty()

# Auto reload mỗi 60 giây
st_autorefresh(interval=60 * 1000, key="refresh")

# Lấy danh sách các symbol futures
@st.cache_data(ttl=300)
def get_futures_symbols():
    try:
        url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
        res = requests.get(url).json()
        symbols = res.get("symbols", [])
        return [s["symbol"] for s in symbols if s.get("contractType") == "PERPETUAL"]
    except Exception as e:
        st.error(f"Lỗi khi lấy symbol: {e}")
        return []

# Lấy giá hiện tại
def get_prices():
    try:
        url = "https://fapi.binance.com/fapi/v1/ticker/price"
        res = requests.get(url).json()
        return {item["symbol"]: float(item["price"]) for item in res}
    except Exception as e:
        st.error(f"Lỗi khi lấy giá: {e}")
        return {}

# Lấy khối lượng 24h
def get_24h_volume():
    try:
        url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
        res = requests.get(url).json()
        return {item["symbol"]: float(item["quoteVolume"]) for item in res}
    except Exception as e:
        st.error(f"Lỗi khi lấy volume: {e}")
        return {}

# Lưu dữ liệu giá cũ bằng session_state
if "prev_prices" not in st.session_state:
    st.session_state.prev_prices = get_prices()

# Tải data mới
futures_symbols = get_futures_symbols()
curr_prices = get_prices()
volumes = get_24h_volume()
movers = []

# Tính % thay đổi
for symbol in futures_symbols:
    if symbol in st.session_state.prev_prices and symbol in curr_prices:
        old = st.session_state.prev_prices[symbol]
        new = curr_prices[symbol]
        if old == 0:
            continue
        change_pct = ((new - old) / old) * 100
        if change_pct >= 1:
            vol = volumes.get(symbol, 0)
            movers.append({
                "Symbol": symbol,
                "Change %": round(change_pct, 1),
                "Volume (24h USDT)": f"{vol:,.0f}"
            })

# Hiển thị kết quả
df = pd.DataFrame(movers)
df = df.sort_values(by="Change %", ascending=False)

with placeholder.container():
    if df.empty:
        st.info("⏳ Không có token nào tăng ≥ 1% trong 1 phút gần nhất.")
    else:
        st.dataframe(df, use_container_width=True)

# Cập nhật giá cũ cho lần kế tiếp
st.session_state.prev_prices = curr_prices

