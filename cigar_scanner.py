import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

CIGAR_DB = {
    "Padron 1964 Anniversary Exclusivo": {
        "brand": "Padron",
        "origin": "Nicaragua",
        "wrapper": "Nicaraguan Maduro (Sun-Grown)",
        "binder": "Nicaraguan",
        "filler": "Nicaraguan (Aged 4 Years)",
        "strength": 85,
        "strength_label": "Medium-Full to Full",
        "notes": "Rich dark cocoa, espresso bean, toasted almond, black pepper, and a velvety sweet cedar finish.",
        "pairing": "Aged Single Malt Scotch, Bourbon, or Double Espresso"
    },
    "Arturo Fuente OpusX Robusto": {
        "brand": "Arturo Fuente",
        "origin": "Dominican Republic",
        "wrapper": "Dominican Rosado (Chateau de la Fuente)",
        "binder": "Dominican",
        "filler": "Dominican",
        "strength": 95,
        "strength_label": "Full-Bodied",
        "notes": "Bold baking spices, leather, dried cherry, sweet cedar, and intense white pepper.",
        "pairing": "XO Cognac, Vintage Port, or Neat Anejo Tequila"
    },
    "Montecristo No. 2": {
        "brand": "Montecristo",
        "origin": "Cuba / Dominican",
        "wrapper": "Connecticut Shade / Cuban Seed",
        "binder": "Dominican / Cuban",
        "filler": "Dominican / Cuban",
        "strength": 60,
        "strength_label": "Medium-Bodied",
        "notes": "Creamy toasted nuts, warm cinnamon, smooth leather, tangy citrus zest, and sweet wood.",
        "pairing": "Cappuccino, Champagne, or Aged Rum"
    },
    "Liga Privada No. 9 Toro": {
        "brand": "Drew Estate",
        "origin": "Nicaragua",
        "wrapper": "Connecticut Broadleaf Oscuro",
        "binder": "Brazilian Mata Fina",
        "filler": "Honduran & Nicaraguan",
        "strength": 90,
        "strength_label": "Full-Bodied",
        "notes": "Thick oily smoke with dark chocolate, earth, charred oak, black coffee, and subtle molasses.",
        "pairing": "Imperial Stout, Barrel-Proof Bourbon, or Dark Rum"
    },
    "Davidoff Winston Churchill Late Hour": {
        "brand": "Davidoff",
        "origin": "Dominican Republic",
        "wrapper": "Ecuadorian Habano Marron",
        "binder": "Mexican San Andres Negro",
        "filler": "Nicaraguan & Dominican (Aged in Scotch Casks)",
        "strength": 75,
        "strength_label": "Medium-Full",
        "notes": "Oak wood, dark roast coffee, sweet caramel, leather, and subtle smoky whisky undertones.",
        "pairing": "Single Malt Whisky, Bourbon, or Black Coffee"
    },
    "Oliva Serie V Melanio Figurado": {
        "brand": "Oliva",
        "origin": "Nicaragua",
        "wrapper": "Ecuadorian Sumatra",
        "binder": "Nicaraguan",
        "filler": "Nicaraguan Jalapa Ligero",
        "strength": 80,
        "strength_label": "Medium-Full",
        "notes": "Toasted caramel, rich leather, roasted hazelnuts, cocoa powder, and balanced spice.",
        "pairing": "Rye Whiskey, Espresso Martini, or Tawny Port"
    },
    "Ashton Classic Magnum": {
        "brand": "Ashton",
        "origin": "Dominican Republic",
        "wrapper": "Connecticut Shade (Golden Blonde)",
        "binder": "Dominican",
        "filler": "Dominican (Aged 3-4 Years)",
        "strength": 35,
        "strength_label": "Mild to Medium",
        "notes": "Silky buttered toast, vanilla bean, light cedar, cashew, and a clean creamy finish.",
        "pairing": "Morning Latte, Chardonnay, or Light Blonde Ale"
    },
    "My Father Le Bijou 1922 Torpedo": {
        "brand": "My Father Cigars",
        "origin": "Nicaragua",
        "wrapper": "Nicaraguan Habano Oscuro",
        "binder": "Nicaraguan",
        "filler": "Nicaraguan",
        "strength": 92,
        "strength_label": "Full-Bodied",
        "notes": "Dark chocolate-covered raisins, espresso, cloves, leather, and signature Nicaraguan pepper.",
        "pairing": "Cabernet Sauvignon, Bourbon, or Dark Roast Coffee"
    }
}

BG_MAHOGANY = "#1C110A"
PANEL_LEATHER = "#2A1A10"
GOLD_ACCENT = "#D4AF37"
CREAM_TEXT = "#F5E6CC"
MUTED_TAN = "#B89F82"

current_photo = None

