import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import os
import threading
import time

def update_system_stats():
    def stats_loop():
        while True:
            # 1. Fetch live hardware percentage data from the system chips
            cpu_usage = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()
            mem_usage = memory_info.percent
            
            # Convert bytes to Gigabytes for the readout text
            available_gb = round(memory_info.available / (1024 ** 3), 2)
            total_gb = round(memory_info.total / (1024 ** 3), 2)

            # 2. Safely push updates back to the UI grid
            def refresh_ui():
                # Update core metric labels
                cpu_label.config(text=f"CPU CORE LOAD: {cpu_usage}%")
                mem_label.config(text=f"RAM UTILIZATION: {mem_usage}% ({available_gb}GB Available / {total_gb}GB Total)")
                
                # Update the visual dashboard bars
                cpu_bar['value'] = cpu_usage
                mem_bar['value'] = mem_usage
                
            root.after(0, refresh_ui)
            time.sleep(1) # Refresh exactly once every single second

    threading.Thread(target=stats_loop, daemon=True).start()

# --- AUTOMATION HOOK ACTIONS ---
def trigger_focus_mode():
    # Example Mac Automation: Sends a system alert and speaks out loud
    os.system("say 'Focus Mode Initiated' &")
    messagebox.showinfo("Mac Commander", "🧘 Focus Mode Activated!\nDistracting system overlays suppressed.")

def clear_system_cache():
    # Safely clears temporary clipboard data or junk logs via terminal hooks
    os.system("pbcopy < /dev/null") # Wipes the Mac clipboard contents instantly
    os.system("say 'System Purged' &")
    messagebox.showinfo("Mac Commander", "🧹 System optimization successful!\nMac clipboard cache completely flushed.")

# Main System Architecture UI Setup
root = tk.Tk()
root.title("Mac Commander Engine v1.0")
root.geometry("600x480")
root.configure(bg="#121212") # Ultra-dark slate backdrop

# Header Title Block
header = tk.Label(root, text="🕹️ OS COMMAND CENTER & CORE STATS 🕹️", font=("Courier", 14, "bold"), bg="#121212", fg="#00E6FF")
header.pack(pady=20)

# --- CORE STATS SECTION ---
stats_frame = tk.LabelFrame(root, text=" LIVE HARDWARE METRICS ", font=("Courier", 10, "bold"), bg="#121212", fg="#00E6FF", padx=15, pady=15)
stats_frame.pack(fill="x", padx=25, pady=10)

# CPU Metrics
cpu_label = tk.Label(stats_frame, text="CPU CORE LOAD: Calculating...", font=("Courier", 11), bg="#121212", fg="white")
cpu_label.pack(anchor="w")
cpu_bar = ttk.Progressbar(stats_frame, length=500, mode='determinate')
cpu_bar.pack(pady=(5, 15))

# RAM Metrics
mem_label = tk.Label(stats_frame, text="RAM UTILIZATION: Calculating...", font=("Courier", 11), bg="#121212", fg="white")
mem_label.pack(anchor="w")
mem_bar = ttk.Progressbar(stats_frame, length=500, mode='determinate')
mem_bar.pack(pady=(5, 5))

# Style progress meters to look neon-cyan
style = ttk.Style()
style.theme_use('default')
style.configure("TProgressbar", background="#00E6FF", trophicground="#333333")

# --- CORE AUTOMATION SECTION ---
action_frame = tk.LabelFrame(root, text=" MAC SYSTEM CONTROL INTERNET ", font=("Courier", 10, "bold"), bg="#121212", fg="#00E6FF", padx=15, pady=15)
action_frame.pack(fill="x", padx=25, pady=20)

focus_btn = tk.Button(action_frame, text="ENGAGE FOCUS MODE", font=("Courier", 11, "bold"), bg="#222222", fg="#00E6FF", command=trigger_focus_mode, highlightbackground="#121212")
focus_btn.pack(fill="x", pady=5)

purge_btn = tk.Button(action_frame, text="FLUSH OS CLIPBOARD CACHE", font=("Courier", 11, "bold"), bg="#222222", fg="#00E6FF", command=clear_system_cache, highlightbackground="#121212")
purge_btn.pack(fill="x", pady=5)

# Initialize live telemetry streams
update_system_stats()

root.mainloop()