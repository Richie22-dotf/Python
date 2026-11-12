from pillow_heif import register_heif_opener
register_heif_opener()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from google import genai
from pydantic import BaseModel
import threading, json, os

class CigarProfile(BaseModel):
    cigar_name: str
    brand: str
    origin: str
    wrapper: str
    binder: str
    filler: str
    strength: int
    strength_label: str
    notes: str
    pairing: str

CIGAR_DB = {
    "INCH Nicaragua No. 60": {"brand": "E.P. Carrillo", "origin": "Nicaragua", "wrapper": "Nicaraguan Habano", "binder": "Nicaraguan", "filler": "Nicaraguan", "strength": 85, "strength_label": "Medium-Full", "notes": "Bold black pepper, dark espresso, rich leather, and toasted cedar.", "pairing": "Bourbon or Double Espresso"},
    "New World by AJ Fernandez": {"brand": "AJ Fernandez", "origin": "Nicaragua", "wrapper": "Nicaraguan Oscuro", "binder": "Nicaraguan", "filler": "Nicaraguan", "strength": 88, "strength_label": "Full-Bodied", "notes": "Dark cocoa, roasted coffee, rich earth, and signature AJ pepper.", "pairing": "Single Malt Scotch or Espresso"},
    "Ashton VSG Sorcerer": {"brand": "Ashton", "origin": "Dominican Republic", "wrapper": "Ecuadorian Sumatra", "binder": "Dominican", "filler": "Dominican", "strength": 90, "strength_label": "Full-Bodied", "notes": "Rich cedar, espresso, dark chocolate, leather, and bold spice.", "pairing": "XO Cognac or Neat Bourbon"},
    "Drew Estate Undercrown Maduro": {"brand": "Drew Estate", "origin": "Nicaragua", "wrapper": "Mexican San Andres", "binder": "Connecticut", "filler": "Brazilian & Nicaraguan", "strength": 78, "strength_label": "Medium-Full", "notes": "Velvety dark chocolate, sweet espresso, earth, and black pepper.", "pairing": "Porter Beer or Cappuccino"},
    "Ashton Classic Magnum": {"brand": "Ashton", "origin": "Dominican Republic", "wrapper": "Connecticut Shade", "binder": "Dominican", "filler": "Dominican", "strength": 35, "strength_label": "Mild to Medium", "notes": "Silky buttered toast, vanilla bean, light cedar, and cashew.", "pairing": "Morning Latte or Chardonnay"}
}

BG, CARD, GOLD, CREAM, TAN = "#1C110A", "#2A1A10", "#D4AF37", "#F5E6CC", "#B89F82"
current_photo = None

def analyze_cigar(pil_img):
    def worker():
        try:
            key = os.environ.get("GEMINI_API_KEY")
            if not key:
                root.after(0, lambda: status_lbl.config(text="MISSING GEMINI_API_KEY", fg="#FF5555"))
                return
            client = genai.Client(api_key=key)
            img_rgb = pil_img.copy().convert("RGB")
            img_rgb.thumbnail((800, 800))

            candidates = [
                m.name.replace("models/", "") for m in client.models.list()
                if "flash" in m.name.lower() and not any(x in m.name.lower() for x in ["audio", "tts", "lite", "8b"])
            ]
            if not candidates:
                candidates = ["gemini-2.5-flash", "gemini-2.0-flash"]

            res = None
            last_err = ""
            for m_name in candidates:
                try:
                    root.after(0, lambda m=m_name: status_lbl.config(text=f"SCANNING VIA {m}...", fg="#00E6FF"))
                    res = client.models.generate_content(
                        model=m_name,
                        contents=[img_rgb, "Identify this cigar from its band and wrapper. Provide accurate sommelier details."],
                        config={"response_mime_type": "application/json", "response_schema": CigarProfile},
                    )
                    if res and res.text:
                        break
                except Exception as inner_e:
                    last_err = str(inner_e)[:42]
                    continue

            if not res or not res.text:
                raise Exception(last_err or "No active Flash model responded")

            data = json.loads(res.text)
            name = data["cigar_name"]
            def update_ui():
                CIGAR_DB[name] = data
                search_var.set("")
                refresh_list()
                select_cigar(name)
                status_lbl.config(text=f"AI MATCH: {name.upper()}", fg="#00FF00")
            root.after(0, update_ui)
        except Exception as e:
            err = str(e)[:42]
            root.after(0, lambda: status_lbl.config(text=f"ERR: {err}", fg="#FF5555"))
    threading.Thread(target=worker, daemon=True).start()