def upload_cigar_photo():
    global current_photo
    file_path = filedialog.askopenfilename(
        title="Select Cigar or Band Photo",
        filetypes=(("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp"),)
    )
    if not file_path:
        return

    try:
        img = Image.open(file_path)
        img.thumbnail((260, 190))
        current_photo = ImageTk.PhotoImage(img)
        image_label.config(image=current_photo, text="")
        
        filename = os.path.basename(file_path).lower()
        matched = False
        for cigar_name in CIGAR_DB:
            brand_word = next(iter(cigar_name.split())).lower()
            if brand_word in filename:
                select_cigar_by_name(cigar_name)
                scan_status.config(text=f"BAND MATCHED: {cigar_name.upper()}", fg="#00FF00")
                matched = True
                break
        if not matched:
            scan_status.config(text="IMAGE LOADED - SELECT BLEND BELOW", fg=GOLD_ACCENT)
    except Exception as e:
        messagebox.showerror("Image Error", f"Could not load photo:\n{e}")

def filter_cigars(*args):
    query = search_var.get().lower().strip()
    cigar_listbox.delete(0, tk.END)
    for name, info in CIGAR_DB.items():
        searchable_text = f"{name} {info['brand']} {info['wrapper']} {info['origin']} {info['notes']}".lower()
        if query in searchable_text:
            cigar_listbox.insert(tk.END, name)

def on_list_select(event):
    selection = cigar_listbox.curselection()
    if selection:
        cigar_name = cigar_listbox.get(next(iter(selection)))
        display_cigar_details(cigar_name)

def select_cigar_by_name(target_name):
    cigar_listbox.selection_clear(0, tk.END)
    for idx in range(cigar_listbox.size()):
        if cigar_listbox.get(idx) == target_name:
            cigar_listbox.selection_set(idx)
            cigar_listbox.see(idx)
            break
    display_cigar_details(target_name)

def display_cigar_details(name):
    info = CIGAR_DB.get(name)
    if not info:
        return
    title_val.config(text=name)
    origin_val.config(text=f"{info['brand']}  |  Origin: {info['origin']}")
    wrapper_val.config(text=info["wrapper"])
    binder_val.config(text=info["binder"])
    filler_val.config(text=info["filler"])
    notes_val.config(text=info["notes"])
    pairing_val.config(text=info["pairing"])
    
    strength_bar["value"] = info["strength"]
    strength_text.config(text=f"{info['strength_label']} ({info['strength']}/100)")

root = tk.Tk()
root.title("Aficionado Lounge - Cigar Scanner & Humidor v1.0")
root.geometry("920x640")
root.configure(bg=BG_MAHOGANY)

header_frame = tk.Frame(root, bg=BG_MAHOGANY)
header_frame.pack(fill="x", padx=25, pady=(18, 10))

tk.Label(
    header_frame,
    text="AFICIONADO CIGAR SOMMELIER & SCANNER",
    font=("Georgia", 18, "bold"),
    bg=BG_MAHOGANY,
    fg=GOLD_ACCENT
).pack()

tk.Label(
    header_frame,
    text="DIGITAL HUMIDOR  |  WRAPPER TELEMETRY  |  TASTING PROFILES",
    font=("Courier", 10),
    bg=BG_MAHOGANY,
    fg=MUTED_TAN
).pack(pady=(2, 0))

main_container = tk.Frame(root, bg=BG_MAHOGANY)
main_container.pack(fill="both", expand=True, padx=25, pady=10)

left_col = tk.Frame(main_container, bg=PANEL_LEATHER, bd=2, relief="ridge", padx=15, pady=15, width=320)
left_col.pack(side="left", fill="y", padx=(0, 15))
left_col.pack_propagate(False)

tk.Label(left_col, text="BAND & WRAPPER VIEWER", font=("Courier", 11, "bold"), bg=PANEL_LEATHER, fg=GOLD_ACCENT).pack(pady=(0, 8))

photo_frame = tk.Frame(left_col, bg="#120B06", bd=2, relief="sunken", width=270, height=200)
photo_frame.pack(pady=5)
photo_frame.pack_propagate(False)

image_label = tk.Label(
    photo_frame,
    text="No Band Photo Loaded\n\nClick Below to Scan\nor Upload Image",
    font=("Courier", 10),
    bg="#120B06",
    fg=MUTED_TAN
)
image_label.pack(expand=True)

scan_btn = tk.Button(
    left_col,
    text="UPLOAD / SCAN CIGAR PHOTO",
    font=("Courier", 10, "bold"),
    bg=GOLD_ACCENT,
    fg="#1C110A",
    command=upload_cigar_photo,
    highlightbackground=PANEL_LEATHER
)
scan_btn.pack(fill="x", pady=(8, 4))

scan_status = tk.Label(left_col, text="OFFLINE HUMIDOR READY", font=("Courier", 9, "bold"), bg=PANEL_LEATHER, fg="#00FF00")
scan_status.pack(pady=(0, 10))

