import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_env_with_api_key():
    # Ensure launched apps inherit GEMINI_API_KEY from ~/.zshrc even if launched outside terminal
    env = os.environ.copy()
    if "GEMINI_API_KEY" not in env:
        zshrc_path = os.path.expanduser("~/.zshrc")
        if os.path.exists(zshrc_path):
            with open(zshrc_path, "r") as f:
                for line in f:
                    if "GEMINI_API_KEY=" in line and not line.strip().startswith("#"):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        env["GEMINI_API_KEY"] = val
    return env

def launch_module(script_name, friendly_name, geometry_arg=None):
    script_path = os.path.join(BASE_DIR, script_name)
    
    if not os.path.exists(script_path):
        messagebox.showerror("Module Missing", f"Could not find {script_name} in your project folder.")
        return
        
    try:
        cmd = [sys.executable, script_path]
        if geometry_arg:
            cmd.append(geometry_arg)
        subprocess.Popen(cmd, cwd=BASE_DIR, env=get_env_with_api_key())
        status_label.config(text=f"STATUS: DEPLOYED {friendly_name.upper()} 🚀", fg="#00FF00")
    except Exception as e:
        messagebox.showerror("Launch Failure", f"Failed to launch {friendly_name}:\n{e}")

def launch_all_systems():
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    
    # Calculate a 3-column x 2-row grid for all 5 applications
    col_w = screen_w // 3
    row_h = (screen_h - 60) // 2
    
    modules = [
        ("clock.py", "Digital Clock", f"{col_w-15}x{row_h-30}+10+35"),
        ("scanner.py", "Network Scanner", f"{col_w-15}x{row_h-30}+{col_w+10}+35"),
        ("commander.py", "Mac Commander", f"{col_w-15}x{row_h-30}+{(col_w*2)+10}+35"),
        ("streamer.py", "Market Streamer", f"{col_w-15}x{row_h-30}+10+{row_h+45}"),
        ("cigar_scanner.py", "Cigar Sommelier", f"{(col_w*2)-15}x{row_h-30}+{col_w+10}+{row_h+45}")
    ]
    
    for script, name, pos in modules:
        launch_module(script, name, pos)
        
    root.iconify()
    status_label.config(text="STATUS: ALL 5 SYSTEMS DEPLOYED & ONLINE ⚡", fg="#00E6FF")

# --- UI LAYOUT ARCHITECTURE ---
root = tk.Tk()
root.title("Master Command Hub v1.2")
root.geometry("580x610")
root.configure(bg="#0D1117")

header = tk.Label(root, text="🎛️ MASTER COMMAND HUB 🎛️", font=("Courier", 18, "bold"), bg="#0D1117", fg="#58A6FF")
header.pack(pady=(20, 5))

subtitle = tk.Label(root, text="UNIFIED 5-APP SUITE LAUNCHER • RICHIE22-DOTF", font=("Courier", 10), bg="#0D1117", fg="#8B949E")
subtitle.pack(pady=(0, 15))

status_label = tk.Label(root, text="STATUS: STANDBY • SELECT MODULE TO DEPLOY", font=("Courier", 10, "bold"), bg="#0D1117", fg="#FFFF00")
status_label.pack(pady=(0, 15))

hub_frame = tk.Frame(root, bg="#161B22", bd=2, relief="groove", padx=25, pady=20)
hub_frame.pack(fill="both", expand=True, padx=30, pady=5)

def create_launch_btn(parent, title, desc, color, script_file):
    btn_frame = tk.Frame(parent, bg="#161B22")
    btn_frame.pack(fill="x", pady=7)
    
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

create_launch_btn(hub_frame, "🕒 DIGITAL CLOCK", "Date & Time Widget", "#58A6FF", "clock.py")
create_launch_btn(hub_frame, "🛡️ NETWORK SCANNER", "Wi-Fi Device Mapper", "#00FF00", "scanner.py")
create_launch_btn(hub_frame, "🕹️ MAC COMMANDER", "CPU, RAM & SSD Stats", "#00E6FF", "commander.py")
create_launch_btn(hub_frame, "📈 MARKET STREAMER", "Crypto, TSLA & Gold", "#FFD700", "streamer.py")
create_launch_btn(hub_frame, "🍂 CIGAR SOMMELIER", "AI Band Vision & Humidor", "#D4AF37", "cigar_scanner.py")

divider = tk.Frame(hub_frame, height=2, bg="#30363D")
divider.pack(fill="x", pady=15)

all_btn = tk.Button(
    hub_frame,
    text="⚡ DEPLOY ALL 5 SYSTEMS ⚡",
    font=("Courier", 12, "bold"),
    bg="#1F6FEB",
    fg="white",
    command=launch_all_systems,
    highlightbackground="#161B22"
)
all_btn.pack(fill="x", pady=5)

footer = tk.Label(root, text="Multi-Process Suite Engine • AI Ready", font=("Courier", 9), bg="#0D1117", fg="#8B949E")
footer.pack(pady=15)

root.mainloop()
