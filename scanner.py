import tkinter as tk
from tkinter import ttk
import subprocess
import re
import threading

def run_scan():
    # 1. Update UI to show the scanner is actively working
    status_label.config(text="Scanning Network Hardware...", fg="#FFFF00")
    progress_bar.start(10)
    scan_button.config(state="disabled")
    
    # Clear the old list data
    for item in tree.get_children():
        tree.delete(item)

    # 2. Run the scan in a background thread so the UI window doesn't freeze!
    def scan_thread():
        devices = []
        try:
            # Executes the Mac's internal Address Resolution Protocol command
            # to list all devices currently talking to your router
            result = subprocess.run(['arp', '-an'], capture_output=True, text=True)
            
            # Use regular expressions to parse out IPs and Mac Addresses cleanly
            pattern = r"\((.*?)\) at (.*?) on"
            matches = re.findall(pattern, result.stdout)
            
            for index, match in enumerate(matches):
                ip = match[0]
                mac = match[1]
                # Filter out expired or invalid entries
                if mac != "(incomplete)":
                    devices.append((f"Device #{index+1}", ip, mac.upper()))
                    
        except Exception as e:
            devices.append(("Error", "Failed to scan", str(e)))

        # 3. Drop back into the main loop to update the screen visually
        root.after(0, lambda: update_ui(devices))

    threading.Thread(target=scan_thread, daemon=True).start()

def update_ui(devices):
    # Stop animations and populate the live grid
    progress_bar.stop()
    scan_button.config(state="normal")
    
    if not devices:
        status_label.config(text="Scan Complete: No extra devices found.", fg="#FF0000")
        return
        
    for dev in devices:
        tree.insert("", "end", values=dev)
        
    status_label.config(text=f"Scan Complete: Found {len(devices)} Active Node(s)", fg="#00FF00")

# Window Architecture Setup (Dark Hacker Mode Theme)
root = tk.Tk()
root.title("Cybersecurity Network Mapper v1.0")
root.geometry("600x450")
root.configure(bg="#1E1E1E")

# Title Banner
title_label = tk.Label(root, text="⚡ LOCAL NETWORK RECONNAISSANCE ⚡", font=("Courier", 16, "bold"), bg="#1E1E1E", fg="#00FF00")
title_label.pack(pady=15)

# Action Control Button
scan_button = tk.Button(root, text="TRIGGER NETWORK SCAN", font=("Courier", 12, "bold"), bg="#333333", fg="#00FF00", command=run_scan, highlightbackground="#1E1E1E")
scan_button.pack(pady=5)

# Visual Progress Bar Loading Element
style = ttk.Style()
style.theme_use('default')
style.configure("Horizontal.TProgressbar", background="#00FF00", trophicground="#333333")
progress_bar = ttk.Progressbar(root, length=400, mode='indeterminate', style="Horizontal.TProgressbar")
progress_bar.pack(pady=10)

# Live Status Subtext
status_label = tk.Label(root, text="System Ready. Awaiting Scan Trigger...", font=("Courier", 11), bg="#1E1E1E", fg="#A0A0A0")
status_label.pack(pady=5)

# Table Grid Layout for Device Mapping Data
columns = ("name", "ip", "mac")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
tree.heading("name", text="DEVICE IDENTIFIER")
tree.heading("ip", text="LOCAL IP ADDRESS")
tree.heading("mac", text="PHYSICAL MAC ADDRESS")

# Style the grid matrix layout to be dark
style.configure("Treeview", background="#2D2D2D", foreground="#00FF00", fieldbackground="#2D2D2D", font=("Courier", 10))
style.configure("Treeview.Heading", background="#333333", foreground="#000000", font=("Courier", 10, "bold"))
tree.pack(fill="both", expand=True, padx=20, pady=10)

root.mainloop()