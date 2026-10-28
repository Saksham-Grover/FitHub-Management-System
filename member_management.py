"""
member_management.py - Member Management screen for FitHub (Member 3).

Features: add, view, update, delete (blocked if the member has bookings),
validation, and search by name, ID or membership type.
All SQL uses parameterised queries to prevent SQL injection.

Run on its own for testing:   py member_management.py
Called from the main menu:    show_member_management(root)
"""
import re
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

import mysql.connector

from db_config import get_connection

MEMBERSHIP_TYPES = ["Casual", "Monthly", "Annual"]
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z '\-]*$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^[0-9 +()\-]+$")

BG = "#2c3e50"
FG = "white"


# ---------------------------------------------------------------------------
# Database helper
# ---------------------------------------------------------------------------
def run_query(sql, params=(), fetch=False):
    """Run one parameterised query. Returns rows if fetch=True, else lastrowid."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, params)
        if fetch:
            return cursor.fetchall()
        connection.commit()
        return cursor.lastrowid
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_member(first, last, phone, email, membership, start_date):
    """Return an error message, or None if all the details are valid."""
    if not first or not last:
        return "First name and last name are required."
    if not NAME_PATTERN.match(first) or not NAME_PATTERN.match(last):
        return "Names may only contain letters, spaces, hyphens and apostrophes."
    if len(first) > 50 or len(last) > 50:
        return "Names must be 50 characters or fewer."
    if not phone and not email:
        return "Enter at least one contact detail (phone or email)."
    if phone:
        digits = re.sub(r"\D", "", phone)
        if not PHONE_PATTERN.match(phone) or not 8 <= len(digits) <= 15:
            return "Phone must have 8-15 digits (spaces, +, - and brackets allowed)."
    if email and (not EMAIL_PATTERN.match(email) or len(email) > 100):
        return "Enter a valid email address, for example name@example.com."
    if membership not in MEMBERSHIP_TYPES:
        return "Choose a membership type: Casual, Monthly or Annual."
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        return "Start date must be a real date in YYYY-MM-DD format."
    return None


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------
class MemberManagement:
    def __init__(self, window):
        self.window = window
        window.title("FitHub - Member Management")
        window.geometry("950x650")
        window.configure(bg=BG)

        self.selected_id = None
        self.first_var = tk.StringVar()
        self.last_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.type_var = tk.StringVar(value=MEMBERSHIP_TYPES[0])
        self.start_var = tk.StringVar(value=str(date.today()))
        self.search_by_var = tk.StringVar(value="Name")
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.build_form()
        self.build_buttons()
        self.build_search()
        self.build_table()
        self.load_members()

    # ----- layout ---------------------------------------------------------
    def build_form(self):
        form = tk.LabelFrame(self.window, text=" Member Details ", bg=BG, fg=FG, padx=10, pady=10)
        form.pack(fill="x", padx=15, pady=(15, 5))

        fields = [
            ("First Name", self.first_var), ("Last Name", self.last_var),
            ("Phone", self.phone_var), ("Email", self.email_var),
        ]
        for i, (label, var) in enumerate(fields):
            row, col = divmod(i, 2)
            tk.Label(form, text=label + ":", bg=BG, fg=FG).grid(row=row, column=col * 2, sticky="e", padx=5, pady=5)
            tk.Entry(form, textvariable=var, width=30).grid(row=row, column=col * 2 + 1, padx=5, pady=5)

        tk.Label(form, text="Membership Type:", bg=BG, fg=FG).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Combobox(form, textvariable=self.type_var, values=MEMBERSHIP_TYPES,
                     state="readonly", width=27).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form, text="Start Date (YYYY-MM-DD):", bg=BG, fg=FG).grid(row=2, column=2, sticky="e", padx=5, pady=5)
        tk.Entry(form, textvariable=self.start_var, width=30).grid(row=2, column=3, padx=5, pady=5)

    def build_buttons(self):
        bar = tk.Frame(self.window, bg=BG)
        bar.pack(fill="x", padx=15, pady=5)
        buttons = [
            ("Add Member", self.add_member, "#27ae60"),
            ("Update Member", self.update_member, "#2980b9"),
            ("Delete Member", self.delete_member, "#c0392b"),
            ("Clear Form", self.clear_form, "#7f8c8d"),
            ("Generate Report", self.generate_report, "#8e44ad"),
            ("Attendance Chart", self.show_chart, "#16a085"),
        ]
        for text, command, colour in buttons:
            tk.Button(bar, text=text, command=command, bg=colour, fg=FG, width=16).pack(side="left", padx=5)

    def build_search(self):
        bar = tk.LabelFrame(self.window, text=" Search ", bg=BG, fg=FG, padx=10, pady=5)
        bar.pack(fill="x", padx=15, pady=5)
        tk.Label(bar, text="Search by:", bg=BG, fg=FG).pack(side="left", padx=5)
        ttk.Combobox(bar, textvariable=self.search_by_var, values=["Name", "ID", "Membership Type"],
                     state="readonly", width=16).pack(side="left", padx=5)
        entry = tk.Entry(bar, textvariable=self.search_var, width=30)
        entry.pack(side="left", padx=5)
        entry.bind("<Return>", lambda event: self.search_members())
        tk.Button(bar, text="Search", command=self.search_members, bg="#2980b9", fg=FG, width=10).pack(side="left", padx=5)
        tk.Button(bar, text="Show All", command=self.show_all, bg="#7f8c8d", fg=FG, width=10).pack(side="left", padx=5)

    def build_table(self):
        frame = tk.Frame(self.window, bg=BG)
        frame.pack(fill="both", expand=True, padx=15, pady=5)
        columns = ("ID", "First Name", "Last Name", "Phone", "Email", "Membership", "Start Date")
        widths = (50, 110, 110, 120, 200, 100, 100)
        self.table = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for column, width in zip(columns, widths):
            self.table.heading(column, text=column)
            self.table.column(column, width=width, anchor="w")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self.on_select)
        tk.Label(self.window, textvariable=self.status_var, bg=BG, fg=FG, anchor="w").pack(fill="x", padx=15, pady=(0, 10))

    # ----- data loading ---------------------------------------------------
    def load_members(self, where="", params=()):
        sql = ("SELECT MemberID, FirstName, LastName, Phone, Email, MembershipType, StartDate "
               "FROM Member" + where + " ORDER BY LastName, FirstName")
        try:
            rows = run_query(sql, params, fetch=True)
        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", str(error))
            return
        self.table.delete(*self.table.get_children())
        for row in rows:
            self.table.insert("", "end", values=[("" if v is None else str(v)) for v in row])
        self.status_var.set(f"Showing {len(rows)} member(s).")

    def on_select(self, event=None):
        selection = self.table.selection()
        if not selection:
            return
        values = self.table.item(selection[0])["values"]
        self.selected_id = int(values[0])
        self.first_var.set(values[1])
        self.last_var.set(values[2])
        # Phone numbers lose their leading zero if Tk converts them to numbers.
        self.phone_var.set(str(values[3]) if values[3] != "" else "")
        self.email_var.set(values[4])
        self.type_var.set(values[5])
        self.start_var.set(values[6])

    def read_form(self):
        return (self.first_var.get().strip(), self.last_var.get().strip(),
                self.phone_var.get().strip(), self.email_var.get().strip(),
                self.type_var.get(), self.start_var.get().strip())

    def clear_form(self):
        self.selected_id = None
        for var in (self.first_var, self.last_var, self.phone_var, self.email_var):
            var.set("")
        self.type_var.set(MEMBERSHIP_TYPES[0])
        self.start_var.set(str(date.today()))
        self.table.selection_remove(self.table.selection())

    # ----- add / update / delete -----------------------------------------
    def add_member(self):
        first, last, phone, email, membership, start = self.read_form()
        error = validate_member(first, last, phone, email, membership, start)
        if error:
            messagebox.showwarning("Invalid Details", error)
            return
        try:
            new_id = run_query(
                "INSERT INTO Member (FirstName, LastName, Phone, Email, MembershipType, StartDate) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (first, last, phone or None, email or None, membership, start))
        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", str(error))
            return
        messagebox.showinfo("Member Added", f"{first} {last} was added with Member ID {new_id}.")
        self.clear_form()
        self.load_members()

    def update_member(self):
        if self.selected_id is None:
            messagebox.showwarning("No Member Selected", "Click a member in the table first.")
            return
        first, last, phone, email, membership, start = self.read_form()
        error = validate_member(first, last, phone, email, membership, start)
        if error:
            messagebox.showwarning("Invalid Details", error)
            return
        try:
            run_query(
                "UPDATE Member SET FirstName = %s, LastName = %s, Phone = %s, Email = %s, "
                "MembershipType = %s, StartDate = %s WHERE MemberID = %s",
                (first, last, phone or None, email or None, membership, start, self.selected_id))
        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", str(error))
            return
        messagebox.showinfo("Member Updated", "The member's details were updated.")
        self.clear_form()
        self.load_members()

    def delete_member(self):
        if self.selected_id is None:
            messagebox.showwarning("No Member Selected", "Click a member in the table first.")
            return
        try:
            # Business rule: a member with bookings cannot be deleted.
            count = run_query("SELECT COUNT(*) FROM Booking WHERE MemberID = %s",
                              (self.selected_id,), fetch=True)[0][0]
            if count > 0:
                messagebox.showerror(
                    "Cannot Delete Member",
                    f"This member has {count} booking(s) and cannot be deleted.")
                return
            if not messagebox.askyesno("Confirm Delete", "Delete this member permanently?"):
                return
            run_query("DELETE FROM Member WHERE MemberID = %s", (self.selected_id,))
        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", str(error))
            return
        messagebox.showinfo("Member Deleted", "The member was deleted.")
        self.clear_form()
        self.load_members()

    # ----- search ---------------------------------------------------------
    def search_members(self):
        term = self.search_var.get().strip()
        if not term:
            self.load_members()
            return
        by = self.search_by_var.get()
        like = f"%{term}%"
        if by == "ID":
            if not term.isdigit():
                messagebox.showwarning("Invalid Search", "Member ID must be a number.")
                return
            self.load_members(" WHERE MemberID = %s", (int(term),))
        elif by == "Name":
            self.load_members(
                " WHERE FirstName LIKE %s OR LastName LIKE %s OR CONCAT(FirstName, ' ', LastName) LIKE %s",
                (like, like, like))
        else:
            self.load_members(" WHERE MembershipType LIKE %s", (like,))

    def show_all(self):
        self.search_var.set("")
        self.load_members()

    # ----- report ---------------------------------------------------------
    def generate_report(self):
        # Attendance statistics by class type and trainer, exported to Excel.
        from attendance_analysis import export_attendance_report
        export_attendance_report()

    def show_chart(self):
        # Attendance per Week chart in its own window.
        from attendance_analysis import show_attendance_chart
        show_attendance_chart(self.window)


def show_member_management(parent=None):
    """Open the Member Management window. Pass the main menu root as parent."""
    if parent is None:
        window = tk.Tk()
        MemberManagement(window)
        window.mainloop()
    else:
        MemberManagement(tk.Toplevel(parent))


if __name__ == "__main__":
    show_member_management()
