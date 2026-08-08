"""
Database API Class for Motor Platform
Encapsulates database access, ORM models, and CRUD operations using SQLAlchemy.
"""

import os
import datetime
import logging
from typing import Optional, List, Dict, Any
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, Date, Text, ForeignKey, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger("database-api")
Base = declarative_base()

# ORM Models
class Motor(Base):
    __tablename__ = "motors"

    tag = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    area = Column(String)
    department = Column(String)
    service = Column(String)
    power_kw = Column(Float)
    voltage = Column(Integer)
    current_amp = Column(Float)
    frequency_hz = Column(Float, default=50.0)
    rpm = Column(Integer)
    efficiency = Column(String)
    pf = Column(Float)
    frame_size = Column(String)
    protection_class = Column(String)
    insulation_class = Column(String)
    duty = Column(String)
    make = Column(String)
    model = Column(String)
    serial_number = Column(String)
    mfg_year = Column(Integer)
    bearing_de = Column(String)
    bearing_nde = Column(String)
    lubrication_type = Column(String)
    cable_size = Column(String)
    cable_length_m = Column(Float)
    starter_type = Column(String)
    breaker_details = Column(String)
    relay_details = Column(String)
    substation = Column(String)
    pcc = Column(String)
    mcc = Column(String)
    feeder = Column(String)
    incoming = Column(String)
    location = Column(String)
    remarks = Column(Text)
    status = Column(String, default="Running") # Running, Standby, Fault
    is_critical = Column(Boolean, default=False)
    commission_date = Column(Date)
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tag": self.tag,
            "name": self.name,
            "area": self.area,
            "department": self.department,
            "service": self.service,
            "power_kw": self.power_kw,
            "voltage": self.voltage,
            "current_amp": self.current_amp,
            "frequency_hz": self.frequency_hz,
            "rpm": self.rpm,
            "efficiency": self.efficiency,
            "pf": self.pf,
            "frame_size": self.frame_size,
            "protection_class": self.protection_class,
            "insulation_class": self.insulation_class,
            "duty": self.duty,
            "make": self.make,
            "model": self.model,
            "serial_number": self.serial_number,
            "mfg_year": self.mfg_year,
            "bearing_de": self.bearing_de,
            "bearing_nde": self.bearing_nde,
            "lubrication_type": self.lubrication_type,
            "cable_size": self.cable_size,
            "cable_length_m": self.cable_length_m,
            "starter_type": self.starter_type,
            "breaker_details": self.breaker_details,
            "relay_details": self.relay_details,
            "substation": self.substation,
            "pcc": self.pcc,
            "mcc": self.mcc,
            "feeder": self.feeder,
            "incoming": self.incoming,
            "location": self.location,
            "remarks": self.remarks,
            "status": self.status,
            "is_critical": self.is_critical,
            "commission_date": self.commission_date.strftime("%Y-%m-%d") if self.commission_date else None,
            "last_maintenance_date": self.last_maintenance_date.strftime("%Y-%m-%d") if self.last_maintenance_date else None,
            "next_maintenance_date": self.next_maintenance_date.strftime("%Y-%m-%d") if self.next_maintenance_date else None
        }


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    motor_tag = Column(String, ForeignKey("motors.tag", ondelete="CASCADE"), index=True)
    log_date = Column(Date, default=datetime.date.today)
    type = Column(String)
    technician = Column(String)
    notes = Column(Text)
    vibration_de_mm_s = Column(Float, nullable=True)
    vibration_nde_mm_s = Column(Float, nullable=True)
    megger_mohm = Column(Float, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "motor_tag": self.motor_tag,
            "log_date": self.log_date.strftime("%Y-%m-%d") if self.log_date else None,
            "type": self.type,
            "technician": self.technician,
            "notes": self.notes,
            "vibration_de_mm_s": self.vibration_de_mm_s,
            "vibration_nde_mm_s": self.vibration_nde_mm_s,
            "megger_mohm": self.megger_mohm
        }


