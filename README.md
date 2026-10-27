# FitHub Class Booking and Membership Management System

## About the Project
FitHub is a database-based application made to help manage fitness classes and gym memberships. The system is being developed to handle class bookings, cancellations, attendance, and general member information.

Python is used for the main application logic, MySQL is used to store and manage the data, and Tkinter is used to create the graphical user interface.

## Technologies Used
The main technologies and libraries used in this project are:
- Python
- MySQL
- Tkinter
- Pandas
- Matplotlib
- bcrypt
- openpyxl

## Main Features
The system includes or is being developed to include the following functions:
1. Staff Login and Authentication
2. Member Management
3. Class Management
4. Booking and Cancellation Management
5. Search and Filtering
6. Excel Report Generation
7. Data Visualisation

## Group Project Details
**Course:** ITAP3010 Developing Data Access Solutions

**Group:** Mel10

## How to Run the Project

### Step 1: Install the Required Libraries
Open the project folder in Visual Studio Code.

Open the terminal and run:
`py -m pip install -r requirements.txt`

This command installs the Python libraries needed to run the application.

### Step 2: Set Up the MySQL Database
1. Open MySQL Workbench.
2. Connect to your local MySQL server.
3. Open the `database/schema.sql` file.
4. Run the SQL script to create the `fithub_db` database.

The database contains five main tables:

- Staff
- Trainer
- Class
- Member
- Booking

### Step 3: Set Up the Database Connection
Open the `db_config.py` file in Visual Studio Code.

Update the MySQL connection details so the application can connect to your local `fithub_db` database.

Personal MySQL passwords should not be uploaded to GitHub.

### Step 4: Create a Staff Account
Create a staff record in the `Staff` table and use a bcrypt-hashed password.

This staff account is used to log in to the FitHub application.

### Step 5: Start the Application
Open the terminal in Visual Studio Code and run:

`py main.py`

The FitHub Staff Login window should open.

Enter a valid Staff ID and password. After a successful login, the Management Options window will appear.

The current menu includes:

1. Class Management
2. Member Management
3. Booking Management

These sections will be connected to their full management features as the project continues.

## Database Design
The FitHub database is made up of five main tables: Staff, Trainer, Class, Member, and Booking.

Primary keys and foreign keys are used to connect the tables and maintain the relationships between the data.

The database structure was created and tested in MySQL Workbench.

The Entity Relationship (ER) diagram is stored in the `database` folder.

## Current Development Status
### Completed
- Created the MySQL database and the five main tables.
- Created and exported the ER diagram.
- Set up and tested the connection between Python and MySQL.
- Created the staff login screen using Tkinter.
- Added bcrypt password verification.
- Tested both successful and unsuccessful login attempts.
- Created the main management menu.
- Connected the login screen to the management menu.
- Set up `main.py` to start the application.
- Created the GitHub repository and development branches.

### Work in Progress
- Class Management functions.
- Member Management functions.
- Booking and Cancellation Management.
- Search and filtering features.
- Data visualisation.
- Excel report generation.
- Combining the different group members' modules.
- Final testing and project documentation.

## Project Status
The FitHub Class Booking and Membership Management System is still under development.
The database structure, staff login system, and main application menu have already been created and tested.
The next stage of development will focus on finishing the management features and connecting all parts of the system together.