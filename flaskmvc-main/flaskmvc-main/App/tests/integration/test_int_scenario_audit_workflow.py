import unittest
from datetime import datetime
from App.models import Asset, Audit, AssetAssignment, Room, CheckEvent, Relocation, MissingDevice, AssetStatus, Building, Floor, Employee
from App.controllers.audit import create_audit, end_audit
from App.controllers.checkevent import create_check_event, check_event_location_discrepancy
from App.controllers.relocation import create_relocation, update_relocation
from App.database import db

class AuditWorkflowIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Database cleanup using faster sequential deletes
        db.session.query(MissingDevice).delete()
        db.session.query(Relocation).delete()
        db.session.query(CheckEvent).delete()
        db.session.query(AssetAssignment).delete()
        db.session.query(Asset).delete()
        db.session.query(Room).delete()
        db.session.query(Floor).delete()
        db.session.query(Building).delete()
        db.session.query(Employee).delete()
        db.session.query(Audit).delete()
        db.session.commit()

        # Database setup
        self.status = AssetStatus.query.filter_by(status_name="Available").first()
        if not self.status:
            self.status = AssetStatus(status_name="Available")
            db.session.add(self.status)
        
        self.building = Building(building_name="Test Building")
        db.session.add(self.building)
        db.session.flush()

        self.floor = Floor(building_id=self.building.building_id, floor_name="First")
        db.session.add(self.floor)
        db.session.flush()

        self.room1 = Room(floor_id=self.floor.floor_id, room_name="Test Room R1")
        self.room2 = Room(floor_id=self.floor.floor_id, room_name="Test Room R2")
        db.session.add(self.room1)
        db.session.add(self.room2)
        
        self.employee = Employee(first_name="John", last_name="Doe", email="john@example.com")
        db.session.add(self.employee)
        db.session.flush()

        # Create two assets
        self.asset1 = Asset(description="Asset 1", status_id=self.status.status_id)
        self.asset2 = Asset(description="Asset 2", status_id=self.status.status_id)
        db.session.add(self.asset1)
        db.session.add(self.asset2)
        db.session.flush()

        # Assign both assets to Room 1
        self.assignment1 = AssetAssignment(asset_id=self.asset1.asset_id, employee_id=self.employee.employee_id, room_id=self.room1.room_id, condition="Good")
        self.assignment2 = AssetAssignment(asset_id=self.asset2.asset_id, employee_id=self.employee.employee_id, room_id=self.room1.room_id, condition="Good")
        db.session.add(self.assignment1)
        db.session.add(self.assignment2)
        
        db.session.commit()

    def test_end_to_end_audit_workflow(self):
        # Step 1: Start Audit
        audit = create_audit(initiator_id=self.employee.employee_id)
        self.assertIsNotNone(audit)
        self.assertEqual(audit.status, "IN_PROGRESS")

        # Step 2: Scan Asset 1 correctly in Room 1
        ce1 = create_check_event(
            audit_id=audit.audit_id, 
            asset_id=self.asset1.asset_id, 
            user_id=self.employee.employee_id, 
            found_room_id=self.room1.room_id, 
            condition_id="Good", 
            status="found"
        )
        self.assertIsNotNone(ce1)
        self.assertFalse(check_event_location_discrepancy(ce1))

        # Step 3: Scan Asset 2 incorrectly in Room 2
        ce2 = create_check_event(
            audit_id=audit.audit_id, 
            asset_id=self.asset2.asset_id, 
            user_id=self.employee.employee_id, 
            found_room_id=self.room2.room_id, 
            condition_id="Good", 
            status="pending relocation"
        )
        self.assertIsNotNone(ce2)
        self.assertTrue(check_event_location_discrepancy(ce2))
        
        # System creates a relocation since it's in the wrong room
        relocation = create_relocation(ce2.check_id, self.room2.room_id)
        self.assertIsNotNone(relocation)

        # Step 4: Try to close Audit. It should fail (return None) due to pending relocation
        closed_audit_fail = end_audit()
        self.assertIsNone(closed_audit_fail)

        # Step 5: Resolve the pending relocation (relocate Asset 2 back to Room 1)
        updated_relocation = update_relocation(relocation.relocation_id, self.room1.room_id)
        self.assertIsNotNone(updated_relocation)

        # Step 6: End Audit successfully
        closed_audit_success = end_audit()
        self.assertIsNotNone(closed_audit_success)
        self.assertEqual(closed_audit_success.status, "COMPLETED")
