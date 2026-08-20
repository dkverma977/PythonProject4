"""
Flask Web Server for Motor Management & Digital Twin Platform
Uses DatabaseAPI class for data management and exposes REST API endpoints.
"""

import os
import io
import logging
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

# Instantiate Database API Class with environment variable support
DATABASE_URL = os.environ.get("DATABASE_URL")
db_api = DatabaseAPI(DATABASE_URL)

# Serve Frontend
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# Authentication Endpoints

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
    """Register a new user account."""
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
        session["user"] = user
        return jsonify({"status": "success", "user": user}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to register user: {str(e)}"}), 500

# REST API Endpoints


@app.route("/api/tree", methods=["GET"])
def get_tree():
    """Retrieve electrical hierarchy layout tree."""
    tree = db_api.get_tree()
    return jsonify(tree)

@app.route("/api/motors", methods=["GET"])
def get_motors():
    """Retrieve motors list with optional query filters."""
    search = request.args.get("search")
    area = request.args.get("area")
    voltage = request.args.get("voltage", type=int)
    make = request.args.get("make")
    status = request.args.get("status")
    
    is_critical_str = request.args.get("is_critical")
    is_critical = None
    if is_critical_str is not None:
        is_critical = is_critical_str.lower() in ["true", "1", "yes"]

    power_min = request.args.get("power_min", type=float)
    power_max = request.args.get("power_max", type=float)

    motors = db_api.get_motors(
        search=search,
        area=area,
        voltage=voltage,
        make=make,
        status=status,
        is_critical=is_critical,
        power_min=power_min,
        power_max=power_max
    )
    return jsonify(motors)

@app.route("/api/motors/<tag>", methods=["GET"])
def get_motor_details(tag):
    """Retrieve details for a specific motor by tag."""
    motor = db_api.get_motor(tag)
    if not motor:
        return jsonify({"error": f"Motor {tag} not found."}), 404
    return jsonify(motor)

@app.route("/api/motors/<tag>/maintenance", methods=["GET"])
def get_maintenance_history(tag):
    """Get maintenance logs timeline for a motor."""
    motor = db_api.get_motor(tag)
    if not motor:
        return jsonify({"error": f"Motor {tag} not found."}), 404
    logs = db_api.get_maintenance_history(tag)
    return jsonify(logs)

@app.route("/api/motors/<tag>/maintenance", methods=["POST"])
def add_maintenance_log(tag):
    """Add a new maintenance log record for a motor."""
    log_data = request.get_json() or {}
    try:
        log = db_api.add_maintenance_log(tag, log_data)
        return jsonify({"status": "success", "msg": "Log added successfully.", "data": log}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to add maintenance log: {str(e)}"}), 400

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard_metrics():
    """Retrieve dashboard summary analytics."""
    analytics = db_api.get_dashboard_analytics()
    return jsonify(analytics)

@app.route("/api/export", methods=["GET"])
def export_excel():
    """Export filtered motors list as an Excel file download."""
    search = request.args.get("search")
    area = request.args.get("area")
    voltage = request.args.get("voltage", type=int)
    make = request.args.get("make")
    status = request.args.get("status")

    is_critical_str = request.args.get("is_critical")
    is_critical = None
    if is_critical_str is not None:
        is_critical = is_critical_str.lower() in ["true", "1", "yes"]

    motors = db_api.get_motors(
        search=search, area=area,
        voltage=voltage, make=make, status=status, is_critical=is_critical
    )

    data_list = []
    for m in motors:
        data_list.append({
            "Motor Tag": m.get("tag"),
            "Motor Name": m.get("name"),
            "Area": m.get("area"),
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
            "Critical": "Yes" if m.get("is_critical") else "No",
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
        download_name="filtered_motors_report.xlsx"
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
