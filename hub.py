import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

# Locate the exact folder where hub.py and your other apps live
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def launch_module(script_name, friendly_name):
    script_path = os.path.join(BASE_DIR, script_name)
    
    # Verify the file exists before trying to launch
    if not os.path.exists(script_path):
        messagebox.showerror("Module Missing", f"Could not find {script_name} in your project folder.")
        return
        
    try:
        # Launch the app in an independent process using the exact same Python engine
        subprocess.Popen([sys.executable, script_path], cwd=BASE_DIR)
        status_label.config(text=f"STATUS: DEPLOYED {friendly_name.upper()} 🚀", fg="#00FF00")
    except Exception as e:
        messagebox.showerror("Launch Failure", f"Failed to launch {friendly_name}:\n{e}")

def launch_all_systems():
    # Deploy all four tools at once for a full command-center screen setup
    modules = [
        ("clock.py", "Digital Clock"),
        ("scanner.py", "Network Scanner"),
        ("commander.py", "Mac Commander"),
        ("streamer.py", "Market Streamer")
    ]
    for script, name in modules:
        launch_module(script, name)
    status_label.config(text="STATUS: ALL SYSTEMS DEPLOYED & ONLINE ⚡", fg="#00E6FF")

# --- UI LAYOUT ARCHITECTURE ---
root = tk.Tk()
root.title("Master Command Hub v1.0")
root.geometry("560x540")
root.configure(bg="#0D1117")

# Header Banner
header = tk.Label(root, text="🎛️ MASTER COMMAND HUB 🎛️", font=("Courier", 18, "bold"), bg="#0D1117", fg="#58A6FF")
header.pack(pady=(20, 5))

subtitle = tk.Label(root, text="UNIFIED SUITE LAUNCHER • RICHIE22-DOTF", font=("Courier", 10), bg="#0D1117", fg="#8B949E")
subtitle.pack(pady=(0, 15))

# Live Status Readout
status_label = tk.Label(root, text="STATUS: STANDBY • SELECT MODULE TO DEPLOY", font=("Courier", 10, "bold"), bg="#0D1117", fg="#FFFF00")
status_label.pack(pady=(0, 15))

# Module Button Container
hub_frame = tk.Frame(root, bg="#161B22", bd=2, relief="groove", padx=25, pady=20)
hub_frame.pack(fill="both", expand=True, padx=30, pady=5)

# Helper to build styled launcher buttons cleanly
def create_launch_btn(parent, title, desc, color, script_file):
    btn_frame = tk.Frame(parent, bg="#161B22")
    btn_frame.pack(fill="x", pady=8)
    
    btn = tk.Button(
        btn_frame,
        text=title,
        font=("Courier", 12, "bold"),
        bg="#21262D",
        fg=color,
        width=24,
        command=lambda: launch_module(script_file, title),
        highlightbackground="#161B22"
    )
    btn.pack(side="left")
    
    lbl = tk.Label(btn_frame, text=desc, font=("Courier", 10), bg="#161B22", fg="#C9D1D9")
    lbl.pack(side="left", padx=15)

# Individual App Launchers
create_launch_btn(hub_frame, "🕒 DIGITAL CLOCK", "Date & Time Widget", "#58A6FF", "clock.py")
create_launch_btn(hub_frame, "🛡️ NETWORK SCANNER", "Wi-Fi Device Mapper", "#00FF00", "scanner.py")
create_launch_btn(hub_frame, "🕹️ MAC COMMANDER", "CPU, RAM & SSD Stats", "#00E6FF", "commander.py")
create_launch_btn(hub_frame, "📈 MARKET STREAMER", "Crypto, TSLA & Gold", "#FFD700", "streamer.py")

# Divider
divider = tk.Frame(hub_frame, height=2, bg="#30363D")
divider.pack(fill="x", pady=15)

# Master "Launch All" Override Button
all_btn = tk.Button(
    hub_frame,
    text="⚡ DEPLOY ALL SYSTEMS SIMULTANEOUSLY ⚡",
    font=("Courier", 12, "bold"),
    bg="#1F6FEB",
    fg="white",
    command=launch_all_systems,
    highlightbackground="#161B22"
)
all_btn.pack(fill="x", pady=5)

# Footer
footer = tk.Label(root, text="Multi-Process Execution Engine • Ready", font=("Courier", 9), bg="#0D1117", fg="#8B949E")
footer.pack(pady=15)

root.mainloop()