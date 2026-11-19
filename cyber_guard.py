import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import subprocess
import threading
import socket
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import time
import re
import os
import sys

try:
    from google import genai
except ImportError:
    genai = None

RISK_PORTS = {
    21: ("FTP", "HIGH", "Unencrypted file transfer; credentials sent in plaintext.", "Disable FTP on the device/router and switch to SFTP (port 22) or FTPS."),
    22: ("SSH", "LOW", "Encrypted remote shell access.", "Ensure password login is disabled (use SSH keys only) and disable root SSH login."),
    23: ("Telnet", "CRITICAL", "Legacy unencrypted remote shell; severe takeover risk.", "Immediately disable Telnet in device/router admin settings and use SSH instead."),
    53: ("DNS", "LOW", "Local DNS resolver service.", "Verify DNS recursion is restricted to local LAN clients only (no WAN exposure)."),
    80: ("HTTP", "MEDIUM", "Unencrypted web admin panel.", "Change default admin credentials, use HTTPS if available, and disable WAN/Remote Management."),
    139: ("NetBIOS", "MEDIUM", "Legacy Windows/SMB name and file sharing service.", "Disable NetBIOS over TCP/IP unless required for legacy local printers/shares."),
    443: ("HTTPS", "LOW", "Encrypted web management interface.", "Confirm strong admin password and ensure remote WAN access is turned off."),
    445: ("SMB", "HIGH", "Network file sharing protocol; target for lateral movement.", "On macOS: System Settings > General > Sharing > turn OFF File Sharing if unused."),
    554: ("RTSP", "HIGH", "Live IP camera video stream.", "Set a strong unique camera password, update firmware, and isolate camera on IoT Wi-Fi."),
    1883: ("MQTT", "MEDIUM", "Smart-home IoT messaging broker.", "Enable username/password auth and TLS on broker; isolate IoT devices from main LAN."),
    3389: ("RDP", "CRITICAL", "Remote Desktop exposed on LAN.", "Enable Network Level Authentication (NLA), enforce strong passwords, and never port-forward 3389."),
    5000: ("UPnP/AirPlay", "MEDIUM", "UPnP service or macOS AirPlay Receiver.", "On Mac: System Settings > General > AirDrop & Handoff > set AirPlay Receiver to Current User. Disable UPnP on router."),
    5900: ("VNC", "HIGH", "Remote screen sharing service.", "Turn off Screen Sharing / Remote Management when not actively needed and require strong auth."),
    8080: ("HTTP-Alt", "MEDIUM", "Alternative web admin portal or proxy.", "Inspect http://<IP>:8080 in browser, change default login, and restrict to LAN only."),
    8443: ("HTTPS-Alt", "LOW", "Encrypted alternative management portal.", "Verify strong admin credentials and keep device firmware up to date.")
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
    open_nums = []
    highest = "SECURE"
    rank = {"SECURE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    for port, (svc, sev, _, _) in RISK_PORTS.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.18)
        if sock.connect_ex((ip, port)) == 0:
            open_services.append(f"{port}/{svc}")
            open_nums.append(port)
            if rank.get(sev, 0) > rank.get(highest, 0):
                highest = sev
        sock.close()
    return open_services, open_nums, highest

root = tk.Tk()
root.title("CyberGuard AI v2.0 • Interactive Vulnerability & Remediation Suite")
root.geometry("1020x710")
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
scanned_inventory = {}

hdr = tk.Frame(root, bg=BG)
hdr.pack(fill="x", padx=20, pady=(14, 6))
tk.Label(hdr, text="CYBERGUARD AI v2.0 • VULNERABILITY & REMEDIATION SUITE", font=("Courier", 15, "bold"), bg=BG, fg=GREEN).pack(side="left")
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
status_lbl = tk.Label(bar, text="STATUS: READY — CLICK ANY HOST ROW FOR INSTANT REMEDIATION", font=("Courier", 10, "bold"), bg=BG, fg=AMBER)
status_lbl.pack(side="left")

def export_report():
    content = ai_box.get("1.0", tk.END).strip()
    if not scanned_inventory:
        messagebox.showinfo("Export Report", "Run an Attack Surface Scan first before exporting a PDF report.")
        return
    default_name = f"CyberGuard_Audit_{time.strftime(chr(37)+chr(89)+chr(37)+chr(109)+chr(37)+chr(100))}.pdf"
    fp = filedialog.asksaveasfilename(
        title="Save PDF Security Audit Report",
        initialfile=default_name,
        defaultextension=".pdf",
        filetypes=(("PDF Document", "*.pdf"),)
    )
    if not fp:
        return

    c = canvas.Canvas(fp, pagesize=letter)
    w, h = letter
    y = h - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(45, y, "CyberGuard AI — Home Network Security Audit Report")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(45, y, f"Generated: {time.strftime(chr(37)+chr(89)+chr(45)+chr(37)+chr(109)+chr(45)+chr(37)+chr(100)+chr(32)+chr(37)+chr(72)+chr(58)+chr(37)+chr(77))}  |  Sensor IP: {local_ip}  |  Hosts Scanned: {len(scanned_inventory)}")
    y -= 28

    c.setFont("Helvetica-Bold", 12)
    c.drawString(45, y, "1. Discovered Network Inventory")
    y -= 18
    c.setFont("Courier-Bold", 9)
    c.drawString(45, y, f"{chr(82)+chr(73)+chr(83)+chr(75):<10} {chr(72)+chr(79)+chr(83)+chr(84):<24} {chr(73)+chr(80):<16} {chr(79)+chr(80)+chr(69)+chr(78)+chr(32)+chr(80)+chr(79)+chr(82)+chr(84)+chr(83)}")
    y -= 14

    c.setFont("Courier", 8.5)
    for ip, d in scanned_inventory.items():
        if y < 60:
            c.showPage()
            y = h - 50
            c.setFont("Courier", 8.5)
        risk = str(d.get("risk", "SECURE"))
        name = str(d.get("name", ""))[:22]
        p_str = ", ".join(d.get("ports", [])) or "None (Filtered)"
        c.drawString(45, y, f"{risk:<10} {name:<24} {ip:<16} {p_str[:38]}")
        y -= 13

    y -= 18
    if y < 90:
        c.showPage()
        y = h - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(45, y, "2. Security Analyst Assessment & Remediation Playbook")
    y -= 18

    c.setFont("Helvetica", 9.5)
    for raw_line in content.splitlines():
        words = raw_line.split(" ") if raw_line.strip() else [""]
        line_buf = ""
        for word in words:
            test = (line_buf + " " + word).strip()
            if len(test) > 92:
                if y < 55:
                    c.showPage()
                    y = h - 50
                    c.setFont("Helvetica", 9.5)
                c.drawString(45, y, line_buf)
                y -= 13
                line_buf = word
            else:
                line_buf = test
        if y < 55:
            c.showPage()
            y = h - 50
            c.setFont("Helvetica", 9.5)
        c.drawString(45, y, line_buf)
        y -= 13

    c.save()
    status_lbl.config(text=f"STATUS: EXPORTED PDF REPORT TO {os.path.basename(fp)}", fg=GREEN)

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
                ports, port_nums, sev = probe_ports(ip)
                with lock:
                    results.append({"name": name, "ip": ip, "mac": mac, "vendor": vendor, "ports": ports, "port_nums": port_nums, "risk": sev})

            threads = [threading.Thread(target=scan_host, args=item) for item in raw]
            for t in threads: t.start()
            for t in threads: t.join()

            results.sort(key=lambda d: int(d.get("ip", "0.0.0.0").split(chr(46)).pop()))

            def update_ui():
                scanned_inventory.clear()
                for r in tree.get_children():
                    tree.delete(r)

                total_ports = 0
                high_risk_hosts = 0
                for d in results:
                    ip = d.get("ip")
                    scanned_inventory.update({ip: d})
                    plist = d.get("ports", [])
                    total_ports += len(plist)
                    risk = d.get("risk", "SECURE")
                    if risk in ("HIGH", "CRITICAL"):
                        high_risk_hosts += 1
                    p_str = ", ".join(plist) if plist else "None (Filtered)"
                    tree.insert("", "end", iid=ip, values=(risk, d.get("name"), ip, d.get("vendor"), p_str))

                hosts_kpi.config(text=str(len(results)))
                ports_kpi.config(text=str(total_ports))
                crit_kpi.config(text=str(high_risk_hosts))
                if high_risk_hosts > 0:
                    posture_kpi.config(text="ACTION NEEDED", fg=RED)
                elif total_ports > 0:
                    posture_kpi.config(text="MODERATE", fg=AMBER)
                else:
                    posture_kpi.config(text="HARDENED", fg=GREEN)

                status_lbl.config(text=f"STATUS: {len(results)} HOSTS PROBED — CLICK ANY ROW TO INSPECT REMEDIATION", fg=GREEN)
                btn_audit.config(state="normal")
                btn_ai.config(state="normal")

            root.after(0, update_ui)
        except Exception as e:
            err = str(e)[:45]
            root.after(0, lambda: (status_lbl.config(text=f"AUDIT ERR: {err}", fg=RED), btn_audit.config(state="normal")))

    threading.Thread(target=worker, daemon=True).start()

def on_row_select(event):
    sel = tree.selection()
    if not sel:
        return
    ip = next(iter(sel))
    host = scanned_inventory.get(ip)
    if not host:
        return

    name = host.get("name", ip)
    mac = host.get("mac", "")
    vendor = host.get("vendor", "")
    risk = host.get("risk", "SECURE")
    port_nums = host.get("port_nums", [])

    console_hdr.config(text=f"TARGET INSPECTOR • {name} ({ip}) [{risk}]", fg=CYAN)
    ai_box.delete("1.0", tk.END)
    ai_box.insert(tk.END, "=== HOST TELEMETRY & REMEDIATION PLAYBOOK ===\n")
    ai_box.insert(tk.END, f"Host: {name}  |  IP: {ip}  |  MAC: {mac}  |  Vendor: {vendor}\n")
    ai_box.insert(tk.END, f"Overall Risk Rating: {risk}\n")
    ai_box.insert(tk.END, "-" * 68 + "\n\n")

    if not port_nums:
        ai_box.insert(tk.END, "✅ STATUS: STEALTH / FILTERED\n")
        ai_box.insert(tk.END, "No high-risk TCP ports responded on this endpoint. Its host firewall is properly dropping unsolicited probes.\n\n")
        if any(k in vendor for k in ("IoT", "Roku", "Sonos", "Google", "Amazon", "Philips")):
            ai_box.insert(tk.END, "💡 IOT SEGMENTATION TIP:\nEven with closed ports, smart-home devices should be placed on an isolated secondary IoT Wi-Fi router with Client Isolation enabled so they cannot reach your Mac or iPad.\n")
        return

    for p in port_nums:
        svc, sev, desc, fix = RISK_PORTS.get(p, ("Service", "MEDIUM", "Open network port.", "Restrict access via firewall."))
        ai_box.insert(tk.END, f"🚨 PORT {p} ({svc}) — SEVERITY: {sev}\n")
        ai_box.insert(tk.END, f"   • Why It Matters: {desc}\n")
        ai_box.insert(tk.END, f"   • How To Remediate: {fix}\n\n")

    ai_box.insert(tk.END, "👉 Want a deep-dive AI assessment for your entire network? Click [AI FULL NETWORK BRIEFING] above.\n")

def generate_ai_briefing():
    if not scanned_inventory:
        return
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key or genai is None:
        ai_box.delete("1.0", tk.END)
        ai_box.insert(tk.END, "Missing GEMINI_API_KEY in environment or google-genai package.\nRun: source ~/.zshrc before launching cyber_guard.py.")
        return

    btn_ai.config(state="disabled")
    console_hdr.config(text="GEMINI SOC ANALYST • FULL NETWORK THREAT BRIEFING", fg=AMBER)
    status_lbl.config(text="STATUS: GEMINI SOC ANALYST GENERATING THREAT BRIEFING...", fg=CYAN)
    ai_box.delete("1.0", tk.END)
    ai_box.insert(tk.END, "Analyzing discovered hosts, open ports, and IoT attack surface...\n")

    def worker():
        try:
            client = genai.Client(api_key=api_key)
            summary_json = json.dumps(list(scanned_inventory.values()), indent=2)
            prompt = (
                "You are a Senior Cybersecurity & Vulnerability Management Analyst auditing a home network. "
                "Review this live subnet recon scan (hosts, vendors, open ports, and risk levels):\n\n"
                f"{summary_json}\n\n"
                "Provide a concise, high-impact Security Assessment:\n"
                "1) OVERALL ATTACK SURFACE SUMMARY (2-3 sentences)\n"
                "2) SPECIFIC VULNERABILITY FINDINGS (explain why any open ports matter on those specific devices)\n"
                "3) TOP 4 ACTIONABLE HARDENING STEPS (router settings, IoT segmentation, firewall rules, UPnP lockdown)."
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
                status_lbl.config(text="STATUS: AI FULL NETWORK BRIEFING READY", fg=GREEN)
                btn_ai.config(state="normal")
            root.after(0, show_report)
        except Exception as e:
            err = str(e)
            root.after(0, lambda: (ai_box.insert(tk.END, f"\nError: {err}"), btn_ai.config(state="normal")))

    threading.Thread(target=worker, daemon=True).start()

btn_export = tk.Button(bar, text="EXPORT REPORT (.PDF)", font=("Courier", 10, "bold"), bg="#1F2937", fg=CYAN, command=export_report, padx=10, pady=4)
btn_export.pack(side="right", padx=(6, 0))

btn_ai = tk.Button(bar, text="AI FULL NETWORK BRIEFING", font=("Courier", 10, "bold"), bg="#1F2937", fg=AMBER, command=generate_ai_briefing, padx=10, pady=4, state="disabled")
btn_ai.pack(side="right", padx=(6, 0))

btn_audit = tk.Button(bar, text="RUN ATTACK SURFACE SCAN", font=("Courier", 10, "bold"), bg="#1F2937", fg=GREEN, command=run_full_audit, padx=10, pady=4)
btn_audit.pack(side="right")

tbl_frame = tk.Frame(root, bg=CARD, bd=1, relief="groove")
tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background="#0D1219", foreground=TEXT, fieldbackground="#0D1219", rowheight=25, font=("Courier", 10))
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
tree.column("name", width=230, anchor="w")
tree.column("ip", width=130, anchor="w")
tree.column("vendor", width=190, anchor="w")
tree.column("ports", width=290, anchor="w")

tree.bind("<<TreeviewSelect>>", on_row_select)

sb = ttk.Scrollbar(tbl_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=sb.set)
tree.pack(side="left", fill="both", expand=True)
sb.pack(side="right", fill="y")

console_hdr = tk.Label(root, text="REMEDIATION INSPECTOR & SOC CONSOLE (CLICK ANY DEVICE ABOVE)", font=("Courier", 10, "bold"), bg=BG, fg=AMBER)
console_hdr.pack(anchor="w", padx=20, pady=(2, 2))

ai_box = scrolledtext.ScrolledText(root, height=11, bg="#0D1219", fg="#D1FAE5", font=("Courier", 10), bd=1, relief="groove", wrap=tk.WORD)
ai_box.pack(fill="both", expand=True, padx=20, pady=(0, 14))
ai_box.insert(tk.END, "1. Wait for the Attack Surface Scan to complete.\n2. Click ANY device row in the table above to inspect its exact port risks and remediation steps.\n3. Or click [AI FULL NETWORK BRIEFING] for an executive Gemini security assessment.\n")

root.after(400, run_full_audit)
root.mainloop()
