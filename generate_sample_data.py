import os
import pandas as pd

def generate_excel():
    print("Generating sample_motors.xlsx...")
    data = [
        # Substation-1, PCC-1, MCC-1, Feeders
        {
            "Motor Tag": "M-101", "Motor Name": "Raw Coal Conveyor-1", "Area": "Coal Handling Plant", "Power": "110 kW", "Voltage": "415 V", "Current": "190 A", "RPM": 1485,
            "Efficiency": "94.5%", "Motor Make": "Siemens", "Model": "1LA8315-4AB60", "Serial Number": "S-98481A22",
            "Frame": "315M", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class F",
            "MCC": "MCC-1", "Feeder": "Feeder-1", "PCC": "PCC-1", "Substation": "Main Substation-1",
            "Incoming": "33kV Incoming-1", "Cable Size": "3C x 185 sq mm Al", "Cable Length": "120 m",
            "Location": "CHP Incline Gantry", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Primary coal transport drive. Critical equipment.", "Status": "Running",
            "Commission Date": "2022-04-12", "Last Maintenance Date": "2026-05-10", "Next Maintenance Date": "2026-11-10",
            "Is Critical": "Yes"
        },
        {
            "Motor Tag": "M-102", "Motor Name": "Coal Crusher-1 Drive", "Area": "Coal Handling Plant", "Power": "250 kW", "Voltage": "3300 V", "Current": "55 A", "RPM": 990,
            "Efficiency": "95.2%", "Motor Make": "ABB", "Model": "M3BP-355MLA", "Serial Number": "A-83921B19",
            "Frame": "355ML", "Duty": "S1 Continuous", "Protection": "IP56", "Insulation": "Class H",
            "MCC": "MCC-1", "Feeder": "Feeder-2", "PCC": "PCC-1", "Substation": "Main Substation-1",
            "Incoming": "33kV Incoming-1", "Cable Size": "3C x 95 sq mm Cu", "Cable Length": "80 m",
            "Location": "Crusher House Level 2", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "HT motor. High vibration area.", "Status": "Running",
            "Commission Date": "2022-05-01", "Last Maintenance Date": "2026-06-15", "Next Maintenance Date": "2026-12-15",
            "Is Critical": "Yes"
        },
        {
            "Motor Tag": "M-103", "Motor Name": "Vibrating Screen-1 Drive", "Area": "Coal Handling Plant", "Power": "22 kW", "Voltage": "415 V", "Current": "39 A", "RPM": 1460,
            "Efficiency": "91.8%", "Motor Make": "Siemens", "Model": "1LE1001-1DB4", "Serial Number": "S-38291C01",
            "Frame": "160L", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class F",
            "MCC": "MCC-1", "Feeder": "Feeder-3", "PCC": "PCC-1", "Substation": "Main Substation-1",
            "Incoming": "33kV Incoming-1", "Cable Size": "3C x 25 sq mm Al", "Cable Length": "150 m",
            "Location": "Crusher House Level 1", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Standard LT drive. Subject to high mechanical vibration.", "Status": "Standby",
            "Commission Date": "2022-04-15", "Last Maintenance Date": "2026-03-20", "Next Maintenance Date": "2026-09-20",
            "Is Critical": "No"
        },
        {
            "Motor Tag": "M-104", "Motor Name": "Bag Filter Fan-1", "Area": "Coal Handling Plant", "Power": "45 kW", "Voltage": "415 V", "Current": "78 A", "RPM": 1475,
            "Efficiency": "93.6%", "Motor Make": "CG Global", "Model": "GD180L", "Serial Number": "C-1293810",
            "Frame": "225M", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class F",
            "MCC": "MCC-1", "Feeder": "Feeder-4", "PCC": "PCC-1", "Substation": "Main Substation-1",
            "Incoming": "33kV Incoming-1", "Cable Size": "3C x 50 sq mm Al", "Cable Length": "110 m",
            "Location": "Bag Filter Area", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "VFD driven for speed control. Interlocked with Crusher.", "Status": "Fault",
            "Commission Date": "2022-04-18", "Last Maintenance Date": "2026-07-02", "Next Maintenance Date": "2026-08-10",
            "Is Critical": "No"
        },
        
        # Substation-1, PCC-1, MCC-2, Feeders
        {
            "Motor Tag": "M-111", "Motor Name": "Boiler Feed Pump-1A", "Area": "Boiler Area", "Power": "630 kW", "Voltage": "6600 V", "Current": "68 A", "RPM": 2980,
            "Efficiency": "96.1%", "Motor Make": "ABB", "Model": "AMI-500L2", "Serial Number": "A-72819C20",
            "Frame": "500L", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class H",
            "MCC": "MCC-2", "Feeder": "Feeder-1", "PCC": "PCC-1", "Substation": "Main Substation-1",
            "Incoming": "33kV Incoming-1", "Cable Size": "3C x 120 sq mm Cu", "Cable Length": "210 m",
            "Location": "Boiler House Pump Floor", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Ultra-critical HT pump. Subject to strict thermal monitoring.", "Status": "Running",
            "Commission Date": "2021-10-10", "Last Maintenance Date": "2026-04-12", "Next Maintenance Date": "2026-10-12",
            "Is Critical": "Yes"
        },
        {
            "Motor Tag": "M-112", "Motor Name": "Boiler Feed Pump-1B", "Area": "Boiler Area", "Power": "630 kW", "Voltage": "6600 V", "Current": "68 A", "RPM": 2980,
            "Efficiency": "96.1%", "Motor Make": "ABB", "Model": "AMI-500L2", "Serial Number": "A-72819C21",
            "Frame": "500L", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class H",
            "MCC": "MCC-2", "Feeder": "Feeder-2", "PCC": "PCC-1", "Substation": "Main Substation-1",
            "Incoming": "33kV Incoming-1", "Cable Size": "3C x 120 sq mm Cu", "Cable Length": "215 m",
            "Location": "Boiler House Pump Floor", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Standby feed pump. Ready for auto-changeover.", "Status": "Standby",
            "Commission Date": "2021-10-12", "Last Maintenance Date": "2026-03-05", "Next Maintenance Date": "2026-09-05",
            "Is Critical": "Yes"
        },
        {
            "Motor Tag": "M-113", "Motor Name": "FD Fan Drive-1", "Area": "Boiler Area", "Power": "132 kW", "Voltage": "415 V", "Current": "225 A", "RPM": 1485,
            "Efficiency": "94.8%", "Motor Make": "Siemens", "Model": "1LA8315-4AB60", "Serial Number": "S-22819C",
            "Frame": "315M", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class F",
            "MCC": "MCC-2", "Feeder": "Feeder-3", "PCC": "PCC-1", "Substation": "Main Substation-1",
            "Incoming": "33kV Incoming-1", "Cable Size": "3C x 240 sq mm Al", "Cable Length": "90 m",
            "Location": "Boiler Draft Fan Floor", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Forced Draft fan. VFD speed controller active.", "Status": "Running",
            "Commission Date": "2021-11-20", "Last Maintenance Date": "2026-06-22", "Next Maintenance Date": "2026-12-22",
            "Is Critical": "Yes"
        },
        
        # Substation-1, PCC-2, MCC-3, Feeders
        {
            "Motor Tag": "M-201", "Motor Name": "Cooling Tower Pump-1A", "Area": "Utility Area", "Power": "90 kW", "Voltage": "415 V", "Current": "155 A", "RPM": 1475,
            "Efficiency": "93.9%", "Motor Make": "CG Global", "Model": "GD250M", "Serial Number": "C-39102",
            "Frame": "280S", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class F",
            "MCC": "MCC-3", "Feeder": "Feeder-1", "PCC": "PCC-2", "Substation": "Main Substation-1",
            "Incoming": "33kV Incoming-1", "Cable Size": "3C x 185 sq mm Al", "Cable Length": "65 m",
            "Location": "Cooling Tower Basin Area", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Continuous circulation duty.", "Status": "Running",
            "Commission Date": "2022-01-15", "Last Maintenance Date": "2026-04-18", "Next Maintenance Date": "2026-10-18",
            "Is Critical": "Yes"
        },
        {
            "Motor Tag": "M-202", "Motor Name": "Cooling Tower Pump-1B", "Area": "Utility Area", "Power": "90 kW", "Voltage": "415 V", "Current": "155 A", "RPM": 1475,
            "Efficiency": "93.9%", "Motor Make": "CG Global", "Model": "GD250M", "Serial Number": "C-39103",
            "Frame": "280S", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class F",
            "MCC": "MCC-3", "Feeder": "Feeder-2", "PCC": "PCC-2", "Substation": "Main Substation-1",
            "Incoming": "33kV Incoming-1", "Cable Size": "3C x 185 sq mm Al", "Cable Length": "70 m",
            "Location": "Cooling Tower Basin Area", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Standby circulation pump.", "Status": "Standby",
            "Commission Date": "2022-01-18", "Last Maintenance Date": "2026-05-15", "Next Maintenance Date": "2026-11-15",
            "Is Critical": "Yes"
        },
        {
            "Motor Tag": "M-203", "Motor Name": "Cooling Tower Fan-1", "Area": "Utility Area", "Power": "30 kW", "Voltage": "415 V", "Current": "53 A", "RPM": 970,
            "Efficiency": "92.4%", "Motor Make": "Siemens", "Model": "1LE1001-2DB4", "Serial Number": "S-38291",
            "Frame": "200L", "Duty": "S1 Continuous", "Protection": "IP56", "Insulation": "Class F",
            "MCC": "MCC-3", "Feeder": "Feeder-3", "PCC": "PCC-2", "Substation": "Main Substation-1",
            "Incoming": "33kV Incoming-1", "Cable Size": "3C x 35 sq mm Al", "Cable Length": "85 m",
            "Location": "Cooling Tower Fan Deck", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Exhaust fan. Humidity exposed bearings.", "Status": "Running",
            "Commission Date": "2022-01-20", "Last Maintenance Date": "2026-06-10", "Next Maintenance Date": "2026-12-10",
            "Is Critical": "No"
        },

        # Substation-2, PCC-4, MCC-4, Feeders
        {
            "Motor Tag": "M-301", "Motor Name": "Compressor-1 Motor", "Area": "Utility Area", "Power": "160 kW", "Voltage": "415 V", "Current": "270 A", "RPM": 1485,
            "Efficiency": "95.0%", "Motor Make": "ABB", "Model": "M3BP-315MLA", "Serial Number": "A-9281A",
            "Frame": "315S", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class F",
            "MCC": "MCC-4", "Feeder": "Feeder-1", "PCC": "PCC-4", "Substation": "Main Substation-2",
            "Incoming": "33kV Incoming-2", "Cable Size": "3C x 300 sq mm Al", "Cable Length": "60 m",
            "Location": "Utility Compressor Room", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Star-Delta starter. Clean dry environment.", "Status": "Running",
            "Commission Date": "2023-02-15", "Last Maintenance Date": "2026-02-15", "Next Maintenance Date": "2026-08-15",
            "Is Critical": "Yes"
        },
        {
            "Motor Tag": "M-302", "Motor Name": "Compressor-2 Motor", "Area": "Utility Area", "Power": "160 kW", "Voltage": "415 V", "Current": "270 A", "RPM": 1485,
            "Efficiency": "95.0%", "Motor Make": "ABB", "Model": "M3BP-315MLA", "Serial Number": "A-9281B",
            "Frame": "315S", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class F",
            "MCC": "MCC-4", "Feeder": "Feeder-2", "PCC": "PCC-4", "Substation": "Main Substation-2",
            "Incoming": "33kV Incoming-2", "Cable Size": "3C x 300 sq mm Al", "Cable Length": "65 m",
            "Location": "Utility Compressor Room", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Standby compressor.", "Status": "Standby",
            "Commission Date": "2023-02-18", "Last Maintenance Date": "2026-01-20", "Next Maintenance Date": "2026-07-20",
            "Is Critical": "Yes"
        },
        
        # Substation-2, PCC-5, MCC-5, Feeders
        {
            "Motor Tag": "M-401", "Motor Name": "Water Intake Pump-1", "Area": "Water Treatment Plant", "Power": "200 kW", "Voltage": "3300 V", "Current": "44 A", "RPM": 1480,
            "Efficiency": "94.8%", "Motor Make": "Siemens", "Model": "1LA8315-4AB60", "Serial Number": "S-38102A",
            "Frame": "315L", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class F",
            "MCC": "MCC-5", "Feeder": "Feeder-1", "PCC": "PCC-5", "Substation": "Main Substation-2",
            "Incoming": "33kV Incoming-2", "Cable Size": "3C x 95 sq mm Al", "Cable Length": "350 m",
            "Location": "River Intake Pump House", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "High static head, remote location.", "Status": "Running",
            "Commission Date": "2023-05-10", "Last Maintenance Date": "2026-05-02", "Next Maintenance Date": "2026-11-02",
            "Is Critical": "Yes"
        },
        {
            "Motor Tag": "M-402", "Motor Name": "Sludge Agitator-1", "Area": "Water Treatment Plant", "Power": "11 kW", "Voltage": "415 V", "Current": "21 A", "RPM": 960,
            "Efficiency": "89.5%", "Motor Make": "CG Global", "Model": "GD160M", "Serial Number": "C-29381A",
            "Frame": "160M", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class F",
            "MCC": "MCC-5", "Feeder": "Feeder-2", "PCC": "PCC-5", "Substation": "Main Substation-2",
            "Incoming": "33kV Incoming-2", "Cable Size": "3C x 10 sq mm Al", "Cable Length": "80 m",
            "Location": "Clarifier Tank 1", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Geared motor. High torque application.", "Status": "Fault",
            "Commission Date": "2023-05-15", "Last Maintenance Date": "2026-04-10", "Next Maintenance Date": "2026-10-10",
            "Is Critical": "No"
        },
        {
            "Motor Tag": "M-403", "Motor Name": "Backwash Blower-1", "Area": "Water Treatment Plant", "Power": "37 kW", "Voltage": "415 V", "Current": "66 A", "RPM": 2930,
            "Efficiency": "93.0%", "Motor Make": "Siemens", "Model": "1LE1001-2AB4", "Serial Number": "S-38102B",
            "Frame": "200L", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class F",
            "MCC": "MCC-5", "Feeder": "Feeder-3", "PCC": "PCC-5", "Substation": "Main Substation-2",
            "Incoming": "33kV Incoming-2", "Cable Size": "3C x 35 sq mm Al", "Cable Length": "120 m",
            "Location": "Filter House Basement", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Used during backwash cycle only. Soft Starter equipped.", "Status": "Standby",
            "Commission Date": "2023-05-20", "Last Maintenance Date": "2026-03-12", "Next Maintenance Date": "2026-09-12",
            "Is Critical": "No"
        },

        # Utility Substation (MCC-6, Feeders)
        {
            "Motor Tag": "M-501", "Motor Name": "Wastewater Transfer Pump", "Area": "Utility Area", "Power": "15 kW", "Voltage": "415 V", "Current": "28 A", "RPM": 1440,
            "Efficiency": "90.2%", "Motor Make": "CG Global", "Model": "GD160M", "Serial Number": "C-29381B",
            "Frame": "160M", "Duty": "S1 Continuous", "Protection": "IP55", "Insulation": "Class F",
            "MCC": "MCC-6", "Feeder": "Feeder-1", "PCC": "PCC-6", "Substation": "Utility Substation",
            "Incoming": "33kV Utility Incomer", "Cable Size": "3C x 16 sq mm Al", "Cable Length": "45 m",
            "Location": "ETP Pump Area", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "ETP plant water transfer pump.", "Status": "Running",
            "Commission Date": "2024-01-10", "Last Maintenance Date": "2026-04-05", "Next Maintenance Date": "2026-10-05",
            "Is Critical": "No"
        },
        {
            "Motor Tag": "M-502", "Motor Name": "ETP Aerator Motor", "Area": "Utility Area", "Power": "22 kW", "Voltage": "415 V", "Current": "39 A", "RPM": 1450,
            "Efficiency": "91.5%", "Motor Make": "Siemens", "Model": "1LE1001-1DB4", "Serial Number": "S-9281C",
            "Frame": "180M", "Duty": "S1 Continuous", "Protection": "IP56", "Insulation": "Class F",
            "MCC": "MCC-6", "Feeder": "Feeder-2", "PCC": "PCC-6", "Substation": "Utility Substation",
            "Incoming": "33kV Utility Incomer", "Cable Size": "3C x 25 sq mm Al", "Cable Length": "50 m",
            "Location": "ETP Aeration Lagoon", "Drawing Link": "ga_motor.svg", "Image Link": "motor_photograph.svg",
            "Remarks": "Outdoor installation. High humidity exposure.", "Status": "Running",
            "Commission Date": "2024-01-12", "Last Maintenance Date": "2026-05-18", "Next Maintenance Date": "2026-11-18",
            "Is Critical": "No"
        }
    ]

    df = pd.DataFrame(data)
    df.to_excel("sample_motors.xlsx", index=False)
    print("sample_motors.xlsx successfully generated!")

