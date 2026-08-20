"""
Database API Class for Motor Platform — MOTO-TWIN Digital Twin Platform
Encapsulates database access, normalized ORM models, Health Scoring, Predictive Analytics, 
Electrical Hierarchy Management, Telemetry, Alarms, Maintenance, Work Orders, Energy, and Audit Logs.
"""

import os
import io
import json
import datetime
import logging
import sqlite3
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey, desc, asc, func, text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

logger = logging.getLogger("database-api")
Base = declarative_base()

# ==========================================
# NORMALIZED ORM MODELS
# ==========================================

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    capacity_mw = Column(Float, default=100.0)
    status = Column(String(50), default="Running")
    remarks = Column(Text)

    substations = relationship("Substation", backref="plant", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tag": self.tag,
            "name": self.name,
            "location": self.location,
            "capacity_mw": self.capacity_mw,
            "status": self.status,
            "remarks": self.remarks
        }


class Substation(Base):
    __tablename__ = "substations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=True)
    tag = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    voltage_kv = Column(Float, default=33.0)
    status = Column(String(50), default="Running")

    transformers = relationship("Transformer", backref="substation", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "plant_id": self.plant_id,
            "tag": self.tag,
            "name": self.name,
            "voltage_kv": self.voltage_kv,
            "status": self.status
        }


class Transformer(Base):
    __tablename__ = "transformers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    substation_id = Column(Integer, ForeignKey("substations.id", ondelete="CASCADE"), nullable=True)
    tag = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    rating_kva = Column(Float, default=2500.0)
    primary_voltage = Column(Float, default=33000.0)
    secondary_voltage = Column(Float, default=415.0)
    manufacturer = Column(String(255), default="ABB")
    impedance = Column(Float, default=6.5)
    oil_temperature = Column(Float, default=55.0)
    winding_temperature = Column(Float, default=65.0)
    loading_percent = Column(Float, default=68.5)
    status = Column(String(50), default="Running")

    pccs = relationship("PCC", backref="transformer", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "substation_id": self.substation_id,
            "tag": self.tag,
            "name": self.name,
            "rating_kva": self.rating_kva,
            "primary_voltage": self.primary_voltage,
            "secondary_voltage": self.secondary_voltage,
            "manufacturer": self.manufacturer,
            "impedance": self.impedance,
            "oil_temperature": self.oil_temperature,
            "winding_temperature": self.winding_temperature,
            "loading_percent": self.loading_percent,
            "status": self.status
        }


class PCC(Base):
    __tablename__ = "pccs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transformer_id = Column(Integer, ForeignKey("transformers.id", ondelete="CASCADE"), nullable=True)
    tag = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    voltage = Column(Float, default=415.0)
    incomer = Column(String(255), default="Main Incomer ACB-1")
    bus_rating = Column(Float, default=4000.0)
    status = Column(String(50), default="Running")

    mccs = relationship("MCC", backref="pcc", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "transformer_id": self.transformer_id,
            "tag": self.tag,
            "name": self.name,
            "voltage": self.voltage,
            "incomer": self.incomer,
            "bus_rating": self.bus_rating,
            "status": self.status
        }


class MCC(Base):
    __tablename__ = "mccs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pcc_id = Column(Integer, ForeignKey("pccs.id", ondelete="CASCADE"), nullable=True)
    tag = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    voltage = Column(Float, default=415.0)
    bus_rating = Column(Float, default=1600.0)
    incomer = Column(String(255), default="MCC Incomer Breaker")
    status = Column(String(50), default="Running")

    feeders = relationship("Feeder", backref="mcc", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "pcc_id": self.pcc_id,
            "tag": self.tag,
            "name": self.name,
            "voltage": self.voltage,
            "bus_rating": self.bus_rating,
            "incomer": self.incomer,
            "status": self.status
        }


class Feeder(Base):
    __tablename__ = "feeders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mcc_id = Column(Integer, ForeignKey("mccs.id", ondelete="CASCADE"), nullable=True)
    tag = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    voltage = Column(Float, default=415.0)
    rated_current = Column(Float, default=250.0)
    cable_size = Column(String(255), default="3C x 185 sq mm Al")
    cable_length_m = Column(Float, default=50.0)
    breaker_type = Column(String(100), default="MPCB")
    breaker_rating = Column(Float, default=250.0)
    overload_setting = Column(Float, default=1.1)
    protection_settings = Column(Text, default="Overcurrent: 110%, Earth Fault: 10%, Phase Loss: Active")
    status = Column(String(50), default="Running")

    motors = relationship("Motor", backref="feeder_ref", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "mcc_id": self.mcc_id,
            "tag": self.tag,
            "name": self.name,
            "voltage": self.voltage,
            "rated_current": self.rated_current,
            "cable_size": self.cable_size,
            "cable_length_m": self.cable_length_m,
            "breaker_type": self.breaker_type,
            "breaker_rating": self.breaker_rating,
            "overload_setting": self.overload_setting,
            "protection_settings": self.protection_settings,
            "status": self.status
        }


class Motor(Base):
    __tablename__ = "motors"

    tag = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    area = Column(String(255))
    service = Column(String(255))
    make = Column(String(255))
    model = Column(String(255))
    serial_number = Column(String(255))
    asset_number = Column(String(255))

    # Electrical
    power_kw = Column(Float)
    voltage = Column(Integer)
    current_amp = Column(Float)
    frequency_hz = Column(Float, default=50.0)
    rpm = Column(Integer)
    pf = Column(Float, default=0.85)
    efficiency = Column(String(255), default="92%")
    phases = Column(Integer, default=3)
    starter_type = Column(String(255), default="DOL")
    rated_load = Column(Float, default=100.0)

    # Mechanical
    frame_size = Column(String(255))
    bearing_de = Column(String(255))
    bearing_nde = Column(String(255))
    lubrication_type = Column(String(255))

    # Protection
    protection_class = Column(String(255), default="IP55")
    insulation_class = Column(String(255), default="Class F")
    duty = Column(String(255), default="S1 Continuous")
    overload_protection = Column(String(255), default="MPCB Thermal Relay")
    earth_fault_protection = Column(String(255), default="CBCT Numerical Relay")
    phase_failure_protection = Column(String(255), default="Phase Loss Relay")

    # Operational & Criticality
    status = Column(String(255), default="Running") # Running, Standby, Fault
    criticality = Column(String(50), default="B - Important") # A - Critical, B - Important, C - Normal
    is_critical = Column(Boolean, default=False)
    production_impact = Column(String(50), default="High")
    safety_impact = Column(String(50), default="Medium")
    environmental_impact = Column(String(50), default="Low")
    redundancy = Column(String(50), default="N+1 Standby")
    replacement_lead_time_days = Column(Integer, default=30)
    repair_cost_usd = Column(Float, default=5000.0)
    failure_frequency = Column(String(50), default="Low")

    installation_date = Column(Date, default=datetime.date(2021, 1, 1))
    commission_date = Column(Date, default=datetime.date(2022, 1, 1))
    expected_life_years = Column(Integer, default=20)
    running_hours = Column(Float, default=8500.0)
    start_count = Column(Integer, default=142)

    # Health & Condition
    health_score = Column(Integer, default=85)
    condition_status = Column(String(50), default="GOOD")

    # Hierarchy FK references & fallback text
    feeder_id = Column(Integer, ForeignKey("feeders.id", ondelete="SET NULL"), nullable=True)
    mcc_id = Column(Integer, ForeignKey("mccs.id", ondelete="SET NULL"), nullable=True)
    pcc_id = Column(Integer, ForeignKey("pccs.id", ondelete="SET NULL"), nullable=True)
    transformer_id = Column(Integer, ForeignKey("transformers.id", ondelete="SET NULL"), nullable=True)
    substation_id = Column(Integer, ForeignKey("substations.id", ondelete="SET NULL"), nullable=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="SET NULL"), nullable=True)

    # Fallback text strings for compatibility
    substation = Column(String(255))
    pcc = Column(String(255))
    mcc = Column(String(255))
    feeder = Column(String(255))
    incoming = Column(String(255), default="Plant Transformer Incomer")
    location = Column(String(255))
    remarks = Column(Text)
    mfg_year = Column(Integer, default=2022)
    cable_size = Column(String(255))
    cable_length_m = Column(Float, default=50.0)
    breaker_details = Column(String(255))
    relay_details = Column(String(255))
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tag": self.tag,
            "motor_tag": self.tag,
            "name": self.name,
            "area": self.area,
            "service": self.service,
            "make": self.make,
            "manufacturer": self.make,
            "model": self.model,
            "serial_number": self.serial_number,
            "asset_number": self.asset_number or f"AST-{self.tag}",
            "power_kw": self.power_kw,
            "voltage": self.voltage,
            "current_amp": self.current_amp,
            "frequency_hz": self.frequency_hz,
            "rpm": self.rpm,
            "pf": self.pf,
            "efficiency": self.efficiency,
            "phases": self.phases,
            "starter_type": self.starter_type,
            "rated_load": self.rated_load,
            "frame_size": self.frame_size,
            "bearing_de": self.bearing_de,
            "bearing_nde": self.bearing_nde,
            "lubrication_type": self.lubrication_type,
            "protection_class": self.protection_class,
            "insulation_class": self.insulation_class,
            "duty": self.duty,
            "overload_protection": self.overload_protection,
            "earth_fault_protection": self.earth_fault_protection,
            "phase_failure_protection": self.phase_failure_protection,
            "status": self.status,
            "criticality": self.criticality or ("A - Critical" if self.is_critical else "B - Important"),
            "is_critical": self.is_critical or (self.criticality == "A - Critical"),
            "production_impact": self.production_impact,
            "safety_impact": self.safety_impact,
            "environmental_impact": self.environmental_impact,
            "redundancy": self.redundancy,
            "replacement_lead_time_days": self.replacement_lead_time_days,
            "repair_cost_usd": self.repair_cost_usd,
            "failure_frequency": self.failure_frequency,
            "installation_date": self.installation_date.strftime("%Y-%m-%d") if self.installation_date else None,
            "commission_date": self.commission_date.strftime("%Y-%m-%d") if self.commission_date else None,
            "expected_life_years": self.expected_life_years,
            "running_hours": self.running_hours,
            "start_count": self.start_count,
            "health_score": self.health_score or 85,
            "condition_status": self.condition_status or "GOOD",
            "feeder_id": self.feeder_id,
            "mcc_id": self.mcc_id,
            "pcc_id": self.pcc_id,
            "transformer_id": self.transformer_id,
            "substation_id": self.substation_id,
            "plant_id": self.plant_id,
            "substation": self.substation,
            "pcc": self.pcc,
            "mcc": self.mcc,
            "feeder": self.feeder,
            "incoming": self.incoming,
            "location": self.location,
            "remarks": self.remarks,
            "mfg_year": self.mfg_year,
            "cable_size": self.cable_size,
            "cable_length_m": self.cable_length_m,
            "breaker_details": self.breaker_details,
            "relay_details": self.relay_details,
            "last_maintenance_date": self.last_maintenance_date.strftime("%Y-%m-%d") if self.last_maintenance_date else None,
            "next_maintenance_date": self.next_maintenance_date.strftime("%Y-%m-%d") if self.next_maintenance_date else None
        }


