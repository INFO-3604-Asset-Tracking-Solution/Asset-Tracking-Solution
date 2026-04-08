import unittest
from App.models import AssetStatus
from App.controllers.assetstatus import (
    create_asset_status, get_all_asset_statuses,
    update_asset_status, delete_asset_status, get_asset_status_by_name
)
from App.database import db

class AssetStatusIntegrationTests(unittest.TestCase):
    def setUp(self):
        # We might not want to delete all if they are used by other tests, 
        # but for clean integration tests we should.
        # Note: Be careful with FK constraints if other models use these.
        # This is why we use a fresh DB or cleanup carefully.
        db.session.query(AssetStatus).delete()
        db.session.commit()

    def test_create_status(self):
        status = create_asset_status("Operational")
        self.assertIsNotNone(status)
        self.assertEqual(status.status_name, "Operational")

    def test_get_status_by_name(self):
        create_asset_status("Maintenance")
        fetched = get_asset_status_by_name("Maintenance")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.status_name, "Maintenance")

    def test_update_status(self):
        status = create_asset_status("Broken")
        updated = update_asset_status(status.status_id, "In Repair")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status_name, "In Repair")

    def test_delete_status(self):
        status = create_asset_status("Temporary")
        success = delete_asset_status(status.status_id)
        self.assertTrue(success)
        self.assertIsNone(AssetStatus.query.get(status.status_id))
