import tkinter as tk
from tkinter import messagebox


def show_main_menu():
    # Create the management options window.
    root = tk.Tk()
    root.title("FitHub - Management Options")
    root.geometry("420x350")
    root.configure(bg="#2c3e50")
    root.resizable(False, False)

    # Show the heading at the top.
    tk.Label(root,text="Select Management Option",font=("Arial", 18, "bold"),bg="#2c3e50",fg="white").pack(pady=30)
    # These buttons will connect to the other modules later.
    def open_management(option):
        messagebox.showinfo("FitHub",f"{option} will be connected later.")
    # Add the three management buttons.
    for option in ["Class Management","Member Management","Booking Management"]:tk.Button(root,text=option,width=25,command=lambda name=option: open_management(name)).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    show_main_menu()
