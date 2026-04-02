import unittest
from datetime import datetime
from App.models import Asset, Audit, AssetAssignment, Room, CheckEvent, Relocation, MissingDevice, AssetStatus, Building, Floor, Employee
from App.controllers.missingdevices import mark_asset_missing, mark_asset_found, mark_asset_lost
from App.controllers.relocation import create_relocation, update_relocation
from App.database import db

class DiscrepancyCRUDIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Database cleanup
        for md in MissingDevice.query.all(): db.session.delete(md)
        for rel in Relocation.query.all(): db.session.delete(rel)
        for ce in CheckEvent.query.all(): db.session.delete(ce)
        for aa in AssetAssignment.query.all(): db.session.delete(aa)
        for a in Asset.query.all(): db.session.delete(a)
        for r in Room.query.all(): db.session.delete(r)
        for f in Floor.query.all(): db.session.delete(f)
        for b in Building.query.all(): db.session.delete(b)
        for e in Employee.query.all(): db.session.delete(e)
        for au in Audit.query.all(): db.session.delete(au)
        db.session.commit()

        # Database setup
        self.status = AssetStatus.query.filter_by(status_name="Available").first()
        if not self.status:
            self.status = AssetStatus(status_name="Available")
            db.session.add(self.status)

        self.lost_status = AssetStatus.query.filter_by(status_name="Lost").first()
        if not self.lost_status:
            self.lost_status = AssetStatus(status_name="Lost")
            db.session.add(self.lost_status)
        
        self.building = Building(building_name="Test Building")
        db.session.add(self.building)
        db.session.flush()

        self.floor = Floor(building_id=self.building.building_id, floor_name="First")
        db.session.add(self.floor)
        db.session.flush()

        self.room = Room(floor_id=self.floor.floor_id, room_name="Test Room R1")
        self.room2 = Room(floor_id=self.floor.floor_id, room_name="Test Room R2")
        db.session.add(self.room)
        db.session.add(self.room2)
        
        self.employee = Employee(first_name="John", last_name="Doe", email="john@example.com")
        db.session.add(self.employee)
        db.session.flush()

        self.asset = Asset(description="Discrepancy test item", status_id=self.status.status_id)
        db.session.add(self.asset)
        db.session.flush()

        self.assignment = AssetAssignment(
            asset_id=self.asset.asset_id, 
            employee_id=self.employee.employee_id, 
            room_id=self.room.room_id, 
            condition="Good"
        )
        db.session.add(self.assignment)
        
        self.audit = Audit(initiator_id=1, start_date=datetime.utcnow(), status="IN_PROGRESS")
        db.session.add(self.audit)
        
        db.session.commit()

    def test_mark_asset_missing(self):
        missing = mark_asset_missing(self.audit.audit_id, self.assignment.assignment_id)
        self.assertIsNotNone(missing)
        self.assertEqual(missing.audit_id, self.audit.audit_id)
        self.assertEqual(missing.assignment_id, self.assignment.assignment_id)
        
    def test_mark_asset_lost(self):
        missing = mark_asset_missing(self.audit.audit_id, self.assignment.assignment_id)
        lost_device = mark_asset_lost(missing.missing_id)
        
        self.assertIsNotNone(lost_device)
        
        # Assignment should be ended
        assignment = AssetAssignment.query.get(self.assignment.assignment_id)
        self.assertEqual(assignment.status, 'returned')
        self.assertIsNotNone(assignment.return_date)
        
        # Asset status should be lost
        asset = Asset.query.get(self.asset.asset_id)
        self.assertEqual(asset.status_id, self.lost_status.status_id)

    def test_relocation_crud(self):
        # Create a check event to base the relocation on
        ce = CheckEvent(
            audit_id=self.audit.audit_id,
            asset_id=self.asset.asset_id,
            user_id=1,
            found_room_id=self.room2.room_id,
            status='pending relocation',
            condition='Good'
        )
        db.session.add(ce)
        db.session.commit()

        # Create Relocation
        relocation = create_relocation(ce.check_id, self.room2.room_id)
        self.assertIsNotNone(relocation)
        self.assertEqual(relocation.check_id, ce.check_id)
        self.assertEqual(relocation.found_in_id, self.room2.room_id)

        # Update Relocation
        updated_rel = update_relocation(relocation.relocation_id, self.room.room_id)
        self.assertIsNotNone(updated_rel)
        
        # Check if the new check event was created with "relocated"
        new_ce = CheckEvent.query.get(updated_rel.new_check_event_id)
        self.assertIsNotNone(new_ce)
        self.assertEqual(new_ce.found_room_id, self.room.room_id)
        self.assertEqual(new_ce.status, 'relocated')

    def test_mark_asset_found(self):
        missing = mark_asset_missing(self.audit.audit_id, self.assignment.assignment_id)
        
        ce = CheckEvent(
            audit_id=self.audit.audit_id,
            asset_id=self.asset.asset_id,
            user_id=1,
            found_room_id=self.room2.room_id,
            status='pending relocation',
            condition='Good'
        )
        db.session.add(ce)
        db.session.commit()
        
        relocation = create_relocation(ce.check_id, self.room2.room_id)
        
        found = mark_asset_found(missing.missing_id, relocation.relocation_id)
        self.assertIsNotNone(found)
        self.assertEqual(found.found_relocation_id, relocation.relocation_id)
