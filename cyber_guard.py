import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import socket
import json
import re
import os
import sys

try:
    from google import genai
except ImportError:
    genai = None

RISK_PORTS = {
    21: ("FTP", "HIGH", "Unencrypted file transfer; credentials sent in plaintext."),
    22: ("SSH", "LOW", "Encrypted remote shell; verify key-only auth & disable root login."),
    23: ("Telnet", "CRITICAL", "Legacy unencrypted remote shell; severe takeover risk."),
    53: ("DNS", "LOW", "Local DNS resolver service."),
    80: ("HTTP", "MEDIUM", "Unencrypted web admin panel; check for default credentials."),
    139: ("NetBIOS", "MEDIUM", "Legacy Windows/SMB file sharing exposure."),
    443: ("HTTPS", "LOW", "Encrypted web interface."),
    445: ("SMB", "HIGH", "File sharing protocol; common target for lateral movement."),
    554: ("RTSP", "HIGH", "IP camera video stream; verify strong password & LAN isolation."),
    1883: ("MQTT", "MEDIUM", "Smart-home IoT broker; check for unauthenticated access."),
    3389: ("RDP", "CRITICAL", "Remote Desktop exposed; high risk if accessible outside LAN."),
    5000: ("UPnP/Flask", "MEDIUM", "UPnP service or dev server; disable UPnP on router if unused."),
    5900: ("VNC", "HIGH", "Remote screen sharing; enforce strong authentication."),
    8080: ("HTTP-Alt", "MEDIUM", "Alternative web admin portal or proxy."),
    8443: ("HTTPS-Alt", "LOW", "Encrypted alternative management port.")
}

OUI_VENDORS = {
    "00:03:93": "Apple", "28:CF:E9": "Apple", "3C:07:54": "Apple", "40:6C:8F": "Apple",
    "60:03:08": "Apple", "70:56:81": "Apple", "88:66:5A": "Apple", "A4:83:E7": "Apple",
    "AC:BC:32": "Apple", "D0:03:4B": "Apple", "F0:18:98": "Apple",
    "B8:27:EB": "Raspberry Pi", "DC:A6:32": "Raspberry Pi", "E4:5F:01": "Raspberry Pi",
    "00:0E:58": "Sonos", "5C:AA:FD": "Sonos", "78:28:CA": "Sonos", "94:9F:3E": "Sonos",
    "B0:A7:37": "Roku", "D8:31:34": "Roku", "CC:6D:A0": "Roku", "AC:3A:7A": "Roku",
    "18:B4:30": "Google Nest", "64:16:66": "Google Nest", "F4:F5:D8": "Google",
    "00:17:88": "Philips Hue", "EC:B5:FA": "Philips Hue",
    "44:65:0D": "Amazon Echo", "68:37:E9": "Amazon", "74:C2:46": "Amazon",
    "C0:25:E9": "TP-Link", "50:C7:BF": "TP-Link", "98:DA:C4": "TP-Link",
    "80:7D:3A": "Espressif IoT", "24:0A:C4": "Espressif IoT", "30:AE:A4": "Espressif IoT"
}

def get_vendor(mac):
    if not mac or mac == "(incomplete)":
        return "Unknown"
    parts = [p.zfill(2).upper() for p in mac.split(":")]
    if len(parts) < 3:
        return "Unknown"
    if int(next(iter(parts)), 16) & 0x02:
        return "Private Wi-Fi (iOS/Mac/Android)"
    return OUI_VENDORS.get(":".join(parts[:3]), "Network Endpoint")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = next(iter(s.getsockname()))
        s.close()
        return ip
    except Exception:
        return "192.168.1.1"

