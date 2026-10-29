import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from openpyxl import Workbook

from database import get_connection


class BookingManagement:
    def __init__(self, root):
        self.root = root
        self.root.title("FitHub - Booking Management")
        self.root.geometry("1100x700")

        # --------------------------------------------------
        # TITLE
        # --------------------------------------------------
        title = tk.Label(
            root,
            text="FitHub Booking Management",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=15)

        # --------------------------------------------------
        # BOOKING FORM
        # --------------------------------------------------
        form_frame = tk.LabelFrame(
            root,
            text="Create New Booking",
            padx=15,
            pady=15
        )
        form_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        # Member
        tk.Label(
            form_frame,
            text="Member:"
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=5
        )

        self.member_combo = ttk.Combobox(
            form_frame,
            state="readonly",
            width=25
        )
        self.member_combo.grid(
            row=0,
            column=1,
            padx=5,
            pady=5
        )

        # Class
        tk.Label(
            form_frame,
            text="Class:"
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=5
        )

        self.class_combo = ttk.Combobox(
            form_frame,
            state="readonly",
            width=25
        )
        self.class_combo.grid(
            row=0,
            column=3,
            padx=5,
            pady=5
        )

        # Class Date
        tk.Label(
            form_frame,
            text="Class Date (YYYY-MM-DD):"
        ).grid(
            row=0,
            column=4,
            padx=5,
            pady=5
        )

        self.date_entry = tk.Entry(
            form_frame,
            width=15
        )
        self.date_entry.grid(
            row=0,
            column=5,
            padx=5,
            pady=5
        )

        # Book Class button
        tk.Button(
            form_frame,
            text="Book Class",
            width=15,
            command=self.book_class
        ).grid(
            row=0,
            column=6,
            padx=10,
            pady=5
        )

        # --------------------------------------------------
        # BOOKINGS TABLE
        # --------------------------------------------------
        table_frame = tk.Frame(root)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        columns = (
            "BookingID",
            "Member",
            "Class",
            "ClassDate",
            "Status",
            "Attendance",
            "Fee"
        )

        self.booking_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "BookingID": "Booking ID",
            "Member": "Member",
            "Class": "Class",
            "ClassDate": "Class Date",
            "Status": "Status",
            "Attendance": "Attendance",
            "Fee": "Fee"
        }

        for column, heading in headings.items():
            self.booking_table.heading(
                column,
                text=heading
            )

        self.booking_table.column(
            "BookingID",
            width=80
        )

        self.booking_table.column(
            "Member",
            width=160
        )

        self.booking_table.column(
            "Class",
            width=160
        )

        self.booking_table.column(
            "ClassDate",
            width=110
        )

        self.booking_table.column(
            "Status",
            width=100
        )

        self.booking_table.column(
            "Attendance",
            width=120
        )

        self.booking_table.column(
            "Fee",
            width=80
        )

        self.booking_table.pack(
            fill="both",
            expand=True
        )
        # --------------------------------------------------
        # SEARCH AND FILTER
        # --------------------------------------------------
        search_frame = tk.LabelFrame(
            root,
            text="Search and Filter Bookings",
            padx=10,
            pady=10
        )
        search_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        # Member Name
        tk.Label(
            search_frame,
            text="Member Name:"
        ).grid(row=0, column=0, padx=5, pady=5)

        self.search_member_entry = tk.Entry(
            search_frame,
            width=18
        )
        self.search_member_entry.grid(
            row=0,
            column=1,
            padx=5,
            pady=5
        )

        # Class Name
        tk.Label(
            search_frame,
            text="Class Name:"
        ).grid(row=0, column=2, padx=5, pady=5)

        self.search_class_entry = tk.Entry(
            search_frame,
            width=18
        )
        self.search_class_entry.grid(
            row=0,
            column=3,
            padx=5,
            pady=5
        )

        # Status
        tk.Label(
            search_frame,
            text="Status:"
        ).grid(row=0, column=4, padx=5, pady=5)

        self.search_status_combo = ttk.Combobox(
            search_frame,
            width=15,
            state="readonly",
            values=[
                "",
                "Booked",
                "Cancelled",
                "Late Cancel"
            ]
        )
        self.search_status_combo.grid(
            row=0,
            column=5,
            padx=5,
            pady=5
        )

        # Class Date
        tk.Label(
            search_frame,
            text="Class Date:"
        ).grid(row=0, column=6, padx=5, pady=5)

        self.search_date_entry = tk.Entry(
            search_frame,
            width=15
        )
        self.search_date_entry.grid(
            row=0,
            column=7,
            padx=5,
            pady=5
        )

        # Search Button
        tk.Button(
            search_frame,
            text="Search",
            width=12,
            command=self.search_bookings
        ).grid(
            row=0,
            column=8,
            padx=5,
            pady=5
        )

        # Clear Search Button
        tk.Button(
            search_frame,
            text="Clear Search",
            width=12,
            command=self.clear_search
        ).grid(
            row=0,
            column=9,
            padx=5,
            pady=5
        )
       
        # --------------------------------------------------
        # BOTTOM BUTTONS
        # --------------------------------------------------
        button_frame = tk.Frame(root)
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="Refresh Bookings",
            width=18,
            command=self.load_bookings
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            button_frame,
            text="Cancel Booking",
            width=18,
            command=self.cancel_booking
        ).pack(
            side="left",
            padx=10
        )

        tk.Button(
            button_frame,
            text="Mark Attendance",
            width=18,
            command=self.mark_attendance
        ).pack(
            side="left",
            padx=10
        )

        tk.Button(
            button_frame,
            text="Generate Report",
            width=18,
            command=self.generate_report
        ).pack(
             side="left",
             padx=5
        )

        tk.Button(
            button_frame,
            text="Close",
            width=12,
            command=root.destroy
        ).pack(
            side="left",
            padx=5
        )

        # Load data when program starts
        self.load_members()
        self.load_classes()
        self.load_bookings()

    # --------------------------------------------------
    # LOAD MEMBERS
    # --------------------------------------------------
    def load_members(self):
        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT MemberID, FirstName, LastName
                FROM Member
                ORDER BY FirstName, LastName
                """
            )

            members = cursor.fetchall()

            self.member_combo["values"] = [
                f"{member[0]} - {member[1]} {member[2]}"
                for member in members
            ]

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Unable to load members:\n{error}"
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # --------------------------------------------------
    # LOAD CLASSES
    # --------------------------------------------------
    def load_classes(self):
        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT ClassID, ClassName
                FROM Class
                ORDER BY ClassName
                """
            )

            classes = cursor.fetchall()

            self.class_combo["values"] = [
                f"{class_item[0]} - {class_item[1]}"
                for class_item in classes
            ]

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load classes:\n{error}"
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # --------------------------------------------------
    # CREATE BOOKING
    # --------------------------------------------------
    def book_class(self):
        selected_member = self.member_combo.get()
        selected_class = self.class_combo.get()
        class_date = self.date_entry.get().strip()

        if not selected_member:
            messagebox.showwarning(
                "Missing Information",
                "Please select a member."
            )
            return

        if not selected_class:
            messagebox.showwarning(
                "Missing Information",
                "Please select a class."
            )
            return

        if not class_date:
            messagebox.showwarning(
                "Missing Information",
                "Please enter a class date."
            )
            return

        # Validate date
        try:
            datetime.strptime(
                class_date,
                "%Y-%m-%d"
            )

        except ValueError:
            messagebox.showerror(
                "Invalid Date",
                "Please use YYYY-MM-DD format."
            )
            return

        member_id = int(
            selected_member.split(" - ")[0]
        )

        class_id = int(
            selected_class.split(" - ")[0]
        )

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            # Check for duplicate booking
            duplicate_query = """
                SELECT COUNT(*)
                FROM Booking
                WHERE MemberID = %s
                AND ClassID = %s
                AND ClassDate = %s
                AND BookingStatus = 'Booked'
            """

            cursor.execute(
                duplicate_query,
                (member_id, class_id, class_date)
            )

            duplicate_count = cursor.fetchone()[0]

            if duplicate_count > 0:
                messagebox.showwarning(
                    "Duplicate Booking",
                    "This member is already booked into this class on this date."
                )
                return

            # Get class capacity
            cursor.execute(
                """
                SELECT Capacity
                FROM Class
                WHERE ClassID = %s
                """,
                (class_id,)
            )

            capacity_result = cursor.fetchone()

            if capacity_result is None:
                messagebox.showerror(
                    "Class Error",
                    "The selected class could not be found."
                )
                return

            capacity = capacity_result[0]

            # Count active bookings
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM Booking
                WHERE ClassID = %s
                AND ClassDate = %s
                AND BookingStatus = 'Booked'
                """,
                (class_id, class_date)
            )

            current_bookings = cursor.fetchone()[0]

            # Prevent overbooking
            if current_bookings >= capacity:
                messagebox.showwarning(
                    "Class Full",
                    f"This class is fully booked.\n"
                    f"Capacity: {capacity}"
                )
                return

            # Create booking
            query = """
                INSERT INTO Booking
                (
                    MemberID,
                    ClassID,
                    ClassDate,
                    BookingStatus,
                    AttendanceStatus,
                    LateCancellationFee,
                    NoShowFee
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                member_id,
                class_id,
                class_date,
                "Booked",
                "Pending",
                0.00,
                0.00
            )

            cursor.execute(
                query,
                values
            )

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Booking created successfully!"
            )

            self.member_combo.set("")
            self.class_combo.set("")
            self.date_entry.delete(
                0,
                tk.END
            )

            self.load_bookings()

        except Exception as error:
            if connection:
                connection.rollback()

            messagebox.showerror(
                "Booking Error",
                f"Could not create booking:\n{error}"
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # --------------------------------------------------
    # CANCEL BOOKING
    # --------------------------------------------------
    def cancel_booking(self):
        selected = self.booking_table.selection()

        if not selected:
            messagebox.showwarning(
                "No Booking Selected",
                "Please select a booking from the table first."
            )
            return

        booking_values = self.booking_table.item(
            selected[0],
            "values"
        )

        booking_id = booking_values[0]
        class_date = booking_values[3]
        status = booking_values[4]

        if status != "Booked":
            messagebox.showwarning(
                "Cannot Cancel",
                "Only active bookings can be cancelled."
            )
            return

        confirm = messagebox.askyesno(
            "Cancel Booking",
            f"Are you sure you want to cancel Booking ID {booking_id}?"
        )

        if not confirm:
            return

        connection = None
        cursor = None

        try:
            booking_date = datetime.strptime(
                str(class_date),
                "%Y-%m-%d"
            )

            now = datetime.now()
            time_remaining = booking_date - now

            # Less than 24 hours = late cancellation
            if time_remaining < timedelta(hours=24):
                new_status = "Cancelled"
                cancellation_fee = 10.00

            else:
                new_status = "Cancelled"
                cancellation_fee = 0.00

            connection = get_connection()
            cursor = connection.cursor()

            query = """
                UPDATE Booking
                SET BookingStatus = %s,
                    CancellationDateTime = NOW(),
                    LateCancellationFee = %s
                WHERE BookingID = %s
            """

            cursor.execute(
                query,
                (
                    new_status,
                    cancellation_fee,
                    booking_id
                )
            )

            connection.commit()

            if new_status == "Late Cancel":
                messagebox.showinfo(
                    "Late Cancellation",
                    f"Booking ID {booking_id} has been cancelled.\n"
                    "Late cancellation fee: $10.00"
                )

            else:
                messagebox.showinfo(
                    "Booking Cancelled",
                    f"Booking ID {booking_id} has been cancelled."
                )

            self.load_bookings()

        except Exception as error:
            if connection:
                connection.rollback()

            messagebox.showerror(
                "Cancellation Error",
                f"Could not cancel booking:\n{error}"
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # --------------------------------------------------
    # MARK ATTENDANCE
    # --------------------------------------------------
    def mark_attendance(self):
        selected = self.booking_table.selection()

        if not selected:
            messagebox.showwarning(
                "No Booking Selected",
                "Please select a booking from the table first."
            )
            return

        booking_values = self.booking_table.item(
            selected[0],
            "values"
        )

        booking_id = booking_values[0]
        class_date = booking_values[3]
        status = booking_values[4]

        # Cannot mark attendance for cancelled bookings
        if status in ("Cancelled", "Late Cancel"):
            messagebox.showwarning(
                "Cannot Mark Attendance",
                "Attendance cannot be marked for a cancelled booking."
            )
            return

        # Check class date
        try:
            booking_date = datetime.strptime(
                str(class_date),
                "%Y-%m-%d"
            ).date()

            today = datetime.now().date()

            if booking_date > today:
                messagebox.showwarning(
                    "Class Not Completed",
                    "Attendance can only be marked after the class date."
                )
                return

        except ValueError:
            messagebox.showerror(
                "Date Error",
                "Invalid class date."
            )
            return

        # Ask whether the member attended
        attended = messagebox.askyesno(
            "Mark Attendance",
            f"Did the member attend Booking ID {booking_id}?\n\n"
            "Yes = Attended\n"
            "No = No-show"
        )

        if attended:
            attendance_status = "Attended"
            no_show_fee = 0.00

        else:
            attendance_status = "No-show"
            no_show_fee = 15.00

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = """
                UPDATE Booking
                SET AttendanceStatus = %s
                WHERE BookingID = %s
            """

            cursor.execute(
                query,
                (
                    attendance_status,
                    booking_id
                )
            )

            connection.commit()

            if attendance_status == "No-show":
                messagebox.showinfo(
                    "Attendance Updated",
                    f"Booking ID {booking_id} marked as No-show.\n"
                    "No-show fee: $15.00"
                )

            else:
                messagebox.showinfo(
                    "Attendance Updated",
                    f"Booking ID {booking_id} marked as Attended."
                )

            self.load_bookings()

        except Exception as error:
            if connection:
                connection.rollback()

            messagebox.showerror(
                "Attendance Error",
                f"Could not update attendance:\n{error}"
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    # --------------------------------------------------
    # LOAD BOOKINGS
    # --------------------------------------------------
    def load_bookings(self):
        # Clear current table
        for row in self.booking_table.get_children():
            self.booking_table.delete(row)

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = """
            SELECT
                b.BookingID,
                CONCAT(m.FirstName, ' ', m.LastName) AS MemberName,
                c.ClassName,
                b.ClassDate,
                b.BookingStatus,
                b.AttendanceStatus,
                b.LateCancellationFee,
                b.NoShowFee
            FROM Booking b
            JOIN Member m
                ON b.MemberID = m.MemberID
            JOIN Class c
                ON b.ClassID = c.ClassID
            ORDER BY b.ClassDate
            """

            cursor.execute(query)
            bookings = cursor.fetchall()

            for booking in bookings:
                self.booking_table.insert(
                    "",
                    "end",
                    values=booking
                )

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load bookings:\n{error}"
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()
    # --------------------------------------------------
    # SEARCH BOOKINGS
    # --------------------------------------------------
    def search_bookings(self):
        member_name = self.search_member_entry.get().strip()
        class_name = self.search_class_entry.get().strip()
        status = self.search_status_combo.get().strip()
        class_date = self.search_date_entry.get().strip()

        # Clear current table
        for row in self.booking_table.get_children():
            self.booking_table.delete(row)

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = """
            SELECT
                b.BookingID,
                CONCAT(m.FirstName, ' ', m.LastName) AS MemberName,
                c.ClassName,
                b.ClassDate,
                b.BookingStatus,
                b.AttendanceStatus,
                b.LateCancellationFee,
                b.NoShowFee
            FROM Booking b
            JOIN Member m
                ON b.MemberID = m.MemberID
            JOIN Class c
                ON b.ClassID = c.ClassID
            WHERE 1 = 1
            """

            parameters = []

            if member_name:
                query += """
                    AND CONCAT(m.FirstName, ' ', m.LastName) LIKE %s
                """
                parameters.append(f"%{member_name}%")

            if class_name:
                query += " AND c.ClassName LIKE %s"
                parameters.append(f"%{class_name}%")

            if status:
                query += " AND b.BookingStatus = %s"
                parameters.append(status)

            if class_date:
                try:
                    datetime.strptime(class_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning(
                        "Invalid Date",
                        "Please enter the class date as YYYY-MM-DD."
                    )
                    return

                query += " AND b.ClassDate = %s"
                parameters.append(class_date)

            query += " ORDER BY b.ClassDate, b.BookingID"

            cursor.execute(query, tuple(parameters))

            bookings = cursor.fetchall()

            for booking in bookings:
                self.booking_table.insert(
                    "",
                    "end",
                    values=booking
                )

            if not bookings:
                messagebox.showinfo(
                    "Search Results",
                    "No matching bookings were found."
                )

        except Exception as error:
            messagebox.showerror(
                "Search Error",
                f"Could not search bookings:\n{error}"
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()


    # --------------------------------------------------
    # CLEAR SEARCH
    # --------------------------------------------------
    def clear_search(self):
        self.search_member_entry.delete(0, tk.END)
        self.search_class_entry.delete(0, tk.END)
        self.search_status_combo.set("")
        self.search_date_entry.delete(0, tk.END)

        self.load_bookings()
    # --------------------------------------------------
    # GENERATE EXCEL REPORT
    # --------------------------------------------------
    def generate_report(self):
        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = """
                SELECT
                    b.BookingID,
                    CONCAT(m.FirstName, ' ', m.LastName) AS MemberName,
                    c.ClassName,
                    b.ClassDate,
                    b.BookingStatus,
                    b.AttendanceStatus,
                    b.LateCancellationFee,
                    b.NoShowFee
                FROM Booking b
                JOIN Member m
                    ON b.MemberID = m.MemberID
                JOIN Class c
                    ON b.ClassID = c.ClassID
                WHERE b.BookingStatus = 'Late Cancel'
                    OR b.AttendanceStatus = 'No-Show'
                ORDER BY b.ClassDate
            """

            cursor.execute(query)
            report_data = cursor.fetchall()

            if not report_data:
                 messagebox.showinfo(
                    "No Report Data",
                    "There are no late cancellations or no-shows to report."
                )
            return


            # Create Excel workbook
            workbook = Workbook()

            sheet = workbook.active
            sheet.title = "Late Cancel and No-show"

            # Column headings
            headings = [
                "Booking ID",
                "Member",
                "Class",
                "Class Date",
                "Booking Status",
                "Attendance Status",
                "Late Cancellation Fee ($)",
                "No-Show Fee ($)"
            ]

            sheet.append(headings)

            # Add booking data
            for booking in report_data:
                sheet.append(list(booking))


            # Make columns wider
            sheet.column_dimensions["A"].width = 15
            sheet.column_dimensions["B"].width = 25
            sheet.column_dimensions["C"].width = 25
            sheet.column_dimensions["D"].width = 18
            sheet.column_dimensions["E"].width = 18
            sheet.column_dimensions["F"].width = 18
            sheet.column_dimensions["G"].width = 22
            sheet.column_dimensions["H"].width = 18

            # Save report
            filename = "booking_report.xlsx"

            workbook.save(filename)

            messagebox.showinfo(
                "Report Generated",
                f"Excel report created successfully.\n\n"
                f"File: {filename}"
            )

        except Exception as error:
            messagebox.showerror(
                "Report Error",
                f"Could not generate report:\n{error}"
            )

        finally:
            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()



# --------------------------------------------------
# START PROGRAM
# --------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BookingManagement(root)
    root.mainloop()
