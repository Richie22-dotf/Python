import tkinter as tk
from tkinter import filedialog, scrolledtext
from PIL import Image, ImageTk
from pillow_heif import register_heif_opener
from google import genai
from pydantic import BaseModel
from typing import List
import threading, json, time, sys, os

register_heif_opener()

class DesktopCigarProfile(BaseModel):
    brand_and_line: str
    origin_and_wrapper: str
    strength: str
    tasting_notes: List[str]
    spirits_pairing: str
    coffee_tea_pairing: str
    wine_beer_pairing: str
    sommelier_verdict: str

root = tk.Tk()
root.title("Fointein AI Cigar Sommelier v2.0 - Desktop Studio")
root.geometry("820x660")
if len(sys.argv) > 1:
    root.geometry(sys.argv.pop())
root.configure(bg="#120C08")

BG, CARD, GOLD, CREAM, AMBER, GREEN = "#120C08", "#1E140E", "#D4AF37", "#F5E6CC", "#E67E22", "#2ECC71"
selected_path = {"path": None}
last_profile = {}

hdr = tk.Frame(root, bg=BG)
hdr.pack(fill="x", padx=20, pady=(14, 6))
tk.Label(hdr, text="FOINTEIN AI CIGAR SOMMELIER v2.0", font=("Georgia", 16, "bold"), bg=BG, fg=GOLD).pack(side="left")
status_lbl = tk.Label(hdr, text="READY FOR BAND SCAN", font=("Courier", 10, "bold"), bg=BG, fg=CREAM)
status_lbl.pack(side="right")

top = tk.Frame(root, bg=BG)
top.pack(fill="x", padx=20, pady=6)

preview_lbl = tk.Label(top, text="No Cigar Photo Loaded\nClick [SELECT CIGAR PHOTO]", width=32, height=11, bg=CARD, fg=CREAM, font=("Courier", 10), bd=1, relief="groove")
preview_lbl.pack(side="left", padx=(0, 14))

ctrl = tk.Frame(top, bg=BG)
ctrl.pack(side="left", fill="both", expand=True)

def get_client():
    key = os.environ.get("GEMINI_API_KEY", "")
    return genai.Client(api_key=key) if key else None

def call_gemini(contents, schema=None):
    client = get_client()
    if not client:
        raise Exception("Missing GEMINI_API_KEY in ~/.zshrc")
    models = [m.name.replace("models/", "") for m in client.models.list() if "gemini" in m.name.lower() and not any(x in m.name.lower() for x in ["audio", "tts", "embedding", "vision-001", "aqa", "imagen", "veo"])]
    models.sort(key=lambda x: (0 if "flash" in x else (1 if "lite" in x else 2), x))
    cfg = {"response_mime_type": "application/json", "response_schema": schema} if schema else None
    for m_name in models:
        try:
            res = client.models.generate_content(model=m_name, contents=contents, config=cfg)
            if res and res.text:
                return res.text
        except Exception:
            continue
    raise Exception("AI models temporarily busy. Try again.")

def choose_photo():
    fp = filedialog.askopenfilename(title="Select Cigar Photo", filetypes=[("Images", "*.jpg *.jpeg *.png *.heic *.webp")])
    if not fp:
        return
    selected_path["path"] = fp
    img = Image.open(fp)
    img.thumbnail((240, 180))
    tk_img = ImageTk.PhotoImage(img)
    preview_lbl.config(image=tk_img, text="", width=240, height=180)
    preview_lbl.image = tk_img
    status_lbl.config(text=f"LOADED: {os.path.basename(fp)}", fg=GOLD)

