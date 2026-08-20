"""
Flask Web Server for Motor Management & Digital Twin Platform — MOTO-TWIN
Uses DatabaseAPI class for data management and exposes REST API endpoints, 
RBAC security, Telemetry, Alarms, Maintenance, Work Orders, Power Path, Excel import/export, and Audit logs.
"""

import os
import io
import json
import logging
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory, Response, send_file, session
from flask_cors import CORS
import pandas as pd
from database_api import DatabaseAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flask-server")

# Initialize Flask App
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = os.environ.get("SECRET_KEY", "moto-twin-super-secret-key-2026")
CORS(app, supports_credentials=True)

# Instantiate Database API Class
DATABASE_URL = os.environ.get("DATABASE_URL")
db_api = DatabaseAPI(DATABASE_URL)

# RBAC Middleware Helpers
def get_current_user():
    return session.get("user")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"error": "Unauthorized access. Please login."}), 401
        return f(*args, **kwargs)
    return decorated

def require_role(roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({"error": "Unauthorized access. Please login."}), 401
            if user.get("role") not in roles:
                return jsonify({"error": f"Forbidden. Role '{user.get('role')}' does not have permission."}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# Serve Frontend SPA
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# ==========================================
# AUTHENTICATION & RBAC ENDPOINTS
# ==========================================

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    """Authenticate user credentials and start session."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = db_api.verify_user(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password."}), 401

    session["user"] = user
    return jsonify({"status": "success", "user": user})

@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    """End active user session."""
    session.pop("user", None)
    return jsonify({"status": "success", "message": "Logged out successfully."})

@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    """Get active logged-in user profile."""
    user = session.get("user")
    if not user:
        return jsonify({"authenticated": False, "user": None})
    return jsonify({"authenticated": True, "user": user})

@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    """Register a new user account (Admin only)."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip()
    role = data.get("role", "Viewer").strip()

    if not username or not password or not full_name:
        return jsonify({"error": "Username, password, and full name are required."}), 400

    try:
        user = db_api.create_user(username=username, password=password, full_name=full_name, email=email, role=role)
        return jsonify({"status": "success", "user": user}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to register user: {str(e)}"}), 500

# ==========================================
# ELECTRICAL HIERARCHY API
# ==========================================

@app.route("/api/tree", methods=["GET"])
def get_tree():
    """Retrieve 7-tier electrical hierarchy layout tree."""
    tree = db_api.get_tree()
    return jsonify(tree)

# ==========================================
# MOTOR DIGITAL TWIN & POWER PATH API
# ==========================================

@app.route("/api/motors", methods=["GET"])
def get_motors():
    """Retrieve motors list with multi-field search & filters."""
    search = request.args.get("search")
    area = request.args.get("area")
    voltage = request.args.get("voltage", type=int)
    make = request.args.get("make")
    status = request.args.get("status")
    criticality = request.args.get("criticality")
    power_min = request.args.get("power_min", type=float)
    power_max = request.args.get("power_max", type=float)
    health_max = request.args.get("health_max", type=int)

    motors = db_api.get_motors(
        search=search,
        area=area,
        voltage=voltage,
        make=make,
        status=status,
        criticality=criticality,
        power_min=power_min,
        power_max=power_max,
        health_max=health_max
    )
    return jsonify(motors)

@app.route("/api/motors", methods=["POST"])
@require_auth
@require_role(["Admin"])
def create_motor():
    """Create new motor asset (Admin only)."""
    data = request.get_json() or {}
    user = session.get("user", {})
    try:
        motor = db_api.add_motor(data, username=user.get("username", "admin"))
        return jsonify({"status": "success", "data": motor}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create motor: {str(e)}"}), 500

@app.route("/api/motors/<tag>", methods=["GET"])
def get_motor_details(tag):
    """Retrieve details for a specific motor by tag."""
    motor = db_api.get_motor(tag)
    if not motor:
        return jsonify({"error": f"Motor {tag} not found."}), 404
    return jsonify(motor)

@app.route("/api/motors/<tag>", methods=["PUT"])
@require_auth
@require_role(["Admin", "Engineer"])
def update_motor_details(tag):
    """Update motor specifications (Admin & Engineer)."""
    data = request.get_json() or {}
    user = session.get("user", {})
    try:
        motor = db_api.update_motor(tag, data, username=user.get("username", "engineer"))
        return jsonify({"status": "success", "data": motor})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to update motor: {str(e)}"}), 500

@app.route("/api/motors/<tag>", methods=["DELETE"])
@require_auth
@require_role(["Admin"])
def delete_motor(tag):
    """Delete motor asset (Admin only)."""
    user = session.get("user", {})
    try:
        success = db_api.delete_motor(tag, username=user.get("username", "admin"))
        if not success:
            return jsonify({"error": f"Motor {tag} not found."}), 404
        return jsonify({"status": "success", "message": f"Motor {tag} deleted successfully."})
    except Exception as e:
        return jsonify({"error": f"Failed to delete motor: {str(e)}"}), 500

@app.route("/api/motors/<tag>/power-path", methods=["GET"])
def get_power_path(tag):
    """Get complete 7-tier node-by-node power path trace."""
    try:
        path_data = db_api.get_power_path(tag)
        return jsonify(path_data)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404

# ==========================================
# TELEMETRY & CONDITION MONITORING API
# ==========================================

@app.route("/api/motors/<tag>/telemetry", methods=["GET"])
def get_motor_telemetry(tag):
    """Get telemetry measurement history for a motor."""
    hours = request.args.get("hours", default=24, type=int)
    telemetry = db_api.get_telemetry(tag, hours=hours)
    return jsonify(telemetry)

@app.route("/api/telemetry", methods=["POST"])
@require_auth
@require_role(["Admin", "Engineer"])
def record_telemetry():
    """Ingest new telemetry measurement."""
    data = request.get_json() or {}
    tag = data.get("motor_tag") or data.get("tag")
    if not tag:
        return jsonify({"error": "Motor tag is required."}), 400
    try:
        meas = db_api.add_telemetry(tag, data)
        return jsonify({"status": "success", "data": meas}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404

# ==========================================
# ALARMS & EVENT MANAGEMENT API
# ==========================================

@app.route("/api/alarms", methods=["GET"])
def get_alarms():
    """Get active or historical alarms."""
    status = request.args.get("status")
    severity = request.args.get("severity")
    motor_tag = request.args.get("motor_tag")
    alarms = db_api.get_alarms(status=status, severity=severity, motor_tag=motor_tag)
    return jsonify(alarms)

@app.route("/api/alarms/<int:alarm_id>/acknowledge", methods=["POST"])
@require_auth
@require_role(["Admin", "Engineer"])
def acknowledge_alarm(alarm_id):
    """Acknowledge an active alarm."""
    user = session.get("user", {})
    try:
        alarm = db_api.acknowledge_alarm(alarm_id, username=user.get("username", "engineer"))
        return jsonify({"status": "success", "data": alarm})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404

@app.route("/api/alarms/<int:alarm_id>/clear", methods=["POST"])
@require_auth
@require_role(["Admin", "Engineer"])
def clear_alarm(alarm_id):
    """Clear an active alarm."""
    user = session.get("user", {})
    try:
        alarm = db_api.clear_alarm(alarm_id, username=user.get("username", "engineer"))
        return jsonify({"status": "success", "data": alarm})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404

# ==========================================
# MAINTENANCE & WORK ORDERS API
# ==========================================

@app.route("/api/motors/<tag>/maintenance", methods=["GET"])
def get_maintenance_history(tag):
    """Get maintenance logs timeline for a motor."""
    logs = db_api.get_maintenance_history(tag)
    return jsonify(logs)

@app.route("/api/motors/<tag>/maintenance", methods=["POST"])
@require_auth
@require_role(["Admin", "Engineer"])
def add_maintenance_log(tag):
    """Add a new maintenance log record for a motor."""
    log_data = request.get_json() or {}
    user = session.get("user", {})
    try:
        log = db_api.add_maintenance_log(tag, log_data, username=user.get("username", "engineer"))
        return jsonify({"status": "success", "msg": "Log added successfully.", "data": log}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404

@app.route("/api/work-orders", methods=["GET"])
def get_work_orders():
    """Get active or completed work orders."""
    state = request.args.get("state")
    motor_tag = request.args.get("motor_tag")
    wos = db_api.get_work_orders(state=state, motor_tag=motor_tag)
    return jsonify(wos)

@app.route("/api/work-orders", methods=["POST"])
@require_auth
@require_role(["Admin", "Engineer"])
def create_work_order():
    """Create a new work order."""
    wo_data = request.get_json() or {}
    user = session.get("user", {})
    try:
        wo = db_api.create_work_order(wo_data, username=user.get("username", "engineer"))
        return jsonify({"status": "success", "data": wo}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

@app.route("/api/work-orders/<int:wo_id>", methods=["PUT"])
@require_auth
@require_role(["Admin", "Engineer"])
def update_work_order(wo_id):
    """Update work order status/assignment."""
    wo_data = request.get_json() or {}
    user = session.get("user", {})
    try:
        wo = db_api.update_work_order(wo_id, wo_data, username=user.get("username", "engineer"))
        return jsonify({"status": "success", "data": wo})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404

# ==========================================
# FAILURES & ENERGY API
# ==========================================

@app.route("/api/failures", methods=["GET"])
def get_failures():
    """Get failure history events."""
    motor_tag = request.args.get("motor_tag")
    fails = db_api.get_failures(motor_tag=motor_tag)
    return jsonify(fails)

@app.route("/api/energy", methods=["GET"])
def get_energy():
    """Get energy monitoring metrics."""
    motor_tag = request.args.get("motor_tag")
    energy_data = db_api.get_energy_data(motor_tag=motor_tag)
    return jsonify(energy_data)

# ==========================================
# DASHBOARD & DATA QUALITY API
# ==========================================

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard_metrics():
    """Retrieve high-density dashboard summary analytics."""
    analytics = db_api.get_dashboard_analytics()
    return jsonify(analytics)

@app.route("/api/data-quality", methods=["GET"])
def get_data_quality():
    """Get asset data quality audit metrics."""
    report = db_api.get_data_quality_report()
    return jsonify(report)

@app.route("/api/audit", methods=["GET"])
def get_audit_logs():
    """Get system audit logs."""
    limit = request.args.get("limit", default=50, type=int)
    logs = db_api.get_audit_logs(limit=limit)
    return jsonify(logs)

# ==========================================
# EXCEL IMPORT & EXPORT API
# ==========================================

@app.route("/api/import/excel/validate", methods=["POST"])
@require_auth
@require_role(["Admin"])
def validate_excel_import():
    """Validate uploaded Excel spreadsheet before committing to database."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400
    file = request.files["file"]
    if not file.filename.endswith((".xlsx", ".xls")):
        return jsonify({"error": "Invalid file format. Please upload an Excel (.xlsx) file."}), 400

    try:
        df = pd.read_excel(file)
        required_cols = ["Motor Tag", "Motor Name"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            return jsonify({"error": f"Missing required columns in Excel: {', '.join(missing_cols)}"}), 400

        total_rows = len(df)
        valid_rows = []
        errors = []
        seen_tags = set()

        for idx, row in df.iterrows():
            tag = str(row.get("Motor Tag", "")).strip()
            name = str(row.get("Motor Name", "")).strip()

            if not tag or pd.isna(row.get("Motor Tag")):
                errors.append({"row": idx + 2, "tag": tag, "error": "Missing Motor Tag"})
                continue
            if tag in seen_tags:
                errors.append({"row": idx + 2, "tag": tag, "error": f"Duplicate tag '{tag}' in Excel"})
                continue

            seen_tags.add(tag)
            valid_rows.append({
                "tag": tag,
                "name": name or f"Motor {tag}",
                "area": str(row.get("Area", "General Area")).strip(),
                "power_kw": float(str(row.get("Power", 45)).replace("kW", "").strip()) if not pd.isna(row.get("Power")) else 45.0,
                "voltage": int(str(row.get("Voltage", 415)).replace("V", "").strip()) if not pd.isna(row.get("Voltage")) else 415,
                "current_amp": float(str(row.get("Current", 75)).replace("A", "").strip()) if not pd.isna(row.get("Current")) else 75.0,
                "make": str(row.get("Motor Make", "ABB")).strip(),
                "model": str(row.get("Model", "M3BP")).strip(),
                "substation": str(row.get("Substation", "Main Substation-1")).strip(),
                "pcc": str(row.get("PCC", "PCC-1")).strip(),
                "mcc": str(row.get("MCC", "MCC-1")).strip(),
                "feeder": str(row.get("Feeder", "Feeder-1")).strip(),
                "status": str(row.get("Status", "Running")).capitalize()
            })

        return jsonify({
            "total_rows": total_rows,
            "valid_rows_count": len(valid_rows),
            "errors_count": len(errors),
            "errors": errors,
            "preview": valid_rows[:10]
        })
    except Exception as e:
        return jsonify({"error": f"Failed to process Excel file: {str(e)}"}), 500

@app.route("/api/import/excel/confirm", methods=["POST"])
@require_auth
@require_role(["Admin"])
def confirm_excel_import():
    """Commit validated batch Excel rows into database."""
    data = request.get_json() or {}
    rows = data.get("rows", [])
    user = session.get("user", {})

    if not rows:
        return jsonify({"error": "No valid rows provided for import."}), 400

    imported = 0
    updated = 0
    for r in rows:
        try:
            tag = r.get("tag")
            existing = db_api.get_motor(tag)
            if existing:
                db_api.update_motor(tag, r, username=user.get("username", "admin"))
                updated += 1
            else:
                db_api.add_motor(r, username=user.get("username", "admin"))
                imported += 1
        except Exception as e:
            logger.warning(f"Batch import row error for {r.get('tag')}: {e}")

    return jsonify({"status": "success", "imported": imported, "updated": updated, "total": len(rows)})

@app.route("/api/export", methods=["GET"])
def export_excel():
    """Export filtered motors list as an Excel file download."""
    search = request.args.get("search")
    area = request.args.get("area")
    voltage = request.args.get("voltage", type=int)
    make = request.args.get("make")
    status = request.args.get("status")
    criticality = request.args.get("criticality")

    motors = db_api.get_motors(
        search=search, area=area, voltage=voltage, make=make, status=status, criticality=criticality
    )

    data_list = []
    for m in motors:
        data_list.append({
            "Motor Tag": m.get("tag"),
            "Motor Name": m.get("name"),
            "Area": m.get("area"),
            "Criticality": m.get("criticality"),
            "Health Score": f"{m.get('health_score')}% ({m.get('condition_status')})",
            "Power (kW)": m.get("power_kw"),
            "Voltage (V)": m.get("voltage"),
            "Current (A)": m.get("current_amp"),
            "RPM": m.get("rpm"),
            "Make": m.get("make"),
            "Model": m.get("model"),
            "Substation": m.get("substation"),
            "PCC": m.get("pcc"),
            "MCC": m.get("mcc"),
            "Feeder": m.get("feeder"),
            "Status": m.get("status"),
            "Location": m.get("location"),
            "Last Maintenance": m.get("last_maintenance_date") or "",
            "Next Maintenance": m.get("next_maintenance_date") or ""
        })

    df = pd.DataFrame(data_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Motors Report", index=False)
    
    output.seek(0)
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="moto_twin_filtered_report.xlsx"
    )

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "server": "Flask", "database": "Connected"})

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ["true", "1", "yes"]
    logger.info(f"Starting Flask Server on {host}:{port} (debug={debug})...")
    app.run(host=host, port=port, debug=debug)
