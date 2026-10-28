import tkinter as tk
from tkinter import ttk, messagebox
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import os

from db_config import get_connection


# These are the class types FitHub offers
CLASS_TYPES = ["Yoga", "HIIT", "Pilates", "Spin", "Boxing"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# This function is used by Member 4 (Booking Management) to check if a class is full
def check_class_capacity(class_id, class_date):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get the max capacity for the class
        cursor.execute("SELECT Capacity FROM Class WHERE ClassID = %s", (class_id,))
        result = cursor.fetchone()
        if not result:
            return (0, 0, True)
        capacity = result[0]

        # Count how many active bookings exist for this class on that date
        cursor.execute(
            "SELECT COUNT(*) FROM Booking WHERE ClassID = %s AND ClassDate = %s AND BookingStatus = 'Booked'",
            (class_id, class_date)
        )
        booked_count = cursor.fetchone()[0]

        is_full = booked_count >= capacity
        return (booked_count, capacity, is_full)

    except Exception as e:
        print(f"Error checking capacity: {e}")
        return (0, 0, False)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


class ClassManagementWindow:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("FitHub - Class Management")
        self.parent.geometry("1050x650")
        self.parent.configure(bg="#2c3e50")

        # Keeps track of which class is selected in the table
        self.selected_class_id = None

        self.build_ui()
        self.load_trainers()
        self.load_classes()

    def build_ui(self):
        # Top heading
        tk.Label(
            self.parent,
            text="Class Management",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=10)

        # Main layout: left side is the form, right side is the table
        main_frame = tk.Frame(self.parent, bg="#2c3e50")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.build_form(main_frame)
        self.build_table(main_frame)

    def build_form(self, parent):
        form_frame = tk.LabelFrame(
            parent,
            text="Class Details",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        form_frame.pack(side="left", fill="y", padx=(0, 10))

        def add_field(label_text, row):
            tk.Label(form_frame, text=label_text, bg="#2c3e50", fg="white", anchor="w").grid(
                row=row, column=0, sticky="w", pady=4
            )

        # Class Name
        add_field("Class Name:", 0)
        self.class_name_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.class_name_var, width=25).grid(row=0, column=1, pady=4)

        # Class Type dropdown
        add_field("Class Type:", 1)
        self.class_type_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.class_type_var, values=CLASS_TYPES, width=23, state="readonly").grid(
            row=1, column=1, pady=4
        )

        # Trainer dropdown - populated from the database
        add_field("Trainer:", 2)
        self.trainer_var = tk.StringVar()
        self.trainer_combo = ttk.Combobox(form_frame, textvariable=self.trainer_var, width=23, state="readonly")
        self.trainer_combo.grid(row=2, column=1, pady=4)

        # Day of Week dropdown
        add_field("Day of Week:", 3)
        self.day_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.day_var, values=DAYS, width=23, state="readonly").grid(
            row=3, column=1, pady=4
        )

        # Start Time - just a text field, format HH:MM
        add_field("Start Time (HH:MM):", 4)
        self.time_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.time_var, width=25).grid(row=4, column=1, pady=4)

        # Capacity
        add_field("Capacity:", 5)
        self.capacity_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.capacity_var, width=25).grid(row=5, column=1, pady=4)

        # Fee
        add_field("Fee ($):", 6)
        self.fee_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.fee_var, width=25).grid(row=6, column=1, pady=4)

        # buttons for add/update/delete/clear
        btn_frame = tk.Frame(form_frame, bg="#2c3e50")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=12)

        btn_style = {"fg": "white", "width": 10, "padx": 4, "pady": 4, "font": ("Arial", 10)}

        tk.Button(btn_frame, text="Add", bg="#27ae60", command=self.add_class, **btn_style).grid(row=0, column=0, padx=4)
        tk.Button(btn_frame, text="Update", bg="#2980b9", command=self.update_class, **btn_style).grid(row=0, column=1, padx=4)
        tk.Button(btn_frame, text="Delete", bg="#c0392b", command=self.delete_class, **btn_style).grid(row=0, column=2, padx=4)
        tk.Button(btn_frame, text="Clear", bg="#7f8c8d", command=self.clear_form, **btn_style).grid(row=0, column=3, padx=4)

        # Search / filter section
        search_frame = tk.LabelFrame(
            form_frame,
            text="Search & Filter",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=8,
            pady=8
        )
        search_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        tk.Label(search_frame, text="Name:", bg="#2c3e50", fg="white").grid(row=0, column=0, sticky="w")
        self.search_name_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_name_var, width=18).grid(row=0, column=1, pady=2)

        tk.Label(search_frame, text="Type:", bg="#2c3e50", fg="white").grid(row=1, column=0, sticky="w")
        self.search_type_var = tk.StringVar()
        ttk.Combobox(search_frame, textvariable=self.search_type_var, values=["All"] + CLASS_TYPES, width=16, state="readonly").grid(
            row=1, column=1, pady=2
        )
        self.search_type_var.set("All")

        tk.Label(search_frame, text="Day:", bg="#2c3e50", fg="white").grid(row=2, column=0, sticky="w")
        self.search_day_var = tk.StringVar()
        ttk.Combobox(search_frame, textvariable=self.search_day_var, values=["All"] + DAYS, width=16, state="readonly").grid(
            row=2, column=1, pady=2
        )
        self.search_day_var.set("All")

        tk.Label(search_frame, text="Min Fee ($):", bg="#2c3e50", fg="white").grid(row=3, column=0, sticky="w")
        self.search_min_fee_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_min_fee_var, width=18).grid(row=3, column=1, pady=2)

        tk.Label(search_frame, text="Max Fee ($):", bg="#2c3e50", fg="white").grid(row=4, column=0, sticky="w")
        self.search_max_fee_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_max_fee_var, width=18).grid(row=4, column=1, pady=2)

        search_btn_frame = tk.Frame(search_frame, bg="#2c3e50")
        search_btn_frame.grid(row=5, column=0, columnspan=2, pady=6)

        tk.Button(search_btn_frame, text="Search", bg="#2980b9", fg="white", width=10, command=self.search_classes).grid(row=0, column=0, padx=4)
        tk.Button(search_btn_frame, text="Show All", bg="#7f8c8d", fg="white", width=10, command=self.load_classes).grid(row=0, column=1, padx=4)

        # report buttons at the bottom
        report_frame = tk.Frame(form_frame, bg="#2c3e50")
        report_frame.grid(row=9, column=0, columnspan=2, pady=(10, 0))

        tk.Button(
            report_frame,
            text="Export Fully Booked (Excel)",
            bg="#2980b9",
            fg="white",
            command=self.export_fully_booked_report
        ).grid(row=0, column=0, padx=4, pady=4)

        tk.Button(
            report_frame,
            text="Bookings by Class Type (Chart)",
            bg="#2980b9",
            fg="white",
            command=self.show_bookings_chart
        ).grid(row=1, column=0, padx=4, pady=4)

    def build_table(self, parent):
        table_frame = tk.Frame(parent, bg="#2c3e50")
        table_frame.pack(side="right", fill="both", expand=True)

        columns = ("ClassID", "Class Name", "Type", "Trainer", "Day", "Start Time", "Capacity", "Fee")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=25)

        # Set column headings and widths, clicking a heading sorts by that column
        widths = [65, 140, 80, 120, 90, 90, 80, 70]
        for col, w in zip(columns, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=w, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Clicking a row fills the form with that class's details
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        self.sort_dir = {}

    def load_trainers(self):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT TrainerID, TrainerName FROM Trainer ORDER BY TrainerName")
            rows = cursor.fetchall()

            # Store as a dict so we can look up TrainerID by name when saving
            self.trainer_map = {name: tid for tid, name in rows}
            self.trainer_id_to_name = {tid: name for tid, name in rows}
            self.trainer_combo["values"] = list(self.trainer_map.keys())

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def load_classes(self):
        # Load all classes from the database and show them in the table
        self.tree.delete(*self.tree.get_children())
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.ClassID, c.ClassName, c.ClassType, t.TrainerName,
                       c.DayOfWeek, c.StartTime, c.Capacity, c.Fee
                FROM Class c
                JOIN Trainer t ON c.TrainerID = t.TrainerID
                ORDER BY c.ClassID
            """)
            rows = cursor.fetchall()
            for row in rows:
                row = list(row)
                # mysql gives timedelta for TIME columns, just cut to HH:MM
                row[5] = str(row[5])[:5]
                row[7] = f"${row[7]:.2f}"
                self.tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_class_id = values[0]

        # Fill the form fields with the selected row's data
        self.class_name_var.set(values[1])
        self.class_type_var.set(values[2])
        self.trainer_var.set(values[3])
        self.day_var.set(values[4])
        self.time_var.set(values[5])
        self.capacity_var.set(values[6])
        # Strip the dollar sign when putting fee back into the entry box
        self.fee_var.set(values[7].replace("$", ""))

    def clear_form(self):
        self.selected_class_id = None
        self.class_name_var.set("")
        self.class_type_var.set("")
        self.trainer_var.set("")
        self.day_var.set("")
        self.time_var.set("")
        self.capacity_var.set("")
        self.fee_var.set("")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def validate_form(self):
        # Make sure all fields are filled and values are valid before saving
        name = self.class_name_var.get().strip()
        class_type = self.class_type_var.get().strip()
        trainer = self.trainer_var.get().strip()
        day = self.day_var.get().strip()
        time_str = self.time_var.get().strip()
        capacity = self.capacity_var.get().strip()
        fee = self.fee_var.get().strip()

        if not all([name, class_type, trainer, day, time_str, capacity, fee]):
            messagebox.showerror("Validation Error", "Please fill in all fields.")
            return None

        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Validation Error", "Start time must be in HH:MM format (e.g. 09:30).")
            return None

        try:
            cap_val = int(capacity)
            if cap_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Capacity must be a positive whole number.")
            return None

        try:
            fee_val = float(fee)
            if fee_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Fee must be 0 or more.")
            return None

        return {
            "name": name,
            "class_type": class_type,
            "trainer_id": self.trainer_map[trainer],
            "day": day,
            "time": time_str,
            "capacity": cap_val,
            "fee": fee_val
        }

    def add_class(self):
        data = self.validate_form()
        if not data:
            return

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Class (ClassName, ClassType, TrainerID, DayOfWeek, StartTime, Capacity, Fee)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (data["name"], data["class_type"], data["trainer_id"], data["day"],
                  data["time"], data["capacity"], data["fee"]))
            conn.commit()
            messagebox.showinfo("Success", "Class added successfully.")
            self.clear_form()
            self.load_classes()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update_class(self):
        if not self.selected_class_id:
            messagebox.showerror("Error", "Please select a class from the table to update.")
            return

        data = self.validate_form()
        if not data:
            return

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Class
                SET ClassName=%s, ClassType=%s, TrainerID=%s, DayOfWeek=%s,
                    StartTime=%s, Capacity=%s, Fee=%s
                WHERE ClassID=%s
            """, (data["name"], data["class_type"], data["trainer_id"], data["day"],
                  data["time"], data["capacity"], data["fee"], self.selected_class_id))
            conn.commit()
            messagebox.showinfo("Success", "Class updated successfully.")
            self.clear_form()
            self.load_classes()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_class(self):
        if not self.selected_class_id:
            messagebox.showerror("Error", "Please select a class from the table to delete.")
            return

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Check if any bookings exist for this class before deleting
            cursor.execute("SELECT COUNT(*) FROM Booking WHERE ClassID = %s", (self.selected_class_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                messagebox.showerror(
                    "Cannot Delete",
                    f"This class has {count} booking(s). Please remove the bookings first before deleting the class."
                )
                return

            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this class?")
            if not confirm:
                return

            cursor.execute("DELETE FROM Class WHERE ClassID = %s", (self.selected_class_id,))
            conn.commit()
            messagebox.showinfo("Success", "Class deleted successfully.")
            self.clear_form()
            self.load_classes()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def search_classes(self):
        # Build a dynamic query using whatever filter fields the user has filled in
        conditions = []
        params = []

        name = self.search_name_var.get().strip()
        class_type = self.search_type_var.get()
        day = self.search_day_var.get()
        min_fee = self.search_min_fee_var.get().strip()
        max_fee = self.search_max_fee_var.get().strip()

        if name:
            conditions.append("c.ClassName LIKE %s")
            params.append(f"%{name}%")
        if class_type and class_type != "All":
            conditions.append("c.ClassType = %s")
            params.append(class_type)
        if day and day != "All":
            conditions.append("c.DayOfWeek = %s")
            params.append(day)
        if min_fee:
            try:
                conditions.append("c.Fee >= %s")
                params.append(float(min_fee))
            except ValueError:
                messagebox.showerror("Error", "Min fee must be a number.")
                return
        if max_fee:
            try:
                conditions.append("c.Fee <= %s")
                params.append(float(max_fee))
            except ValueError:
                messagebox.showerror("Error", "Max fee must be a number.")
                return

        query = """
            SELECT c.ClassID, c.ClassName, c.ClassType, t.TrainerName,
                   c.DayOfWeek, c.StartTime, c.Capacity, c.Fee
            FROM Class c
            JOIN Trainer t ON c.TrainerID = t.TrainerID
        """
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY c.ClassID"

        self.tree.delete(*self.tree.get_children())
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            for row in rows:
                row = list(row)
                row[5] = str(row[5])[:5]
                row[7] = f"${row[7]:.2f}"
                self.tree.insert("", "end", values=row)

            if not rows:
                messagebox.showinfo("Search", "No classes found matching those filters.")

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def sort_column(self, col):
        # click header to sort, click again to reverse
        ascending = self.sort_dir.get(col, True)
        rows = [(self.tree.set(child, col), child) for child in self.tree.get_children()]
        rows.sort(key=lambda x: x[0].lower(), reverse=not ascending)

        for i, (_, child) in enumerate(rows):
            self.tree.move(child, "", i)

        self.sort_dir[col] = not ascending

    def export_fully_booked_report(self):
        # Find classes where bookings on a specific date have reached the capacity
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.ClassID, c.ClassName, c.ClassType, t.TrainerName,
                       c.DayOfWeek, c.StartTime, c.Capacity,
                       b.ClassDate, COUNT(b.BookingID) as Booked
                FROM Class c
                JOIN Trainer t ON c.TrainerID = t.TrainerID
                JOIN Booking b ON b.ClassID = c.ClassID AND b.BookingStatus = 'Booked'
                GROUP BY c.ClassID, b.ClassDate
                HAVING Booked >= c.Capacity
                ORDER BY b.ClassDate, c.ClassName
            """)
            rows = cursor.fetchall()

            if not rows:
                messagebox.showinfo("Report", "No fully booked classes found at the moment.")
                return

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Fully Booked Classes"

            headers = ["Class ID", "Class Name", "Type", "Trainer", "Day", "Start Time", "Capacity", "Date", "Booked"]
            header_fill = PatternFill(start_color="2980B9", end_color="2980B9", fill_type="solid")

            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")

            for row_num, row in enumerate(rows, 2):
                for col_num, value in enumerate(row, 1):
                    # timedelta comes back from mysql for TIME columns
                    value = str(value)[:5] if hasattr(value, 'seconds') else value
                    ws.cell(row=row_num, column=col_num, value=value)

            # set some basic column widths so it looks decent
            col_widths = {1: 10, 2: 20, 3: 12, 4: 18, 5: 12, 6: 12, 7: 10, 8: 14, 9: 10}
            for col_idx, width in col_widths.items():
                ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = width

            # TODO: maybe let the user pick where to save instead of current folder
            filename = f"fully_booked_classes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            wb.save(filename)
            messagebox.showinfo("Report Saved", f"Report saved as:\n{os.path.abspath(filename)}")

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def show_bookings_chart(self):
        # Count bookings per class type and show as a bar chart in a new window
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.ClassType, COUNT(b.BookingID) as TotalBookings
                FROM Class c
                LEFT JOIN Booking b ON b.ClassID = c.ClassID AND b.BookingStatus = 'Booked'
                GROUP BY c.ClassType
                ORDER BY TotalBookings DESC
            """)
            rows = cursor.fetchall()

            if not rows:
                messagebox.showinfo("Chart", "No booking data to display yet.")
                return

            types = [row[0] for row in rows]
            counts = [row[1] for row in rows]

            chart_window = tk.Toplevel(self.parent)
            chart_window.title("Bookings by Class Type")
            chart_window.configure(bg="#2c3e50")

            fig, ax = plt.subplots(figsize=(7, 5))
            colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]
            bars = ax.bar(types, counts, color=colors[:len(types)])

            # Show the count on top of each bar
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + 0.3,
                    str(int(height)),
                    ha="center",
                    va="bottom",
                    fontsize=10
                )

            ax.set_title("Bookings by Class Type", fontsize=14)
            ax.set_xlabel("Class Type")
            ax.set_ylabel("Total Bookings")
            ax.set_ylim(0, max(counts) + 5 if counts else 10)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# Run standalone for testing without the full app
if __name__ == "__main__":
    root = tk.Tk()
    app = ClassManagementWindow(root)
    root.mainloop()