class MotorMeasurement(Base):
    __tablename__ = "motor_measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    motor_tag = Column(String(255), ForeignKey("motors.tag", ondelete="CASCADE"), index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    voltage = Column(Float)
    current = Column(Float)
    active_power_kw = Column(Float)
    reactive_power_kvar = Column(Float)
    apparent_power_kva = Column(Float)
    power_factor = Column(Float)
    frequency = Column(Float, default=50.0)
    energy_kwh = Column(Float)
    load_percent = Column(Float)
    running_hours = Column(Float)
    start_count = Column(Integer)

    vibration_de = Column(Float)
    vibration_nde = Column(Float)
    temperature_de = Column(Float)
    temperature_nde = Column(Float)
    winding_temperature = Column(Float)
    ambient_temperature = Column(Float, default=32.0)

    vfd_frequency = Column(Float, nullable=True)
    vfd_output_current = Column(Float, nullable=True)
    vfd_temperature = Column(Float, nullable=True)
    vfd_status = Column(String(50), nullable=True)

    data_source = Column(String(50), default="SIMULATED") # LIVE, SIMULATED, HISTORICAL, MANUAL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "motor_tag": self.motor_tag,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "voltage": self.voltage,
            "current": self.current,
            "active_power_kw": self.active_power_kw,
            "reactive_power_kvar": self.reactive_power_kvar,
            "apparent_power_kva": self.apparent_power_kva,
            "power_factor": self.power_factor,
            "frequency": self.frequency,
            "energy_kwh": self.energy_kwh,
            "load_percent": self.load_percent,
            "running_hours": self.running_hours,
            "start_count": self.start_count,
            "vibration_de": self.vibration_de,
            "vibration_nde": self.vibration_nde,
            "temperature_de": self.temperature_de,
            "temperature_nde": self.temperature_nde,
            "winding_temperature": self.winding_temperature,
            "ambient_temperature": self.ambient_temperature,
            "vfd_frequency": self.vfd_frequency,
            "vfd_output_current": self.vfd_output_current,
            "vfd_temperature": self.vfd_temperature,
            "vfd_status": self.vfd_status,
            "data_source": self.data_source
        }


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    motor_tag = Column(String(255), ForeignKey("motors.tag", ondelete="CASCADE"), index=True)
    log_date = Column(Date, default=datetime.date.today)
    type = Column(String(255)) # Preventive, Predictive, Breakdown, Corrective
    technician = Column(String(255))
    work_description = Column(Text)
    notes = Column(Text)
    findings = Column(Text)
    vibration_de_mm_s = Column(Float, nullable=True)
    vibration_nde_mm_s = Column(Float, nullable=True)
    megger_mohm = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    parts_replaced = Column(String(255), nullable=True)
    root_cause = Column(String(255), nullable=True)
    corrective_action = Column(String(255), nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "motor_tag": self.motor_tag,
            "log_date": self.log_date.strftime("%Y-%m-%d") if self.log_date else None,
            "type": self.type,
            "technician": self.technician,
            "work_description": self.work_description or self.notes,
            "notes": self.notes,
            "findings": self.findings,
            "vibration_de_mm_s": self.vibration_de_mm_s,
            "vibration_nde_mm_s": self.vibration_nde_mm_s,
            "megger_mohm": self.megger_mohm,
            "temperature_c": self.temperature_c,
            "parts_replaced": self.parts_replaced,
            "root_cause": self.root_cause,
            "corrective_action": self.corrective_action
        }


class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    motor_tag = Column(String(255), ForeignKey("motors.tag", ondelete="CASCADE"), index=True)
    maintenance_type = Column(String(100), default="Preventive Maintenance")
    frequency_days = Column(Integer, default=180)
    last_completed = Column(Date, nullable=True)
    next_due = Column(Date, nullable=False)
    assigned_technician = Column(String(255), default="Eng. Suresh Kumar")
    status = Column(String(50), default="UP TO DATE") # OVERDUE, DUE TODAY, DUE THIS WEEK, DUE THIS MONTH, UP TO DATE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "motor_tag": self.motor_tag,
            "maintenance_type": self.maintenance_type,
            "frequency_days": self.frequency_days,
            "last_completed": self.last_completed.strftime("%Y-%m-%d") if self.last_completed else None,
            "next_due": self.next_due.strftime("%Y-%m-%d") if self.next_due else None,
            "assigned_technician": self.assigned_technician,
            "status": self.status
        }


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("maintenance_schedules.id", ondelete="SET NULL"), nullable=True)
    motor_tag = Column(String(255), ForeignKey("motors.tag", ondelete="CASCADE"), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(50), default="Medium") # Low, Medium, High, Critical
    state = Column(String(50), default="OPEN") # OPEN, ASSIGNED, IN PROGRESS, COMPLETED, CANCELLED
    assigned_technician = Column(String(255), default="Eng. Rajesh V")
    created_date = Column(Date, default=datetime.date.today)
    due_date = Column(Date, default=lambda: datetime.date.today() + datetime.timedelta(days=7))
    completed_date = Column(Date, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "schedule_id": self.schedule_id,
            "motor_tag": self.motor_tag,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "state": self.state,
            "assigned_technician": self.assigned_technician,
            "created_date": self.created_date.strftime("%Y-%m-%d") if self.created_date else None,
            "due_date": self.due_date.strftime("%Y-%m-%d") if self.due_date else None,
            "completed_date": self.completed_date.strftime("%Y-%m-%d") if self.completed_date else None
        }


class MotorFailure(Base):
    __tablename__ = "motor_failures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    motor_tag = Column(String(255), ForeignKey("motors.tag", ondelete="CASCADE"), index=True)
    failure_date = Column(Date, default=datetime.date.today)
    failure_mode = Column(String(100), default="Bearing Failure") # Bearing, Winding, Overload, Vibration, Lubrication, Electrical, Mechanical, Other
    failure_type = Column(String(100), default="Sudden Breakdown")
    root_cause = Column(Text)
    downtime_hours = Column(Float, default=4.5)
    production_loss = Column(Float, default=12000.0)
    repair_cost = Column(Float, default=3500.0)
    corrective_action = Column(Text)
    technician = Column(String(255), default="Eng. Suresh Kumar")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "motor_tag": self.motor_tag,
            "failure_date": self.failure_date.strftime("%Y-%m-%d") if self.failure_date else None,
            "failure_mode": self.failure_mode,
            "failure_type": self.failure_type,
            "root_cause": self.root_cause,
            "downtime_hours": self.downtime_hours,
            "production_loss": self.production_loss,
            "repair_cost": self.repair_cost,
            "corrective_action": self.corrective_action,
            "technician": self.technician
        }


class MotorAlarm(Base):
    __tablename__ = "motor_alarms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    motor_tag = Column(String(255), ForeignKey("motors.tag", ondelete="CASCADE"), index=True)
    parameter = Column(String(100), nullable=False) # Vibration, DE Temp, Current, Winding Temp, Insulation Resistance
    actual_value = Column(Float, nullable=False)
    limit_value = Column(Float, nullable=False)
    severity = Column(String(50), default="WARNING") # INFO, WARNING, HIGH, CRITICAL
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(255), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    cleared = Column(Boolean, default=False)
    cleared_at = Column(DateTime, nullable=True)
    root_cause = Column(String(255), nullable=True)
    corrective_action = Column(String(255), nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "motor_tag": self.motor_tag,
            "parameter": self.parameter,
            "actual_value": self.actual_value,
            "limit_value": self.limit_value,
            "severity": self.severity,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.strftime("%Y-%m-%d %H:%M:%S") if self.acknowledged_at else None,
            "cleared": self.cleared,
            "cleared_at": self.cleared_at.strftime("%Y-%m-%d %H:%M:%S") if self.cleared_at else None,
            "root_cause": self.root_cause,
            "corrective_action": self.corrective_action
        }


