from .user import create_user
from App.controllers.asset import *
from App.controllers.assetassignment import *
from App.controllers.assetstatus import *
from App.controllers.employee import *
from App.controllers.audit import *
from App.controllers.room import *
from App.controllers.building import *
from App.controllers.floor import *
from App.controllers.missingdevices import *
from App.controllers.relocation import *
from App.controllers.checkevent import *
from App.controllers.notification import *
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
        user1 = create_user('admin@gmail.com', 'Admin User', 'adminpass', 'Administrator')
        user2 = create_user('manager@gmail.com', 'Manager User', 'managerpass', 'Manager')
        user3 = create_user('auditor@gmail.com', 'Auditor User', 'auditorpass', 'Auditor')
        print("Default users added.")

        print("Adding default employees...")
        # Assuming assignee IDs are auto-incrementing integers
        create_employee ("John", "Doe", "john.doe@mail.com")
        create_employee("Jane", "Smith", "jane.smith@mail.com")        

        # ... (rest of your default data creation: rooms) ...
        # Make sure these use IDs that don't conflict if hardcoded (e.g., use strings '1', '2' if IDs are strings)
        print("Adding default buildings...")
        building1 = create_building("Building A")
        building2 = create_building("Building B")
        print("Default buildings added.")

        print("Adding default floors...")
        floor1 = create_floor(building1.building_id, "Floor 1")
        floor2 = create_floor(building1.building_id, "Floor 2")
        floor3 = create_floor(building2.building_id, "Floor 1")
        floor4 = create_floor(building2.building_id, "Floor 2")
        print("Default floors added.")

        print("Adding default rooms...")
        room1 = create_room(floor1.floor_id, "Asset Room: 101")
        room2 = create_room(floor2.floor_id, "Asset Room: 201")
        room3 = create_room(floor3.floor_id, "Asset Room: 301")
        room4 = create_room(floor4.floor_id, "Asset Room: 401")
        print("Default rooms added.")

        print("Ensuring default values...")
        ensure_defaults()
        
        print("Adding default asset statuses...")
        if not get_asset_status_by_name("Good"):
            create_asset_status("Good")
        if not get_asset_status_by_name("Missing"):
            create_asset_status("Missing")
        if not get_asset_status_by_name("Misplaced"):
            create_asset_status("Misplaced")
        if not get_asset_status_by_name("Lost"):
            create_asset_status("Lost")
        print("Default asset statuses added.")

        print("Adding sample assets...")
        a1 = add_asset("Dell Latitude 5420", "Dell", "Latitude 5420", "SN-DELL-123", 1200.00, "Standard office laptop", "Good")
        a2 = add_asset("Logitech MX Master 3", "Logitech", "MX Master 3", "SN-LOGI-456", 99.00, "Ergonomic mouse", "Good")
        a3 = add_asset("HP LaserJet Pro", "HP", "LaserJet Pro M404n", "SN-HP-789", 350.00, "Department printer", "Good")
        a4 = add_asset("Samsung 27\" Monitor", "Samsung", "S27R350", "SN-SAM-321", 200.00, "Desk monitor", "Good")
        print("Sample assets added.")

        # Get room IDs 
        room1 = Room.query.first()
        room2 = Room.query.offset(1).first()

        print("Adding default audits...")
        
        audit1 = create_audit(user1.user_id) # Should be in_progress by default
        end_audit()
        
        # Manually create some completed audits for history
        audit2 = create_audit(user2.user_id)
        end_audit()
        
        audit3 = create_audit(user2.user_id)
         
        db.session.commit()
        print("Default audits added.")

        print("Adding check events for sample data...")
        if audit2 and a1 and room1:
            create_check_event(audit2.audit_id, a1.asset_id, user1.user_id, room1.room_id, "Good", "found")
        if audit2 and a2 and room1:
            create_check_event(audit2.audit_id, a2.asset_id, user1.user_id, room1.room_id, "Needs Repair", "found")
        if audit3 and a3 and room2:
            create_check_event(audit3.audit_id, a3.asset_id, user3.user_id, room2.room_id, "Good", "found")
        
        print("Adding additional employees for sample data...")
        employees_created_count = 0
        
        for i in range(3, 11):
            temp_employee = create_employee(
                first_name=f"SampleFirst{i}",
                last_name=f"SampleLast{i}",
                email=f"sample{i}@example.com",
            )
            if temp_employee:
                employees_created_count += 1
        print(f"Added {employees_created_count} additional sample employees.")

        print("Adding sample asset assignments...")
        if a1 and user1:
            create_asset_assignment(a1.asset_id, user1.user_id, room1.room_id, "Good")
        if a2 and user2:
            create_asset_assignment(a2.asset_id, user2.user_id, room1.room_id, "Good")
        if a3 and user3:
            create_asset_assignment(a3.asset_id, user3.user_id, room2.room_id, "Good")
        print("Asset assignments added.")

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
    # unknown_room_id = "UNKNOWN"
    # unknown_room = get_room(unknown_room_id)

    # if not unknown_room:
    #     unknown_room = create_room(unknown_room_id, "Unknown Room")
    #     print(f"Created unknown room: {unknown_room_id}")
    
    # return {
    #     "room": unknown_room
    # }
    return {}