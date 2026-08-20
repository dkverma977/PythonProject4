import os
import sqlalchemy
from database_api import DatabaseAPI, Base, Motor

def reset_and_seed():
    print("Connecting to database...")
    db = DatabaseAPI()
    
    print("Dropping existing tables...")
    try:
        Base.metadata.drop_all(bind=db.engine)
    except Exception as e:
        print(f"Drop warning: {e}")

    print("Recreating tables with correct normalized schema...")
    Base.metadata.create_all(bind=db.engine)
    
    print("Seeding database with normalized electrical hierarchy & telemetry...")
    db.auto_seed()
    
    session = db.get_session()
    try:
        count = session.query(Motor).count()
        print(f"Success! Motor count in database: {count}")
    finally:
        session.close()

if __name__ == '__main__':
    reset_and_seed()
