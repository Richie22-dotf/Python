import tkinter as tk
from tkinter import scrolledtext
import subprocess, threading, tempfile, sys, os

try:
    import sounddevice as sd
    from scipy.io.wavfile import write as wav_write
except ImportError:
    sd = None

try:
    from google import genai
except ImportError:
    genai = None

BASE_DIR = "/Users/richardlung/Documents/Python"
PY = "/usr/local/bin/python3"

VOICE_COMMANDS = {
    "cyber guard": ("CyberGuard AI Vulnerability Auditor", "cyber_guard.py"),
    "cyberguard": ("CyberGuard AI Vulnerability Auditor", "cyber_guard.py"),
    "cyber": ("CyberGuard AI Vulnerability Auditor", "cyber_guard.py"),
    "network": ("Network Command & Speed Suite", "scanner.py"),
    "scanner": ("Network Command & Speed Suite", "scanner.py"),
    "market": ("Global Market Streamer v2.0", "streamer.py"),
    "streamer": ("Global Market Streamer v2.0", "streamer.py"),
    "clock": ("Luxury Photo Flip-Clock", "clock.py"),
    "commander": ("Mac System Commander", "commander.py"),
    "cigar": ("Cigar Sommelier Desktop", "cigar_scanner.py"),
    "hub": ("Master Command Hub", "hub.py")
}

root = tk.Tk()
root.title("J.A.R.V.I.S. v2.1 - Native Gemini Audio Desk Assistant")
root.geometry("680x520")
if len(sys.argv) > 1:
    root.geometry(sys.argv.pop())
root.configure(bg="#090D12")

BG, CARD, CYAN, GREEN, AMBER, RED, TEXT = "#090D12", "#111720", "#00E6FF", "#00FF66", "#FFB020", "#FF4D4D", "#E6EDF3"

hdr = tk.Frame(root, bg=BG)
hdr.pack(fill="x", padx=20, pady=(16, 6))
tk.Label(hdr, text="J.A.R.V.I.S. v2.1 - GEMINI AUDIO & DESK CONSOLE", font=("Courier", 14, "bold"), bg=BG, fg=CYAN).pack(side="left")

status_lbl = tk.Label(root, text="STATUS: STANDBY - PRESS [LISTEN MIC] OR TYPE A COMMAND", font=("Courier", 10, "bold"), bg=BG, fg=AMBER)
status_lbl.pack(anchor="w", padx=20, pady=(2, 8))

log_box = scrolledtext.ScrolledText(root, height=16, bg="#0D1219", fg=TEXT, font=("Courier", 10), bd=1, relief="groove", wrap=tk.WORD)
log_box.pack(fill="both", expand=True, padx=20, pady=(0, 10))
log_box.insert(tk.END, "System online (Gemini Audio Engine Ready). Say or type:\n  - Open CyberGuard\n  - Launch Market Streamer\n  - Run Network Scanner\n  - Or ask any question!\n" + "-"*60 + "\n")

