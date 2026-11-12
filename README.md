# Python Desktop Command Suite & AI Portfolio

A unified collection of custom macOS desktop applications built in Python, featuring real-time hardware telemetry, local network mapping, live financial market streaming, and multimodal AI Vision recognition.

## Applications Included

- **Master Command Hub (`hub.py`):** Central multi-process desktop launcher with automatic API key inheritance and multi-window grid deployment.
- **AI Cigar Sommelier (`cigar_scanner.py`):** Multimodal cigar band scanner and curated digital humidor that identifies blends, wrappers, strength profiles, and drink pairings from photos.
- **Global Market Streamer (`streamer.py`):** Live multi-asset financial ticker tracking Bitcoin, Ethereum, Solana, Tesla, and Gold.
- **Mac System Commander (`commander.py`):** Live macOS hardware telemetry dashboard monitoring CPU load, RAM usage, and SSD disk capacity.
- **Network Device Scanner (`scanner.py`):** Local Wi-Fi subnet scanner mapping connected IP addresses and active network devices.
- **Digital Desktop Clock (`clock.py`):** Sleek dark-mode desktop clock and date widget with live second-by-second updates.

## Quick Start

1. Install dependencies:
   `python3 -m pip install pillow pillow-heif google-genai pydantic yfinance psutil requests`
2. Set your Gemini API key:
   `export GEMINI_API_KEY="your_api_key_here"`
3. Launch the Master Command Hub:
   `python3 hub.py`
