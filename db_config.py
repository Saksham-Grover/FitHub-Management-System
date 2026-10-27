import mysql.connector


def get_connection():
    # Connect to the FitHub MySQL database.
    return mysql.connector.connect(
        # Use the local MySQL server.
        host="127.0.0.1",
        # Log in with the MySQL root user.
        user="root",
        # Replace this with your actual MySQL password.
        password="SQL-PASSWORD",
        # Use the FitHub database for the connection.
        database="fithub_db"
    )