import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageDraw
from pillow_heif import register_heif_opener
import time
import json
import sys
import os

register_heif_opener()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "clock_config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                path = data.get("bg_image", "")
                if path and not os.path.exists(path):
                    path = None
                return {
                    "bg_image": path,
                    "position": data.get("position", "bottom-left"),
                    "dim_level": data.get("dim_level", 0.70)
                }
        except Exception:
            pass
    return {"bg_image": None, "position": "bottom-left", "dim_level": 0.70}

def save_config():
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "bg_image": state["img_path"],
                "position": state["position"],
                "dim_level": state["dim_level"]
            }, f)
    except Exception:
        pass

saved = load_config()

root = tk.Tk()
root.title("Luxury Flip-Clock & Calendar v3.0")
root.geometry("760x440")
if len(sys.argv) > 1:
    root.geometry(sys.argv.pop())
root.configure(bg="#0D1117")

canvas = tk.Canvas(root, bg="#0D1117", highlightthickness=0)
canvas.pack(fill="both", expand=True)

state = {
    "img_path": saved["bg_image"],
    "pil_orig": None,
    "tk_bg": None,
    "dim_level": saved["dim_level"],
    "position": saved["position"]
}

if state["img_path"]:
    try:
        state["pil_orig"] = Image.open(state["img_path"]).convert("RGB")
    except Exception:
        state["pil_orig"] = None

def choose_backdrop():
    fp = filedialog.askopenfilename(
        title="Choose Personal Backdrop Photo",
        filetypes=(("Images", "*.png *.jpg *.jpeg *.heic *.HEIC *.webp *.bmp"), ("All Files", "*.*"))
    )
    if not fp:
        return
    try:
        state["pil_orig"] = Image.open(fp).convert("RGB")
        state["img_path"] = fp
        save_config()
        render_canvas()
    except Exception as e:
        messagebox.showerror("Photo Error", f"Could not load image:\n{e}")

def cycle_brightness():
    levels = [0.50, 0.70, 0.90]
    curr = state["dim_level"]
    next_idx = (levels.index(curr) + 1) % len(levels) if curr in levels else 1
    state["dim_level"] = levels[next_idx]
    save_config()
    render_canvas()

def cycle_position():
    positions = ["bottom-left", "bottom-right", "top-left", "center"]
    curr = state["position"]
    next_idx = (positions.index(curr) + 1) % len(positions) if curr in positions else 0
    state["position"] = positions[next_idx]
    save_config()
    render_canvas()

