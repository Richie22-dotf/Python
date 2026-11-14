import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import socket
import re
import sys

try:
    import speedtest
except ImportError:
    speedtest = None

OUI_VENDORS = {
    "00:03:93": "Apple", "00:05:02": "Apple", "00:0A:27": "Apple", "00:0A:95": "Apple",
    "00:11:24": "Apple", "00:14:51": "Apple", "00:16:CB": "Apple", "00:17:F2": "Apple",
    "00:19:E3": "Apple", "00:1B:63": "Apple", "00:1E:C2": "Apple", "00:21:E9": "Apple",
    "00:23:12": "Apple", "00:23:DF": "Apple", "00:25:00": "Apple", "00:25:BC": "Apple",
    "00:26:08": "Apple", "00:26:B0": "Apple", "28:CF:E9": "Apple", "3C:07:54": "Apple",
    "40:6C:8F": "Apple", "60:03:08": "Apple", "70:56:81": "Apple", "88:66:5A": "Apple",
    "A4:83:E7": "Apple", "AC:BC:32": "Apple", "D0:03:4B": "Apple", "F0:18:98": "Apple",
    "B8:27:EB": "Raspberry Pi", "DC:A6:32": "Raspberry Pi", "E4:5F:01": "Raspberry Pi",
    "00:0E:58": "Sonos", "5C:AA:FD": "Sonos", "78:28:CA": "Sonos", "94:9F:3E": "Sonos",
    "B0:A7:37": "Roku", "D8:31:34": "Roku", "CC:6D:A0": "Roku", "AC:3A:7A": "Roku",
    "18:B4:30": "Google Nest", "64:16:66": "Google Nest", "F4:F5:D8": "Google",
    "30:FD:38": "Google", "54:60:09": "Google", "A4:77:33": "Google",
    "00:17:88": "Philips Hue", "EC:B5:FA": "Philips Hue",
    "44:65:0D": "Amazon Echo", "68:37:E9": "Amazon", "74:C2:46": "Amazon", "F0:27:2D": "Amazon",
    "00:1A:11": "Google", "34:CE:00": "Xiaomi", "7C:2F:80": "Gigaset",
    "00:50:56": "VMware", "08:00:27": "VirtualBox",
    "00:1B:44": "SanDisk", "00:E0:4C": "Realtek", "00:15:5D": "Microsoft",
    "24:5E:BE": "QNAP", "00:11:32": "Synology",
    "00:04:4B": "NVIDIA", "48:B0:2D": "NVIDIA",
    "74:DA:38": "Edimax", "C0:25:E9": "TP-Link", "50:C7:BF": "TP-Link", "98:DA:C4": "TP-Link",
    "80:7D:3A": "Espressif Smart Home", "24:0A:C4": "Espressif Smart Home",
    "30:AE:A4": "Espressif Smart Home", "CC:50:E3": "Espressif Smart Home"
}

def get_vendor(mac):
    if not mac or mac == "(incomplete)":
        return "Unknown"
    parts = [p.zfill(2).upper() for p in mac.split(":")]
    if len(parts) < 3:
        return "Unknown"
    first_byte = int(next(iter(parts)), 16)
    if first_byte & 0x02:
        return "Private Wi-Fi (iOS/Mac/Android)"
    prefix = ":".join(parts[:3])
    return OUI_VENDORS.get(prefix, "Network Device")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = next(iter(s.getsockname()))
        s.close()
        return ip
    except Exception:
        return "192.168.1.1"

def resolve_device_name(ip, vendor, my_ip, arp_host=""):
    if arp_host and arp_host != "?":
        return arp_host.replace(".lan", "").replace(".local", "")
    if ip == my_ip:
        return socket.gethostname().replace(".local", "") + " (This Mac)"
    if ip.endswith(".1") or ip.endswith(".254"):
        return "Main Wi-Fi Router / Gateway"

    try:
        host = next(iter(socket.gethostbyaddr(ip)))
        if host and host != ip:
            return host.replace(".lan", "").replace(".local", "")
    except Exception:
        pass

    try:
        out = subprocess.check_output(["smbutil", "status", "-ae", ip], stderr=subprocess.DEVNULL, timeout=0.6).decode("utf-8", errors="ignore")
        m = re.search(r"Server:\s+([^\s\r\n]+)", out)
        if m:
            return m.group(1)
    except Exception:
        pass

    last_octet = ip.split(".")[-1]
    if "Apple" in vendor:
        return f"Apple Device (.{last_octet})"
    if "Private Wi-Fi" in vendor:
        return f"Mobile / Laptop (.{last_octet})"
    return f"{vendor} (.{last_octet})"