class MotorEnergy(Base):
    __tablename__ = "motor_energy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    motor_tag = Column(String(255), ForeignKey("motors.tag", ondelete="CASCADE"), index=True)
    record_date = Column(Date, default=datetime.date.today, index=True)
    daily_kwh = Column(Float, default=450.0)
    monthly_kwh = Column(Float, default=13500.0)
    yearly_kwh = Column(Float, default=162000.0)
    avg_load_percent = Column(Float, default=78.5)
    running_hours = Column(Float, default=21.5)
    estimated_cost = Column(Float, default=54.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "motor_tag": self.motor_tag,
            "record_date": self.record_date.strftime("%Y-%m-%d") if self.record_date else None,
            "daily_kwh": self.daily_kwh,
            "monthly_kwh": self.monthly_kwh,
            "yearly_kwh": self.yearly_kwh,
            "avg_load_percent": self.avg_load_percent,
            "running_hours": self.running_hours,
            "estimated_cost": self.estimated_cost
        }


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    role = Column(String(50), default="Viewer") # Admin, Engineer, Viewer
    must_change_password = Column(Boolean, default=False)
    created_at = Column(Date, default=datetime.date.today)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "must_change_password": self.must_change_password,
            "created_at": self.created_at.strftime("%Y-%m-%d") if self.created_at else None
        }


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    ip_address = Column(String(100), default="127.0.0.1")
    action = Column(String(255), nullable=False) # MOTOR_CREATED, MOTOR_UPDATED, ALARM_ACKNOWLEDGED, etc.
    entity = Column(String(100))
    entity_id = Column(String(255))
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "ip_address": self.ip_address,
            "action": self.action,
            "entity": self.entity,
            "entity_id": self.entity_id,
            "old_value": self.old_value,
            "new_value": self.new_value
        }


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    motor_tag = Column(String(255), ForeignKey("motors.tag", ondelete="CASCADE"), index=True)
    doc_type = Column(String(100), default="Datasheet") # Datasheet, Single-line Diagram, Nameplate Photo, Manual
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    upload_date = Column(Date, default=datetime.date.today)
    uploaded_by = Column(String(255), default="System")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "motor_tag": self.motor_tag,
            "doc_type": self.doc_type,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "upload_date": self.upload_date.strftime("%Y-%m-%d") if self.upload_date else None,
            "uploaded_by": self.uploaded_by
        }


# ==========================================
# HEALTH SCORE & PREDICTIVE ANALYTICS ENGINES
# ==========================================

def calculate_motor_health(motor: Motor, db: Session) -> Tuple[int, str, List[Dict[str, Any]]]:
    """
    Calculate Motor Health Score from 0 to 100 based on weighted engineering metrics:
    - Vibration (max 20 pts penalty)
    - Temperature (max 20 pts penalty)
    - Voltage/Current Deviation (max 15 pts penalty)
    - Insulation Megger Resistance (max 15 pts penalty)
    - Active Alarms (max 15 pts penalty)
    - Overdue Maintenance (max 15 pts penalty)
    Returns: (score, condition_status, contributing_factors)
    """
    score = 100
    factors = []

    # 1. Fetch latest telemetry measurement if available
    latest_meas = db.query(MotorMeasurement).filter(MotorMeasurement.motor_tag == motor.tag).order_by(desc(MotorMeasurement.timestamp)).first()
    
    vib_de = latest_meas.vibration_de if latest_meas and latest_meas.vibration_de is not None else 2.1
    vib_nde = latest_meas.vibration_nde if latest_meas and latest_meas.vibration_nde is not None else 1.5
    temp_de = latest_meas.temperature_de if latest_meas and latest_meas.temperature_de is not None else 65.0
    temp_wind = latest_meas.winding_temperature if latest_meas and latest_meas.winding_temperature is not None else 72.0
    v_actual = latest_meas.voltage if latest_meas and latest_meas.voltage is not None else (motor.voltage or 415.0)

    # 2. Vibration penalty (ISO 10816 Zone A <2.8, B <4.5, C <7.1, D >7.1 mm/s)
    max_vib = max(vib_de, vib_nde)
    if max_vib >= 7.1:
        score -= 20
        factors.append({"factor": "Vibration", "value": f"{max_vib:.1f} mm/s", "status": "CRITICAL", "impact": "-20 pts"})
    elif max_vib >= 4.5:
        score -= 12
        factors.append({"factor": "Vibration", "value": f"{max_vib:.1f} mm/s", "status": "WARNING", "impact": "-12 pts"})
    elif max_vib >= 2.8:
        score -= 5
        factors.append({"factor": "Vibration", "value": f"{max_vib:.1f} mm/s", "status": "MODERATE", "impact": "-5 pts"})
    else:
        factors.append({"factor": "Vibration", "value": f"{max_vib:.1f} mm/s", "status": "NORMAL", "impact": "0 pts"})

    # 3. Temperature penalty
    if temp_de >= 90 or temp_wind >= 110:
        score -= 20
        factors.append({"factor": "Bearing/Winding Temp", "value": f"DE {temp_de}°C / Wind {temp_wind}°C", "status": "CRITICAL", "impact": "-20 pts"})
    elif temp_de >= 78 or temp_wind >= 95:
        score -= 10
        factors.append({"factor": "Bearing/Winding Temp", "value": f"DE {temp_de}°C / Wind {temp_wind}°C", "status": "WARNING", "impact": "-10 pts"})
    else:
        factors.append({"factor": "Bearing/Winding Temp", "value": f"DE {temp_de}°C / Wind {temp_wind}°C", "status": "NORMAL", "impact": "0 pts"})

    # 4. Voltage Deviation penalty
    v_rated = float(motor.voltage or 415)
    v_dev_pct = abs((v_actual - v_rated) / v_rated) * 100
    if v_dev_pct > 10:
        score -= 15
        factors.append({"factor": "Voltage Deviation", "value": f"{v_dev_pct:.1f}% ({v_actual}V)", "status": "CRITICAL", "impact": "-15 pts"})
    elif v_dev_pct > 5:
        score -= 8
        factors.append({"factor": "Voltage Deviation", "value": f"{v_dev_pct:.1f}% ({v_actual}V)", "status": "WARNING", "impact": "-8 pts"})
    else:
        factors.append({"factor": "Voltage Deviation", "value": f"{v_dev_pct:.1f}% ({v_actual}V)", "status": "NORMAL", "impact": "0 pts"})

    # 5. Insulation Megger penalty
    latest_maint = db.query(MaintenanceLog).filter(MaintenanceLog.motor_tag == motor.tag, MaintenanceLog.megger_mohm != None).order_by(desc(MaintenanceLog.log_date)).first()
    megger = latest_maint.megger_mohm if latest_maint else 150.0
    if megger < 5.0:
        score -= 15
        factors.append({"factor": "Insulation Resistance", "value": f"{megger} MΩ", "status": "CRITICAL", "impact": "-15 pts"})
    elif megger < 20.0:
        score -= 8
        factors.append({"factor": "Insulation Resistance", "value": f"{megger} MΩ", "status": "WARNING", "impact": "-8 pts"})
    else:
        factors.append({"factor": "Insulation Resistance", "value": f"{megger} MΩ", "status": "NORMAL", "impact": "0 pts"})

    # 6. Active Alarms penalty
    active_alarms = db.query(MotorAlarm).filter(MotorAlarm.motor_tag == motor.tag, MotorAlarm.cleared == False).all()
    if active_alarms:
        critical_alarms = sum(1 for a in active_alarms if a.severity in ["CRITICAL", "HIGH"])
        if critical_alarms > 0:
            score -= 15
            factors.append({"factor": "Active Alarms", "value": f"{len(active_alarms)} alarms ({critical_alarms} Critical)", "status": "CRITICAL", "impact": "-15 pts"})
        else:
            score -= 8
            factors.append({"factor": "Active Alarms", "value": f"{len(active_alarms)} alarms", "status": "WARNING", "impact": "-8 pts"})

    # 7. Overdue Maintenance penalty
    if motor.next_maintenance_date and motor.next_maintenance_date < datetime.date.today():
        days_overdue = (datetime.date.today() - motor.next_maintenance_date).days
        score -= 10
        factors.append({"factor": "Maintenance Status", "value": f"Overdue by {days_overdue} days", "status": "WARNING", "impact": "-10 pts"})

    score = max(0, min(100, score))

    if score >= 90:
        condition = "HEALTHY"
    elif score >= 75:
        condition = "GOOD"
    elif score >= 60:
        condition = "WARNING"
    elif score >= 40:
        condition = "POOR"
    else:
        condition = "CRITICAL"

    return score, condition, factors


