import unittest
from App.models import AssetAssignment


class AssetAssignmentUnitTests(unittest.TestCase):

    def test_new_asset_assignment(self):
        aa = AssetAssignment(
            "AA1", "asset1", "assigned1", "F1",
            assignment_date="2025-03-07 12:00:00", return_date="2025-03-08 12:00:00"
        )
        self.assertEqual(aa.assignment_id, "AA1")
        self.assertEqual(aa.asset_id, "asset1")
        self.assertEqual(aa.assigned_to_assignee_id, "assigned1")
        self.assertEqual(aa.floor_id, "F1")
        self.assertEqual(aa.assignment_date, "2025-03-07 12:00:00")
        self.assertEqual(aa.return_date, "2025-03-08 12:00:00")

    def test_get_json(self):
        aa = AssetAssignment(
            "AA1", "asset1", "assigned1", "1st Floor",
            assignment_date="2025-03-07 12:00:00", return_date="2025-03-08 12:00:00"
        )
        expected = {
            'assignment_id': "AA1",
            'asset_id': "asset1",
            'assigned_to_assignee_id': "assigned1",
            'floor_id': "1st Floor",
            'assignment_date': "2025-03-07 12:00:00",
            'return_date': "2025-03-08 12:00:00"
        }
        self.assertEqual(aa.get_json(), expected)