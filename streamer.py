import tkinter as tk
from tkinter import ttk
import threading
import time
import sys

try:
    import yfinance as yf
except ImportError:
    yf = None

ASSETS = [
    ("BTC-USD", "BITCOIN", "$"),
    ("ETH-USD", "ETHEREUM", "$"),
    ("SOL-USD", "SOLANA", "$"),
    ("TSLA", "TESLA INC", "$"),
    ("NVDA", "NVIDIA CORP", "$"),
    ("GC=F", "GOLD FUTURES", "$")
]

root = tk.Tk()
root.title("Global Market Streamer v2.0 - Live Sparklines & Alerts")
root.geometry("680x540")
if len(sys.argv) > 1:
    root.geometry(sys.argv.pop())
root.configure(bg="#090D12")

BG = "#090D12"
CARD = "#111720"
GREEN = "#00FF66"
RED = "#FF4D4D"
CYAN = "#00E6FF"
GOLD = "#D4AF37"
TEXT = "#E6EDF3"
MUTED = "#8B949E"

hdr = tk.Frame(root, bg=BG)
hdr.pack(fill="x", padx=18, pady=(14, 6))
tk.Label(hdr, text="GLOBAL MARKET STREAMER v2.0", font=("Courier", 15, "bold"), bg=BG, fg=CYAN).pack(side="left")
status_lbl = tk.Label(hdr, text="SYNCING LIVE FEED...", font=("Courier", 10, "bold"), bg=BG, fg=GOLD)
status_lbl.pack(side="right")

rows_frame = tk.Frame(root, bg=BG)
rows_frame.pack(fill="both", expand=True, padx=18, pady=4)

ui_cards = {}
latest_prices = {}

for sym, label, prefix in ASSETS:
    card = tk.Frame(rows_frame, bg=CARD, bd=1, relief="groove", padx=12, pady=8)
    card.pack(fill="x", pady=4)

    left = tk.Frame(card, bg=CARD, width=155)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)
    tk.Label(left, text=sym.replace("-USD", "").replace("=F", ""), font=("Courier", 12, "bold"), bg=CARD, fg=TEXT, anchor="w").pack(fill="x")
    tk.Label(left, text=label, font=("Courier", 8), bg=CARD, fg=MUTED, anchor="w").pack(fill="x")

    canvas = tk.Canvas(card, width=210, height=38, bg="#0D1219", highlightthickness=1, highlightbackground="#1E293B")
    canvas.pack(side="left", padx=12)

    right = tk.Frame(card, bg=CARD)
    right.pack(side="right", fill="y")
    price_lbl = tk.Label(right, text="--.--", font=("Courier", 13, "bold"), bg=CARD, fg=TEXT, anchor="e")
    price_lbl.pack(fill="x")
    chg_lbl = tk.Label(right, text="0.00%", font=("Courier", 9, "bold"), bg=CARD, fg=MUTED, anchor="e")
    chg_lbl.pack(fill="x")

    ui_cards.update({sym: (price_lbl, chg_lbl, canvas, prefix)})

alert_frame = tk.Frame(root, bg=CARD, bd=1, relief="groove", padx=12, pady=8)
alert_frame.pack(fill="x", padx=18, pady=(4, 14))

tk.Label(alert_frame, text="TARGET ALERT:", font=("Courier", 9, "bold"), bg=CARD, fg=GOLD).pack(side="left")
alert_sym = ttk.Combobox(alert_frame, values=[a[0] for a in ASSETS], width=9, state="readonly")
alert_sym.set("BTC-USD")
alert_sym.pack(side="left", padx=6)

alert_price_var = tk.StringVar(value="")
alert_entry = tk.Entry(alert_frame, textvariable=alert_price_var, width=10, bg="#0D1219", fg=TEXT, insertbackground=TEXT, font=("Courier", 10))
alert_entry.pack(side="left", padx=4)

alert_status = tk.Label(alert_frame, text="Enter target price (e.g. 95000)", font=("Courier", 9), bg=CARD, fg=MUTED)
alert_status.pack(side="left", padx=8)

active_alert = {"sym": None, "target": None}

def set_alert():
    try:
        val = float(alert_price_var.get().strip())
        s = alert_sym.get()
        active_alert.update({"sym": s, "target": val})
        alert_status.config(text=f"ARMED: {s} @ ${val:,.2f}", fg=CYAN)
    except ValueError:
        alert_status.config(text="Invalid number", fg=RED)

tk.Button(alert_frame, text="ARM", font=("Courier", 9, "bold"), bg="#1F2937", fg=GREEN, command=set_alert, padx=8).pack(side="right")

def draw_sparkline(canvas, points, color):
    canvas.delete("all")
    if len(points) < 2:
        return
    mn, mx = min(points), max(points)
    span = (mx - mn) if mx != mn else 1.0
    w, h = 210, 38
    coords = []
    for i, val in enumerate(points):
        x = 6 + (i / (len(points) - 1)) * (w - 12)
        y = (h - 6) - ((val - mn) / span) * (h - 12)
        coords.extend([x, y])
    canvas.create_line(*coords, fill=color, width=2, smooth=True)

def fetch_market_data():
    if yf is None:
        status_lbl.config(text="ERR: pip install yfinance", fg=RED)
        return

    def worker():
        updates = []
        for sym, _, _ in ASSETS:
            try:
                hist = yf.Ticker(sym).history(period="5d", interval="1h")
                closes = [float(v) for v in hist["Close"].dropna().tolist()]
                if len(closes) >= 2:
                    curr = closes[-1]
                    prev = closes[-24] if len(closes) >= 24 else closes[0]
                    pct = ((curr - prev) / prev) * 100.0
                    updates.append((sym, curr, pct, closes[-36:]))
            except Exception:
                continue

        def apply_ui():
            for sym, curr, pct, series in updates:
                latest_prices.update({sym: curr})
                p_lbl, c_lbl, canv, prefix = ui_cards.get(sym)
                color = GREEN if pct >= 0 else RED
                sign = "+" if pct >= 0 else ""
                p_lbl.config(text=f"{prefix}{curr:,.2f}", fg=TEXT)
                c_lbl.config(text=f"{sign}{pct:.2f}% (24h)", fg=color)
                draw_sparkline(canv, series, color)

            t_sym = active_alert.get("sym")
            t_val = active_alert.get("target")
            if t_sym and t_val is not None and t_sym in latest_prices:
                cur_p = latest_prices.get(t_sym)
                if cur_p >= t_val:
                    alert_status.config(text=f"TRIGGERED! {t_sym} HIT ${cur_p:,.2f}", fg=GREEN)

            status_lbl.config(text=f"LIVE - {time.strftime(chr(37)+chr(72)+chr(58)+chr(37)+chr(77)+chr(58)+chr(37)+chr(83))}", fg=GREEN)

        root.after(0, apply_ui)

    threading.Thread(target=worker, daemon=True).start()
    root.after(20000, fetch_market_data)

fetch_market_data()
root.mainloop()
