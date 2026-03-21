from .user import create_user
from App.controllers.asset import *
from App.controllers.assetassignment import *
from App.controllers.assetstatus import *
from App.controllers.employee import *
from App.controllers.audit import *
from App.controllers.room import *
from App.controllers.missingdevices import *
from App.controllers.relocation import *
from App.controllers.checkevent import *
from App.controllers.notifications import *
from App.models import Employee
from datetime import datetime
from App.database import db
from sqlalchemy import inspect


def initialize():
    print("--- Running Database Initialization ---")

    # Now try dropping all tables
    try:
        print("Dropping all tables...")
        db.drop_all()

        print("Creating all tables...")
        db.create_all()

        print("Database rest complete.")
        
    except Exception as e:
        db.session.rollback()
        print(f"!!! Warning: Error during reset: {e}. Proceeding with drop_all...")
        return  # stop if create fails    

    # Add default data (user, rooms, etc.)
    try:
        print("Adding default users...")
        # Ensure this doesn't fail
        create_user('admin@gmail.com', 'Admin User', 'adminpass', 'Administrator')
        create_user('manager@gmail.com', 'Manager User', 'managerpass', 'Manager')
        create_user('auditor@gmail.com', 'Auditor User', 'auditorpass', 'Auditor')
        print("Default users added.")

        print("Adding default employees...")
        # Assuming assignee IDs are auto-incrementing integers
        create_employee ("John", "Doe", "john.doe@mail.com")
        create_employee("Jane", "Smith", "jane.smith@mail.com")        

        # ... (rest of your default data creation: rooms) ...
        # Make sure these use IDs that don't conflict if hardcoded (e.g., use strings '1', '2' if IDs are strings)
       
        print("Adding default rooms...")
        create_room( "1", "Asset Room: 101")
        create_room( "2", "Asset Room: 201")
        print("Default rooms added.")

        print("Ensuring default values...")
        ensure_defaults()
        
        print("Adding additional employees for sample data...")
        employees_created_count = 0
        
        for i in range(3, 21):
            # Check if an employee with this ID somehow already exists (unlikely after drop/create)
            if not Employee.query.get(i):
                temp_employee = create_employee(
                    first_name=f"SampleFirst{i}",
                    last_name=f"SampleLast{i}",
                    email=f"sample{i}@example.com",
                )
                if temp_employee:
                    employees_created_count += 1
                else:
                    print(f"Warning: Could not create sample employee {i}")
            else:
                print(f"Info: Employee with ID {i} already exists, skipping creation.")
        print(f"Added {employees_created_count} additional sample employees.")

        print("--- Database Initialization Finished Successfully ---")

    except Exception as e:
        db.session.rollback()
        print(f"!!!!!! ERROR during default data creation: {e}")


def ensure_defaults():
    """
    Ensures default data exists without wiping existing data.
    This is safe to run in production.
    """
    inspector = inspect(db.engine)
    
    if not (inspector.has_table('room') and inspector.has_table('user')):
        # Tables don't exist yet, so don't try to add defaults
        return
    
    # Create unknown room if it doesn't exist
    unknown_room_id = "UNKNOWN"
    unknown_room = get_room(unknown_room_id)

    if not unknown_room:
        unknown_room = create_room(unknown_room_id, "Unknown Room")
        print(f"Created unknown room: {unknown_room_id}")
    
    return {
        "room": unknown_room
    }