root = tk.Tk()
root.title("Network Command & Speed Suite v2.1")
root.geometry("880x580")
if len(sys.argv) > 1:
    root.geometry(sys.argv.pop())
root.configure(bg="#0D1117")

BG = "#0D1117"
CARD = "#161B22"
GREEN = "#00FF66"
CYAN = "#00E6FF"
GOLD = "#D4AF37"
TEXT = "#E6EDF3"
MUTED = "#8B949E"

header_frame = tk.Frame(root, bg=BG)
header_frame.pack(fill="x", padx=20, pady=(15, 8))

tk.Label(header_frame, text="🛡️ NETWORK COMMAND & SPEED SUITE v2.1", font=("Courier", 16, "bold"), bg=BG, fg=GREEN).pack(side="left")
local_ip = get_local_ip()
tk.Label(header_frame, text=f"LOCAL IP: {local_ip}", font=("Courier", 11, "bold"), bg=BG, fg=CYAN).pack(side="right")

metrics_frame = tk.Frame(root, bg=BG)
metrics_frame.pack(fill="x", padx=20, pady=6)

def make_metric_card(parent, title, default_val, color):
    card = tk.Frame(parent, bg=CARD, bd=1, relief="groove", padx=12, pady=10)
    card.pack(side="left", fill="both", expand=True, padx=4)
    tk.Label(card, text=title, font=("Courier", 9, "bold"), bg=CARD, fg=MUTED).pack()
    val_lbl = tk.Label(card, text=default_val, font=("Courier", 15, "bold"), bg=CARD, fg=color)
    val_lbl.pack(pady=(4, 0))
    return val_lbl

dl_lbl = make_metric_card(metrics_frame, "DOWNLOAD SPEED", "-- Mbps", GREEN)
ul_lbl = make_metric_card(metrics_frame, "UPLOAD SPEED", "-- Mbps", CYAN)
ping_lbl = make_metric_card(metrics_frame, "INTERNET PING", "-- ms", GOLD)
dev_count_lbl = make_metric_card(metrics_frame, "ACTIVE DEVICES", "0 Online", "#FF7B72")

ctrl_frame = tk.Frame(root, bg=BG)
ctrl_frame.pack(fill="x", padx=20, pady=10)

status_lbl = tk.Label(ctrl_frame, text="STATUS: READY FOR RECON OR SPEED TEST", font=("Courier", 10, "bold"), bg=BG, fg=GOLD)
status_lbl.pack(side="left")

def run_speed_test():
    if speedtest is None:
        status_lbl.config(text="ERR: Run 'pip install speedtest-cli' first", fg="#FF5555")
        return

    btn_speed.config(state="disabled")
    status_lbl.config(text="STATUS: TESTING DOWNLOAD & UPLOAD SPEEDS (~15s)...", fg=CYAN)
    dl_lbl.config(text="Testing...")
    ul_lbl.config(text="Testing...")

    def worker():
        try:
            st = speedtest.Speedtest(secure=True)
            st.get_best_server()
            dl = st.download() / 1_000_000
            ul = st.upload() / 1_000_000
            ping_ms = st.results.ping

            def update_ui():
                dl_lbl.config(text=f"{dl:.1f} Mbps")
                ul_lbl.config(text=f"{ul:.1f} Mbps")
                ping_lbl.config(text=f"{ping_ms:.0f} ms")
                status_lbl.config(text="STATUS: SPEED TEST COMPLETE ⚡", fg=GREEN)
                btn_speed.config(state="normal")
            root.after(0, update_ui)
        except Exception as e:
            err = str(e)[:40]
            def err_ui():
                dl_lbl.config(text="-- Mbps")
                ul_lbl.config(text="-- Mbps")
                status_lbl.config(text=f"SPEED TEST ERR: {err}", fg="#FF5555")
                btn_speed.config(state="normal")
            root.after(0, err_ui)

    threading.Thread(target=worker, daemon=True).start()