tk.Label(left_col, text="SEARCH BY BRAND, WRAPPER OR NOTE:", font=("Courier", 9, "bold"), bg=PANEL_LEATHER, fg=MUTED_TAN).pack(anchor="w")
search_var = tk.StringVar()
search_var.trace_add("write", filter_cigars)

search_entry = tk.Entry(left_col, textvariable=search_var, font=("Courier", 11), bg="#120B06", fg=CREAM_TEXT, insertbackground=GOLD_ACCENT)
search_entry.pack(fill="x", pady=(3, 8))

cigar_listbox = tk.Listbox(
    left_col,
    font=("Georgia", 11),
    bg="#120B06",
    fg=CREAM_TEXT,
    selectbackground=GOLD_ACCENT,
    selectforeground="#1C110A",
    bd=0,
    highlightthickness=1,
    highlightcolor=GOLD_ACCENT
)
cigar_listbox.pack(fill="both", expand=True)
cigar_listbox.bind("<<ListboxSelect>>", on_list_select)

right_col = tk.Frame(main_container, bg=PANEL_LEATHER, bd=2, relief="ridge", padx=25, pady=20)
right_col.pack(side="right", fill="both", expand=True)

title_val = tk.Label(right_col, text="", font=("Georgia", 20, "bold"), bg=PANEL_LEATHER, fg=GOLD_ACCENT, anchor="w", wraplength=500, justify="left")
title_val.pack(fill="x")

origin_val = tk.Label(right_col, text="", font=("Courier", 11, "bold"), bg=PANEL_LEATHER, fg=MUTED_TAN, anchor="w")
origin_val.pack(fill="x", pady=(2, 12))

ttk.Separator(right_col, orient="horizontal").pack(fill="x", pady=5)

leaf_frame = tk.Frame(right_col, bg=PANEL_LEATHER)
leaf_frame.pack(fill="x", pady=10)

def add_spec_row(parent, row_idx, label_title):
    tk.Label(parent, text=label_title, font=("Courier", 11, "bold"), bg=PANEL_LEATHER, fg=GOLD_ACCENT, width=12, anchor="w").grid(row=row_idx, column=0, sticky="w", pady=5)
    val_lbl = tk.Label(parent, text="", font=("Georgia", 12), bg=PANEL_LEATHER, fg=CREAM_TEXT, anchor="w", wraplength=380, justify="left")
    val_lbl.grid(row=row_idx, column=1, sticky="w", pady=5)
    return val_lbl

wrapper_val = add_spec_row(leaf_frame, 0, "WRAPPER:")
binder_val = add_spec_row(leaf_frame, 1, "BINDER:")
filler_val = add_spec_row(leaf_frame, 2, "FILLER:")

ttk.Separator(right_col, orient="horizontal").pack(fill="x", pady=10)

tk.Label(right_col, text="BODY & STRENGTH PROFILE:", font=("Courier", 11, "bold"), bg=PANEL_LEATHER, fg=GOLD_ACCENT, anchor="w").pack(fill="x")

style = ttk.Style()
style.theme_use("default")
style.configure("Cigar.Horizontal.TProgressbar", background=GOLD_ACCENT, troughcolor="#120B06", thickness=16)

strength_bar = ttk.Progressbar(right_col, style="Cigar.Horizontal.TProgressbar", length=400, mode="determinate", maximum=100)
strength_bar.pack(fill="x", pady=(6, 2))

strength_text = tk.Label(right_col, text="", font=("Courier", 10, "bold"), bg=PANEL_LEATHER, fg=CREAM_TEXT, anchor="e")
strength_text.pack(fill="x", pady=(0, 10))

tk.Label(right_col, text="TASTING NOTES & AROMA:", font=("Courier", 11, "bold"), bg=PANEL_LEATHER, fg=GOLD_ACCENT, anchor="w").pack(fill="x", pady=(5, 2))
notes_val = tk.Label(right_col, text="", font=("Georgia", 12, "italic"), bg=PANEL_LEATHER, fg=CREAM_TEXT, anchor="w", wraplength=500, justify="left")
notes_val.pack(fill="x", pady=(0, 12))

tk.Label(right_col, text="RECOMMENDED LOUNGE PAIRING:", font=("Courier", 11, "bold"), bg=PANEL_LEATHER, fg=GOLD_ACCENT, anchor="w").pack(fill="x", pady=(5, 2))
pairing_val = tk.Label(right_col, text="", font=("Georgia", 12), bg=PANEL_LEATHER, fg=CREAM_TEXT, anchor="w", wraplength=500, justify="left")
pairing_val.pack(fill="x")

filter_cigars()
select_cigar_by_name("Padron 1964 Anniversary Exclusivo")

root.lift()
root.attributes("-topmost", True)
root.after(500, lambda: root.attributes("-topmost", False))

root.mainloop()