def generate_svg_drawings():
    print("Generating mock SVG assets...")
    img_dir = os.path.join("static", "assets", "images")
    drw_dir = os.path.join("static", "assets", "drawings")
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(drw_dir, exist_ok=True)

    # Helper function for base SVG wrapping
    def write_file(path, content):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())

    # 1. motor_photograph.svg
    write_file(os.path.join(img_dir, "motor_photograph.svg"), '''
<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#1a1a1a"/>
  <path d="M 0 50 L 400 50 M 0 100 L 400 100 M 0 150 L 400 150 M 0 200 L 400 200 M 0 250 L 400 250 M 50 0 L 50 300 M 100 0 L 100 300 M 150 0 L 150 300 M 200 0 L 200 300 M 250 0 L 250 300 M 300 0 L 300 300 M 350 0 L 350 300" stroke="#333333" stroke-width="0.5" fill="none"/>
  <text x="200" y="35" text-anchor="middle" fill="#00ffcc" font-family="Consolas, monospace" font-size="16" font-weight="bold">MOTO-TWIN DIGITAL ASSET</text>
  <g transform="translate(100, 80)">
    <rect x="20" y="110" width="30" height="20" rx="4" fill="#555555" stroke="#777777" stroke-width="2"/>
    <rect x="150" y="110" width="30" height="20" rx="4" fill="#555555" stroke="#777777" stroke-width="2"/>
    <rect x="10" y="125" width="180" height="10" fill="#2d3436"/>
    <rect x="30" y="20" width="140" height="100" rx="20" fill="#0984e3" stroke="#74b9ff" stroke-width="3"/>
    <line x1="50" y1="20" x2="50" y2="120" stroke="#00dec5" stroke-width="3"/>
    <line x1="70" y1="20" x2="70" y2="120" stroke="#00dec5" stroke-width="3"/>
    <line x1="90" y1="20" x2="90" y2="120" stroke="#00dec5" stroke-width="3"/>
    <line x1="110" y1="20" x2="110" y2="120" stroke="#00dec5" stroke-width="3"/>
    <line x1="130" y1="20" x2="130" y2="120" stroke="#00dec5" stroke-width="3"/>
    <line x1="150" y1="20" x2="150" y2="120" stroke="#00dec5" stroke-width="3"/>
    <rect x="75" y="0" width="50" height="25" fill="#dfe6e9" stroke="#b2bec3" stroke-width="2"/>
    <circle cx="100" cy="12" r="4" fill="#2d3436"/>
    <rect x="170" y="60" width="40" height="20" fill="#b2bec3"/>
    <rect x="210" y="50" width="15" height="40" rx="2" fill="#636e72" stroke="#b2bec3" stroke-width="2"/>
    <path d="M 30 20 L 5 35 L 5 105 L 30 120 Z" fill="#2d3436" stroke="#b2bec3" stroke-width="2"/>
    <line x1="12" y1="45" x2="12" y2="95" stroke="#7f8c8d" stroke-width="2"/>
    <line x1="20" y1="40" x2="20" y2="100" stroke="#7f8c8d" stroke-width="2"/>
  </g>
  <text x="200" y="270" text-anchor="middle" fill="#888" font-family="Arial" font-size="12">Mock Photograph: 3-Phase Induction Motor (Siemens/ABB Style)</text>
</svg>
''')

    # 2. nameplate.svg
    write_file(os.path.join(img_dir, "nameplate.svg"), '''
<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#dfe6e9" stroke="#636e72" stroke-width="8"/>
  <rect x="20" y="20" width="360" height="260" fill="none" stroke="#2d3436" stroke-width="2"/>
  <text x="200" y="50" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="bold" fill="#2d3436">3~ INDUCTION MOTOR</text>
  <line x1="40" y1="65" x2="360" y2="65" stroke="#2d3436" stroke-width="2"/>
  <g font-family="Consolas, monospace" font-size="13" fill="#2d3436">
    <text x="45" y="90">MAKE: SIEMENS / ABB</text>
    <text x="220" y="90">TYPE: 3-PHASE IND.</text>
    <text x="45" y="115">IEC FRAME: 315M</text>
    <text x="220" y="115">DUTY: S1 (CONT.)</text>
    <text x="45" y="140">POWER: 110 kW (150 HP)</text>
    <text x="220" y="140">RPM: 1485 r/min</text>
    <text x="45" y="165">VOLTAGE: 415 V  Y/D</text>
    <text x="220" y="165">CURRENT: 190 A</text>
    <text x="45" y="190">FREQ: 50 Hz</text>
    <text x="220" y="190">PF: 0.86  EFF: 94.5%</text>
    <text x="45" y="215">IP CLASS: IP55</text>
    <text x="220" y="215">INSUL. CLASS: F</text>
    <text x="45" y="240">DE BRG: 6319-C3</text>
    <text x="220" y="240">NDE BRG: 6316-C3</text>
  </g>
  <circle cx="15" cy="15" r="4" fill="#7f8c8d" stroke="#2d3436"/>
  <circle cx="385" cy="15" r="4" fill="#7f8c8d" stroke="#2d3436"/>
  <circle cx="15" cy="285" r="4" fill="#7f8c8d" stroke="#2d3436"/>
  <circle cx="385" cy="285" r="4" fill="#7f8c8d" stroke="#2d3436"/>
</svg>
''')

    # 3. panel_photograph.svg
    write_file(os.path.join(img_dir, "panel_photograph.svg"), '''
<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#2c3e50"/>
  <rect x="60" y="40" width="280" height="220" fill="#34495e" stroke="#bdc3c7" stroke-width="4"/>
  <line x1="60" y1="40" x2="60" y2="260" stroke="#7f8c8d" stroke-width="6"/>
  <rect x="310" y="130" width="15" height="40" rx="3" fill="#7f8c8d" stroke="#95a5a6" stroke-width="2"/>
  <circle cx="100" cy="70" r="10" fill="#e74c3c" stroke="#2c3e50" stroke-width="2"/>
  <circle cx="130" cy="70" r="10" fill="#f1c40f" stroke="#2c3e50" stroke-width="2"/>
  <circle cx="160" cy="70" r="10" fill="#2ecc71" stroke="#2c3e50" stroke-width="2"/>
  <circle cx="230" cy="70" r="10" fill="#2ecc71" fill-opacity="0.4" stroke="#2c3e50" stroke-width="2"/>
  <circle cx="260" cy="70" r="10" fill="#e74c3c" fill-opacity="0.4" stroke="#2c3e50" stroke-width="2"/>
  <circle cx="290" cy="70" r="10" fill="#f39c12" fill-opacity="0.4" stroke="#2c3e50" stroke-width="2"/>
  <rect x="100" y="100" width="200" height="25" fill="#dfe6e9" stroke="#2d3436" stroke-width="1"/>
  <text x="200" y="117" text-anchor="middle" font-family="Arial" font-size="10" font-weight="bold" fill="#2d3436">FEEDER: M-101 (RAW COAL CONVEYOR)</text>
  <g transform="translate(180, 140)">
    <circle cx="20" cy="20" r="25" fill="#2d3436" stroke="#7f8c8d" stroke-width="3"/>
    <rect x="15" y="-5" width="10" height="35" rx="3" fill="#e74c3c" stroke="#c0392b" stroke-width="1" transform="rotate(90, 20, 20)"/>
    <text x="20" y="-12" text-anchor="middle" fill="#bdc3c7" font-family="Arial" font-size="10" font-weight="bold">ON</text>
    <text x="52" y="24" text-anchor="left" fill="#bdc3c7" font-family="Arial" font-size="10" font-weight="bold">OFF</text>
  </g>
  <rect x="100" y="200" width="110" height="40" fill="#1e272e" stroke="#7f8c8d" stroke-width="2"/>
  <text x="105" y="215" font-family="Consolas, monospace" font-size="10" fill="#0be881">I_A: 188.4 A</text>
  <text x="105" y="230" font-family="Consolas, monospace" font-size="10" fill="#0be881">F_Hz: 50.02</text>
  <circle cx="260" cy="220" r="12" fill="#27ae60" stroke="#2ecc71" stroke-width="2"/>
  <text x="260" y="238" text-anchor="middle" font-family="Arial" font-size="8" fill="#bdc3c7">START</text>
  <circle cx="300" cy="220" r="12" fill="#c0392b" stroke="#e74c3c" stroke-width="2"/>
  <text x="300" y="238" text-anchor="middle" font-family="Arial" font-size="8" fill="#bdc3c7">STOP</text>
  <text x="200" y="285" text-anchor="middle" fill="#bdc3c7" font-family="Arial" font-size="10">Mock Photograph: Electrical MCC Panel Feeder Compartment</text>
</svg>
''')

    # 4. location_photograph.svg
    write_file(os.path.join(img_dir, "location_photograph.svg"), '''
<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#2d3436"/>
  <path d="M 0 250 L 150 150 L 300 250 M 200 250 L 300 180 L 400 250" stroke="#555" stroke-width="2" fill="none"/>
  <g transform="translate(40, 100)">
    <line x1="30" y1="50" x2="30" y2="120" stroke="#7f8c8d" stroke-width="4"/>
    <line x1="160" y1="50" x2="160" y2="120" stroke="#7f8c8d" stroke-width="4"/>
    <line x1="280" y1="50" x2="280" y2="120" stroke="#7f8c8d" stroke-width="4"/>
    <circle cx="30" cy="40" r="15" fill="#b2bec3" stroke="#2d3436" stroke-width="2"/>
    <circle cx="160" cy="40" r="15" fill="#b2bec3" stroke="#2d3436" stroke-width="2"/>
    <circle cx="280" cy="40" r="15" fill="#b2bec3" stroke="#2d3436" stroke-width="2"/>
    <rect x="30" y="25" width="250" height="8" rx="4" fill="#000" stroke="#333" stroke-width="1"/>
    <rect x="30" y="47" width="250" height="8" rx="4" fill="#000" stroke="#333" stroke-width="1"/>
    <g transform="translate(240, 45)">
      <circle cx="30" cy="30" r="15" fill="none" stroke="#e74c3c" stroke-width="2">
        <animate attributeName="r" values="10;25;10" dur="2s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="1;0;1" dur="2s" repeatCount="indefinite"/>
      </circle>
      <rect x="15" y="20" width="30" height="20" fill="#0984e3" stroke="#fff" stroke-width="1.5"/>
      <circle cx="30" cy="30" r="5" fill="#e74c3c"/>
    </g>
    <path d="M 60 20 Q 75 10 90 20 Q 105 10 120 20 Q 135 10 150 20 Q 165 10 180 20" stroke="none" fill="#555"/>
  </g>
  <text x="200" y="270" text-anchor="middle" fill="#bdc3c7" font-family="Arial" font-size="12">Location Mockup: Coal Conveyor Incline Assembly</text>
</svg>
''')

    # 5. foundation_photograph.svg
    write_file(os.path.join(img_dir, "foundation_photograph.svg"), '''
<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#57606f"/>
  <polygon points="50,220 120,80 350,80 280,220" fill="#747d8c" stroke="#a4b0be" stroke-width="4"/>
  <polygon points="100,180 145,95 305,95 260,180" fill="#2f3542" stroke="#57606f" stroke-width="2"/>
  <g transform="translate(100, 180)">
    <rect x="-10" y="-15" width="20" height="15" fill="#b2bec3" stroke="#2d3436" stroke-width="1.5"/>
    <circle cx="0" cy="-15" r="8" fill="#dfe6e9" stroke="#2d3436"/>
    <line x1="0" y1="-15" x2="0" y2="-25" stroke="#b2bec3" stroke-width="4"/>
  </g>
  <g transform="translate(260, 180)">
    <rect x="-10" y="-15" width="20" height="15" fill="#b2bec3" stroke="#2d3436" stroke-width="1.5"/>
    <circle cx="0" cy="-15" r="8" fill="#dfe6e9" stroke="#2d3436"/>
    <line x1="0" y1="-15" x2="0" y2="-25" stroke="#b2bec3" stroke-width="4"/>
  </g>
  <g transform="translate(145, 95)">
    <rect x="-6" y="-10" width="12" height="10" fill="#b2bec3" stroke="#2d3436" stroke-width="1.5"/>
    <circle cx="0" cy="-10" r="5" fill="#dfe6e9" stroke="#2d3436"/>
    <line x1="0" y1="-10" x2="0" y2="-18" stroke="#b2bec3" stroke-width="3"/>
  </g>
  <g transform="translate(305, 95)">
    <rect x="-6" y="-10" width="12" height="10" fill="#b2bec3" stroke="#2d3436" stroke-width="1.5"/>
    <circle cx="0" cy="-10" r="5" fill="#dfe6e9" stroke="#2d3436"/>
    <line x1="0" y1="-10" x2="0" y2="-18" stroke="#b2bec3" stroke-width="3"/>
  </g>
  <path d="M 80 180 L 95 195 L 90 205 M 240 120 L 250 135 L 245 145" stroke="#2f3542" stroke-width="1.5" fill="none"/>
  <polygon points="98,185 143,99 307,99 262,185" fill="none" stroke="#2ed573" stroke-width="2" stroke-dasharray="4 2"/>
  <text x="200" y="270" text-anchor="middle" fill="#ced6e0" font-family="Arial" font-size="12">Foundation Detail: Anchor Bolts &amp; Epoxy Grouting</text>
</svg>
''')

    # 6. sld_substation.svg
    write_file(os.path.join(drw_dir, "sld_substation.svg"), '''
<svg width="800" height="600" viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#001e3d" stroke="#00ffff" stroke-width="4"/>
  <path d="M 0 50 L 800 50 M 0 100 L 800 100 M 0 150 L 800 150 M 0 200 L 800 200 M 0 250 L 800 250 M 0 300 L 800 300 M 0 350 L 800 350 M 0 400 L 800 400 M 0 450 L 800 450 M 0 500 L 800 500 M 0 550 L 800 550 M 50 0 L 50 600 M 100 0 L 100 600 M 150 0 L 150 600 M 200 0 L 200 600 M 250 0 L 250 600 M 300 0 L 300 600 M 350 0 L 350 600 M 400 0 L 400 600 M 450 0 L 450 600 M 500 0 L 500 600 M 550 0 L 550 600 M 600 0 L 600 600 M 650 0 L 650 600 M 700 0 L 700 600 M 750 0 L 750 600" stroke="#002d5a" stroke-width="0.5" fill="none"/>
  <rect x="15" y="15" width="770" height="570" fill="none" stroke="#00ffff" stroke-width="1.5" stroke-dasharray="10 5"/>
  <rect x="450" y="470" width="320" height="100" fill="#001e3d" stroke="#00ffff" stroke-width="2"/>
  <g font-family="Consolas, monospace" font-size="10" fill="#00ffff">
    <text x="460" y="490" font-size="14" font-weight="bold">PLANT SINGLE LINE DIAGRAM</text>
    <text x="460" y="510">SYS: 33kV / 6.6kV / 415V DISTRIBUTION</text>
    <text x="460" y="525">DRAWN BY: DIGITAL TWIN ENG.</text>
    <text x="460" y="540">DWG NO: MT-SLD-CHP-001</text>
    <text x="460" y="555">SCALE: N.T.S.   DATE: 2026-08-07</text>
  </g>
  <g stroke="#ff3f34" stroke-width="2" fill="none" transform="translate(200, 30)">
    <text x="-80" y="20" font-family="Arial" font-size="12" font-weight="bold" fill="#ff3f34">33kV GRID INCOMER</text>
    <path d="M 0 0 L 0 30 L 10 40 L -10 50 L 0 60 L 0 80" />
    <polygon points="0,80 -5,90 5,90" fill="#ff3f34"/>
    <rect x="-15" y="90" width="30" height="40" fill="#001e3d" stroke="#ff3f34" stroke-width="2"/>
    <line x1="-15" y1="90" x2="15" y2="130" />
    <text x="25" y="115" font-family="Arial" font-size="10" fill="#ff3f34">52 (SF6 CB)</text>
    <line x1="0" y1="130" x2="0" y2="170"/>
  </g>
  <g stroke="#ffd32a" stroke-width="2" fill="none" transform="translate(200, 200)">
    <circle cx="0" cy="20" r="20" stroke="#ffd32a"/>
    <circle cx="0" cy="45" r="20" stroke="#ffd32a"/>
    <text x="30" y="38" font-family="Arial" font-size="11" fill="#ffd32a">TR-1 (33/6.6kV, 5MVA)</text>
    <text x="-40" y="20" font-family="Arial" font-size="10" fill="#ffd32a">Dyn11</text>
    <line x1="0" y1="65" x2="0" y2="110"/>
  </g>
  <g transform="translate(100, 310)">
    <line x1="0" y1="0" x2="600" y2="0" stroke="#ffd32a" stroke-width="6"/>
    <text x="10" y="-10" font-family="Arial" font-size="12" font-weight="bold" fill="#ffd32a">MAIN SUBSTATION BUSBAR (6.6 kV, 50Hz)</text>
  </g>
  <g stroke="#0be881" stroke-width="2" fill="none" transform="translate(200, 310)">
    <line x1="0" y1="0" x2="0" y2="40"/>
    <rect x="-10" y="40" width="20" height="30" fill="#001e3d" stroke="#0be881"/>
    <line x1="-10" y1="40" x2="10" y2="70"/>
    <text x="15" y="60" font-family="Arial" font-size="10" fill="#0be881">HT Vacuum CB</text>
    <line x1="0" y1="70" x2="0" y2="110"/>
    <circle cx="0" cy="120" r="15" fill="#001e3d" stroke="#0be881"/>
    <text x="0" y="124" text-anchor="middle" font-family="Arial" font-size="10" font-weight="bold" fill="#0be881">M</text>
    <text x="25" y="125" font-family="Arial" font-size="11" fill="#0be881">M-102 (Coal Crusher-1, 250kW)</text>
  </g>
  <g stroke="#05c46b" stroke-width="2" fill="none" transform="translate(500, 310)">
    <line x1="0" y1="0" x2="0" y2="40"/>
    <circle cx="0" cy="60" r="18" stroke="#05c46b"/>
    <circle cx="0" cy="85" r="18" stroke="#05c46b"/>
    <text x="25" y="75" font-family="Arial" font-size="10" fill="#05c46b">TR-2 (6.6kV/415V, 1.6MVA)</text>
    <line x1="0" y1="103" x2="0" y2="130"/>
  </g>
  <g transform="translate(350, 440)">
    <line x1="0" y1="0" x2="300" y2="0" stroke="#0be881" stroke-width="4"/>
    <text x="10" y="-10" font-family="Arial" font-size="11" font-weight="bold" fill="#0be881">PCC-1 BUSBAR (415 V)</text>
  </g>
  <g stroke="#0be881" stroke-width="1.5" fill="none" transform="translate(400, 440)">
    <line x1="0" y1="0" x2="0" y2="30"/>
    <line x1="-5" y1="30" x2="5" y2="30"/>
    <line x1="0" y1="30" x2="-10" y2="50"/>
    <line x1="-5" y1="50" x2="5" y2="50"/>
    <text x="12" y="45" font-family="Arial" font-size="9" fill="#0be881">MCC-1 Incomer</text>
  </g>
</svg>
''')

    # 7. ga_motor.svg
    write_file(os.path.join(drw_dir, "ga_motor.svg"), '''
<svg width="800" height="600" viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#111" stroke="#333" stroke-width="4"/>
  <path d="M 0 50 L 800 50 M 0 100 L 800 100 M 0 150 L 800 150 M 0 200 L 800 200 M 0 250 L 800 250 M 0 300 L 800 300 M 0 350 L 800 350 M 0 400 L 800 400 M 0 450 L 800 450 M 0 500 L 800 500 M 0 550 L 800 550 M 50 0 L 50 600 M 100 0 L 100 600 M 150 0 L 150 600 M 200 0 L 200 600 M 250 0 L 250 600 M 300 0 L 300 600 M 350 0 L 350 600 M 400 0 L 400 600 M 450 0 L 450 600 M 500 0 L 500 600 M 550 0 L 550 600 M 600 0 L 600 600 M 650 0 L 650 600 M 700 0 L 700 600 M 750 0 L 750 600" stroke="#222" stroke-width="0.5" fill="none"/>
  <rect x="20" y="20" width="760" height="560" fill="none" stroke="#444" stroke-width="2"/>
  <rect x="480" y="480" width="300" height="100" fill="#111" stroke="#444" stroke-width="1.5"/>
  <g font-family="monospace" font-size="10" fill="#888">
    <text x="490" y="500" font-size="12" font-weight="bold" fill="#fff">GENERAL ARRANGEMENT DRAWING</text>
    <text x="490" y="520">FRAME: IEC 315M / 355M TYPE</text>
    <text x="490" y="535">EQUIP: 3-PHASE AC INDUCTION MOTOR</text>
    <text x="490" y="550">DRW NO: MT-GA-315M-R0</text>
    <text x="490" y="565">ALL DIMENSIONS ARE IN MM</text>
  </g>
  <g transform="translate(100, 150)" stroke="#39ff14" stroke-width="2" fill="none">
    <text x="80" y="-30" font-family="Arial" font-size="14" font-weight="bold" fill="#fff" text-anchor="middle">FRONT VIEW</text>
    <rect x="0" y="0" width="160" height="130" rx="10"/>
    <line x1="20" y1="0" x2="20" y2="130" stroke="#39ff14" stroke-width="1"/>
    <line x1="40" y1="0" x2="40" y2="130" stroke="#39ff14" stroke-width="1"/>
    <line x1="60" y1="0" x2="60" y2="130" stroke="#39ff14" stroke-width="1"/>
    <line x1="80" y1="0" x2="80" y2="130" stroke="#39ff14" stroke-width="1"/>
    <line x1="100" y1="0" x2="100" y2="130" stroke="#39ff14" stroke-width="1"/>
    <line x1="120" y1="0" x2="120" y2="130" stroke="#39ff14" stroke-width="1"/>
    <line x1="140" y1="0" x2="140" y2="130" stroke="#39ff14" stroke-width="1"/>
    <circle cx="80" cy="65" r="30" fill="#111" stroke="#39ff14" stroke-width="2"/>
    <circle cx="80" cy="65" r="8" fill="#39ff14"/>
    <rect x="76" y="35" width="8" height="12" fill="#39ff14"/>
    <rect x="-10" y="130" width="30" height="15"/>
    <rect x="140" y="130" width="30" height="15"/>
    <line x1="-30" y1="145" x2="190" y2="145" stroke="#888" stroke-width="1"/>
    <line x1="-20" y1="0" x2="-20" y2="145" stroke="#888" stroke-dasharray="3 3"/>
    <line x1="-25" y1="0" x2="-15" y2="0" stroke="#888"/>
    <line x1="-25" y1="145" x2="-15" y2="145" stroke="#888"/>
    <text x="-40" y="75" font-family="Arial" font-size="10" fill="#888" transform="rotate(-90, -40, 75)">H: 315 mm</text>
  </g>
  <g transform="translate(420, 150)" stroke="#39ff14" stroke-width="2" fill="none">
    <text x="140" y="-30" font-family="Arial" font-size="14" font-weight="bold" fill="#fff" text-anchor="middle">SIDE VIEW</text>
    <rect x="50" y="10" width="180" height="120" rx="4"/>
    <rect x="100" y="-15" width="60" height="25"/>
    <path d="M 50 10 L 10 20 L 10 120 L 50 130 Z"/>
    <rect x="230" y="50" width="60" height="40"/>
    <rect x="65" y="130" width="30" height="15"/>
    <rect x="185" y="130" width="30" height="15"/>
    <line x1="10" y1="170" x2="290" y2="170" stroke="#888"/>
    <line x1="10" y1="130" x2="10" y2="175" stroke="#888" stroke-dasharray="3 3"/>
    <line x1="290" y1="90" x2="290" y2="175" stroke="#888" stroke-dasharray="3 3"/>
    <text x="150" y="185" font-family="Arial" font-size="10" fill="#888" text-anchor="middle">L: 1180 mm</text>
  </g>
</svg>
''')

    print("SVG assets generated successfully!")

if __name__ == "__main__":
    generate_excel()
    generate_svg_drawings()
