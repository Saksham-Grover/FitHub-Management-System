-- FitHub Class Booking and Membership Management System
--------------- Database Schema ------------------
-- Group Name: Mel10
CREATE DATABASE IF NOT EXISTS fithub_db;
USE fithub_db;
-- Staff Table
CREATE TABLE IF NOT EXISTS Staff (
    StaffID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL
);

