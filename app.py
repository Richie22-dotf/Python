import tkinter as tk

def convert_text():
    # 1. Get text from the input box
    user_input = entry.get()
    
    # 2. Count how many letters the user typed
    letter_count = len(user_input)
    
    # 3. Display the uppercase text AND the letter count on the screen
    result_label.config(text=f"Output: {user_input.upper()}\n({letter_count} characters)")

# Create the main window layout
root = tk.Tk()
root.title("My Upgraded Python App")
root.geometry("400x280") # Made slightly taller to fit the extra text

# Add an instruction label
instruction_label = tk.Label(root, text="Type something below:", font=("Arial", 12))
instruction_label.pack(pady=10)

# Add the text input box
entry = tk.Entry(root, font=("Arial", 14), width=25)
entry.pack(pady=5)

# Add the action button
button = tk.Button(root, text="Convert and Count", command=convert_text, font=("Arial", 12))
button.pack(pady=10)

# Add the live output display area (Now with a green color!)
result_label = tk.Label(root, text="Output: ", font=("Arial", 14, "bold"), fg="darkgreen")
result_label.pack(pady=20)

# Keep the window running on your desktop
root.mainloop()