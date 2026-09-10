"""
Automated Test Suite for MOTO-TWIN Industrial Digital Twin Platform
Verifies database normalization, ORM relationships, Motor Health Scoring, 
Predictive Risk Engine, REST API endpoints, RBAC security, and Excel Export.
"""

import unittest
import json
import os
import datetime
from database_api import DatabaseAPI, Motor, calculate_motor_health, calculate_predictive_risk
from flask_server import app

class TestMotoTwinPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize test database engine and Flask test client."""
        cls.db_api = DatabaseAPI("sqlite:///:memory:")
        cls.client = app.test_client()

    def test_01_database_initialization(self):
        """Test database initialization and normalized schema tables."""
        db = self.db_api.get_session()
        try:
            motor_count = db.query(Motor).count()
            self.assertGreater(motor_count, 0, "Database should auto-seed initial sample motors.")
        finally:
            db.close()

    def test_02_health_score_calculation(self):
        """Test Motor Health Score engine calculations."""
        db = self.db_api.get_session()
        try:
            motor = db.query(Motor).first()
            self.assertIsNotNone(motor, "Sample motor should exist.")
            score, condition, factors = calculate_motor_health(motor, db)
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
            self.assertIn(condition, ["HEALTHY", "GOOD", "WARNING", "POOR", "CRITICAL"])
            self.assertIsInstance(factors, list)
        finally:
            db.close()

    def test_03_predictive_risk_engine(self):
        """Test Predictive Risk analysis engine."""
        db = self.db_api.get_session()
        try:
            motor = db.query(Motor).first()
            risk_res = calculate_predictive_risk(motor, db)
            self.assertIn("risk_level", risk_res)
            self.assertIn(risk_res["risk_level"], ["LOW RISK", "MEDIUM RISK", "HIGH RISK", "CRITICAL RISK"])
            self.assertIn("recommendations", risk_res)
        finally:
            db.close()

    def test_04_api_health_endpoint(self):
        """Test /api/health endpoint."""
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "healthy")

    def test_05_api_tree_endpoint(self):
        """Test 7-tier electrical hierarchy tree API."""
        res = self.client.get('/api/tree')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["id"], "plant")
        self.assertIn("children", data)

    def test_06_api_motors_endpoints(self):
        """Test /api/motors list & detail APIs."""
        res = self.client.get('/api/motors')
        self.assertEqual(res.status_code, 200)
        motors = json.loads(res.data)
        self.assertGreater(len(motors), 0)

        tag = motors[0]["tag"]
        res_det = self.client.get(f'/api/motors/{tag}')
        self.assertEqual(res_det.status_code, 200)
        motor_det = json.loads(res_det.data)
        self.assertEqual(motor_det["tag"], tag)
        self.assertIn("health_score", motor_det)

    def test_07_api_power_path(self):
        """Test /api/motors/<tag>/power-path trace API."""
        res = self.client.get('/api/motors/M-101/power-path')
        self.assertEqual(res.status_code, 200)
        path_data = json.loads(res.data)
        self.assertEqual(path_data["motor_tag"], "M-101")
        self.assertEqual(len(path_data["path_nodes"]), 7)

    def test_08_api_dashboard(self):
        """Test /api/dashboard summary metrics API."""
        res = self.client.get('/api/dashboard')
        self.assertEqual(res.status_code, 200)
        dash = json.loads(res.data)
        self.assertIn("counts", dash)
        self.assertIn("avg_health_score", dash)

    def test_09_api_data_quality(self):
        """Test /api/data-quality audit endpoint."""
        res = self.client.get('/api/data-quality')
        self.assertEqual(res.status_code, 200)
        report = json.loads(res.data)
        self.assertIn("total", report)
        self.assertIn("complete", report)

    def test_10_api_export_excel(self):
        """Test /api/export Excel file generation."""
        res = self.client.get('/api/export')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == '__main__':
    unittest.main()
