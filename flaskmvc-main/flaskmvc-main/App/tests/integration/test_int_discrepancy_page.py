import unittest
from datetime import datetime

from App.database import db
from App.views.discrepancy import _build_discrepancy_rows
from App.controllers.missingdevices import mark_asset_missing
from App.controllers.relocation import create_relocation, update_relocation
from App.models import (
    Asset,
    Audit,
    AssetAssignment,
    AssetStatus,
    Building,
    CheckEvent,
    Employee,
    Floor,
    MissingDevice,
    Relocation,
    Room,
)


class DiscrepancyPageIntegrationTests(unittest.TestCase):
    def setUp(self):
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

        self.status = AssetStatus.query.filter_by(status_name="Available").first()
        if not self.status:
            self.status = AssetStatus(status_name="Available")
            db.session.add(self.status)
            db.session.flush()

        self.building = Building(building_name="HQ")
        db.session.add(self.building)
        db.session.flush()

        self.floor = Floor(building_id=self.building.building_id, floor_name="First")
        db.session.add(self.floor)
        db.session.flush()

        self.room1 = Room(floor_id=self.floor.floor_id, room_name="R1")
        self.room2 = Room(floor_id=self.floor.floor_id, room_name="R2")
        db.session.add(self.room1)
        db.session.add(self.room2)
        db.session.flush()

        self.employee = Employee(first_name="Dis", last_name="Tester", email="discrepancy@example.com")
        db.session.add(self.employee)
        db.session.flush()

        self.audit1 = Audit(initiator_id=1, start_date=datetime.utcnow(), status="IN_PROGRESS")
        self.audit2 = Audit(initiator_id=1, start_date=datetime.utcnow(), status="IN_PROGRESS")
        db.session.add(self.audit1)
        db.session.add(self.audit2)
        db.session.flush()

        self.asset1 = Asset(description="Asset A1", status_id=self.status.status_id)
        self.asset2 = Asset(description="Asset A2", status_id=self.status.status_id)
        self.asset3 = Asset(description="Asset A3", status_id=self.status.status_id)
        db.session.add(self.asset1)
        db.session.add(self.asset2)
        db.session.add(self.asset3)
        db.session.flush()

        self.assignment1 = AssetAssignment(
            asset_id=self.asset1.asset_id,
            employee_id=self.employee.employee_id,
            room_id=self.room1.room_id,
            condition="Good",
        )
        self.assignment2 = AssetAssignment(
            asset_id=self.asset2.asset_id,
            employee_id=self.employee.employee_id,
            room_id=self.room1.room_id,
            condition="Good",
        )
        self.assignment3 = AssetAssignment(
            asset_id=self.asset3.asset_id,
            employee_id=self.employee.employee_id,
            room_id=self.room1.room_id,
            condition="Good",
        )
        db.session.add(self.assignment1)
        db.session.add(self.assignment2)
        db.session.add(self.assignment3)
        db.session.commit()

    def test_build_rows_scopes_to_selected_audit(self):
        # Audit 1 missing + relocation
        mark_asset_missing(self.audit1.audit_id, self.assignment1.assignment_id)
        ce1 = CheckEvent(
            audit_id=self.audit1.audit_id,
            asset_id=self.asset2.asset_id,
            user_id=1,
            found_room_id=self.room2.room_id,
            status="pending relocation",
            condition="Good",
        )
        db.session.add(ce1)
        db.session.commit()
        create_relocation(ce1.check_id, self.room2.room_id)

        # Audit 2 missing should not appear when querying audit1
        mark_asset_missing(self.audit2.audit_id, self.assignment3.assignment_id)

        rows = _build_discrepancy_rows(self.audit1.audit_id)
        row_asset_ids = {row["asset_id"] for row in rows}

        self.assertIn(self.asset1.asset_id, row_asset_ids)
        self.assertIn(self.asset2.asset_id, row_asset_ids)
        self.assertNotIn(self.asset3.asset_id, row_asset_ids)

    def test_build_rows_sets_expected_action_flags(self):
        # Missing row
        mark_asset_missing(self.audit1.audit_id, self.assignment1.assignment_id)

        # In-review relocation row
        ce_in_review = CheckEvent(
            audit_id=self.audit1.audit_id,
            asset_id=self.asset2.asset_id,
            user_id=1,
            found_room_id=self.room2.room_id,
            status="pending relocation",
            condition="Good",
        )
        db.session.add(ce_in_review)
        db.session.commit()
        in_review_relocation = create_relocation(ce_in_review.check_id, self.room2.room_id)

        # Resolved relocation row
        ce_resolved = CheckEvent(
            audit_id=self.audit1.audit_id,
            asset_id=self.asset3.asset_id,
            user_id=1,
            found_room_id=self.room2.room_id,
            status="pending relocation",
            condition="Good",
        )
        db.session.add(ce_resolved)
        db.session.commit()
        resolved_relocation = create_relocation(ce_resolved.check_id, self.room2.room_id)
        update_relocation(resolved_relocation.relocation_id, self.room1.room_id)

        rows = _build_discrepancy_rows(self.audit1.audit_id)
        by_asset = {row["asset_id"]: row for row in rows}

        missing_row = by_asset[self.asset1.asset_id]
        self.assertEqual(missing_row["row_type"], "missing")
        self.assertTrue(missing_row["can_mark_lost"])
        self.assertFalse(missing_row["can_mark_relocated"])

        in_review_row = by_asset[self.asset2.asset_id]
        self.assertEqual(in_review_row["row_type"], "relocation")
        self.assertTrue(in_review_row["can_mark_relocated"])

        resolved_row = by_asset[self.asset3.asset_id]
        self.assertEqual(resolved_row["row_type"], "relocation")
        self.assertFalse(resolved_row["can_mark_relocated"])