def render_canvas(event=None):
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w < 20 or h < 20:
        return

    # 1. Build Base Background Image (RGBA so we can composite frosted-glass cards)
    if state["pil_orig"]:
        img = state["pil_orig"].copy()
        img_ratio = img.width / img.height
        win_ratio = w / h

        if win_ratio > img_ratio:
            new_w = w
            new_h = int(w / img_ratio)
        else:
            new_h = h
            new_w = int(h * img_ratio)

        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        img = img.crop((left, top, left + w, top + h))
        img = ImageEnhance.Brightness(img).enhance(state["dim_level"]).convert("RGBA")
    else:
        img = Image.new("RGBA", (w, h), (13, 17, 23, 255))

    # 2. Calculate Proportional Flip-Card & Calendar Geometry
    pos = state["position"]
    is_center = (pos == "center")

    card_h = max(68, int(h * (0.26 if is_center else 0.21)))
    card_w = int(card_h * 0.92)
    gap = max(6, int(card_h * 0.10))
    pill_w = int(card_h * 0.44)
    cal_w = int(card_h * 0.96)
    radius = max(8, int(card_h * 0.14))

    total_w = (card_w * 2) + gap + (gap // 2) + pill_w + int(gap * 1.6) + cal_w
    margin_x = max(18, int(w * 0.04))
    margin_y = max(18, int(h * 0.06))

    if is_center:
        start_x = (w - total_w) // 2
        start_y = (h - card_h) // 2
    elif pos == "bottom-left":
        start_x = margin_x
        start_y = h - card_h - margin_y
    elif pos == "bottom-right":
        start_x = w - total_w - margin_x
        start_y = h - card_h - margin_y
    else:  # top-left
        start_x = margin_x
        start_y = margin_y

    # 3. Draw Translucent Frosted Flip-Cards & Calendar Card on Overlay Layer
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    glass_fill = (16, 19, 26, 190)       # Deep smoked glass
    pill_fill = (16, 19, 26, 165)        # Slightly lighter smoked glass
    gold_border = (212, 175, 55, 175)    # Luxury gold trim
    subtle_border = (255, 255, 255, 45)
    hinge_color = (0, 0, 0, 170)

    # Hour Card
    hx1, hy1 = start_x, start_y
    hx2, hy2 = hx1 + card_w, hy1 + card_h
    draw.rounded_rectangle([hx1, hy1, hx2, hy2], radius=radius, fill=glass_fill, outline=gold_border, width=2)

    # Minute Card
    mx1, my1 = hx2 + gap, start_y
    mx2, my2 = mx1 + card_w, my1 + card_h
    draw.rounded_rectangle([mx1, my1, mx2, my2], radius=radius, fill=glass_fill, outline=gold_border, width=2)

    # Uniform AM/PM + Seconds Side Pill
    px1, py1 = mx2 + (gap // 2), start_y
    px2, py2 = px1 + pill_w, py1 + card_h
    draw.rounded_rectangle([px1, py1, px2, py2], radius=radius, fill=pill_fill, outline=subtle_border, width=1)
    draw.line([px1 + 6, (py1 + py2) // 2, px2 - 6, (py1 + py2) // 2], fill=(255, 255, 255, 40), width=1)

    # Calendar Leaf Card
    cx1, cy1 = px2 + int(gap * 1.6), start_y
    cx2, cy2 = cx1 + cal_w, cy1 + card_h
    header_h = int(card_h * 0.28)
    draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=radius, fill=glass_fill, outline=gold_border, width=2)
    # Gold Top Month Banner
    draw.rounded_rectangle([cx1 + 1, cy1 + 1, cx2 - 1, cy1 + header_h], radius=radius, fill=(212, 175, 55, 230))
    draw.rectangle([cx1 + 1, cy1 + (header_h // 2), cx2 - 1, cy1 + header_h], fill=(212, 175, 55, 230))

    # Composite Frosted Glass Overlay onto Background Photo
    composited = Image.alpha_composite(img, overlay).convert("RGB")
    state["tk_bg"] = ImageTk.PhotoImage(composited)

    canvas.delete("all")
    canvas.create_image(0, 0, image=state["tk_bg"], anchor="nw")

    # 4. Draw Crisp Typography Inside Each Card
    now_hr = time.strftime("%I")
    now_min = time.strftime("%M")
    now_sec = time.strftime(":%S")
    now_ampm = time.strftime("%p")
    now_month = time.strftime("%b").upper()
    now_day_num = time.strftime("%d").lstrip("0") or "1"
    now_weekday = time.strftime("%a").upper()

    flip_font = ("Helvetica Neue", max(24, int(card_h * 0.56)), "bold")
    badge_font = ("Avenir Next", max(10, int(card_h * 0.17)), "bold")
    cal_month_font = ("Avenir Next", max(9, int(header_h * 0.58)), "bold")
    cal_num_font = ("Helvetica Neue", max(20, int(card_h * 0.40)), "bold")
    cal_day_font = ("Avenir Next", max(9, int(card_h * 0.15)), "bold")

    # Hour & Minute Digits
    canvas.create_text((hx1 + hx2) // 2, (hy1 + hy2) // 2, text=now_hr, font=flip_font, fill="#FFFFFF")
    canvas.create_text((mx1 + mx2) // 2, (my1 + my2) // 2, text=now_min, font=flip_font, fill="#FFFFFF")

    # Flip-Clock Center Split-Hinge Line Across Both Time Tiles
    mid_y = (hy1 + hy2) // 2
    canvas.create_line(hx1 + 2, mid_y, hx2 - 2, mid_y, fill="#0A0C10", width=2)
    canvas.create_line(mx1 + 2, mid_y, mx2 - 2, mid_y, fill="#0A0C10", width=2)

    # Uniform AM/PM (Top Half) & Seconds (Bottom Half) Inside Side Pill
    pill_cx = (px1 + px2) // 2
    canvas.create_text(pill_cx, py1 + int(card_h * 0.27), text=now_ampm, font=badge_font, fill="#D4AF37")
    canvas.create_text(pill_cx, py1 + int(card_h * 0.73), text=now_sec, font=badge_font, fill="#E6EDF3")

    # Calendar Leaf Text (Month Banner, Day Number, Weekday)
    cal_cx = (cx1 + cx2) // 2
    canvas.create_text(cal_cx, cy1 + (header_h // 2), text=now_month, font=cal_month_font, fill="#1C110A")
    canvas.create_text(cal_cx, cy1 + header_h + int((card_h - header_h) * 0.42), text=now_day_num, font=cal_num_font, fill="#FFFFFF")
    canvas.create_text(cal_cx, cy1 + header_h + int((card_h - header_h) * 0.80), text=now_weekday, font=cal_day_font, fill="#D4AF37")

    # 5. Floating Top-Right Controls
    canvas.create_window(w - 15, 15, window=controls_frame, anchor="ne")

controls_frame = tk.Frame(canvas, bg="#161B22", bd=1, relief="flat")

tk.Button(controls_frame, text="🖼️ Photo", font=("Avenir Next", 10, "bold"), bg="#21262D", fg="#D4AF37", command=choose_backdrop, bd=0, padx=8, pady=3).pack(side="left", padx=(0, 4))
tk.Button(controls_frame, text="📍 Move", font=("Avenir Next", 10, "bold"), bg="#21262D", fg="#58A6FF", command=cycle_position, bd=0, padx=8, pady=3).pack(side="left", padx=(0, 4))
tk.Button(controls_frame, text="☀️ Tint", font=("Avenir Next", 10, "bold"), bg="#21262D", fg="#F5E6CC", command=cycle_brightness, bd=0, padx=8, pady=3).pack(side="left")

def tick():
    render_canvas()
    root.after(1000, tick)

canvas.bind("<Configure>", render_canvas)
tick()
root.mainloop()
