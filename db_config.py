import mysql.connector


def get_connection():
    # Connect to the FitHub MySQL database.
    return mysql.connector.connect(
        # Use the local MySQL server.
        host="127.0.0.1",
        # Log in with the MySQL root user.
        user="root",
        # No password set for root on this machine (uses socket auth).
        password="",
        # Use the FitHub database for the connection.
        database="fithub_db"
    )