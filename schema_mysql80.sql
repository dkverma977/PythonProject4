-- ==============================================================================
-- MySQL 8.0 Compatible Database Schema
-- 
-- Rules Implemented:
-- 1. User Foreign Keys: All relationships reference parent tables (users, motors, 
--    lookups, calendar days) via strict FOREIGN KEY constraints.
-- 2. Never Repeat Days (Data Normalization):
--    - Dates/Days are normalized into a master `calendar_days` table to avoid repeating
--      date attributes and calculations across logs/events.
--    - Recurring schedule days are normalized into `days_of_week`.
--    - String attributes (departments, areas, substations, manufacturers, types) 
--      are fully normalized into lookup tables to eliminate duplicate data.
-- 3. No Standalone Indexes: Explicit CREATE INDEX statements have been excluded as requested.
-- ==============================================================================

-- Drop existing tables in reverse dependency order
DROP TABLE IF EXISTS maintenance_schedules;
DROP TABLE IF EXISTS maintenance_logs;
DROP TABLE IF EXISTS motors;
DROP TABLE IF EXISTS maintenance_types;
DROP TABLE IF EXISTS feeders;
DROP TABLE IF EXISTS mccs;
DROP TABLE IF EXISTS substations;
DROP TABLE IF EXISTS manufacturers;
DROP TABLE IF EXISTS areas;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS days_of_week;
DROP TABLE IF EXISTS calendar_days;
DROP TABLE IF EXISTS users;

-- ------------------------------------------------------------------------------
-- 1. USERS / TECHNICIANS TABLE (User FK Parent)
-- ------------------------------------------------------------------------------
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    user_role VARCHAR(30) NOT NULL DEFAULT 'Technician',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ------------------------------------------------------------------------------
-- 2. CALENDAR DAYS TABLE (Never Repeat Days - Master Date Dimension)
-- ------------------------------------------------------------------------------
CREATE TABLE calendar_days (
    day_id INT AUTO_INCREMENT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day_name VARCHAR(10) NOT NULL,
    day_of_week TINYINT NOT NULL COMMENT '1=Monday, 7=Sunday',
    month_num TINYINT NOT NULL,
    month_name VARCHAR(15) NOT NULL,
    year_num SMALLINT NOT NULL,
    is_weekend TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ------------------------------------------------------------------------------
-- 3. DAYS OF WEEK TABLE (Normalized Schedule Days)
-- ------------------------------------------------------------------------------
CREATE TABLE days_of_week (
    day_code TINYINT PRIMARY KEY COMMENT '1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat, 7=Sun',
    day_name VARCHAR(10) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ------------------------------------------------------------------------------
-- 4. NORMALIZED LOOKUP TABLES (Eliminate Data Redundancy)
-- ------------------------------------------------------------------------------
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE areas (
    area_id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    area_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE manufacturers (
    manufacturer_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE substations (
    substation_id INT AUTO_INCREMENT PRIMARY KEY,
    substation_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE mccs (
    mcc_id INT AUTO_INCREMENT PRIMARY KEY,
    substation_id INT NOT NULL,
    mcc_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (substation_id) REFERENCES substations(substation_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE feeders (
    feeder_id INT AUTO_INCREMENT PRIMARY KEY,
    mcc_id INT NOT NULL,
    feeder_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (mcc_id) REFERENCES mccs(mcc_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE maintenance_types (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ------------------------------------------------------------------------------
-- 5. MOTORS MASTER TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE motors (
    motor_id INT AUTO_INCREMENT PRIMARY KEY,
    tag VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    area_id INT NOT NULL,
    feeder_id INT,
    manufacturer_id INT,
    created_by_user_id INT NOT NULL,
    power_kw DECIMAL(8,2),
    voltage_v INT,
    current_amp DECIMAL(8,2),
    frequency_hz DECIMAL(5,2) DEFAULT 50.00,
    rpm INT,
    efficiency_pct DECIMAL(5,2),
    power_factor DECIMAL(4,3),
    frame_size VARCHAR(30),
    protection_class VARCHAR(30),
    insulation_class VARCHAR(30),
    duty_cycle VARCHAR(30),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    mfg_year SMALLINT,
    location VARCHAR(200),
    status VARCHAR(30) DEFAULT 'Running',
    is_critical TINYINT(1) DEFAULT 0,
    commission_day_id INT,
    remarks TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (area_id) REFERENCES areas(area_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (feeder_id) REFERENCES feeders(feeder_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (commission_day_id) REFERENCES calendar_days(day_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ------------------------------------------------------------------------------
-- 6. MAINTENANCE LOGS TABLE (FK to User, Motor, Maintenance Type, Calendar Day)
-- ------------------------------------------------------------------------------
CREATE TABLE maintenance_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    motor_id INT NOT NULL,
    log_day_id INT NOT NULL,
    type_id INT NOT NULL,
    technician_user_id INT NOT NULL,
    notes TEXT,
    vibration_de_mm_s DECIMAL(6,2),
    vibration_nde_mm_s DECIMAL(6,2),
    megger_mohm DECIMAL(8,2),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (motor_id) REFERENCES motors(motor_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (log_day_id) REFERENCES calendar_days(day_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (type_id) REFERENCES maintenance_types(type_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (technician_user_id) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ------------------------------------------------------------------------------
-- 7. RECURRING MAINTENANCE SCHEDULES TABLE (FK to Motor, Days of Week, User)
-- ------------------------------------------------------------------------------
CREATE TABLE maintenance_schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    motor_id INT NOT NULL,
    day_code TINYINT NOT NULL,
    type_id INT NOT NULL,
    assigned_technician_id INT NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (motor_id) REFERENCES motors(motor_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (day_code) REFERENCES days_of_week(day_code)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (type_id) REFERENCES maintenance_types(type_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (assigned_technician_id) REFERENCES users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
