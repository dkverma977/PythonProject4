import os
import re
import datetime
import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, Date, Text, ForeignKey, desc, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import io

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("motor-management-server")

# Database Setup
import urllib.parse
from sqlalchemy import text

db_password = urllib.parse.quote_plus("sagar@1729")
server_url = f"mysql+pymysql://root:{db_password}@localhost:3306"
DATABASE_URL = f"{server_url}/motor_data"

# Create database if it doesn't exist
temp_engine = create_engine(server_url, isolation_level="AUTOCOMMIT")
with temp_engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS motor_data"))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Motor(Base):
    __tablename__ = "motors"

    tag = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    area = Column(String(255))
    service = Column(String(255))
    power_kw = Column(Float)
    voltage = Column(Integer)
    current_amp = Column(Float)
    frequency_hz = Column(Float, default=50.0)
    rpm = Column(Integer)
    efficiency = Column(String(255))
    pf = Column(Float)
    frame_size = Column(String(255))
    protection_class = Column(String(255))
    insulation_class = Column(String(255))
    duty = Column(String(255))
    make = Column(String(255))
    model = Column(String(255))
    serial_number = Column(String(255))
    mfg_year = Column(Integer)
    bearing_de = Column(String(255))
    bearing_nde = Column(String(255))
    lubrication_type = Column(String(255))
    cable_size = Column(String(255))
    cable_length_m = Column(Float)
    starter_type = Column(String(255))
    breaker_details = Column(String(255))
    relay_details = Column(String(255))
    substation = Column(String(255))
    pcc = Column(String(255))
    mcc = Column(String(255))
    feeder = Column(String(255))
    incoming = Column(String(255))
    location = Column(String(255))
    remarks = Column(Text)
    status = Column(String(255), default="Running") # Running, Standby, Fault
    is_critical = Column(Boolean, default=False)
    commission_date = Column(Date)
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date)

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    motor_tag = Column(String(255), ForeignKey("motors.tag", ondelete="CASCADE"), index=True)
    log_date = Column(Date, default=datetime.date.today)
    type = Column(String(255)) # Bearing Replacement, Lubrication, Alignment, Insulation Test, Megger Test, Vibration Report, Overhauling
    technician = Column(String(255))
    notes = Column(Text)
    vibration_de_mm_s = Column(Float, nullable=True)
    vibration_nde_mm_s = Column(Float, nullable=True)
    megger_mohm = Column(Float, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas for validation
class MaintenanceLogCreate(BaseModel):
    type: str
    technician: str
    notes: str
    log_date: Optional[str] = None # YYYY-MM-DD
    vibration_de_mm_s: Optional[float] = None
    vibration_nde_mm_s: Optional[float] = None
    megger_mohm: Optional[float] = None

class MotorResponse(BaseModel):
    tag: str
    name: str
    area: Optional[str]
    power_kw: Optional[float]
    voltage: Optional[int]
    status: str
    is_critical: bool
    make: Optional[str]
    substation: Optional[str]
    pcc: Optional[str]
    mcc: Optional[str]
    feeder: Optional[str]

    class Config:
        orm_mode = True

app = FastAPI(title="Industrial Motor Asset Management & Power Feeding System API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper parser function
def clean_power(val) -> float:
    if pd.isna(val):
        return 0.0
    s = str(val).lower().strip()
    match = re.search(r"([0-9\.]+)", s)
    if match:
        return float(match.group(1))
    return 0.0

def clean_voltage(val) -> int:
    if pd.isna(val):
        return 415
    s = str(val).lower().strip()
    match = re.search(r"([0-9\.]+)", s)
    if match:
        num = float(match.group(1))
        # Handle cases like 3.3 kV or 6.6 kV
        if "kv" in s or num < 50:
            return int(num * 1000)
        return int(num)
    return 415

def clean_date(val) -> Optional[datetime.date]:
    if pd.isna(val) or str(val).strip() == "":
        return None
    try:
        return pd.to_datetime(val).date()
    except Exception:
        return None

# Endpoints
@app.get("/api/tree")
def get_tree(db: Session = Depends(get_db)):
    motors = db.query(Motor).all()
    if not motors:
        return {"id": "plant", "label": "Plant Network (Empty)", "type": "plant", "children": []}

    # Hierarchy building: Substation -> PCC -> MCC -> Feeder -> Motor
    tree = {
        "id": "plant",
        "label": "Industrial Plant",
        "type": "plant",
        "status": "Running",
        "children": []
    }

    # Temporary groupings
    subs = {}
    for m in motors:
        s_name = m.substation or "General Substation"
        p_name = m.pcc or "PCC-1"
        m_name = m.mcc or "MCC-1"
        f_name = m.feeder or "Feeder-1"

        if s_name not in subs:
            subs[s_name] = {}
        if p_name not in subs[s_name]:
            subs[s_name][p_name] = {}
        if m_name not in subs[s_name][p_name]:
            subs[s_name][p_name][m_name] = {}
        if f_name not in subs[s_name][p_name][m_name]:
            subs[s_name][p_name][m_name][f_name] = []
        
        subs[s_name][p_name][m_name][f_name].append(m)

    # Build recursively and assign status based on children status (Fault takes priority, then Standby, then Running)
    def determine_node_status(children_list) -> str:
        statuses = [c["status"] for c in children_list if "status" in c and c["status"]]
        if "Fault" in statuses:
            return "Fault"
        if all(s == "Standby" for s in statuses):
            return "Standby"
        return "Running"

    sub_nodes = []
    for s_name, pccs in subs.items():
        pcc_nodes = []
        for p_name, mccs in pccs.items():
            mcc_nodes = []
            for m_name, feeders in mccs.items():
                feeder_nodes = []
                for f_name, motor_list in feeders.items():
                    m_nodes = []
                    for m in motor_list:
                        m_nodes.append({
                            "id": m.tag,
                            "label": f"{m.tag} - {m.name}",
                            "type": "motor",
                            "status": m.status,
                            "is_critical": m.is_critical,
                            "power": f"{m.power_kw} kW",
                            "voltage": f"{m.voltage} V"
                        })
                    
                    f_status = determine_node_status(m_nodes)
                    feeder_nodes.append({
                        "id": f"{s_name}|{p_name}|{m_name}|{f_name}",
                        "label": f_name,
                        "type": "feeder",
                        "status": f_status,
                        "children": sorted(m_nodes, key=lambda x: x["id"])
                    })
                
                m_status = determine_node_status(feeder_nodes)
                mcc_nodes.append({
                    "id": f"{s_name}|{p_name}|{m_name}",
                    "label": m_name,
                    "type": "mcc",
                    "status": m_status,
                    "children": sorted(feeder_nodes, key=lambda x: x["label"])
                })

            p_status = determine_node_status(mcc_nodes)
            pcc_nodes.append({
                "id": f"{s_name}|{p_name}",
                "label": p_name,
                "type": "pcc",
                "status": p_status,
                "children": sorted(mcc_nodes, key=lambda x: x["label"])
            })

        s_status = determine_node_status(pcc_nodes)
        sub_nodes.append({
            "id": s_name,
            "label": s_name,
            "type": "substation",
            "status": s_status,
            "children": sorted(pcc_nodes, key=lambda x: x["label"])
        })

    tree["children"] = sorted(sub_nodes, key=lambda x: x["label"])
    tree["status"] = determine_node_status(tree["children"])
    return tree

@app.get("/api/motors")
def get_motors(
    search: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    voltage: Optional[int] = Query(None),
    make: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_critical: Optional[bool] = Query(None),
    power_min: Optional[float] = Query(None),
    power_max: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Motor)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            Motor.tag.like(search_filter) |
            Motor.name.like(search_filter) |
            Motor.area.like(search_filter) |
            Motor.make.like(search_filter) |
            Motor.location.like(search_filter) |
            Motor.mcc.like(search_filter) |
            Motor.feeder.like(search_filter)
        )

    if area:
        query = query.filter(Motor.area == area)
    if voltage:
        query = query.filter(Motor.voltage == voltage)
    if make:
        query = query.filter(Motor.make == make)
    if status:
        query = query.filter(Motor.status == status)
    if is_critical is not None:
        query = query.filter(Motor.is_critical == is_critical)
    if power_min is not None:
        query = query.filter(Motor.power_kw >= power_min)
    if power_max is not None:
        query = query.filter(Motor.power_kw <= power_max)

    motors = query.all()
    return motors

@app.get("/api/motors/{tag}")
def get_motor_details(tag: str, db: Session = Depends(get_db)):
    motor = db.query(Motor).filter(Motor.tag == tag).first()
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {tag} not found.")
    return motor

@app.get("/api/motors/{tag}/maintenance")
def get_maintenance_history(tag: str, db: Session = Depends(get_db)):
    logs = db.query(MaintenanceLog).filter(MaintenanceLog.motor_tag == tag).order_by(desc(MaintenanceLog.log_date)).all()
    return logs

@app.post("/api/motors/{tag}/maintenance")
def add_maintenance_log(tag: str, log_data: MaintenanceLogCreate, db: Session = Depends(get_db)):
    motor = db.query(Motor).filter(Motor.tag == tag).first()
    if not motor:
        raise HTTPException(status_code=404, detail=f"Motor {tag} not found.")
    
    # Parse date
    log_d = datetime.date.today()
    if log_data.log_date:
        try:
            log_d = datetime.datetime.strptime(log_data.log_date, "%Y-%m-%d").date()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # Create log
    log = MaintenanceLog(
        motor_tag=tag,
        log_date=log_d,
        type=log_data.type,
        technician=log_data.technician,
        notes=log_data.notes,
        vibration_de_mm_s=log_data.vibration_de_mm_s,
        vibration_nde_mm_s=log_data.vibration_nde_mm_s,
        megger_mohm=log_data.megger_mohm
    )
    db.add(log)

    # Update motor maintenance timestamps
    motor.last_maintenance_date = log_d
    motor.next_maintenance_date = log_d + datetime.timedelta(days=180) # Next service in 6 months by default
    db.commit()

    return {"status": "success", "msg": "Maintenance log added successfully."}

@app.get("/api/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    motors = db.query(Motor).all()
    if not motors:
        return {
            "counts": {"motors": 0, "running": 0, "standby": 0, "fault": 0, "substations": 0, "pccs": 0, "mccs": 0, "feeders": 0},
            "power_dist": [], "area_dist": [], "voltage_dist": [], "make_dist": []
        }

    total = len(motors)
    running = sum(1 for m in motors if m.status == "Running")
    standby = sum(1 for m in motors if m.status == "Standby")
    fault = sum(1 for m in motors if m.status == "Fault")

    # Unique entity sets
    subs = set(m.substation for m in motors if m.substation)
    pccs = set(f"{m.substation}|{m.pcc}" for m in motors if m.substation and m.pcc)
    mccs = set(f"{m.substation}|{m.pcc}|{m.mcc}" for m in motors if m.substation and m.pcc and m.mcc)
    feeders = set(f"{m.substation}|{m.pcc}|{m.mcc}|{m.feeder}" for m in motors if m.substation and m.pcc and m.mcc and m.feeder)

    # 1. Power distribution classification
    power_ranges = {"<15 kW": 0, "15-55 kW": 0, "55-150 kW": 0, ">150 kW": 0}
    for m in motors:
        kw = m.power_kw or 0.0
        if kw < 15:
            power_ranges["<15 kW"] += 1
        elif kw <= 55:
            power_ranges["15-55 kW"] += 1
        elif kw <= 150:
            power_ranges["55-150 kW"] += 1
        else:
            power_ranges[">150 kW"] += 1

    # 2. Area counts
    areas = {}
    for m in motors:
        areas[m.area] = areas.get(m.area, 0) + 1

    # 3. Voltage counts
    voltages = {}
    for m in motors:
        v_str = f"{m.voltage} V" if m.voltage < 1000 else f"{m.voltage/1000:.1f} kV"
        voltages[v_str] = voltages.get(v_str, 0) + 1

    # 4. Make counts
    makes = {}
    for m in motors:
        makes[m.make] = makes.get(m.make, 0) + 1

    return {
        "counts": {
            "motors": total,
            "running": running,
            "standby": standby,
            "fault": fault,
            "substations": len(subs),
            "pccs": len(pccs),
            "mccs": len(mccs),
            "feeders": len(feeders)
        },
        "power_dist": [{"range": k, "count": v} for k, v in power_ranges.items()],
        "area_dist": [{"area": k, "count": v} for k, v in areas.items()],
        "voltage_dist": [{"voltage": k, "count": v} for k, v in voltages.items()],
        "make_dist": [{"make": k, "count": v} for k, v in makes.items()]
    }

@app.get("/api/export")
def export_filtered_motors(
    search: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    voltage: Optional[int] = Query(None),
    make: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_critical: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    # Re-use filtering logic
    query = db.query(Motor)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            Motor.tag.like(search_filter) | Motor.name.like(search_filter) |
            Motor.area.like(search_filter) |
            Motor.make.like(search_filter)
        )
    if area:
        query = query.filter(Motor.area == area)
    if voltage:
        query = query.filter(Motor.voltage == voltage)
    if make:
        query = query.filter(Motor.make == make)
    if status:
        query = query.filter(Motor.status == status)
    if is_critical is not None:
        query = query.filter(Motor.is_critical == is_critical)

    motors = query.all()
    
    # Generate Excel in memory
    data_list = []
    for m in motors:
        data_list.append({
            "Motor Tag": m.tag,
            "Motor Name": m.name,
            "Area": m.area,
            "Power (kW)": m.power_kw,
            "Voltage (V)": m.voltage,
            "Current (A)": m.current_amp,
            "RPM": m.rpm,
            "Efficiency": m.efficiency,
            "Make": m.make,
            "Model": m.model,
            "Serial Number": m.serial_number,
            "MCC": m.mcc,
            "Feeder": m.feeder,
            "PCC": m.pcc,
            "Substation": m.substation,
            "Status": m.status,
            "Critical": "Yes" if m.is_critical else "No",
            "Location": m.location,
            "Last Maintenance": m.last_maintenance_date.strftime("%Y-%m-%d") if m.last_maintenance_date else "",
            "Next Maintenance": m.next_maintenance_date.strftime("%Y-%m-%d") if m.next_maintenance_date else ""
        })

    df = pd.DataFrame(data_list)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Motors Report", index=False)
    
    output.seek(0)
    return StreamingResponse(
        output,
        mediaType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=filtered_motors_report.xlsx"}
    )

# Serve static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

# Auto-seed database from sample excel if file exists and DB is empty
@app.on_event("startup")
def startup_db_seed():
    db = SessionLocal()
    try:
        motor_count = db.query(Motor).count()
        if motor_count == 0 and os.path.exists("sample_motors.xlsx"):
            logger.info("Database is empty, auto-seeding from sample_motors.xlsx...")
            df = pd.read_excel("sample_motors.xlsx")
            for index, row in df.iterrows():
                power_val = clean_power(row.get("Power"))
                voltage_val = clean_voltage(row.get("Voltage"))
                current_val = clean_power(row.get("Current"))
                rpm_val = int(row.get("RPM")) if not pd.isna(row.get("RPM")) else 1500
                eff = str(row.get("Efficiency")) if not pd.isna(row.get("Efficiency")) else "92%"
                raw_status = str(row.get("Status")).capitalize() if not pd.isna(row.get("Status")) else "Running"
                
                comm_d = clean_date(row.get("Commission Date"))
                last_m = clean_date(row.get("Last Maintenance Date"))
                next_m = clean_date(row.get("Next Maintenance Date"))
                is_crit = str(row.get("Is Critical")).lower() in ["yes", "true", "1", "y"]

                motor = Motor(
                    tag=str(row["Motor Tag"]).strip(),
                    name=str(row["Motor Name"]).strip(),
                    area=str(row.get("Area")).strip(),
                    service="Conveyor / Pump Duty",
                    power_kw=power_val,
                    voltage=voltage_val,
                    current_amp=current_val,
                    rpm=rpm_val,
                    efficiency=eff,
                    pf=0.85,
                    frame_size=str(row.get("Frame")).strip(),
                    protection_class=str(row.get("Protection")).strip(),
                    insulation_class=str(row.get("Insulation")).strip(),
                    duty=str(row.get("Duty")).strip(),
                    make=str(row.get("Motor Make")).strip(),
                    model=str(row.get("Model")).strip(),
                    serial_number=str(row.get("Serial Number")).strip(),
                    mfg_year=2022,
                    bearing_de="6312-C3",
                    bearing_nde="6212-C3",
                    lubrication_type=str(row.get("Lubrication Type")).strip() if not pd.isna(row.get("Lubrication Type")) else "Grease Mobilith SHC 100",
                    cable_size=str(row.get("Cable Size")).strip(),
                    cable_length_m=clean_power(row.get("Cable Length")) if not pd.isna(row.get("Cable Length")) else 50.0,
                    starter_type=str(row.get("Starter Type")).strip() if not pd.isna(row.get("Starter Type")) else "DOL",
                    breaker_details="MPCB Protected",
                    relay_details="Numerical Relay",
                    substation=str(row["Substation"]).strip(),
                    pcc=str(row["PCC"]).strip(),
                    mcc=str(row["MCC"]).strip(),
                    feeder=str(row["Feeder"]).strip(),
                    incoming=str(row.get("Incoming")).strip() if not pd.isna(row.get("Incoming")) else "Plant Transformer Incomer",
                    location=str(row.get("Location")).strip(),
                    remarks=str(row.get("Remarks")).strip() if not pd.isna(row.get("Remarks")) else "",
                    status=raw_status,
                    is_critical=is_crit,
                    commission_date=comm_d or datetime.date(2022, 1, 1),
                    last_maintenance_date=last_m or datetime.date(2026, 1, 1),
                    next_maintenance_date=next_m or datetime.date(2026, 7, 1)
                )
                db.add(motor)
                
                # Generate mock maintenance log timeline
                m_types = ["Lubrication", "Insulation Test", "Alignment", "Bearing Replacement"]
                for i, log_type in enumerate(m_types):
                    log_d = (last_m or datetime.date(2026, 1, 1)) - datetime.timedelta(days=i*120)
                    m_log = MaintenanceLog(
                        motor_tag=motor.tag,
                        log_date=log_d,
                        type=log_type,
                        technician="Eng. Suresh Kumar",
                        notes=f"Routine {log_type.lower()} maintenance completed. Values within normal range.",
                        vibration_de_mm_s=round(np.random.uniform(1.2, 2.8), 2),
                        vibration_nde_mm_s=round(np.random.uniform(0.8, 1.8), 2),
                        megger_mohm=round(np.random.uniform(50, 450), 1)
                    )
                    db.add(m_log)
            db.commit()
            logger.info("Database auto-seeding completed.")
    except Exception as e:
        logger.error(f"Failed to auto-seed database: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
