import tkinter as tk
from tkinter import messagebox

import bcrypt
import mysql.connector

from db_config import get_connection


def login():
    # Get the Staff ID and password entered by the user.
    staff_id = staff_id_entry.get().strip()
    password = password_entry.get()
    # Make sure both fields have been filled in correctly.
    if not staff_id.isdigit() or not password:
        messagebox.showerror("Error", "Enter a valid Staff ID and password.")
        return
    connection = None
    cursor = None
    try:
        # Connect to the FitHub database.
        connection = get_connection()
        cursor = connection.cursor()

        # Find the staff account using its ID.
        cursor.execute(
            "SELECT PasswordHash FROM Staff WHERE StaffID = %s",
            (int(staff_id),)
        )

        staff = cursor.fetchone()
        # Check the entered password against the saved hash.
        if staff and bcrypt.checkpw(
            password.encode("utf-8"),
            staff[0].encode("utf-8")
        ):
            messagebox.showinfo("Success", "Login successful!")
            root.destroy()
        else:
            messagebox.showerror("Error", "Incorrect Staff ID or password.")

    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", str(error))

    finally:
        # Close the database connection when we're finished.
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Create the main login window.
root = tk.Tk()
root.title("FitHub - Staff Login")
root.geometry("400x300")
root.configure(bg="#2c3e50")
root.resizable(False, False)

# Add the login heading.
tk.Label(root,text="FitHub Login",font=("Arial", 20, "bold"),bg="#2c3e50",fg="white").pack(pady=20)

# Add the Staff ID field.
tk.Label(root,text="Staff ID:",bg="#2c3e50",fg="white").pack()

staff_id_entry = tk.Entry(root, width=30)
staff_id_entry.pack(pady=8)

# Add the password field and hide the typed characters.
tk.Label(root,text="Password:",bg="#2c3e50",fg="white").pack()
password_entry = tk.Entry(root, width=30, show="*")
password_entry.pack(pady=8)

# Add the button to check the login details.
tk.Button(root,text="Login",command=login,bg="#2980b9",fg="white",width=15).pack(pady=20)

root.mainloop()
