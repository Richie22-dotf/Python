import tkinter as tk
import requests
import yfinance as yf
import threading
import time

# Store previous prices to detect upward or downward movement
last_prices = {"BTC": 0.0, "ETH": 0.0, "SOL": 0.0, "TSLA": 0.0, "GOLD": 0.0}

def get_coinbase_price(coin_symbol):
    parts = ["https://coinbase.com", "v2", "prices", f"{coin_symbol}-USD", "spot"]
    url = "/".join(parts)
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()
    data = response.json()
    return float(data["data"]["amount"])

def get_yahoo_price(ticker_symbol):
    # yfinance handles all URL routing and security headers automatically
    ticker = yf.Ticker(ticker_symbol)
    return float(ticker.fast_info["last_price"])

def fetch_live_data():
    def stream_loop():
        while True:
            try:
                # 1. Fetch live crypto prices from Coinbase
                btc_price = get_coinbase_price("BTC")
                eth_price = get_coinbase_price("ETH")
                sol_price = get_coinbase_price("SOL")
                
                # 2. Fetch live stock and commodity prices via yfinance
                tsla_price = get_yahoo_price("TSLA")
                gold_price = get_yahoo_price("GC=F")
                
                # 3. Update the visual dashboard safely
                def update_ui():
                    status_label.config(text="STATUS: MULTI-MARKET STREAM ACTIVE 🟢", fg="#00FF00")
                    update_asset_display(btc_label, "BITCOIN (BTC)", btc_price, "BTC")
                    update_asset_display(eth_label, "ETHEREUM (ETH)", eth_price, "ETH")
                    update_asset_display(sol_label, "SOLANA (SOL)", sol_price, "SOL")
                    update_asset_display(tsla_label, "TESLA (TSLA)", tsla_price, "TSLA")
                    update_asset_display(gold_label, "GOLD (XAU)", gold_price, "GOLD")
                
                root.after(0, update_ui)
                
            except Exception as e:
                print(f"Stream Error: {e}")
                root.after(0, lambda: status_label.config(text="STATUS: RECONNECTING TO STREAM... 🟡", fg="#FFFF00"))
            
            time.sleep(5)

    threading.Thread(target=stream_loop, daemon=True).start()

def update_asset_display(label_widget, name, current_price, asset_key):
    global last_prices
    old_price = last_prices[asset_key]
    
    if old_price == 0.0:
        color = "#FFFFFF"
        arrow = "●"
    elif current_price > old_price:
        color = "#00FF00"
        arrow = "▲"
    elif current_price < old_price:
        color = "#FF3333"
        arrow = "▼"
    else:
        color = "#A0A0A0"
        arrow = "―"
        
    last_prices[asset_key] = current_price
    label_widget.config(text=f"{name:<15}: ${current_price:,.2f}  {arrow}", fg=color)

# --- UI LAYOUT ARCHITECTURE ---
root = tk.Tk()
root.title("Global Multi-Market Streamer v2.1")
root.geometry("580x520")
import sys
if len(sys.argv) > 1:
    root.geometry(sys.argv[1])                
root.configure(bg="#0D1117")

header = tk.Label(root, text="📈 GLOBAL MULTI-MARKET STREAMER 📈", font=("Courier", 15, "bold"), bg="#0D1117", fg="#58A6FF")
header.pack(pady=(20, 5))

status_label = tk.Label(root, text="STATUS: INITIALIZING CLOUD HANDSHAKE...", font=("Courier", 10, "bold"), bg="#0D1117", fg="#FFFF00")
status_label.pack(pady=(0, 15))

ticker_frame = tk.Frame(root, bg="#161B22", bd=2, relief="groove", padx=20, pady=15)
ticker_frame.pack(fill="both", expand=True, padx=30, pady=10)

# Asset Price Labels
btc_label = tk.Label(ticker_frame, text="BITCOIN (BTC)  : Fetching...", font=("Courier", 15, "bold"), bg="#161B22", fg="white")
btc_label.pack(pady=10, anchor="w")

eth_label = tk.Label(ticker_frame, text="ETHEREUM (ETH) : Fetching...", font=("Courier", 15, "bold"), bg="#161B22", fg="white")
eth_label.pack(pady=10, anchor="w")

sol_label = tk.Label(ticker_frame, text="SOLANA (SOL)   : Fetching...", font=("Courier", 15, "bold"), bg="#161B22", fg="white")
sol_label.pack(pady=10, anchor="w")

# Divider line between Crypto and Stocks/Commodities
divider = tk.Frame(ticker_frame, height=2, bg="#30363D")
divider.pack(fill="x", pady=10)

tsla_label = tk.Label(ticker_frame, text="TESLA (TSLA)   : Fetching...", font=("Courier", 15, "bold"), bg="#161B22", fg="white")
tsla_label.pack(pady=10, anchor="w")

gold_label = tk.Label(ticker_frame, text="GOLD (XAU)     : Fetching...", font=("Courier", 15, "bold"), bg="#161B22", fg="white")
gold_label.pack(pady=10, anchor="w")

footer = tk.Label(root, text="Coinbase + Yahoo Finance Feeds • Auto-Syncs Every 5s", font=("Courier", 9), bg="#0D1117", fg="#8B949E")
footer.pack(pady=15)

fetch_live_data()
root.mainloop()
