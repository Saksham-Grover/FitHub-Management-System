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

-- Trainer Table
CREATE TABLE IF NOT EXISTS Trainer (
    TrainerID INT AUTO_INCREMENT PRIMARY KEY,
    TrainerName VARCHAR(100) NOT NULL
);

-- Class Table
CREATE TABLE IF NOT EXISTS Class (
    ClassID INT AUTO_INCREMENT PRIMARY KEY,
    ClassName VARCHAR(100) NOT NULL,
    ClassType VARCHAR(50) NOT NULL,
    TrainerID INT NOT NULL,
    DayOfWeek VARCHAR(15) NOT NULL,
    StartTime TIME NOT NULL,
    Capacity INT NOT NULL,
    Fee DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (TrainerID) REFERENCES Trainer(TrainerID),
    CHECK (Capacity > 0),
    CHECK (Fee >= 0),
    INDEX idx_class_search (ClassType, DayOfWeek)
);

-- Member Table
CREATE TABLE IF NOT EXISTS Member (
    MemberID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Phone VARCHAR(20),
    Email VARCHAR(100),
    MembershipType ENUM('Casual', 'Monthly', 'Annual') NOT NULL,
    StartDate DATE NOT NULL,
    INDEX idx_member_name (LastName, FirstName)
);

