
from datetime import datetime, date
from db_config import get_connection


# Check if a fitness class has any available spaces.
# Member 4 can use this before making a booking.
def check_class_capacity(class_id, class_date):
    if isinstance(class_date, str):
        class_date = date.fromisoformat(class_date)

    if not isinstance(class_date, date):
        raise ValueError("Enter a valid class date.")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Get the maximum number of people allowed.
        cursor.execute(
            "SELECT Capacity FROM Class WHERE ClassID = %s",
            (class_id,)
        )
        result = cursor.fetchone()

        if result is None:
            raise ValueError("Class not found.")

        capacity = result[0]

        # Count active bookings for the chosen date.
        cursor.execute(
            """SELECT COUNT(*) FROM Booking
               WHERE ClassID = %s
               AND ClassDate = %s
               AND BookingStatus = 'Booked'""",
            (class_id, class_date)
        )

        booked = cursor.fetchone()[0]

        # Return True when at least one place is free.
        return booked < capacity

    finally:
        cursor.close()
        connection.close()
