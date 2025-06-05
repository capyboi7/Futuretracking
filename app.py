import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="🚀 Futures Pump Detector", layout="wide")
st.title("🚀 Binance Futures Token Pump (1 min ≥ 2%)")
placeholder = st.empty()

@st.cache_data(ttl=60)
def get_futures_symbols():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    res = requests.get(url).json()
    return [s["symbol"] for s in res["symbols"] if s["contractType"] == "PERPETUAL"]

def get_prices():
    url = "https://fapi.binance.com/fapi/v1/ticker/price"
    res = requests.get(url).json()
    return {item["symbol"]: float(item["price"]) for item in res}

def get_24h_volume():
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
    res = requests.get(url).json()
    return {item["symbol"]: float(item["quoteVolume"]) for item in res}

futures_symbols = get_futures_symbols()
prev_prices = get_prices()
time.sleep(60)

while True:
    curr_prices = get_prices()
    volumes = get_24h_volume()
    movers = []

    for symbol in futures_symbols:
        if symbol in prev_prices and symbol in curr_prices:
            old = prev_prices[symbol]
            new = curr_prices[symbol]
            change_pct = ((new - old) / old) * 100
            if change_pct >= 2:
                vol = volumes.get(symbol, 0)
                movers.append({
                    "Symbol": symbol,
                    "Change %": round(change_pct, 2),
                    "Volume (24h USDT)": f"{vol:,.0f}"
                })

    df = pd.DataFrame(movers)
    df = df.sort_values(by="Change %", ascending=False)

    with placeholder.container():
        if df.empty:
            st.info("⏳ Không có token nào tăng ≥ 2% trong 1 phút gần nhất.")
        else:
            st.dataframe(df, use_container_width=True)

    prev_prices = curr_prices
    time.sleep(60)
