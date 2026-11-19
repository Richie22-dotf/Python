# 🎛️ Python Desktop Command Suite & AI Portfolio

A unified collection of custom macOS desktop security & telemetry utilities, cross-device Streamlit AI web apps, and iPadOS tools built in Python. Features active subnet vulnerability scanning, real-time hardware & network diagnostics, custom photo flip-clocks, and multimodal Google Gemini Vision applications.

---

## 🚀 Applications Included

### 1. Master Command Hub (`hub.py`)
* **What it does:** Central multi-process desktop launcher for your entire 6-application macOS command suite.
* **Key features:** Automatically inherits `GEMINI_API_KEY` from `~/.zshrc`, launches individual modules on demand, or deploys all 6 desktop systems simultaneously across a calculated 3x2 screen grid.

### 2. CyberGuard AI — Home Vulnerability & Recon Auditor (`cyber_guard.py`)
* **What it does:** Active home-network attack surface scanner, interactive remediation inspector, and AI Security Analyst console.
* **Key features:** Sweeps your local Wi-Fi subnet, probes 15 high-risk TCP ports (`Telnet`, `FTP`, `SMB`, `RTSP`, `RDP`, `VNC`, `UPnP/AirPlay`, `HTTP/HTTPS`), provides instant **Click-to-Inspect Remediation** playbooks per host, generates executive **Gemini SOC Analyst** threat briefings, and exports formatted **PDF Security Audit Reports** (`reportlab`).

### 3. Network Command & Speed Suite v2.1 (`scanner.py`)
* **What it does:** Real-time local network mapper and internet performance dashboard.
* **Key features:** Resolves readable device hostnames, maps IP and MAC addresses, identifies hardware manufacturers via OUI lookup, continuously monitors live internet ping (`8.8.8.8`), and runs multi-threaded Download/Upload speed tests (`speedtest-cli`).

### 4. Fointein AI Cigar Sommelier v2.0 (`mobile_cigar_app.py`)
* **What it does:** Cross-device multimodal cigar band scanner, digital humidor, and curated drink pairing studio deployed on Streamlit Cloud.
* **Key features:** Features a custom Cigar & Aged Rum SVG emblem, identifies cigar blends and tasting notes from photos or live camera, builds a **3-tier Sommelier Pairing Flight** (Spirits, Coffee/Tea, Wine/Craft Beer), includes an interactive **Pair My Drink** matcher, and generates shareable tasting cards.

### 5. 12 Esthetics AI • Beauty & Ethics Scanner (`beauty_scanner.py`)
* **What it does:** Multimodal skincare, haircare, and cosmetic ingredient & supply-chain ethics auditor deployed on Streamlit Cloud.
* **Key features:** Identifies main active and base ingredients from product labels, flags potential irritants, scores formulation cleanliness (`0–100`), audits cruelty-free status and high-risk supply chains (mica, palm oil, squalane), and saves audited items to a **Digital Vanity Shelf**.

### 6. AI Cigar Sommelier — macOS Desktop (`cigar_scanner.py`)
* **What it does:** Native macOS desktop cigar band scanner and digital humidor integrated into the Master Command Hub.
* **Key features:** Uses `google-genai` and `Pillow` (`HEIC`/`JPG`/`PNG`) to analyze cigar bands and catalog blends locally.

### 7. Luxury Photo Flip-Clock & Calendar (`clock.py`)
* **What it does:** Customizable macOS desktop flip-clock and desk calendar widget over personal photography.
* **Key features:** Translucent smoked-glass flip tiles, uniform `AM/PM` and seconds badge, gold-topped desk calendar leaf, one-click photo switcher, 4 corner positions, and brightness controls.

### 8. Global Market Streamer (`streamer.py`) & Mac System Commander (`commander.py`)
* **What they do:** Live financial market ticker (`BTC`, `ETH`, `SOL`, `TSLA`, `Gold`) and real-time macOS hardware telemetry (`CPU`, `RAM`, `Disk` via `psutil`).

---

## 🛠️ Mac Desktop Quick Start

1. **Clone the repository:**
   git clone https://github.com && cd Python

2. **Install required dependencies:**
   python3 -m pip install pillow pillow-heif google-genai pydantic yfinance psutil requests streamlit speedtest-cli reportlab

3. **Set your Google Gemini API key:**
   export GEMINI_API_KEY="your_api_key_here"

4. **Launch the 6-System Master Command Hub:**
   python3 hub.py
