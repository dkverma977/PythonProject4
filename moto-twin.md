# MOTO-TWIN - Industrial Motor & Electrical Power Management Digital Twin

**Repository**: `https://github.com/dkverma977/PythonProject4.git`  
**Subfolder**: `moto-twin` | **Default Branch**: `master`  
**Web URL**: `https://github.com/dkverma977/PythonProject4/tree/master/moto-twin`

---

## 📌 Executive Overview

**MOTO-TWIN** is an enterprise-grade Industrial Digital Twin and Asset Management System designed for electrical engineers, reliability teams, and plant maintenance managers. It provides full digital representation, operational telemetry tracking, single-line power feeder tracing, and health analytics for industrial electric motors across complex power distribution hierarchies.

---

## 🏗 System Architecture

The application adopts a decoupled architecture with a Python Flask REST API backend, SQLAlchemy ORM data persistence layer, and a high-performance modular vanilla JavaScript ES6 frontend.

```
       +--------------------------------------------------------+
       |                  CLIENT BROWSERS                       |
       |  Desktop / Laptop / Tablet / Mobile (Responsive UI)    |
       +---------------------------+----------------------------+
                                   |
                                   | HTTP / REST API (JSON)
                                   v
       +--------------------------------------------------------+
       |                PYTHON FLASK WEB SERVER                 |
       |                  (flask_server.py)                     |
       +---------------------------+----------------------------+
                                   |
                                   | SQLAlchemy ORM
                                   v
       +--------------------------------------------------------+
       |                 DATABASE ENGINE LAYER                  |
       |     SQLite (motor_platform.db) / MySQL (motor_data)    |
       +--------------------------------------------------------+
```

---

## ⭐ Key Features

1. **Electrical Power Hierarchy Tree**:
   - Interactive tree visualization mapping the physical plant power network:  
     `Plant` ➔ `Substation` ➔ `Power Control Center (PCC)` ➔ `Motor Control Center (MCC)` ➔ `Feeder` ➔ `Motor Asset`.
   - Node expansion/collapse, instant filtering, and color-coded status badges.

2. **Asset Telemetry Dashboard**:
   - Real-time KPI summaries: Total Motors, Running Motors, Standby Motors, and Fault Alerts.
   - Interactive charts (Chart.js) for motor status distribution, area breakdown, voltage levels, and vibration telemetry metrics.

3. **Digital Twin Motor Specifications**:
   - Comprehensive asset nameplate data: Power (kW), Operating Voltage (V), Rated Current (A), Speed (RPM), Frame Size, Protection Rating (IP), Insulation Class, Bearing Specifications (DE/NDE), Cable Specs, and Starter Type.

4. **Maintenance Telemetry & Health Monitoring**:
   - Historical maintenance logs tracker recording Megger Insulation Resistance (MΩ), Drive End (DE) Vibration (mm/s), Non-Drive End (NDE) Vibration (mm/s), technician details, and service logs.

5. **Role-Based Access Control (RBAC)**:
   - **Admin**: Full administrative permissions including motor creation, editing, deletion, and Excel batch importing.
   - **Engineer**: Maintenance log entry and operational state updates.
   - **Viewer**: Read-only asset inspection and export access.

6. **Responsive Multi-Screen Adaptability**:
   - Dynamic slide-over drawers for Left Tree Navigation and Right Equipment Details on tablet and mobile viewports (<1024px).
   - Fluid grid layouts supporting 320px smartphones up to 4K ultra-wide SCADA monitoring stations.

7. **Export & Reporting**:
   - Single-click filtered Excel spreadsheet generation (`.xlsx`) via openpyxl.
   - Print and PDF asset datasheet export.

---

## 📁 Directory & File Structure