def speak(text):
    clean = text.replace("*", "").replace("#", "").replace("`", "")[:450]
    subprocess.Popen(["say", "-v", "Daniel", clean], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def log_msg(sender, msg):
    log_box.insert(tk.END, f"[{sender}] {msg}\n\n")
    log_box.see(tk.END)

def process_command(cmd_text):
    q = cmd_text.strip()
    if not q:
        return
    log_msg("YOU", q)
    low = q.lower()

    if any(w in low for w in ("open", "launch", "start", "run")):
        for key, (label, script) in VOICE_COMMANDS.items():
            if key in low:
                path = os.path.join(BASE_DIR, script)
                if os.path.exists(path):
                    subprocess.Popen([PY, path], env=os.environ.copy())
                    reply = f"Launching {label} now."
                    log_msg("JARVIS", reply)
                    speak(reply)
                    status_lbl.config(text=f"STATUS: LAUNCHED {label.upper()}", fg=GREEN)
                    return

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key or genai is None:
        log_msg("JARVIS", "GEMINI_API_KEY is missing. Run source ~/.zshrc before launching.")
        return

    status_lbl.config(text="STATUS: THINKING...", fg=CYAN)
    def ai_worker():
        try:
            client = genai.Client(api_key=api_key)
            models = [m.name.replace("models/", "") for m in client.models.list() if "gemini" in m.name.lower() and not any(x in m.name.lower() for x in ["audio", "tts", "embedding", "vision-001", "aqa", "imagen", "veo"])]
            models.sort(key=lambda x: (0 if "flash" in x else (1 if "lite" in x else 2), x))
            prompt = f"You are JARVIS, a sharp, concise AI desk assistant for Richard. Answer in 2-3 clear sentences suitable for voice playback: {q}"
            answer = ""
            for m_name in models:
                try:
                    res = client.models.generate_content(model=m_name, contents=prompt)
                    if res and res.text:
                        answer = res.text.strip()
                        break
                except Exception:
                    continue
            if not answer:
                answer = "All AI models are briefly busy. Please try again."
            root.after(0, lambda: (log_msg("JARVIS", answer), speak(answer), status_lbl.config(text="STATUS: READY", fg=GREEN)))
        except Exception as e:
            err = str(e)
            root.after(0, lambda: (log_msg("ERROR", err), status_lbl.config(text="STATUS: ERROR", fg=RED)))

    threading.Thread(target=ai_worker, daemon=True).start()

def listen_mic():
    if sd is None:
        log_msg("SYSTEM", "Run: /usr/local/bin/python3 -m pip install sounddevice scipy")
        return
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key or genai is None:
        log_msg("SYSTEM", "Missing GEMINI_API_KEY in ~/.zshrc.")
        return
    btn_listen.config(state="disabled")
    status_lbl.config(text="STATUS: LISTENING (4 SECONDS)... SPEAK NOW", fg=GREEN)

    def mic_worker():
        tmp_path = None
        try:
            fs = 16000
            rec = sd.rec(int(4 * fs), samplerate=fs, channels=1, dtype="int16")
            sd.wait()
            root.after(0, lambda: status_lbl.config(text="STATUS: GEMINI TRANSCRIBING...", fg=CYAN))
            fd, tmp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            wav_write(tmp_path, fs, rec)
            wav_bytes = open(tmp_path, "rb").read()
            client = genai.Client(api_key=api_key)
            models = [m.name.replace("models/", "") for m in client.models.list() if "gemini" in m.name.lower() and not any(x in m.name.lower() for x in ["audio", "tts", "embedding", "vision-001", "aqa", "imagen", "veo"])]
            models.sort(key=lambda x: (0 if "flash" in x else (1 if "lite" in x else 2), x))
            text = ""
            for m_name in models:
                try:
                    res = client.models.generate_content(model=m_name, contents=["Transcribe the exact spoken words. Return ONLY the text, or NONE if silent.", {"inline_data": {"data": wav_bytes, "mime_type": "audio/wav"}}])
                    if res and res.text:
                        text = res.text.strip()
                        break
                except Exception:
                    continue
            if not text or text.upper() == "NONE":
                root.after(0, lambda: (btn_listen.config(state="normal"), status_lbl.config(text="STATUS: NO SPEECH DETECTED", fg=AMBER)))
            else:
                root.after(0, lambda: (btn_listen.config(state="normal"), process_command(text)))
        except Exception as e:
            err = f"Mic notice: {e}"
            root.after(0, lambda: (btn_listen.config(state="normal"), status_lbl.config(text="STATUS: STANDBY", fg=AMBER), log_msg("MIC", err)))
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    threading.Thread(target=mic_worker, daemon=True).start()

ctrl = tk.Frame(root, bg=BG)
ctrl.pack(fill="x", padx=20, pady=(0, 16))

entry_var = tk.StringVar()
entry = tk.Entry(ctrl, textvariable=entry_var, bg=CARD, fg=TEXT, insertbackground=TEXT, font=("Courier", 11))
entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
entry.bind("<Return>", lambda e: (process_command(entry_var.get()), entry_var.set("")))

tk.Button(ctrl, text="SEND", font=("Courier", 10, "bold"), bg="#1F2937", fg=CYAN, command=lambda: (process_command(entry_var.get()), entry_var.set("")), padx=12, pady=5).pack(side="left", padx=(0, 6))
btn_listen = tk.Button(ctrl, text="[LISTEN MIC]", font=("Courier", 10, "bold"), bg="#1F2937", fg=GREEN, command=listen_mic, padx=14, pady=5)
btn_listen.pack(side="left")

root.mainloop()