def analyze_cigar():
    fp = selected_path.get("path")
    if not fp:
        status_lbl.config(text="SELECT A CIGAR PHOTO FIRST", fg=AMBER)
        return
    btn_scan.config(state="disabled")
    status_lbl.config(text="ANALYZING BAND & PAIRING FLIGHT...", fg=GOLD)
    out_box.delete("1.0", tk.END)
    out_box.insert(tk.END, "Inspecting cigar band, wrapper leaf, and crafting 3-tier pairing flight...\n")

    def worker():
        try:
            img = Image.open(fp).convert("RGB")
            img.thumbnail((1024, 1024))
            prompt = "Analyze this cigar photo as a Master Cigar Sommelier. Identify brand_and_line, origin_and_wrapper, strength, tasting_notes, and curate a 3-tier pairing flight: spirits_pairing, coffee_tea_pairing, wine_beer_pairing, plus sommelier_verdict."
            raw = call_gemini([img, prompt], schema=DesktopCigarProfile)
            data = json.loads(raw)
            last_profile.clear()
            last_profile.update(data)

            def render():
                out_box.delete("1.0", tk.END)
                out_box.insert(tk.END, f"CIGAR: {data.get('brand_and_line')}\n")
                out_box.insert(tk.END, f"ORIGIN & WRAPPER: {data.get('origin_and_wrapper')}  |  STRENGTH: {data.get('strength')}\n")
                out_box.insert(tk.END, f"TASTING NOTES: {', '.join(data.get('tasting_notes', []))}\n")
                out_box.insert(tk.END, "-" * 66 + "\n")
                out_box.insert(tk.END, f"1. SPIRITS PAIRING:      {data.get('spirits_pairing')}\n")
                out_box.insert(tk.END, f"2. COFFEE / TEA PAIRING: {data.get('coffee_tea_pairing')}\n")
                out_box.insert(tk.END, f"3. WINE / BEER PAIRING:  {data.get('wine_beer_pairing')}\n")
                out_box.insert(tk.END, "-" * 66 + "\n")
                out_box.insert(tk.END, f"SOMMELIER VERDICT: {data.get('sommelier_verdict')}\n")
                status_lbl.config(text="ANALYSIS COMPLETE", fg=GREEN)
                btn_scan.config(state="normal")
            root.after(0, render)
        except Exception as e:
            err = str(e)
            root.after(0, lambda: (out_box.insert(tk.END, f"\nError: {err}"), status_lbl.config(text="ERROR", fg=AMBER), btn_scan.config(state="normal")))

    threading.Thread(target=worker, daemon=True).start()

def pair_drink():
    drink = drink_var.get().strip()
    if not drink:
        return
    cigar_ctx = last_profile.get("brand_and_line", "a medium-to-full bodied premium cigar")
    status_lbl.config(text=f"EVALUATING PAIRING WITH {drink.upper()}...", fg=GOLD)

    def worker():
        try:
            prompt = f"As Master Cigar Sommelier for Fointein AI, evaluate pairing '{drink}' with {cigar_ctx}. Rate synergy (1-10) and give 2 crisp sentences on why the flavors work or clash."
            ans = call_gemini([prompt])
            root.after(0, lambda: (out_box.insert(tk.END, f"\n[CUSTOM DRINK CHECK: {drink.upper()}]\n{ans.strip()}\n"), out_box.see(tk.END), status_lbl.config(text="PAIRING EVALUATED", fg=GREEN)))
        except Exception as e:
            err = str(e)
            root.after(0, lambda: out_box.insert(tk.END, f"\nError: {err}\n"))

    threading.Thread(target=worker, daemon=True).start()

tk.Button(ctrl, text="1. SELECT CIGAR PHOTO", font=("Courier", 11, "bold"), bg="#2A1A10", fg=GOLD, command=choose_photo, pady=8).pack(fill="x", pady=(0, 8))
btn_scan = tk.Button(ctrl, text="2. ANALYZE BAND & PAIRING FLIGHT", font=("Courier", 11, "bold"), bg="#D4AF37", fg="#120C08", command=analyze_cigar, pady=8)
btn_scan.pack(fill="x", pady=(0, 12))

tk.Label(ctrl, text="PAIR MY DRINK (Enter Rum, Bourbon, Espresso, etc.):", font=("Courier", 9, "bold"), bg=BG, fg=CREAM, anchor="w").pack(fill="x")
drink_row = tk.Frame(ctrl, bg=BG)
drink_row.pack(fill="x", pady=(4, 0))
drink_var = tk.StringVar()
tk.Entry(drink_row, textvariable=drink_var, bg=CARD, fg=CREAM, insertbackground=CREAM, font=("Courier", 10)).pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 6))
tk.Button(drink_row, text="MATCH", font=("Courier", 10, "bold"), bg="#2A1A10", fg=GOLD, command=pair_drink, padx=10, pady=4).pack(side="right")

out_box = scrolledtext.ScrolledText(root, height=15, bg=CARD, fg=CREAM, font=("Courier", 10), bd=1, relief="groove", wrap=tk.WORD)
out_box.pack(fill="both", expand=True, padx=20, pady=(6, 16))
out_box.insert(tk.END, "Welcome to Fointein AI Cigar Sommelier v2.0 (Desktop Edition).\nSelect a cigar photo above to identify the blend and unlock your 3-tier pairing flight.\n")

root.mainloop()