def upload_photo():
    global current_photo
    fp = filedialog.askopenfilename(filetypes=(("Images", "*.png *.jpg *.jpeg *.heic *.HEIC *.webp"), ("All", "*.*")))
    if not fp: return
    img = Image.open(fp)
    thumb = img.copy()
    thumb.thumbnail((250, 180))
    current_photo = ImageTk.PhotoImage(thumb)
    img_lbl.config(image=current_photo, text="")
    status_lbl.config(text="AI ANALYZING CIGAR BAND...", fg="#00E6FF")
    analyze_cigar(img)

def refresh_list(*args):
    q = search_var.get().lower().strip()
    listbox.delete(0, tk.END)
    for name, info in CIGAR_DB.items():
        if q in f"{name} {info['brand']} {info['wrapper']} {info['notes']}".lower():
            listbox.insert(tk.END, name)

def select_cigar(name):
    info = CIGAR_DB.get(name)
    if not info: return
    title_lbl.config(text=name)
    sub_lbl.config(text=f"{info['brand']}  |  Origin: {info['origin']}")
    wrap_lbl.config(text=f"Wrapper: {info['wrapper']}  |  Binder: {info['binder']}  |  Filler: {info['filler']}")
    bar["value"] = info["strength"]
    str_lbl.config(text=f"Strength: {info['strength_label']} ({info['strength']}/100)")
    notes_lbl.config(text=f"Notes: {info['notes']}")
    pair_lbl.config(text=f"Pairing: {info['pairing']}")

root = tk.Tk()
root.title("Aficionado AI Cigar Scanner v2.0")
root.geometry("860x580")
root.configure(bg=BG)

tk.Label(root, text="AFICIONADO AI CIGAR SOMMELIER v2.0", font=("Georgia", 17, "bold"), bg=BG, fg=GOLD).pack(pady=(15, 10))
main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=20, pady=10)

left = tk.Frame(main, bg=CARD, padx=15, pady=15, width=290)
left.pack(side="left", fill="y", padx=(0, 15))
left.pack_propagate(False)

img_lbl = tk.Label(left, text="No Photo Loaded", bg="#120B06", fg=TAN, width=32, height=11)
img_lbl.pack(pady=5)
tk.Button(left, text="SCAN CIGAR WITH AI VISION", font=("Courier", 10, "bold"), bg=GOLD, fg=BG, command=upload_photo).pack(fill="x", pady=6)
status_lbl = tk.Label(left, text="LIVE AI VISION READY", font=("Courier", 9, "bold"), bg=CARD, fg="#00FF00")
status_lbl.pack(pady=(0, 10))

search_var = tk.StringVar()
search_var.trace_add("write", refresh_list)
tk.Entry(left, textvariable=search_var, bg="#120B06", fg=CREAM, insertbackground=GOLD).pack(fill="x", pady=5)
listbox = tk.Listbox(left, bg="#120B06", fg=CREAM, selectbackground=GOLD, selectforeground=BG, font=("Georgia", 11))
listbox.pack(fill="both", expand=True)
listbox.bind("<<ListboxSelect>>", lambda e: select_cigar(listbox.get(listbox.curselection())) if listbox.curselection() else None)

right = tk.Frame(main, bg=CARD, padx=25, pady=20)
right.pack(side="right", fill="both", expand=True)
title_lbl = tk.Label(right, text="", font=("Georgia", 19, "bold"), bg=CARD, fg=GOLD, anchor="w")
title_lbl.pack(fill="x")
sub_lbl = tk.Label(right, text="", font=("Courier", 11, "bold"), bg=CARD, fg=TAN, anchor="w")
sub_lbl.pack(fill="x", pady=(2, 15))
wrap_lbl = tk.Label(right, text="", font=("Georgia", 12), bg=CARD, fg=CREAM, anchor="w", wraplength=460, justify="left")
wrap_lbl.pack(fill="x", pady=10)
bar = ttk.Progressbar(right, length=400, mode="determinate", maximum=100)
bar.pack(fill="x", pady=(15, 4))
str_lbl = tk.Label(right, text="", font=("Courier", 10, "bold"), bg=CARD, fg=CREAM, anchor="w")
str_lbl.pack(fill="x", pady=(0, 15))
notes_lbl = tk.Label(right, text="", font=("Georgia", 12, "italic"), bg=CARD, fg=CREAM, anchor="w", wraplength=460, justify="left")
notes_lbl.pack(fill="x", pady=10)
pair_lbl = tk.Label(right, text="", font=("Georgia", 12), bg=CARD, fg=CREAM, anchor="w", wraplength=460, justify="left")
pair_lbl.pack(fill="x", pady=10)

refresh_list()
select_cigar("INCH Nicaragua No. 60")
root.lift()
root.mainloop()