```
d:\Antigravity/
├── static/                         # Web Application Static Assets
│   ├── index.html                  # Main SPA Single Page Application HTML markup
│   ├── style.css                   # Custom CSS Design System & Responsive Media Queries
│   ├── app.js                      # Core JS ES6 Orchestrator & State Manager
│   ├── components/                 # UI Subcomponents (ES6 Modules)
│   │   ├── TreeComponent.js        # Electrical Distribution Tree component
│   │   ├── DashboardComponent.js   # Analytics Dashboard & Chart.js renderer
│   │   ├── CenterPanelComponent.js# Equipment grid, list views & breadcrumbs
│   │   └── RightPanelComponent.js # Asset detail cards, maintenance logs & tabs
│   └── assets/                     # Icons, branding, and images
├── database_api.py                 # Database API class, SQLAlchemy Models & Auto-seeding
├── flask_server.py                 # Primary Flask REST API Server & Router
├── server.py                       # Alternative FastAPI backend implementation
├── wsgi.py                         # WSGI production entrypoint (Waitress / Gunicorn)
├── motor_platform.db              # SQLite Database file (Default zero-config storage)
├── sample_motors.xlsx              # Initial sample dataset for auto-seeding
├── reset_db.py                     # Database purge & reset execution script
├── generate_sample_data.py         # Mock dataset & SQL generator script
├── schema_mysql80.sql              # MySQL 8.0 DDL database creation script
├── db_structure.sql                # SQL database table structure dump
├── db_data.sql                     # SQL database initial data insert dump
├── requirements.txt                # Python package dependencies manifest
└── moto-twin.md                    # Comprehensive Project Documentation
```

---

## 🗄 Database Schema & Data Models

### 1. `motors` Table
| Column | Type | Primary Key | Description |
|---|---|---|---|
| `tag` | VARCHAR(255) | Yes | Unique Motor Tag Identifier (e.g. `M-101`) |
| `name` | VARCHAR(255) | No | Motor Name / Equipment Designation |
| `area` | VARCHAR(255) | No | Plant Area (e.g. `Raw Material Handling`) |
| `service` | VARCHAR(255) | No | Service Description (e.g. `Belt Conveyor Drive`) |
| `power_kw` | FLOAT | No | Power rating in Kilowatts |
| `voltage` | INTEGER | No | Operating Voltage (e.g. `415`, `3300`, `6600`) |
| `current_amp` | FLOAT | No | Full Load Current in Amperes |
| `frequency_hz`| FLOAT | No | Line Frequency (Default: 50.0 Hz) |
| `rpm` | INTEGER | No | Synchronous Speed in RPM |
| `efficiency` | VARCHAR(255) | No | Efficiency Class / Percentage (e.g. `IE3 / 94.5%`) |
| `pf` | FLOAT | No | Power Factor |
| `frame_size` | VARCHAR(255) | No | IEC / NEMA Frame designation |
| `protection_class` | VARCHAR(255) | No | Ingress Protection (e.g. `IP55`, `IP65`) |
| `insulation_class` | VARCHAR(255) | No | Thermal Insulation Class (`Class F`, `Class H`) |
| `duty` | VARCHAR(255) | No | Duty Cycle Rating (`S1 Continuous`) |
| `make` | VARCHAR(255) | No | Manufacturer Make (e.g. `ABB`, `Siemens`) |
| `model` | VARCHAR(255) | No | Model Number |
| `serial_number`| VARCHAR(255) | No | Manufacturer Serial Number |
| `bearing_de` | VARCHAR(255) | No | Drive End Bearing designation |
| `bearing_nde` | VARCHAR(255) | No | Non-Drive End Bearing designation |
| `lubrication_type` | VARCHAR(255) | No | Grease / Oil Specification |
| `starter_type` | VARCHAR(255) | No | Starter Mechanism (`VFD`, `DOL`, `Soft Starter`) |
| `substation` | VARCHAR(255) | No | Parent Substation Tag |
| `pcc` | VARCHAR(255) | No | Power Control Center Tag |
| `mcc` | VARCHAR(255) | No | Motor Control Center Tag |
| `feeder` | VARCHAR(255) | No | Power Feeder Designation |
| `status` | VARCHAR(255) | No | Operational State (`Running`, `Standby`, `Fault`) |
| `is_critical` | BOOLEAN | No | High Criticality Indicator Flag |

