import tkinter as tk
import time

def update_time():
    # 1. Get the current time and date from your Mac
    current_time = time.strftime("%I:%M:%S %p")
    current_date = time.strftime("%A, %b %d, %Y") # Format: Day, Month Date, Year
    
    # 2. Update both displays on the screen
    time_label.config(text=current_time)
    date_label.config(text=current_date)
    
    # 3. Refresh every single second
    root.after(1000, update_time)

# Main layout setup (Keeping your blue theme!)
root = tk.Tk()
root.title("My Live Digital Clock & Date")
root.geometry("450x200") 
import sys
if len(sys.argv) > 1:
    root.geometry(sys.argv.pop())# Made slightly taller for the date
root.configure(bg="blue")

# Time display string
time_label = tk.Label(
    root, 
    text="", 
    font=("Arial", 44, "bold"), 
    bg="blue", 
    fg="white" # Swapped to white text so it looks crisp on blue
)
time_label.pack(pady=(20, 0))

# Date display string
date_label = tk.Label(
    root, 
    text="", 
    font=("Arial", 18, "italic"), 
    bg="blue", 
    fg="#E0E0E0" # Light gray text so it stands out subtly
)
date_label.pack(pady=10)

# Start the live tracking loop
update_time()

root.mainloop()
