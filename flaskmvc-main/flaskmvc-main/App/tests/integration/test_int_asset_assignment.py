import unittest
from App.controllers import (
    create_asset_assignment, get_asset_assignment_by_id,
    update_asset_assignment, delete_asset_assignment
)


class AssetAssignmentIntegrationTests(unittest.TestCase):
    def test_create_asset_assignment(self):
        aa = create_asset_assignment("AA1", "asset1", "assigned1", "F1")
        self.assertEqual(aa.assignment_id, "AA1")
        self.assertIsNotNone(aa.assignment_date)  
        
    def test_update_asset_assignment(self):
        create_asset_assignment(
            "AA2", "asset2", "assigned2", "F1",
            assignment_date="2025-03-07 12:00:00", return_date="2025-03-08 12:00:00"
        )
        updated = update_asset_assignment("AA2", asset_id="asset3", return_date="2025-03-09 12:00:00")
        self.assertEqual(updated.asset_id, "asset3")
        self.assertEqual(updated.return_date, "2025-03-09 12:00:00")

    def test_delete_asset_assignment(self):
        create_asset_assignment("AA3", "asset3", "assigned3", "F1")
        result = delete_asset_assignment("AA3")
        self.assertTrue(result)
        aa = get_asset_assignment_by_id("AA3")
        self.assertIsNone(aa)
        