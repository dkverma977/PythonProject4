import sqlalchemy
from database_api import DatabaseAPI, Base, Motor, MaintenanceLog
import os

def reset_and_seed():
    print("Connecting to database...")
    db = DatabaseAPI()
    
    print("Dropping all existing tables in motor_data to avoid foreign key issues...")
    with db.engine.connect() as conn:
        conn.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 0;"))
        tables = conn.execute(sqlalchemy.text("SHOW TABLES;")).fetchall()
        for table in tables:
            conn.execute(sqlalchemy.text(f"DROP TABLE `{table[0]}`;"))
        conn.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 1;"))
        conn.commit()
    
    print("Recreating tables with correct schema...")
    Base.metadata.create_all(bind=db.engine)
    
    print("Generating sample excel file...")
    os.system("python generate_sample_data.py")
    
    print("Seeding database...")
    db.auto_seed()
    
    # Verify
    with db.engine.connect() as conn:
        count = conn.execute(sqlalchemy.text('SELECT COUNT(*) FROM motors')).scalar()
        print(f"Success! Motor count in database: {count}")

if __name__ == '__main__':
    reset_and_seed()