def calculate_predictive_risk(motor: Motor, db: Session) -> Dict[str, Any]:
    """
    Statistical engineering rule-based predictive maintenance risk engine.
    Returns failure risk level (LOW, MEDIUM, HIGH, CRITICAL), risk reasons, and action recommendations.
    """
    score, condition, factors = calculate_motor_health(motor, db)
    reasons = []
    recommendations = []

    # Rule 1: High vibration trend
    latest_meas = db.query(MotorMeasurement).filter(MotorMeasurement.motor_tag == motor.tag).order_by(desc(MotorMeasurement.timestamp)).limit(10).all()
    if len(latest_meas) >= 2:
        v1 = latest_meas[0].vibration_de or 0
        v2 = latest_meas[-1].vibration_de or 0
        if v1 > v2 * 1.15 and v1 > 3.5:
            reasons.append(f"Vibration DE increased by {((v1-v2)/v2)*100:.1f}% over recent readings ({v1:.1f} mm/s)")
            recommendations.append("Perform laser shaft alignment and inspect DE bearing lubrication.")

    # Rule 2: High temperature trend
    if latest_meas and (latest_meas[0].temperature_de or 0) > 78:
        reasons.append(f"Drive End bearing operating at elevated temperature ({latest_meas[0].temperature_de:.1f}°C)")
        recommendations.append("Replenish Mobilith SHC grease and inspect cooling fan casing.")

    # Rule 3: Low insulation resistance
    latest_maint = db.query(MaintenanceLog).filter(MaintenanceLog.motor_tag == motor.tag, MaintenanceLog.megger_mohm != None).order_by(desc(MaintenanceLog.log_date)).first()
    if latest_maint and (latest_maint.megger_mohm or 100) < 15.0:
        reasons.append(f"Insulation resistance degraded to {latest_maint.megger_mohm} MΩ")
        recommendations.append("Schedule winding polarization index (PI) test and dry-out procedure.")

    # Rule 4: Overdue maintenance & alarms
    if motor.next_maintenance_date and motor.next_maintenance_date < datetime.date.today():
        reasons.append(f"Preventive maintenance overdue (due {motor.next_maintenance_date})")
        recommendations.append("Issue high-priority work order for routine maintenance inspection.")

    active_alarms = db.query(MotorAlarm).filter(MotorAlarm.motor_tag == motor.tag, MotorAlarm.cleared == False).count()
    if active_alarms > 0:
        reasons.append(f"{active_alarms} un-cleared active alarms present")

    if score < 40 or len(reasons) >= 3:
        risk_level = "CRITICAL RISK"
    elif score < 60 or len(reasons) == 2:
        risk_level = "HIGH RISK"
    elif score < 75 or len(reasons) == 1:
        risk_level = "MEDIUM RISK"
    else:
        risk_level = "LOW RISK"

    if not recommendations:
        recommendations.append("Continue routine condition monitoring per standard maintenance schedule.")

    return {
        "motor_tag": motor.tag,
        "motor_name": motor.name,
        "health_score": score,
        "condition": condition,
        "risk_level": risk_level,
        "reasons": reasons,
        "recommendations": recommendations
    }


# ==========================================
# DATABASE API CLASS ENCAPSULATION
# ==========================================

