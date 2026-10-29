# FitHub Class Booking and Membership Management System

## About the Project

FitHub is a database-based application designed to help manage fitness classes, gym members, bookings, cancellations, attendance, and other membership-related information.

The project uses Python for the main application logic, MySQL for storing and managing data, and Tkinter for the graphical user interface.

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

The system includes or is being developed to support the following features:

1. Staff Login and Authentication
2. Class Management
3. Member Management
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

```bash
py -m pip install -r requirements.txt
```

This will install the Python libraries required for the application.

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

### Step 3: Configure the Database Connection

Open the `db_config.py` file in Visual Studio Code.

Update the MySQL connection details so the application can connect to the local `fithub_db` database.

Personal MySQL passwords should not be uploaded to GitHub.

### Step 4: Create a Staff Account

Create a staff record in the `Staff` table using a bcrypt-hashed password.

This staff account is used to log in to the FitHub application.

### Step 5: Run the Application

Open the Visual Studio Code terminal and run:

```bash
py main.py
```

The FitHub Staff Login window should appear.

Enter a valid Staff ID and password. After a successful login, the Management Options window will open.

The main menu includes:

1. Class Management
2. Member Management
3. Booking Management

Each section is connected to its related management functions as development continues.

## Database Design

The FitHub database contains five main tables:

- Staff
- Trainer
- Class
- Member
- Booking

Primary keys and foreign keys are used to connect the tables and maintain the relationships between the data.

The database structure was created and tested using MySQL Workbench.

The Entity Relationship (ER) diagram is stored in the `database` folder.

## Current Development Status

### Completed

- Created the MySQL database and the five main tables.
- Created and exported the ER diagram.
- Set up and tested the connection between Python and MySQL.
- Created the staff login interface using Tkinter.
- Added bcrypt password verification.
- Tested successful and unsuccessful login attempts.
- Created the main management menu.
- Connected the login screen to the management menu.
- Set up `main.py` to launch the application.
- Created the GitHub repository and development branches.
- Added and tested the Class Management module.
- Connected Class Management to the FitHub main menu.

### Work in Progress

- Member Management functionality.
- Booking and Cancellation Management.
- Final integration of all group members' modules.
- Full system testing.
- Final project documentation.

## Member 2 - Class Management

Member 2 developed the Class Management section of the FitHub system.

### Features Implemented

The Class Management module includes:

- A Tkinter-based Class Management interface.
- Adding new fitness classes.
- Viewing existing classes.
- Updating class details.
- Deleting classes.
- Searching and filtering classes.
- Filtering classes by fee.
- Checking class capacity before a booking is made.
- Generating Excel reports for fully booked classes.
- Displaying bookings by class type using Matplotlib.

### Files Developed

The following files were created for the Class Management module:

- `class_management.py`
- `class_capacity.py`
- `test_class_management.py`

### Testing Completed

Five unit tests were created for class-capacity checking, and all five tests passed successfully.

The Class Management GUI was also tested for the following functions:

- Adding a new class.
- Updating class details.
- Searching and filtering classes.
- Deleting a class.
- Generating an Excel report.
- Opening the bookings chart.

The Class Management module is now connected to the FitHub main menu and can be accessed through the application after login.

## Project Status

The FitHub Class Booking and Membership Management System is still under development.

The main database structure, ER diagram, staff login system, management menu, and Class Management module have been created and tested.

The next stage of the project will focus on completing the remaining management modules, combining the work from all group members, and carrying out final system testing and documentation.