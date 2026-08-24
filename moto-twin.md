# MOTO-TWIN Industrial Digital Twin Platform Documentation

## Executive Overview
**MOTO-TWIN** is a comprehensive, enterprise-grade Industrial Motor & Electrical Power Management Digital Twin Platform designed for continuous condition monitoring, predictive maintenance, power path tracing, energy optimization, and fleet reliability management.

---

## 1. Electrical Power Hierarchy & Data Architecture
The platform enforces a normalized 7-tier power distribution hierarchy matching international industrial SCADA/DCS standards:

```
[Plant] (Industrial Facility / Microgrid)
  └── [Substation] (Main Substation / 33kV Switchyard)
        └── [Transformer] (Step-down Power Transformer 33kV / 6.6kV / 415V)
              └── [PCC] (Power Control Center Incomer Switchgear)
                    └── [MCC] (Motor Control Center Cabinet / Switchboard)
                          └── [Feeder] (Feeder Switch / Vacuum Circuit Breaker / MPCB)
                                └── [Motor] (Low-Voltage & High-Voltage Electric Motors)
```

---

## 2. Dynamic Health Score Engine (0–100%)
Every motor asset dynamically calculates a Health Score from live telemetry, mechanical parameters, and historical maintenance logs using the weighted formula:

$$\text{Health Score} = 100 - (\Delta_{\text{Vibration}} + \Delta_{\text{BearingTemp}} + \Delta_{\text{WindingTemp}} + \Delta_{\text{VoltageDev}} + \Delta_{\text{Megger}} + \Delta_{\text{Alarms}} + \Delta_{\text{OverdueMaint}})$$

### Health Score Classification
- **HEALTHY (90–100%)**: Optimal operation, zero anomalies detected.
- **GOOD (75–89%)**: Normal operation within standard ISO 10816 bounds.
- **WARNING (60–74%)**: Elevated vibration or winding temperature; scheduled inspection advised.
- **POOR (45–50%)**: Severe operating deviation; immediate predictive maintenance required.
- **CRITICAL (0–44%)**: Emergency fault condition or trip; high risk of catastrophic failure.

---

## 3. Statistical Predictive Maintenance Risk Engine
The predictive maintenance engine analyzes historical telemetry trends, operating hours, and alarm frequencies to classify assets into 4 risk tiers:

| Risk Level | Trigger Criteria | Automated Recommendations |
| :--- | :--- | :--- |
| **LOW RISK** | Health Score ≥ 75%, zero active critical alarms. | Routine maintenance per 6-month schedule. |
| **MEDIUM RISK** | Health Score 60–74% or overdue PM > 30 days. | Re-lubricate bearings, inspect alignment within 14 days. |
| **HIGH RISK** | Health Score 45–59% or active warning alarms. | Perform dynamic balancing, thermography & vibration analysis. |
| **CRITICAL RISK** | Health Score < 45% or Status = 'Fault'. | Emergency stop / isolator lock-out, issue urgent work order. |

---

## 4. REST API Endpoint Specification

### Authentication & User Management
- `POST /api/auth/login`: Authenticate user session.
- `POST /api/auth/logout`: Destroy user session.
- `GET /api/auth/me`: Fetch active session details and role permissions.

### Hierarchy & Digital Twin Assets
- `GET /api/tree`: Returns the complete 7-tier electrical distribution tree structure.
- `GET /api/motors`: Fetch all motor assets with optional search and column filtering.
- `POST /api/motors`: Create a new motor asset (*Admin role required*).
- `GET /api/motors/<tag>`: Fetch detailed motor specifications, health breakdown, and predictive risk analysis.
- `GET /api/motors/<tag>/power-path`: Retrieve 7-tier upstream power trace mapping.

### Telemetry & Alarms
- `GET /api/telemetry`: Query operating telemetry history for trend plotting.
- `GET /api/alarms`: List active and historical threshold alarms.
- `POST /api/alarms/<id>/acknowledge`: Acknowledge active alarm (*Engineer role required*).
- `POST /api/alarms/<id>/clear`: Clear alarm condition.

### Maintenance & Work Orders
- `GET /api/motors/<tag>/maintenance`: Fetch maintenance history timeline.
- `POST /api/motors/<tag>/maintenance`: Log maintenance activity (*Engineer role required*).
- `GET /api/work-orders`: List maintenance work orders.
- `POST /api/work-orders`: Generate a new maintenance work order.

### Audit & Excel I/O
- `GET /api/data-quality`: Generate database completeness & integrity audit report.
- `GET /api/audit`: Query system audit log trail.
- `POST /api/import/excel/validate`: Validate batch Excel file and output preview report.
- `POST /api/import/excel/confirm`: Execute batch database import.
- `GET /api/export`: Stream filtered motor fleet data as formatted Excel spreadsheet.

---

## 5. Role-Based Access Control (RBAC) Matrix

| Feature / Endpoint | Viewer | Engineer | Admin |
| :--- | :---: | :---: | :---: |
| Browse Hierarchy Tree & Dashboard Analytics | ✅ | ✅ | ✅ |
| View 14-Tab Digital Twin Cards & Telemetry Trends | ✅ | ✅ | ✅ |
| Acknowledge / Clear Alarms | ❌ | ✅ | ✅ |
| Log Maintenance & Create Work Orders | ❌ | ✅ | ✅ |
| Add / Edit / Delete Motors | ❌ | ❌ | ✅ |
| Batch Excel Import & System Audit Logs | ❌ | ❌ | ✅ |

---

## 6. Verification & Automated Testing Suite
Run the unit test suite to verify database schemas, health score math, and API contracts:

```bash
.venv\Scripts\python.exe test_platform.py
```
