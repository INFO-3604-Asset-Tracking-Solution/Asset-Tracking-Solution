import unittest
from datetime import datetime
from App.models import AssetAssignment, Asset, Employee, Room, Floor, Building, AssetStatus
from App.controllers.assetassignment import (
    create_asset_assignment, get_asset_assignment_by_id,
    update_asset_assignment, delete_asset_assignment
)
from App.database import db

class AssetAssignmentIntegrationTests(unittest.TestCase):
    def setUp(self):
        db.session.query(AssetAssignment).delete()
        db.session.query(Asset).delete()
        db.session.query(Room).delete()
        db.session.query(Floor).delete()
        db.session.query(Building).delete()
        db.session.query(Employee).delete()
        db.session.commit()

        self.status = AssetStatus.query.filter_by(status_name="Available").first()
        if not self.status:
            self.status = AssetStatus(status_name="Available")
            db.session.add(self.status)

        self.building = Building(building_name="HQ")
        db.session.add(self.building)
        db.session.flush()

        self.floor = Floor(building_id=self.building.building_id, floor_name="1st")
        db.session.add(self.floor)
        db.session.flush()

        self.room = Room(floor_id=self.floor.floor_id, room_name="IT Dept")
        db.session.add(self.room)
        
        self.employee = Employee(first_name="Alice", last_name="Smith", email="alice@example.com")
        db.session.add(self.employee)
        
        self.asset = Asset(description="Laptop", status_id=self.status.status_id)
        db.session.add(self.asset)
        
        db.session.commit()

    def test_create_asset_assignment(self):
        aa = create_asset_assignment(self.asset.asset_id, self.employee.employee_id, self.room.room_id, "Good")
        self.assertIsNotNone(aa)
        self.assertIsNotNone(aa.assignment_id)
        self.assertEqual(aa.status, 'in_use')
        
    def test_update_asset_assignment(self):
        aa = create_asset_assignment(self.asset.asset_id, self.employee.employee_id, self.room.room_id, "Good")
        
        updated = update_asset_assignment(aa.assignment_id, return_date=datetime.utcnow())
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, 'returned')
        self.assertIsNotNone(updated.return_date)

    def test_delete_asset_assignment(self):
        aa = create_asset_assignment(self.asset.asset_id, self.employee.employee_id, self.room.room_id, "Good")
        result = delete_asset_assignment(aa.assignment_id)
        self.assertTrue(result)
        fetched = get_asset_assignment_by_id(aa.assignment_id)
        self.assertIsNone(fetched)