class DatabaseAPI:
    """Class encapsulation for database management and CRUD operations."""

    def __init__(self, db_url: str = None):
        if db_url is None:
            db_url = os.environ.get("DATABASE_URL")
            if not db_url:
                if os.path.exists("motor_platform.db"):
                    db_url = "sqlite:///motor_platform.db"
                else:
                    import urllib.parse
                    db_password = urllib.parse.quote_plus("sagar@1729")
                    db_url = f"mysql+pymysql://root:{db_password}@localhost:3306/motor_data"
        
        # Create database if mysql and it doesn't exist
        if db_url.startswith("mysql"):
            try:
                from sqlalchemy import text
                server_url = db_url.rsplit('/', 1)[0]
                db_name = db_url.rsplit('/', 1)[1]
                temp_engine = create_engine(server_url, isolation_level="AUTOCOMMIT")
                with temp_engine.connect() as conn:
                    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
            except Exception as e:
                logger.warning(f"MySQL connection failed ({e}). Falling back to SQLite motor_platform.db...")
                db_url = "sqlite:///motor_platform.db"

        self.db_url = db_url
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        self.engine = create_engine(db_url, connect_args=connect_args)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.init_db()

    def init_db(self):
        """Create tables if they do not exist, auto-migrate legacy schemas, and trigger seed migration."""
        try:
            # Check if legacy table exists without asset_number
            if self.db_url.startswith("sqlite") and os.path.exists("motor_platform.db"):
                with self.engine.connect() as conn:
                    result = conn.execute(text("PRAGMA table_info(motors);")).fetchall()
                    col_names = [r[1] for r in result]
                    if result and "asset_number" not in col_names:
                        logger.info("Legacy SQLite schema detected. Recreating tables for Digital Twin schema...")
                        Base.metadata.drop_all(bind=self.engine)

            Base.metadata.create_all(bind=self.engine, checkfirst=True)
        except Exception as e:
            logger.warning(f"Table creation check warning: {e}")
        self.auto_seed()

    def get_session(self) -> Session:
        """Helper to get a database session."""
        return self.SessionLocal()

    # ==========================================
    # SEEDING & MIGRATION ENGINE
    # ==========================================

    def auto_seed(self):
        """Seed initial normalized hierarchy, motors, telemetry, alarms, work orders, failures if empty."""
        db = self.get_session()
        try:
            # 1. Seed Plant & Hierarchy
            plant = db.query(Plant).first()
            if not plant:
                logger.info("Seeding normalized electrical hierarchy nodes...")
                plant = Plant(tag="PLANT-01", name="Main Industrial Complex", location="Industrial Zone, Sector 4", capacity_mw=120.0)
                db.add(plant)
                db.flush()

                # Substations
                ss1 = Substation(plant_id=plant.id, tag="SS-01", name="Main Substation-1", voltage_kv=33.0)
                ss2 = Substation(plant_id=plant.id, tag="SS-02", name="Main Substation-2", voltage_kv=33.0)
                ss3 = Substation(plant_id=plant.id, tag="SS-03", name="Utility Substation", voltage_kv=11.0)
                db.add_all([ss1, ss2, ss3])
                db.flush()

                # Transformers
                tr1 = Transformer(substation_id=ss1.id, tag="TR-01", name="33kV/415V Power Transformer 1", rating_kva=3150.0, primary_voltage=33000.0, secondary_voltage=415.0)
                tr2 = Transformer(substation_id=ss2.id, tag="TR-02", name="33kV/3.3kV Power Transformer 2", rating_kva=5000.0, primary_voltage=33000.0, secondary_voltage=3300.0)
                tr3 = Transformer(substation_id=ss3.id, tag="TR-03", name="11kV/415V Utility Transformer", rating_kva=1600.0, primary_voltage=11000.0, secondary_voltage=415.0)
                db.add_all([tr1, tr2, tr3])
                db.flush()

                # PCCs
                pcc1 = PCC(transformer_id=tr1.id, tag="PCC-1", name="PCC Panel 1", voltage=415.0, incomer="Incomer ACB-1")
                pcc2 = PCC(transformer_id=tr1.id, tag="PCC-2", name="PCC Panel 2", voltage=415.0, incomer="Incomer ACB-2")
                pcc4 = PCC(transformer_id=tr2.id, tag="PCC-4", name="PCC Panel 4 (HT)", voltage=3300.0, incomer="HT Incomer VCB-1")
                pcc5 = PCC(transformer_id=tr2.id, tag="PCC-5", name="PCC Panel 5 (HT)", voltage=3300.0, incomer="HT Incomer VCB-2")
                pcc6 = PCC(transformer_id=tr3.id, tag="PCC-6", name="PCC Panel 6 (Utility)", voltage=415.0, incomer="Utility ACB-1")
                db.add_all([pcc1, pcc2, pcc4, pcc5, pcc6])
                db.flush()

                # MCCs
                mcc1 = MCC(pcc_id=pcc1.id, tag="MCC-1", name="Coal Handling MCC-1", voltage=415.0)
                mcc2 = MCC(pcc_id=pcc1.id, tag="MCC-2", name="Boiler Area MCC-2", voltage=415.0)
                mcc3 = MCC(pcc_id=pcc2.id, tag="MCC-3", name="Utility Area MCC-3", voltage=415.0)
                mcc4 = MCC(pcc_id=pcc4.id, tag="MCC-4", name="Compressor MCC-4", voltage=415.0)
                mcc5 = MCC(pcc_id=pcc5.id, tag="MCC-5", name="WTP Plant MCC-5", voltage=3300.0)
                mcc6 = MCC(pcc_id=pcc6.id, tag="MCC-6", name="ETP Plant MCC-6", voltage=415.0)
                db.add_all([mcc1, mcc2, mcc3, mcc4, mcc5, mcc6])
                db.flush()

                # Feeders
                feeders_list = []
                for mcc in [mcc1, mcc2, mcc3, mcc4, mcc5, mcc6]:
                    for f_idx in range(1, 5):
                        f_tag = f"Feeder-{f_idx}"
                        f_node = Feeder(mcc_id=mcc.id, tag=f"{mcc.tag}-{f_tag}", name=f"{mcc.name} {f_tag}", voltage=mcc.voltage, rated_current=250.0)
                        feeders_list.append(f_node)
                db.add_all(feeders_list)
                db.commit()

            # 2. Seed Motors if empty
            count = db.query(Motor).count()
            if count == 0 and os.path.exists("sample_motors.xlsx"):
                logger.info("Database motors empty. Seeding from sample_motors.xlsx...")
                df = pd.read_excel("sample_motors.xlsx")
                for index, row in df.iterrows():
                    comm_d = pd.to_datetime(row.get("Commission Date")).date() if not pd.isna(row.get("Commission Date")) else datetime.date(2022, 1, 1)
                    last_m = pd.to_datetime(row.get("Last Maintenance Date")).date() if not pd.isna(row.get("Last Maintenance Date")) else datetime.date(2026, 1, 1)
                    next_m = pd.to_datetime(row.get("Next Maintenance Date")).date() if not pd.isna(row.get("Next Maintenance Date")) else datetime.date(2026, 7, 1)
                    is_crit = str(row.get("Is Critical")).lower() in ["yes", "true", "1", "y"]
                    crit_level = "A - Critical" if is_crit else ("B - Important" if index % 2 == 0 else "C - Normal")

                    motor = Motor(
                        tag=str(row["Motor Tag"]).strip(),
                        name=str(row["Motor Name"]).strip(),
                        area=str(row.get("Area")).strip(),
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
                        criticality=crit_level,
                        commission_date=comm_d,
                        last_maintenance_date=last_m,
                        next_maintenance_date=next_m,
                        running_hours=round(float(np.random.uniform(5000, 18000)), 1),
                        start_count=int(np.random.randint(40, 320))
                    )
                    db.add(motor)
                    db.flush()

                    # 3. Add telemetry history (24 points)
                    now = datetime.datetime.utcnow()
                    for t_idx in range(24):
                        t_stamp = now - datetime.timedelta(hours=23 - t_idx)
                        vib_de_val = 1.8 + (0.8 if motor.status == "Fault" else 0.0) + np.random.uniform(-0.3, 0.4)
                        vib_nde_val = 1.2 + (0.5 if motor.status == "Fault" else 0.0) + np.random.uniform(-0.2, 0.3)
                        temp_de_val = 62.0 + (22.0 if motor.status == "Fault" else 0.0) + np.random.uniform(-2.0, 4.0)
                        
                        meas = MotorMeasurement(
                            motor_tag=motor.tag,
                            timestamp=t_stamp,
                            voltage=motor.voltage + float(np.random.uniform(-5, 5)),
                            current=motor.current_amp * (0.85 if motor.status == "Standby" else (1.15 if motor.status == "Fault" else 0.95)),
                            active_power_kw=motor.power_kw * (0.8 if motor.status == "Running" else 0.0),
                            reactive_power_kvar=motor.power_kw * 0.3,
                            apparent_power_kva=motor.power_kw * 0.85,
                            power_factor=0.85 + np.random.uniform(-0.03, 0.03),
                            frequency=50.0 + np.random.uniform(-0.1, 0.1),
                            energy_kwh=motor.power_kw * 20.0,
                            load_percent=78.5 if motor.status == "Running" else 0.0,
                            running_hours=motor.running_hours,
                            start_count=motor.start_count,
                            vibration_de=round(vib_de_val, 2),
                            vibration_nde=round(vib_nde_val, 2),
                            temperature_de=round(temp_de_val, 1),
                            temperature_nde=round(temp_de_val - 5.0, 1),
                            winding_temperature=round(temp_de_val + 8.0, 1),
                            ambient_temperature=30.0,
                            data_source="SIMULATED"
                        )
                        db.add(meas)

                    # 4. Add Maintenance logs
                    m_types = ["Lubrication", "Insulation Test", "Alignment", "Bearing Replacement"]
                    for i, log_type in enumerate(m_types):
                        log_d = last_m - datetime.timedelta(days=i*120)
                        m_log = MaintenanceLog(
                            motor_tag=motor.tag,
                            log_date=log_d,
                            type=log_type,
                            technician="Eng. Suresh Kumar",
                            work_description=f"Routine {log_type.lower()} inspection completed per maintenance schedule.",
                            notes=f"Routine {log_type.lower()} completed.",
                            findings="All clearance tolerances within manufacturer specifications.",
                            vibration_de_mm_s=round(np.random.uniform(1.2, 2.8), 2),
                            vibration_nde_mm_s=round(np.random.uniform(0.8, 1.8), 2),
                            megger_mohm=round(np.random.uniform(50, 450), 1),
                            temperature_c=65.0
                        )
                        db.add(m_log)

                    # 5. Add Maintenance Schedules & Work Orders
                    sched = MaintenanceSchedule(
                        motor_tag=motor.tag,
                        maintenance_type="Semi-Annual PM Inspection",
                        frequency_days=180,
                        last_completed=last_m,
                        next_due=next_m,
                        assigned_technician="Eng. Suresh Kumar",
                        status="OVERDUE" if next_m < datetime.date.today() else "UP TO DATE"
                    )
                    db.add(sched)
                    db.flush()

                    if next_m < datetime.date.today() or motor.status == "Fault":
                        wo = WorkOrder(
                            schedule_id=sched.id,
                            motor_tag=motor.tag,
                            title=f"Inspect & Servicing - {motor.tag}",
                            description=f"High priority maintenance work order for {motor.name}.",
                            priority="High" if motor.status == "Fault" else "Medium",
                            state="IN PROGRESS" if motor.status == "Fault" else "OPEN",
                            assigned_technician="Eng. Rajesh V",
                            due_date=datetime.date.today() + datetime.timedelta(days=3)
                        )
                        db.add(wo)

                    # 6. Add Alarms if Fault or Moderate
                    if motor.status == "Fault" or index % 3 == 0:
                        alarm = MotorAlarm(
                            motor_tag=motor.tag,
                            parameter="Vibration DE" if index % 2 == 0 else "Winding Temperature",
                            actual_value=4.8 if index % 2 == 0 else 88.5,
                            limit_value=4.5 if index % 2 == 0 else 85.0,
                            severity="CRITICAL" if motor.status == "Fault" else "WARNING",
                            timestamp=now - datetime.timedelta(minutes=45),
                            acknowledged=False,
                            cleared=False,
                            root_cause="High mechanical load and bearing wear",
                            corrective_action="Check lubrication and balance rotor assembly"
                        )
                        db.add(alarm)

                    # 7. Add Failures
                    if motor.status == "Fault" or is_crit:
                        fail = MotorFailure(
                            motor_tag=motor.tag,
                            failure_date=datetime.date.today() - datetime.timedelta(days=45),
                            failure_mode="Bearing Failure" if index % 2 == 0 else "Overload Trip",
                            failure_type="Operational Trip",
                            root_cause="Lack of grease lubrication leading to DE bearing overheating.",
                            downtime_hours=5.5,
                            production_loss=15000.0,
                            repair_cost=4200.0,
                            corrective_action="Replaced 6312-C3 DE bearing and re-aligned coupling.",
                            technician="Eng. Suresh Kumar"
                        )
                        db.add(fail)

                    # 8. Add Energy record
                    eng = MotorEnergy(
                        motor_tag=motor.tag,
                        record_date=datetime.date.today(),
                        daily_kwh=round(motor.power_kw * 18.5, 1),
                        monthly_kwh=round(motor.power_kw * 18.5 * 30, 1),
                        yearly_kwh=round(motor.power_kw * 18.5 * 365, 1),
                        avg_load_percent=82.0 if motor.status == "Running" else 0.0,
                        running_hours=18.5 if motor.status == "Running" else 0.0,
                        estimated_cost=round(motor.power_kw * 18.5 * 0.12, 2)
                    )
                    db.add(eng)

                    # 9. Calculate initial health score
                    score, cond, _ = calculate_motor_health(motor, db)
                    motor.health_score = score
                    motor.condition_status = cond

                db.commit()
                logger.info("Auto-seeding and digital twin initial calculations complete.")

            # Seed default users
            user_count = db.query(User).count()
            if user_count == 0:
                logger.info("Seeding default RBAC user accounts...")
                default_users = [
                    User(username="admin", password_hash=generate_password_hash("admin"), full_name="System Administrator", email="admin@mototwin.com", role="Admin"),
                    User(username="engineer", password_hash=generate_password_hash("engineer"), full_name="Electrical Lead Engineer", email="engineer@mototwin.com", role="Engineer")
                ]
                for u in default_users:
                    db.add(u)
                db.commit()

        except Exception as e:
            logger.error(f"Auto-seeding error: {e}")
            db.rollback()
        finally:
            db.close()

    # ==========================================
    # HIERARCHY & TREE NAVIGATION API
    # ==========================================

    def get_tree(self) -> Dict[str, Any]:
        """Build full 7-tier normalized hierarchy tree: Plant -> Substation -> Transformer -> PCC -> MCC -> Feeder -> Motor."""
        db = self.get_session()
        try:
            motors = db.query(Motor).all()
            if not motors:
                return {"id": "plant", "label": "Plant Network (Empty)", "type": "plant", "children": []}

            tree = {
                "id": "plant",
                "label": "Main Industrial Plant",
                "type": "plant",
                "status": "Running",
                "children": []
            }

            subs = {}
            for m in motors:
                s_name = m.substation or "Main Substation-1"
                tr_name = f"TR-{(m.voltage or 415) > 1000 and '02' or '01'}"
                p_name = m.pcc or "PCC-1"
                m_name = m.mcc or "MCC-1"
                f_name = m.feeder or "Feeder-1"

                subs.setdefault(s_name, {}).setdefault(tr_name, {}).setdefault(p_name, {}).setdefault(m_name, {}).setdefault(f_name, []).append(m)

            def calc_status(node_list):
                statuses = [c["status"] for c in node_list if "status" in c]
                if "Fault" in statuses:
                    return "Fault"
                if all(s == "Standby" for s in statuses):
                    return "Standby"
                return "Running"

            sub_nodes = []
            for s_name, trs in subs.items():
                tr_nodes = []
                for tr_name, pccs in trs.items():
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
                                    "criticality": m.criticality or "B - Important",
                                    "health_score": m.health_score or 85,
                                    "condition": m.condition_status or "GOOD",
                                    "power": f"{m.power_kw} kW",
                                    "voltage": f"{m.voltage} V"
                                } for m in motor_list]

                                feeder_nodes.append({
                                    "id": f"{s_name}|{tr_name}|{p_name}|{m_name}|{f_name}",
                                    "label": f_name,
                                    "type": "feeder",
                                    "status": calc_status(m_nodes),
                                    "children": sorted(m_nodes, key=lambda x: x["id"])
                                })
                            mcc_nodes.append({
                                "id": f"{s_name}|{tr_name}|{p_name}|{m_name}",
                                "label": m_name,
                                "type": "mcc",
                                "status": calc_status(feeder_nodes),
                                "children": sorted(feeder_nodes, key=lambda x: x["label"])
                            })
                        pcc_nodes.append({
                            "id": f"{s_name}|{tr_name}|{p_name}",
                            "label": p_name,
                            "type": "pcc",
                            "status": calc_status(mcc_nodes),
                            "children": sorted(mcc_nodes, key=lambda x: x["label"])
                        })
                    tr_nodes.append({
                        "id": f"{s_name}|{tr_name}",
                        "label": tr_name,
                        "type": "transformer",
                        "status": calc_status(pcc_nodes),
                        "children": sorted(pcc_nodes, key=lambda x: x["label"])
                    })
                sub_nodes.append({
                    "id": s_name,
                    "label": s_name,
                    "type": "substation",
                    "status": calc_status(tr_nodes),
                    "children": sorted(tr_nodes, key=lambda x: x["label"])
                })

            tree["children"] = sorted(sub_nodes, key=lambda x: x["label"])
            tree["status"] = calc_status(tree["children"])
            return tree
        finally:
            db.close()

    # ==========================================
    # POWER PATH TRACE ENGINE
    # ==========================================

    def get_power_path(self, tag: str) -> Dict[str, Any]:
        """Generate full node-by-node power path trace for a motor."""
        db = self.get_session()
        try:
            motor = db.query(Motor).filter(Motor.tag == tag).first()
            if not motor:
                raise ValueError(f"Motor {tag} not found.")

            s_name = motor.substation or "Main Substation-1"
            tr_name = f"TR-{(motor.voltage or 415) > 1000 and '02' or '01'}"
            p_name = motor.pcc or "PCC-1"
            m_name = motor.mcc or "MCC-1"
            f_name = motor.feeder or "Feeder-1"

            path_nodes = [
                {"tier": "Plant", "tag": "PLANT-01", "name": "Main Industrial Plant", "status": "Running", "rating": "120 MW"},
                {"tier": "Substation", "tag": s_name, "name": f"{s_name} (33kV/11kV)", "status": "Running", "rating": "33 kV"},
                {"tier": "Transformer", "tag": tr_name, "name": f"Power Transformer ({tr_name})", "status": "Running", "rating": "3150 kVA"},
                {"tier": "PCC", "tag": p_name, "name": f"Power Control Center ({p_name})", "status": "Running", "rating": f"{motor.voltage} V / 4000A"},
                {"tier": "MCC", "tag": m_name, "name": f"Motor Control Center ({m_name})", "status": "Running", "rating": f"{motor.voltage} V / 1600A"},
                {"tier": "Feeder", "tag": f_name, "name": f"Power Feeder ({f_name})", "status": "Running", "rating": f"{motor.current_amp * 1.25:.1f} A ({motor.cable_size})"},
                {"tier": "Motor Asset", "tag": motor.tag, "name": motor.name, "status": motor.status, "rating": f"{motor.power_kw} kW / {motor.voltage} V"}
            ]

            return {
                "motor_tag": motor.tag,
                "motor_name": motor.name,
                "path_nodes": path_nodes
            }
        finally:
            db.close()

    # ==========================================
    # MOTOR CRUD & ASSET MANAGEMENT API
    # ==========================================

    def get_motors(self, search: str = None, area: str = None,
                   voltage: int = None, make: str = None, status: str = None,
                   criticality: str = None, power_min: float = None, power_max: float = None,
                   health_max: int = None) -> List[Dict[str, Any]]:
        """Query motors with multi-field search and filters."""
        db = self.get_session()
        try:
            query = db.query(Motor)
            if search:
                sf = f"%{search}%"
                query = query.filter(
                    Motor.tag.like(sf) | Motor.name.like(sf) | Motor.area.like(sf) |
                    Motor.make.like(sf) | Motor.location.like(sf) | Motor.mcc.like(sf) | Motor.feeder.like(sf)
                )
            if area:
                query = query.filter(Motor.area == area)
            if voltage:
                query = query.filter(Motor.voltage == voltage)
            if make:
                query = query.filter(Motor.make == make)
            if status:
                query = query.filter(Motor.status == status)
            if criticality:
                query = query.filter(Motor.criticality.like(f"%{criticality}%"))
            if power_min is not None:
                query = query.filter(Motor.power_kw >= power_min)
            if power_max is not None:
                query = query.filter(Motor.power_kw <= power_max)
            if health_max is not None:
                query = query.filter(Motor.health_score <= health_max)

            motors = query.all()
            # Dynamic health score refresh
            res = []
            for m in motors:
                score, cond, _ = calculate_motor_health(m, db)
                m.health_score = score
                m.condition_status = cond
                res.append(m.to_dict())
            db.commit()
            return res
        finally:
            db.close()

    def get_motor(self, tag: str) -> Optional[Dict[str, Any]]:
        """Retrieve single motor details with health score & condition."""
        db = self.get_session()
        try:
            motor = db.query(Motor).filter(Motor.tag == tag).first()
            if not motor:
                return None
            score, cond, factors = calculate_motor_health(motor, db)
            motor.health_score = score
            motor.condition_status = cond
            db.commit()

            data = motor.to_dict()
            data["health_factors"] = factors
            data["predictive_risk"] = calculate_predictive_risk(motor, db)
            return data
        finally:
            db.close()

    def add_motor(self, motor_data: Dict[str, Any], username: str = "admin") -> Dict[str, Any]:
        """Create new motor asset."""
        db = self.get_session()
        try:
            tag = str(motor_data.get("tag") or motor_data.get("motor_tag")).strip()
            existing = db.query(Motor).filter(Motor.tag == tag).first()
            if existing:
                raise ValueError(f"Motor tag '{tag}' already exists.")

            m = Motor(
                tag=tag,
                name=str(motor_data.get("name", "New Motor")).strip(),
                area=str(motor_data.get("area", "General Area")).strip(),
                service=str(motor_data.get("service", "General Drive")).strip(),
                make=str(motor_data.get("make", motor_data.get("manufacturer", "ABB"))).strip(),
                model=str(motor_data.get("model", "M3BP")).strip(),
                serial_number=str(motor_data.get("serial_number", "SN-1001")).strip(),
                power_kw=float(motor_data.get("power_kw", 45.0)),
                voltage=int(motor_data.get("voltage", 415)),
                current_amp=float(motor_data.get("current_amp", 75.0)),
                rpm=int(motor_data.get("rpm", 1475)),
                pf=float(motor_data.get("pf", 0.85)),
                efficiency=str(motor_data.get("efficiency", "94%")),
                frame_size=str(motor_data.get("frame_size", "225M")),
                bearing_de=str(motor_data.get("bearing_de", "6312-C3")),
                bearing_nde=str(motor_data.get("bearing_nde", "6212-C3")),
                lubrication_type=str(motor_data.get("lubrication_type", "Grease")),
                protection_class=str(motor_data.get("protection_class", "IP55")),
                insulation_class=str(motor_data.get("insulation_class", "Class F")),
                duty=str(motor_data.get("duty", "S1 Continuous")),
                starter_type=str(motor_data.get("starter_type", "DOL")),
                status=str(motor_data.get("status", "Running")),
                criticality=str(motor_data.get("criticality", "B - Important")),
                is_critical=str(motor_data.get("criticality", "")).startswith("A"),
                substation=str(motor_data.get("substation", "Main Substation-1")),
                pcc=str(motor_data.get("pcc", "PCC-1")),
                mcc=str(motor_data.get("mcc", "MCC-1")),
                feeder=str(motor_data.get("feeder", "Feeder-1")),
                location=str(motor_data.get("location", "Plant Area")),
                remarks=str(motor_data.get("remarks", ""))
            )
            db.add(m)
            db.flush()

            # Initial health
            score, cond, _ = calculate_motor_health(m, db)
            m.health_score = score
            m.condition_status = cond

            # Audit log
            self._log_audit(db, username, "MOTOR_CREATED", "Motor", tag, None, json.dumps(m.to_dict()))
            db.commit()
            return m.to_dict()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def update_motor(self, tag: str, motor_data: Dict[str, Any], username: str = "admin") -> Dict[str, Any]:
        """Update existing motor asset."""
        db = self.get_session()
        try:
            m = db.query(Motor).filter(Motor.tag == tag).first()
            if not m:
                raise ValueError(f"Motor {tag} not found.")

            old_val = json.dumps(m.to_dict())
            for key, val in motor_data.items():
                if hasattr(m, key) and key not in ["tag", "motor_tag"]:
                    setattr(m, key, val)

            score, cond, _ = calculate_motor_health(m, db)
            m.health_score = score
            m.condition_status = cond

            self._log_audit(db, username, "MOTOR_UPDATED", "Motor", tag, old_val, json.dumps(m.to_dict()))
            db.commit()
            return m.to_dict()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def delete_motor(self, tag: str, username: str = "admin") -> bool:
        """Delete motor asset."""
        db = self.get_session()
        try:
            m = db.query(Motor).filter(Motor.tag == tag).first()
            if not m:
                return False
            old_val = json.dumps(m.to_dict())
            db.delete(m)
            self._log_audit(db, username, "MOTOR_DELETED", "Motor", tag, old_val, None)
            db.commit()
            return True
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    # ==========================================
    # TELEMETRY & CONDITION MONITORING API
    # ==========================================

    def get_telemetry(self, tag: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get telemetry history records for a motor."""
        db = self.get_session()
        try:
            since = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
            records = db.query(MotorMeasurement).filter(
                MotorMeasurement.motor_tag == tag,
                MotorMeasurement.timestamp >= since
            ).order_by(asc(MotorMeasurement.timestamp)).all()
            return [r.to_dict() for r in records]
        finally:
            db.close()

    def add_telemetry(self, tag: str, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record real-time or simulated telemetry measurement."""
        db = self.get_session()
        try:
            m = db.query(Motor).filter(Motor.tag == tag).first()
            if not m:
                raise ValueError(f"Motor {tag} not found.")

            meas = MotorMeasurement(
                motor_tag=tag,
                timestamp=datetime.datetime.utcnow(),
                voltage=float(telemetry_data.get("voltage", m.voltage or 415)),
                current=float(telemetry_data.get("current", m.current_amp or 75)),
                active_power_kw=float(telemetry_data.get("active_power_kw", m.power_kw or 45)),
                reactive_power_kvar=float(telemetry_data.get("reactive_power_kvar", 15)),
                apparent_power_kva=float(telemetry_data.get("apparent_power_kva", 50)),
                power_factor=float(telemetry_data.get("power_factor", 0.85)),
                frequency=float(telemetry_data.get("frequency", 50.0)),
                energy_kwh=float(telemetry_data.get("energy_kwh", 450)),
                load_percent=float(telemetry_data.get("load_percent", 78.5)),
                running_hours=float(telemetry_data.get("running_hours", m.running_hours or 8500)),
                start_count=int(telemetry_data.get("start_count", m.start_count or 100)),
                vibration_de=float(telemetry_data.get("vibration_de", 1.8)),
                vibration_nde=float(telemetry_data.get("vibration_nde", 1.2)),
                temperature_de=float(telemetry_data.get("temperature_de", 65.0)),
                temperature_nde=float(telemetry_data.get("temperature_nde", 58.0)),
                winding_temperature=float(telemetry_data.get("winding_temperature", 72.0)),
                ambient_temperature=float(telemetry_data.get("ambient_temperature", 32.0)),
                vfd_frequency=telemetry_data.get("vfd_frequency"),
                vfd_output_current=telemetry_data.get("vfd_output_current"),
                vfd_temperature=telemetry_data.get("vfd_temperature"),
                vfd_status=telemetry_data.get("vfd_status"),
                data_source=telemetry_data.get("data_source", "LIVE")
            )
            db.add(meas)

            # Auto-check alarm limits
            if meas.vibration_de > 4.5 or meas.temperature_de > 85.0:
                alarm = MotorAlarm(
                    motor_tag=tag,
                    parameter="Vibration DE" if meas.vibration_de > 4.5 else "Bearing Temperature",
                    actual_value=meas.vibration_de if meas.vibration_de > 4.5 else meas.temperature_de,
                    limit_value=4.5 if meas.vibration_de > 4.5 else 85.0,
                    severity="CRITICAL" if (meas.vibration_de > 7.1 or meas.temperature_de > 95) else "WARNING",
                    timestamp=datetime.datetime.utcnow(),
                    acknowledged=False,
                    cleared=False,
                    root_cause="High operational load or mechanical stress",
                    corrective_action="Inspect bearing assembly and rotor balance"
                )
                db.add(alarm)

            # Recalculate health
            score, cond, _ = calculate_motor_health(m, db)
            m.health_score = score
            m.condition_status = cond

            db.commit()
            return meas.to_dict()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    # ==========================================
    # ALARMS & EVENTS API
    # ==========================================

    def get_alarms(self, status: str = None, severity: str = None, motor_tag: str = None) -> List[Dict[str, Any]]:
        """Fetch active or historical alarms."""
        db = self.get_session()
        try:
            query = db.query(MotorAlarm)
            if status == "active":
                query = query.filter(MotorAlarm.cleared == False)
            elif status == "unacknowledged":
                query = query.filter(MotorAlarm.acknowledged == False)
            elif status == "cleared":
                query = query.filter(MotorAlarm.cleared == True)
            if severity:
                query = query.filter(MotorAlarm.severity == severity)
            if motor_tag:
                query = query.filter(MotorAlarm.motor_tag == motor_tag)

            alarms = query.order_by(desc(MotorAlarm.timestamp)).all()
            return [a.to_dict() for a in alarms]
        finally:
            db.close()

    def acknowledge_alarm(self, alarm_id: int, username: str = "engineer") -> Dict[str, Any]:
        """Acknowledge an active alarm."""
        db = self.get_session()
        try:
            alarm = db.query(MotorAlarm).filter(MotorAlarm.id == alarm_id).first()
            if not alarm:
                raise ValueError(f"Alarm {alarm_id} not found.")
            alarm.acknowledged = True
            alarm.acknowledged_by = username
            alarm.acknowledged_at = datetime.datetime.utcnow()

            self._log_audit(db, username, "ALARM_ACKNOWLEDGED", "Alarm", str(alarm_id), None, f"Acknowledged by {username}")
            db.commit()
            return alarm.to_dict()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def clear_alarm(self, alarm_id: int, username: str = "engineer") -> Dict[str, Any]:
        """Clear an active alarm."""
        db = self.get_session()
        try:
            alarm = db.query(MotorAlarm).filter(MotorAlarm.id == alarm_id).first()
            if not alarm:
                raise ValueError(f"Alarm {alarm_id} not found.")
            alarm.cleared = True
            alarm.cleared_at = datetime.datetime.utcnow()

            self._log_audit(db, username, "ALARM_CLEARED", "Alarm", str(alarm_id), None, f"Cleared by {username}")
            db.commit()
            return alarm.to_dict()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    # ==========================================
    # MAINTENANCE & WORK ORDERS API
    # ==========================================

    def get_maintenance_history(self, tag: str) -> List[Dict[str, Any]]:
        """Get maintenance logs for a motor."""
        db = self.get_session()
        try:
            logs = db.query(MaintenanceLog).filter(MaintenanceLog.motor_tag == tag).order_by(desc(MaintenanceLog.log_date)).all()
            return [l.to_dict() for l in logs]
        finally:
            db.close()

    def add_maintenance_log(self, tag: str, log_data: Dict[str, Any], username: str = "engineer") -> Dict[str, Any]:
        """Add maintenance log for a motor."""
        db = self.get_session()
        try:
            m = db.query(Motor).filter(Motor.tag == tag).first()
            if not m:
                raise ValueError(f"Motor {tag} not found.")

            log_d = datetime.date.today()
            if log_data.get("log_date"):
                log_d = datetime.datetime.strptime(log_data["log_date"], "%Y-%m-%d").date()

            log = MaintenanceLog(
                motor_tag=tag,
                log_date=log_d,
                type=log_data.get("type", "Preventive Maintenance"),
                technician=log_data.get("technician", username),
                work_description=log_data.get("work_description", log_data.get("notes", "Routine inspection")),
                notes=log_data.get("notes", ""),
                findings=log_data.get("findings", "Normal operational state"),
                vibration_de_mm_s=log_data.get("vibration_de_mm_s"),
                vibration_nde_mm_s=log_data.get("vibration_nde_mm_s"),
                megger_mohm=log_data.get("megger_mohm"),
                temperature_c=log_data.get("temperature_c"),
                parts_replaced=log_data.get("parts_replaced"),
                root_cause=log_data.get("root_cause"),
                corrective_action=log_data.get("corrective_action")
            )
            db.add(log)
            m.last_maintenance_date = log_d
            m.next_maintenance_date = log_d + datetime.timedelta(days=180)

            # Update health
            score, cond, _ = calculate_motor_health(m, db)
            m.health_score = score
            m.condition_status = cond

            self._log_audit(db, username, "MAINTENANCE_CREATED", "MaintenanceLog", tag, None, json.dumps(log.to_dict()))
            db.commit()
            return log.to_dict()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def get_work_orders(self, state: str = None, motor_tag: str = None) -> List[Dict[str, Any]]:
        """Fetch active or historical work orders."""
        db = self.get_session()
        try:
            query = db.query(WorkOrder)
            if state:
                query = query.filter(WorkOrder.state == state)
            if motor_tag:
                query = query.filter(WorkOrder.motor_tag == motor_tag)

            wos = query.order_by(desc(WorkOrder.created_date)).all()
            return [w.to_dict() for w in wos]
        finally:
            db.close()

    def create_work_order(self, wo_data: Dict[str, Any], username: str = "engineer") -> Dict[str, Any]:
        """Create a new maintenance work order."""
        db = self.get_session()
        try:
            tag = str(wo_data.get("motor_tag")).strip()
            wo = WorkOrder(
                schedule_id=wo_data.get("schedule_id"),
                motor_tag=tag,
                title=str(wo_data.get("title", f"Work Order for {tag}")).strip(),
                description=str(wo_data.get("description", "")).strip(),
                priority=str(wo_data.get("priority", "Medium")),
                state=str(wo_data.get("state", "OPEN")),
                assigned_technician=str(wo_data.get("assigned_technician", username)),
                due_date=datetime.date.today() + datetime.timedelta(days=7)
            )
            db.add(wo)
            self._log_audit(db, username, "WORK_ORDER_CREATED", "WorkOrder", tag, None, json.dumps(wo.to_dict()))
            db.commit()
            return wo.to_dict()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def update_work_order(self, wo_id: int, wo_data: Dict[str, Any], username: str = "engineer") -> Dict[str, Any]:
        """Update work order status."""
        db = self.get_session()
        try:
            wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
            if not wo:
                raise ValueError(f"Work Order {wo_id} not found.")

            old_val = json.dumps(wo.to_dict())
            if "state" in wo_data:
                wo.state = wo_data["state"]
                if wo_data["state"] == "COMPLETED":
                    wo.completed_date = datetime.date.today()
            if "assigned_technician" in wo_data:
                wo.assigned_technician = wo_data["assigned_technician"]
            if "priority" in wo_data:
                wo.priority = wo_data["priority"]

            self._log_audit(db, username, "WORK_ORDER_UPDATED", "WorkOrder", str(wo_id), old_val, json.dumps(wo.to_dict()))
            db.commit()
            return wo.to_dict()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    # ==========================================
    # FAILURES & ENERGY API
    # ==========================================

    def get_failures(self, motor_tag: str = None) -> List[Dict[str, Any]]:
        """Get failure history events."""
        db = self.get_session()
        try:
            query = db.query(MotorFailure)
            if motor_tag:
                query = query.filter(MotorFailure.motor_tag == motor_tag)
            fails = query.order_by(desc(MotorFailure.failure_date)).all()
            return [f.to_dict() for f in fails]
        finally:
            db.close()

    def get_energy_data(self, motor_tag: str = None) -> Dict[str, Any]:
        """Get energy monitoring summary and top energy consumer rankings."""
        db = self.get_session()
        try:
            query = db.query(MotorEnergy)
            if motor_tag:
                query = query.filter(MotorEnergy.motor_tag == motor_tag)
            records = query.all()

            top_consumers = db.query(Motor).order_by(desc(Motor.power_kw)).limit(5).all()

            return {
                "total_daily_kwh": sum(r.daily_kwh for r in records),
                "total_monthly_kwh": sum(r.monthly_kwh for r in records),
                "total_yearly_kwh": sum(r.yearly_kwh for r in records),
                "records": [r.to_dict() for r in records],
                "top_consumers": [{"tag": m.tag, "name": m.name, "power_kw": m.power_kw, "daily_kwh": round(m.power_kw * 18.5, 1)} for m in top_consumers]
            }
        finally:
            db.close()

    # ==========================================
    # DASHBOARD & ANALYTICS API
    # ==========================================

    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Get comprehensive high-density dashboard summary metrics."""
        db = self.get_session()
        try:
            motors = db.query(Motor).all()
            if not motors:
                return {
                    "counts": {"motors": 0, "running": 0, "standby": 0, "fault": 0, "critical": 0, "substations": 0, "pccs": 0, "mccs": 0, "feeders": 0},
                    "avg_health_score": 100, "active_alarms_count": 0, "maintenance_overdue_count": 0, "daily_energy_kwh": 0,
                    "power_dist": [], "area_dist": [], "voltage_dist": [], "make_dist": [], "criticality_dist": [], "health_dist": []
                }

            total = len(motors)
            running = sum(1 for m in motors if m.status == "Running")
            standby = sum(1 for m in motors if m.status == "Standby")
            fault = sum(1 for m in motors if m.status == "Fault")
            crit_count = sum(1 for m in motors if (m.criticality and m.criticality.startswith("A")) or m.is_critical)

            scores = []
            for m in motors:
                score, cond, _ = calculate_motor_health(m, db)
                m.health_score = score
                m.condition_status = cond
                scores.append(score)
            db.commit()

            avg_health = int(np.mean(scores)) if scores else 100
            active_alarms = db.query(MotorAlarm).filter(MotorAlarm.cleared == False).count()
            overdue_maint = sum(1 for m in motors if m.next_maintenance_date and m.next_maintenance_date < datetime.date.today())
            total_energy = sum(m.power_kw * 18.5 for m in motors if m.status == "Running")

            subs = set(m.substation for m in motors if m.substation)
            pccs = set(f"{m.substation}|{m.pcc}" for m in motors if m.substation and m.pcc)
            mccs = set(f"{m.substation}|{m.pcc}|{m.mcc}" for m in motors if m.substation and m.pcc and m.mcc)
            feeders = set(f"{m.substation}|{m.pcc}|{m.mcc}|{m.feeder}" for m in motors if m.substation and m.pcc and m.mcc and m.feeder)

            power_ranges = {"<15 kW": 0, "15-55 kW": 0, "55-150 kW": 0, ">150 kW": 0}
            areas = {}
            voltages = {}
            makes = {}
            criticalities = {"A - Critical": 0, "B - Important": 0, "C - Normal": 0}
            health_categories = {"Healthy (90-100)": 0, "Good (75-89)": 0, "Warning (60-74)": 0, "Poor (40-59)": 0, "Critical (0-39)": 0}

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

                crit_key = m.criticality or "B - Important"
                criticalities[crit_key] = criticalities.get(crit_key, 0) + 1

                h_val = m.health_score or 85
                if h_val >= 90:
                    health_categories["Healthy (90-100)"] += 1
                elif h_val >= 75:
                    health_categories["Good (75-89)"] += 1
                elif h_val >= 60:
                    health_categories["Warning (60-74)"] += 1
                elif h_val >= 40:
                    health_categories["Poor (40-59)"] += 1
                else:
                    health_categories["Critical (0-39)"] += 1

            return {
                "counts": {
                    "motors": total,
                    "running": running,
                    "standby": standby,
                    "fault": fault,
                    "critical": crit_count,
                    "substations": len(subs),
                    "pccs": len(pccs),
                    "mccs": len(mccs),
                    "feeders": len(feeders)
                },
                "avg_health_score": avg_health,
                "active_alarms_count": active_alarms,
                "maintenance_overdue_count": overdue_maint,
                "daily_energy_kwh": round(total_energy, 1),
                "power_dist": [{"range": k, "count": v} for k, v in power_ranges.items()],
                "area_dist": [{"area": k, "count": v} for k, v in areas.items()],
                "voltage_dist": [{"voltage": k, "count": v} for k, v in voltages.items()],
                "make_dist": [{"make": k, "count": v} for k, v in makes.items()],
                "criticality_dist": [{"criticality": k, "count": v} for k, v in criticalities.items()],
                "health_dist": [{"category": k, "count": v} for k, v in health_categories.items()]
            }
        finally:
            db.close()

    # ==========================================
    # DATA QUALITY ENGINE
    # ==========================================

    def get_data_quality_report(self) -> Dict[str, Any]:
        """Perform data quality checks across all motors."""
        db = self.get_session()
        try:
            motors = db.query(Motor).all()
            total = len(motors)
            complete = 0
            incomplete = 0
            invalid = 0
            orphaned = 0
            issues = []

            for m in motors:
                has_issue = False
                if not m.substation or not m.pcc or not m.mcc or not m.feeder:
                    orphaned += 1
                    has_issue = True
                    issues.append({"tag": m.tag, "issue": "Missing electrical hierarchy link"})

                if not m.power_kw or not m.voltage or not m.current_amp:
                    invalid += 1
                    has_issue = True
                    issues.append({"tag": m.tag, "issue": "Invalid electrical nameplate parameters"})

                if not m.bearing_de or not m.make or not m.serial_number:
                    incomplete += 1
                    has_issue = True

                if not has_issue:
                    complete += 1

            return {
                "total": total,
                "complete": complete,
                "incomplete": incomplete,
                "invalid": invalid,
                "orphaned": orphaned,
                "issues": issues[:15]
            }
        finally:
            db.close()

    # ==========================================
    # AUTHENTICATION, USER & AUDIT LOG API
    # ==========================================

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        db = self.get_session()
        try:
            user = db.query(User).filter(User.username == username).first()
            return user.to_dict() if user else None
        finally:
            db.close()

    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        db = self.get_session()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user and check_password_hash(user.password_hash, password):
                return user.to_dict()
            return None
        finally:
            db.close()

    def create_user(self, username: str, password: str, full_name: str, email: str = None, role: str = "Viewer") -> Dict[str, Any]:
        db = self.get_session()
        try:
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                raise ValueError(f"Username '{username}' is already taken.")
            
            pwd_hash = generate_password_hash(password)
            new_user = User(
                username=username,
                password_hash=pwd_hash,
                full_name=full_name,
                email=email,
                role=role
            )
            db.add(new_user)
            db.commit()
            return new_user.to_dict()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        db = self.get_session()
        try:
            logs = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit).all()
            return [l.to_dict() for l in logs]
        finally:
            db.close()

    def _log_audit(self, db: Session, username: str, action: str, entity: str, entity_id: str, old_val: str = None, new_val: str = None):
        """Internal helper to insert audit event."""
        log = AuditLog(
            username=username,
            timestamp=datetime.datetime.utcnow(),
            action=action,
            entity=entity,
            entity_id=entity_id,
            old_value=old_val,
            new_value=new_val
        )
        db.add(log)

    # ==========================================
    # BACKUP & RESTORE API
    # ==========================================

    def backup_database(self) -> str:
        """Create a backup of the current database file."""
        if not self.db_url.startswith("sqlite"):
            raise NotImplementedError("Backup currently supported for SQLite engine.")
        backup_filename = f"motor_platform_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        if os.path.exists("motor_platform.db"):
            import shutil
            shutil.copy("motor_platform.db", backup_filename)
            return backup_filename
        raise FileNotFoundError("motor_platform.db file not found.")

    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup file."""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file '{backup_path}' does not exist.")
        import shutil
        shutil.copy(backup_path, "motor_platform.db")
        return True