def resolve_name(ip, vendor, my_ip, arp_host=""):
    if arp_host and arp_host != "?":
        return arp_host.replace(".lan", "").replace(".local", "")
    if ip == my_ip:
        return socket.gethostname().replace(".local", "") + " (This Mac)"
    if ip.endswith(".1") or ip.endswith(".254"):
        return "Gateway Router"
    try:
        h = next(iter(socket.gethostbyaddr(ip)))
        if h and h != ip:
            return h.replace(".lan", "").replace(".local", "")
    except Exception:
        pass
    return f"{vendor} (.{ip.split(chr(46)).pop()})"

def probe_ports(ip):
    open_services = []
    highest = "SECURE"
    rank = {"SECURE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    for port, (svc, sev, _) in RISK_PORTS.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.18)
        if sock.connect_ex((ip, port)) == 0:
            open_services.append(f"{port}/{svc}")
            if rank.get(sev, 0) > rank.get(highest, 0):
                highest = sev
        sock.close()
    return open_services, highest

root = tk.Tk()
root.title("CyberGuard AI • Home Vulnerability & Recon Auditor")
root.geometry("980x680")
if len(sys.argv) > 1:
    root.geometry(sys.argv.pop())
root.configure(bg="#090D12")

BG = "#090D12"
CARD = "#111720"
GREEN = "#00FF66"
CYAN = "#00E6FF"
RED = "#FF4D4D"
AMBER = "#FFB020"
TEXT = "#E6EDF3"
MUTED = "#8B949E"

local_ip = get_local_ip()
scanned_inventory = []

hdr = tk.Frame(root, bg=BG)
hdr.pack(fill="x", padx=20, pady=(14, 6))
tk.Label(hdr, text="CYBERGUARD AI • HOME VULNERABILITY AUDITOR", font=("Courier", 16, "bold"), bg=BG, fg=GREEN).pack(side="left")
tk.Label(hdr, text=f"SENSOR IP: {local_ip}", font=("Courier", 11, "bold"), bg=BG, fg=CYAN).pack(side="right")

kpi_frame = tk.Frame(root, bg=BG)
kpi_frame.pack(fill="x", padx=20, pady=6)

def make_kpi(parent, label, val, color):
    c = tk.Frame(parent, bg=CARD, bd=1, relief="groove", padx=12, pady=8)
    c.pack(side="left", fill="both", expand=True, padx=4)
    tk.Label(c, text=label, font=("Courier", 9, "bold"), bg=CARD, fg=MUTED).pack()
    lbl = tk.Label(c, text=val, font=("Courier", 14, "bold"), bg=CARD, fg=color)
    lbl.pack(pady=(3, 0))
    return lbl

hosts_kpi = make_kpi(kpi_frame, "DISCOVERED HOSTS", "0", CYAN)
ports_kpi = make_kpi(kpi_frame, "OPEN PORTS DETECTED", "0", AMBER)
crit_kpi = make_kpi(kpi_frame, "HIGH / CRITICAL RISKS", "0", RED)
posture_kpi = make_kpi(kpi_frame, "NETWORK POSTURE", "PENDING SCAN", GREEN)

bar = tk.Frame(root, bg=BG)
bar.pack(fill="x", padx=20, pady=8)
status_lbl = tk.Label(bar, text="STATUS: READY TO AUDIT ATTACK SURFACE", font=("Courier", 10, "bold"), bg=BG, fg=AMBER)
status_lbl.pack(side="left")

def run_full_audit():
    btn_audit.config(state="disabled")
    btn_ai.config(state="disabled")
    status_lbl.config(text="STATUS: SWEEPING SUBNET & PROBING 15 HIGH-RISK PORTS...", fg=CYAN)

    def worker():
        try:
            subnet = ".".join(local_ip.split(".")[:3])
            procs = [subprocess.Popen(["ping", "-c", "1", "-W", "180", f"{subnet}.{i}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for i in range(1, 255)]
            for p in procs:
                p.wait()

            arp_out = subprocess.check_output(["arp", "-a"]).decode("utf-8", errors="ignore")
            raw = []
            for line in arp_out.splitlines():
                hm = re.match(r"^([^\s?]+)\s+\((\d+\.\d+\.\d+\.\d+)\)", line)
                im = re.search(r"\((\d+\.\d+\.\d+\.\d+)\)", line)
                mm = re.search(r"at\s+([0-9a-fA-F:]+)", line)
                if im and mm:
                    ip, mac = im.group(1), mm.group(1)
                    if mac != "ff:ff:ff:ff:ff:ff" and not ip.endswith(".255"):
                        raw.append((ip, mac.upper(), hm.group(1) if hm else ""))

            results = []
            lock = threading.Lock()
            def scan_host(ip, mac, ah):
                vendor = get_vendor(mac)
                name = resolve_name(ip, vendor, local_ip, ah)
                ports, sev = probe_ports(ip)
                with lock:
                    results.append({"name": name, "ip": ip, "mac": mac, "vendor": vendor, "ports": ports, "risk": sev})

            threads = [threading.Thread(target=scan_host, args=item) for item in raw]
            for t in threads: t.start()
            for t in threads: t.join()

            results.sort(key=lambda d: int(d.get("ip", "0.0.0.0").split(chr(46)).pop()))

            def update_ui():
                scanned_inventory.clear()
                scanned_inventory.extend(results)
                for r in tree.get_children():
                    tree.delete(r)

                total_ports = 0
                high_risk_hosts = 0
                for d in results:
                    plist = d.get("ports", [])
                    total_ports += len(plist)
                    risk = d.get("risk", "SECURE")
                    if risk in ("HIGH", "CRITICAL"):
                        high_risk_hosts += 1
                    p_str = ", ".join(plist) if plist else "None (Filtered)"
                    tree.insert("", "end", values=(risk, d.get("name"), d.get("ip"), d.get("vendor"), p_str))

                hosts_kpi.config(text=str(len(results)))
                ports_kpi.config(text=str(total_ports))
                crit_kpi.config(text=str(high_risk_hosts))
                if high_risk_hosts > 0:
                    posture_kpi.config(text="ACTION NEEDED", fg=RED)
                elif total_ports > 0:
                    posture_kpi.config(text="MODERATE", fg=AMBER)
                else:
                    posture_kpi.config(text="HARDENED", fg=GREEN)

                status_lbl.config(text=f"STATUS: AUDIT COMPLETE — {len(results)} HOSTS PROBED", fg=GREEN)
                btn_audit.config(state="normal")
                btn_ai.config(state="normal")

            root.after(0, update_ui)
        except Exception as e:
            err = str(e)[:45]
            root.after(0, lambda: (status_lbl.config(text=f"AUDIT ERR: {err}", fg=RED), btn_audit.config(state="normal")))

    threading.Thread(target=worker, daemon=True).start()

def generate_ai_briefing():
    if not scanned_inventory:
        return
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key or genai is None:
        ai_box.delete("1.0", tk.END)
        ai_box.insert(tk.END, "Missing GEMINI_API_KEY in environment or google-genai package.\nRun: source ~/.zshrc before launching cyber_guard.py.")
        return

    btn_ai.config(state="disabled")
    status_lbl.config(text="STATUS: GEMINI SOC ANALYST GENERATING THREAT BRIEFING...", fg=CYAN)
    ai_box.delete("1.0", tk.END)
    ai_box.insert(tk.END, "Analyzing discovered hosts, open ports, and IoT attack surface...\n")

    def worker():
        try:
            client = genai.Client(api_key=api_key)
            summary_json = json.dumps(scanned_inventory, indent=2)
            prompt = (
                "You are a Senior Cybersecurity Analyst auditing a home network. "
                "Review this live subnet recon scan (hosts, vendors, open ports, and risk levels):\n\n"
                f"{summary_json}\n\n"
                "Provide a concise Security Assessment:\n"
                "1) OVERALL ATTACK SURFACE SUMMARY (2-3 sentences)\n"
                "2) SPECIFIC VULNERABILITY FINDINGS (explain any open ports like 21, 23, 80, 445, 554, 1883, 3389, 5000, 8080)\n"
                "3) TOP 4 ACTIONABLE HARDENING STEPS (router settings, IoT isolation, firewall rules, UPnP lockdown)."
            )
            live_models = [
                m.name.replace("models/", "") for m in client.models.list()
                if "gemini" in m.name.lower() and not any(x in m.name.lower() for x in ["audio", "tts", "embedding", "vision-001", "aqa", "imagen", "veo"])
            ]
            live_models.sort(key=lambda x: (0 if "lite" in x else (1 if "flash" in x else 2), x))
            report = ""
            for m_name in live_models:
                try:
                    res = client.models.generate_content(model=m_name, contents=prompt)
                    if res and res.text:
                        report = res.text
                        break
                except Exception:
                    continue
            if not report:
                report = "All Gemini models are temporarily busy. Please try again in a few seconds."

            def show_report():
                ai_box.delete("1.0", tk.END)
                ai_box.insert(tk.END, report)
                status_lbl.config(text="STATUS: AI THREAT & HARDENING BRIEFING READY", fg=GREEN)
                btn_ai.config(state="normal")
            root.after(0, show_report)
        except Exception as e:
            err = str(e)
            root.after(0, lambda: (ai_box.insert(tk.END, f"\nError: {err}"), btn_ai.config(state="normal")))

    threading.Thread(target=worker, daemon=True).start()

btn_ai = tk.Button(bar, text="AI VULNERABILITY BRIEFING", font=("Courier", 10, "bold"), bg="#1F2937", fg=AMBER, command=generate_ai_briefing, padx=10, pady=4, state="disabled")
btn_ai.pack(side="right", padx=(6, 0))

btn_audit = tk.Button(bar, text="RUN ATTACK SURFACE SCAN", font=("Courier", 10, "bold"), bg="#1F2937", fg=GREEN, command=run_full_audit, padx=10, pady=4)
btn_audit.pack(side="right")

tbl_frame = tk.Frame(root, bg=CARD, bd=1, relief="groove")
tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background="#0D1219", foreground=TEXT, fieldbackground="#0D1219", rowheight=24, font=("Courier", 10))
style.configure("Treeview.Heading", background="#1C2430", foreground=CYAN, font=("Courier", 10, "bold"))
style.map("Treeview", background=[("selected", "#1F6FEB")])

cols = ("risk", "name", "ip", "vendor", "ports")
tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", height=8)
tree.heading("risk", text="RISK")
tree.heading("name", text="DEVICE / HOSTNAME")
tree.heading("ip", text="IP ADDRESS")
tree.heading("vendor", text="VENDOR")
tree.heading("ports", text="OPEN PORTS & SERVICES")

tree.column("risk", width=95, anchor="center")
tree.column("name", width=220, anchor="w")
tree.column("ip", width=130, anchor="w")
tree.column("vendor", width=180, anchor="w")
tree.column("ports", width=280, anchor="w")

sb = ttk.Scrollbar(tbl_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=sb.set)
tree.pack(side="left", fill="both", expand=True)
sb.pack(side="right", fill="y")

ai_hdr = tk.Label(root, text="GEMINI SOC ANALYST • THREAT & HARDENING PLAYBOOK", font=("Courier", 10, "bold"), bg=BG, fg=AMBER)
ai_hdr.pack(anchor="w", padx=20, pady=(2, 2))

ai_box = scrolledtext.ScrolledText(root, height=11, bg="#0D1219", fg="#D1FAE5", font=("Courier", 10), bd=1, relief="groove", wrap=tk.WORD)
ai_box.pack(fill="both", expand=True, padx=20, pady=(0, 14))
ai_box.insert(tk.END, "Run an Attack Surface Scan above, then click [AI VULNERABILITY BRIEFING] for a tailored defensive report.\n")

root.after(400, run_full_audit)
root.mainloop()