### 2. `users` Table
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER (PK) | Auto-increment User ID |
| `username` | VARCHAR(255) | Unique Username |
| `password_hash` | VARCHAR(255) | Werkzeug Hashed Password |
| `full_name` | VARCHAR(255) | Full Name |
| `email` | VARCHAR(255) | Email Address |
| `role` | VARCHAR(50) | Role: `Admin`, `Engineer`, or `Viewer` |

### 3. `maintenance_logs` Table
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER (PK) | Auto-increment Log ID |
| `motor_tag` | VARCHAR(255) (FK) | Foreign Key referencing `motors.tag` |
| `log_date` | DATE | Date of Maintenance Event |
| `type` | VARCHAR(255) | Event Category (`Lubrication`, `Insulation Test`, `Alignment`, `Bearing Replacement`) |
| `technician` | VARCHAR(255) | Name of Maintenance Engineer / Technician |
| `vibration_de_mm_s` | FLOAT | DE Vibration Measurement (mm/s RMS) |
| `vibration_nde_mm_s` | FLOAT | NDE Vibration Measurement (mm/s RMS) |
| `megger_mohm` | FLOAT | Insulation Resistance (MΩ) |
| `notes` | TEXT | Detailed Maintenance Observations |

---

## 📡 REST API Documentation

| Endpoint | Method | Description | Access Level |
|---|---|---|---|
| `/api/health` | `GET` | Health check & DB status endpoint | Public |
| `/api/auth/login` | `POST` | User authentication & session start | Public |
| `/api/auth/logout` | `POST` | Terminate user session | Logged-in Users |
| `/api/auth/me` | `GET` | Retrieve active user profile | Public / Session |
| `/api/auth/register` | `POST` | Create new user account | Public / Admin |
| `/api/tree` | `GET` | Retrieve complete plant hierarchy tree structure | Public |
| `/api/motors` | `GET` | Fetch list of motors with optional filters (`area`, `voltage`, `make`, `status`, `search`) | Public |
| `/api/motors/<tag>` | `GET` | Fetch single motor details by tag | Public |
| `/api/motors` | `POST` | Register a new motor asset | Admin |
| `/api/motors/<tag>` | `PUT` | Update motor details | Admin / Engineer |
| `/api/motors/<tag>` | `DELETE` | Delete motor asset | Admin |
| `/api/dashboard` | `GET` | Retrieve dashboard KPI metrics & distribution stats | Public |
| `/api/motors/<tag>/maintenance` | `GET` | Fetch maintenance history for a motor | Public |
| `/api/motors/<tag>/maintenance` | `POST` | Append a new maintenance log entry | Admin / Engineer |
| `/api/export/excel` | `GET` | Download filtered motor list as `.xlsx` spreadsheet | Public |

---

## 🚀 Installation & Running Guide

### 1. Prerequisites
- **Python**: Version 3.9 or higher
- **Virtual Environment**: Pre-configured in `.venv`

### 2. Dependencies Installation
```bash
.venv\Scripts\pip.exe install -r requirements.txt
```

### 3. Launching the Web Server
To start the Flask server locally:
```bash
.venv\Scripts\python.exe flask_server.py
```

The application will automatically initialize the database (using `motor_platform.db` or configured MySQL) and start listening at:
👉 **`http://127.0.0.1:8000`**

### 4. Default Credentials for Testing
- **Admin Account**: `username: admin`, `password: admin123`
- **Engineer Account**: `username: engineer`, `password: eng123`
- **Viewer Account**: `username: viewer`, `password: view123`

---

## 📱 Multi-Screen & Responsive System

- **Desktop & Ultra-Wide Screens (≥1025px)**:
  Side-by-side 3-column split view (Left Power Tree, Center Focal Dashboard/Equipment List, Right Technical Asset Details) with interactive resizable splitters.

- **Mobile & Tablet Screens (<1024px)**:
  Full-width center layout with drawer toggle buttons (`#mobile-tree-toggle`, `#mobile-details-toggle`) and touch backdrop overlay (`.drawer-backdrop`).

---

## 📄 License & Repository Details
- **Repository URL**: `https://github.com/dkverma977/PythonProject4.git`
- **Subfolder**: `moto-twin`
- **Branch**: `master`
