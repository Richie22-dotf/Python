# 🎛️ Python Desktop Command Suite & AI Portfolio

A unified collection of custom macOS desktop applications, mobile web tools, and iPadOS utilities built in Python. Features real-time hardware telemetry, local network mapping, live financial market streaming, custom photo flip-clocks, and multimodal AI Vision recognition.

---

## 🚀 Applications Included

### 1. Master Command Hub (`hub.py`)
* **What it does:** Central multi-process desktop launcher for your entire macOS application suite.
* **Key features:** Automatically inherits your `GEMINI_API_KEY` from `~/.zshrc`, launches individual modules on demand, or deploys all 5 desktop applications simultaneously in a calculated 3x2 screen grid.

### 2. AI Cigar Sommelier — Desktop (`cigar_scanner.py`)
* **What it does:** Multimodal cigar band scanner and curated digital humidor for macOS.
* **Key features:** Uses Google Gemini Vision (`google-genai`) and `Pillow` (`HEIC`/`JPG`/`PNG`) to read cigar bands from photos, identify blends, wrappers, strength scores, tasting notes, and drink pairings, and add them to your searchable mahogany-and-gold humidor.

### 3. AI Cigar Sommelier — Mobile & Web (`mobile_cigar_app.py`)
* **What it does:** Responsive web application deployed on Streamlit Cloud for iPhone, M4 iPad, and desktop browsers.
* **Key features:** Supports live mobile camera capture (`st.camera_input`) and photo uploads, dynamically discovers active Gemini Vision models via `client.models.list()`, and saves directly to your iPhone/iPad Home Screen as a full-screen web app.

### 4. Luxury Photo Flip-Clock & Calendar (`clock.py`)
* **What it does:** Customizable macOS desktop clock and desk calendar widget with personal photo backdrops.
* **Key features:** Renders translucent smoked-glass flip-clock tiles, a uniform `AM/PM` + seconds badge, and a gold-topped desk calendar leaf over any personal photo. Includes one-click controls to swap photos (`🖼️ Photo`), cycle 4 corner positions (`📍 Move`) so faces stay unobstructed, and adjust photo brightness (`☀️ Tint`).

### 5. Global Market Streamer (`streamer.py`)
* **What it does:** Live multi-asset financial price monitor.
* **Key features:** Streams real-time prices and directional indicators for Bitcoin, Ethereum, Solana, Tesla (`TSLA`), and Gold using background threading so the interface never freezes.

### 6. Mac System Commander (`commander.py`)
* **What it does:** Live macOS hardware telemetry dashboard.
* **Key features:** Monitors real-time CPU load, RAM memory usage, and SSD disk capacity using `psutil`.

### 7. Network Device Scanner (`scanner.py`)
* **What it does:** Local Wi-Fi subnet scanner and device mapper.
* **Key features:** Scans your local network to map connected IP addresses and active devices.

---

## 🛠️ Mac Desktop Quick Start

1. **Clone the repository:**
   git clone https://github.com && cd Python

2. **Install required dependencies:**
   python3 -m pip install pillow pillow-heif google-genai pydantic yfinance psutil requests streamlit

3. **Set your Google Gemini API key:**
   export GEMINI_API_KEY="your_api_key_here"

4. **Launch the Master Command Hub:**
   python3 hub.py