def scan_network():
    btn_scan.config(state="disabled")
    status_lbl.config(text="STATUS: SWEEPING WI-FI & RESOLVING DEVICE NAMES...", fg=CYAN)

    def worker():
        try:
            subnet = ".".join(local_ip.split(".")[:3])
            procs = []
            for i in range(1, 255):
                target = f"{subnet}.{i}"
                p = subprocess.Popen(["ping", "-c", "1", "-W", "200", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                procs.append(p)
            for p in procs:
                p.wait()

            arp_out = subprocess.check_output(["arp", "-a"]).decode("utf-8", errors="ignore")
            raw_entries = []
            for line in arp_out.splitlines():
                host_match = re.match(r"^([^\s?]+)\s+\((\d+\.\d+\.\d+\.\d+)\)", line)
                ip_match = re.search(r"\((\d+\.\d+\.\d+\.\d+)\)", line)
                mac_match = re.search(r"at\s+([0-9a-fA-F:]+)", line)
                if ip_match and mac_match:
                    ip = ip_match.group(1)
                    mac = mac_match.group(1)
                    arp_host = host_match.group(1) if host_match else ""
                    if mac != "ff:ff:ff:ff:ff:ff" and not ip.endswith(".255"):
                        raw_entries.append((ip, mac.upper(), arp_host))

            devices = []
            lock = threading.Lock()
            def resolve_worker(ip, mac, arp_host):
                vendor = get_vendor(mac)
                name = resolve_device_name(ip, vendor, local_ip, arp_host)
                with lock:
                    devices.append((name, ip, mac, vendor))

            threads = []
            for ip, mac, arp_host in raw_entries:
                t = threading.Thread(target=resolve_worker, args=(ip, mac, arp_host))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()

            devices.sort(key=lambda row: int(list(row).pop(1).split(chr(46)).pop()))

            def update_table():
                for row in tree.get_children():
                    tree.delete(row)
                for name, ip, mac, vendor in devices:
                    tree.insert("", "end", values=(name, ip, mac, vendor))
                dev_count_lbl.config(text=f"{len(devices)} Online")
                status_lbl.config(text=f"STATUS: MAPPED {len(devices)} NAMED DEVICES 🛡️", fg=GREEN)
                btn_scan.config(state="normal")

            root.after(0, update_table)
        except Exception as e:
            err = str(e)[:40]
            root.after(0, lambda: (status_lbl.config(text=f"SCAN ERR: {err}", fg="#FF5555"), btn_scan.config(state="normal")))

    threading.Thread(target=worker, daemon=True).start()

btn_speed = tk.Button(ctrl_frame, text="⚡ RUN SPEED TEST", font=("Courier", 10, "bold"), bg="#21262D", fg=CYAN, command=run_speed_test, padx=10, pady=4)
btn_speed.pack(side="right", padx=(6, 0))

btn_scan = tk.Button(ctrl_frame, text="🔍 SCAN WI-FI DEVICES", font=("Courier", 10, "bold"), bg="#21262D", fg=GREEN, command=scan_network, padx=10, pady=4)
btn_scan.pack(side="right")

table_frame = tk.Frame(root, bg=CARD, bd=1, relief="groove")
table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

style = ttk.Style()
style.theme_use("default")

table_frame = tk.Frame(root, bg=CARD, bd=1, relief="groove")
table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background="#12161E", foreground=TEXT, fieldbackground="#12161E", rowheight=26, font=("Courier", 10))
style.configure("Treeview.Heading", background="#21262D", foreground=GOLD, font=("Courier", 10, "bold"))
style.map("Treeview", background=[("selected", "#1F6FEB")])

columns = ("name", "ip", "mac", "vendor")
tree = ttk.Treeview(table_frame, columns=columns, show="headings")
tree.heading("name", text="DEVICE NAME")
tree.heading("ip", text="IP ADDRESS")
tree.heading("mac", text="MAC ADDRESS")
tree.heading("vendor", text="DETECTED VENDOR")

tree.column("name", width=250, anchor="w")
tree.column("ip", width=135, anchor="w")
tree.column("mac", width=165, anchor="w")
tree.column("vendor", width=260, anchor="w")

scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def live_ping_loop():
    def worker():
        try:
            out = subprocess.check_output(["ping", "-c", "1", "-W", "1000", "8.8.8.8"], stderr=subprocess.DEVNULL).decode("utf-8")
            m = re.search(r"time=([\d.]+)\s*ms", out)
            if m:
                ms = float(m.group(1))
                color = GREEN if ms < 40 else (GOLD if ms < 100 else "#FF5555")
                root.after(0, lambda: ping_lbl.config(text=f"{ms:.0f} ms", fg=color))
        except Exception:
            root.after(0, lambda: ping_lbl.config(text="OFFLINE", fg="#FF5555"))
    threading.Thread(target=worker, daemon=True).start()
    root.after(4000, live_ping_loop)

live_ping_loop()
root.after(500, scan_network)
root.mainloop()