class DatabaseAPI:
    """Class encapsulation for database management and CRUD operations."""

    def __init__(self, db_url: str = None):
        if db_url is None:
            db_url = os.environ.get("DATABASE_URL", "sqlite:///./motor_platform.db")
        self.db_url = db_url
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        self.engine = create_engine(db_url, connect_args=connect_args)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.init_db()

    def init_db(self):
        """Create tables if they do not exist."""
        Base.metadata.create_all(bind=self.engine)
        self.auto_seed()

    def get_session(self) -> Session:
        """Helper to get a database session."""
        return self.SessionLocal()

    def auto_seed(self):
        """Seed initial motors from sample_motors.xlsx if DB is empty."""
        db = self.get_session()
        try:
            count = db.query(Motor).count()
            if count == 0 and os.path.exists("sample_motors.xlsx"):
                logger.info("Database empty. Auto-seeding from sample_motors.xlsx...")
                df = pd.read_excel("sample_motors.xlsx")
                for index, row in df.iterrows():
                    comm_d = pd.to_datetime(row.get("Commission Date")).date() if not pd.isna(row.get("Commission Date")) else datetime.date(2022, 1, 1)
                    last_m = pd.to_datetime(row.get("Last Maintenance Date")).date() if not pd.isna(row.get("Last Maintenance Date")) else datetime.date(2026, 1, 1)
                    next_m = pd.to_datetime(row.get("Next Maintenance Date")).date() if not pd.isna(row.get("Next Maintenance Date")) else datetime.date(2026, 7, 1)
                    is_crit = str(row.get("Is Critical")).lower() in ["yes", "true", "1", "y"]

                    motor = Motor(
                        tag=str(row["Motor Tag"]).strip(),
                        name=str(row["Motor Name"]).strip(),
                        area=str(row.get("Area")).strip(),
                        department=str(row.get("Department")).strip(),
                        service="Conveyor / Pump Duty",
                        power_kw=float(str(row.get("Power")).replace('kW','').strip()) if not pd.isna(row.get("Power")) else 45.0,
                        voltage=int(str(row.get("Voltage")).replace('V','').strip()) if not pd.isna(row.get("Voltage")) else 415,
                        current_amp=float(str(row.get("Current")).replace('A','').strip()) if not pd.isna(row.get("Current")) else 75.0,
                        rpm=int(row.get("RPM")) if not pd.isna(row.get("RPM")) else 1500,
                        efficiency=str(row.get("Efficiency")) if not pd.isna(row.get("Efficiency")) else "92%",
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
                        lubrication_type="Grease Mobilith SHC 100",
                        cable_size=str(row.get("Cable Size")).strip(),
                        cable_length_m=50.0,
                        starter_type="DOL",
                        breaker_details="MPCB Protected",
                        relay_details="Numerical Relay",
                        substation=str(row["Substation"]).strip(),
                        pcc=str(row["PCC"]).strip(),
                        mcc=str(row["MCC"]).strip(),
                        feeder=str(row["Feeder"]).strip(),
                        incoming="Plant Transformer Incomer",
                        location=str(row.get("Location")).strip(),
                        remarks=str(row.get("Remarks")).strip() if not pd.isna(row.get("Remarks")) else "",
                        status=str(row.get("Status")).capitalize() if not pd.isna(row.get("Status")) else "Running",
                        is_critical=is_crit,
                        commission_date=comm_d,
                        last_maintenance_date=last_m,
                        next_maintenance_date=next_m
                    )
                    db.add(motor)

                    # Add sample maintenance logs
                    m_types = ["Lubrication", "Insulation Test", "Alignment", "Bearing Replacement"]
                    for i, log_type in enumerate(m_types):
                        log_d = last_m - datetime.timedelta(days=i*120)
                        m_log = MaintenanceLog(
                            motor_tag=motor.tag,
                            log_date=log_d,
                            type=log_type,
                            technician="Eng. Suresh Kumar",
                            notes=f"Routine {log_type.lower()} completed.",
                            vibration_de_mm_s=round(np.random.uniform(1.2, 2.8), 2),
                            vibration_nde_mm_s=round(np.random.uniform(0.8, 1.8), 2),
                            megger_mohm=round(np.random.uniform(50, 450), 1)
                        )
                        db.add(m_log)
                db.commit()
                logger.info("Auto-seeding finished successfully.")
        except Exception as e:
            logger.error(f"Auto-seeding error: {e}")
            db.rollback()
        finally:
            db.close()

    def get_tree(self) -> Dict[str, Any]:
        """Build layout hierarchy tree: Substation -> PCC -> MCC -> Feeder -> Motor."""
        db = self.get_session()
        try:
            motors = db.query(Motor).all()
            if not motors:
                return {"id": "plant", "label": "Plant Network (Empty)", "type": "plant", "children": []}

            tree = {
                "id": "plant",
                "label": "Industrial Plant",
                "type": "plant",
                "status": "Running",
                "children": []
            }

            subs = {}
            for m in motors:
                s_name = m.substation or "General Substation"
                p_name = m.pcc or "PCC-1"
                m_name = m.mcc or "MCC-1"
                f_name = m.feeder or "Feeder-1"

                subs.setdefault(s_name, {}).setdefault(p_name, {}).setdefault(m_name, {}).setdefault(f_name, []).append(m)

            def calc_status(node_list):
                statuses = [c["status"] for c in node_list if "status" in c]
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
                            m_nodes = [{
                                "id": m.tag,
                                "label": f"{m.tag} - {m.name}",
                                "type": "motor",
                                "status": m.status,
                                "is_critical": m.is_critical,
                                "power": f"{m.power_kw} kW",
                                "voltage": f"{m.voltage} V"
                            } for m in motor_list]

                            feeder_nodes.append({
                                "id": f"{s_name}|{p_name}|{m_name}|{f_name}",
                                "label": f_name,
                                "type": "feeder",
                                "status": calc_status(m_nodes),
                                "children": sorted(m_nodes, key=lambda x: x["id"])
                            })
                        mcc_nodes.append({
                            "id": f"{s_name}|{p_name}|{m_name}",
                            "label": m_name,
                            "type": "mcc",
                            "status": calc_status(feeder_nodes),
                            "children": sorted(feeder_nodes, key=lambda x: x["label"])
                        })
                    pcc_nodes.append({
                        "id": f"{s_name}|{p_name}",
                        "label": p_name,
                        "type": "pcc",
                        "status": calc_status(mcc_nodes),
                        "children": sorted(mcc_nodes, key=lambda x: x["label"])
                    })
                sub_nodes.append({
                    "id": s_name,
                    "label": s_name,
                    "type": "substation",
                    "status": calc_status(pcc_nodes),
                    "children": sorted(pcc_nodes, key=lambda x: x["label"])
                })

            tree["children"] = sorted(sub_nodes, key=lambda x: x["label"])
            tree["status"] = calc_status(tree["children"])
            return tree
        finally:
            db.close()

    def get_motors(self, search: str = None, area: str = None, department: str = None,
                   voltage: int = None, make: str = None, status: str = None,
                   is_critical: bool = None, power_min: float = None, power_max: float = None) -> List[Dict[str, Any]]:
        """Query motors with optional filters."""
        db = self.get_session()
        try:
            query = db.query(Motor)
            if search:
                sf = f"%{search}%"
                query = query.filter(
                    Motor.tag.like(sf) | Motor.name.like(sf) | Motor.area.like(sf) |
                    Motor.department.like(sf) | Motor.make.like(sf) | Motor.location.like(sf)
                )
            if area:
                query = query.filter(Motor.area == area)
            if department:
                query = query.filter(Motor.department == department)
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

            return [m.to_dict() for m in query.all()]
        finally:
            db.close()

    def get_motor(self, tag: str) -> Optional[Dict[str, Any]]:
        """Retrieve single motor details by tag."""
        db = self.get_session()
        try:
            motor = db.query(Motor).filter(Motor.tag == tag).first()
            return motor.to_dict() if motor else None
        finally:
            db.close()

    def get_maintenance_history(self, tag: str) -> List[Dict[str, Any]]:
        """Get maintenance logs for a motor."""
        db = self.get_session()
        try:
            logs = db.query(MaintenanceLog).filter(MaintenanceLog.motor_tag == tag).order_by(desc(MaintenanceLog.log_date)).all()
            return [l.to_dict() for l in logs]
        finally:
            db.close()

    def add_maintenance_log(self, tag: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a maintenance log for a motor."""
        db = self.get_session()
        try:
            motor = db.query(Motor).filter(Motor.tag == tag).first()
            if not motor:
                raise ValueError(f"Motor {tag} not found.")

            log_d = datetime.date.today()
            if log_data.get("log_date"):
                log_d = datetime.datetime.strptime(log_data["log_date"], "%Y-%m-%d").date()

            log = MaintenanceLog(
                motor_tag=tag,
                log_date=log_d,
                type=log_data.get("type", "General Inspection"),
                technician=log_data.get("technician", "Maintenance Engineer"),
                notes=log_data.get("notes", ""),
                vibration_de_mm_s=log_data.get("vibration_de_mm_s"),
                vibration_nde_mm_s=log_data.get("vibration_nde_mm_s"),
                megger_mohm=log_data.get("megger_mohm")
            )
            db.add(log)
            motor.last_maintenance_date = log_d
            motor.next_maintenance_date = log_d + datetime.timedelta(days=180)
            db.commit()
            return log.to_dict()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Get dashboard summary metrics and distributions."""
        db = self.get_session()
        try:
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

            subs = set(m.substation for m in motors if m.substation)
            pccs = set(f"{m.substation}|{m.pcc}" for m in motors if m.substation and m.pcc)
            mccs = set(f"{m.substation}|{m.pcc}|{m.mcc}" for m in motors if m.substation and m.pcc and m.mcc)
            feeders = set(f"{m.substation}|{m.pcc}|{m.mcc}|{m.feeder}" for m in motors if m.substation and m.pcc and m.mcc and m.feeder)

            power_ranges = {"<15 kW": 0, "15-55 kW": 0, "55-150 kW": 0, ">150 kW": 0}
            areas = {}
            voltages = {}
            makes = {}

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

                if m.area:
                    areas[m.area] = areas.get(m.area, 0) + 1
                if m.voltage:
                    v_str = f"{m.voltage} V" if m.voltage < 1000 else f"{m.voltage/1000:.1f} kV"
                    voltages[v_str] = voltages.get(v_str, 0) + 1
                if m.make:
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
        finally:
            db.close()
