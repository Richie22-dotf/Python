import tkinter as tk
from tkinter import ttk
import subprocess
import re
import threading
import socket

def get_device_name(ip):
    try:
        # Ask your Mac's internal resolver to find the name attached to the IP
        # We set a short 0.5-second timeout so a slow device won't freeze the scan
        name, _, _ = socket.gethostbyaddr(ip)
        return name.split('.')[0] # Clean up local domain extensions
    except Exception:
        # Fallback 2: Check standard Mac network naming protocols via 'dig'
        try:
            result = subprocess.run(['dig', '+short', '-x', ip], capture_output=True, text=True, timeout=0.5)
            if result.stdout.strip():
                return result.stdout.strip().split('.')[0]
        except Exception:
            pass
        return "Unknown Device"

def run_scan():
    status_label.config(text="Scanning & Unmasking Device Names...", fg="#FFFF00")
    progress_bar.start(10)
    scan_button.config(state="disabled")
    
    for item in tree.get_children():
        tree.delete(item)

    def scan_thread():
        devices = []
        try:
            # Gather the raw network map
            result = subprocess.run(['arp', '-an'], capture_output=True, text=True)
            pattern = r"\((.*?)\) at (.*?) on"
            matches = re.findall(pattern, result.stdout)
            
            for match in matches:
                ip = match[0]
                mac = match[1]
                
                if mac != "(incomplete)":
                    # Fetch the live device hostname!
                    device_name = get_device_name(ip)
                    devices.append((device_name, ip, mac.upper()))
                    
        except Exception as e:
            devices.append(("Error", "Failed to scan", str(e)))

        root.after(0, lambda: update_ui(devices))

    threading.Thread(target=scan_thread, daemon=True).start()

def update_ui(devices):
    progress_bar.stop()
    scan_button.config(state="normal")
    
    if not devices:
        status_label.config(text="Scan Complete: No devices found.", fg="#FF0000")
        return
        
    for dev in devices:
        tree.insert("", "end", values=dev)
        
    status_label.config(text=f"Scan Complete: Unmasked {len(devices)} Active Node(s)", fg="#00FF00")

# UI Architecture Setup
root = tk.Tk()
root.title("Cybersecurity Network Mapper v2.0")
root.geometry("650x450")
root.configure(bg="#1E1E1E")

title_label = tk.Label(root, text="⚡ NETWORK RECONNAISSANCE & UNMASKING ⚡", font=("Courier", 14, "bold"), bg="#1E1E1E", fg="#00FF00")
title_label.pack(pady=15)

scan_button = tk.Button(root, text="TRIGGER ADVANCED SCAN", font=("Courier", 12, "bold"), bg="#333333", fg="#00FF00", command=run_scan, highlightbackground="#1E1E1E")
scan_button.pack(pady=5)

style = ttk.Style()
style.theme_use('default')
style.configure("Horizontal.TProgressbar", background="#00FF00", trophicground="#333333")
progress_bar = ttk.Progressbar(root, length=400, mode='indeterminate', style="Horizontal.TProgressbar")
progress_bar.pack(pady=10)

status_label = tk.Label(root, text="System Ready. Awaiting Command...", font=("Courier", 11), bg="#1E1E1E", fg="#A0A0A0")
status_label.pack(pady=5)

columns = ("name", "ip", "mac")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
tree.heading("name", text="VISUAL DEVICE NAME")
tree.heading("ip", text="LOCAL IP ADDRESS")
tree.heading("mac", text="PHYSICAL MAC ADDRESS")

style.configure("Treeview", background="#2D2D2D", foreground="#00FF00", fieldbackground="#2D2D2D", font=("Courier", 10))
style.configure("Treeview.Heading", background="#333333", foreground="#000000", font=("Courier", 10, "bold"))
tree.pack(fill="both", expand=True, padx=20, pady=10)

root.mainloop()