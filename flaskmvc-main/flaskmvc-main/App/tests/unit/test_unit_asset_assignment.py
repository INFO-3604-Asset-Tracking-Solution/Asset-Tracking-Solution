import unittest
from datetime import datetime
from App.models import AssetAssignment

class AssetAssignmentUnitTests(unittest.TestCase):

    def test_new_asset_assignment(self):
        start = datetime(2025, 3, 7, 12, 0, 0)
        end = datetime(2025, 3, 8, 12, 0, 0)
        aa = AssetAssignment(
            asset_id="AST1", employee_id=1, room_id=101, condition="Good",
            assignment_date=start, return_date=end
        )
        self.assertEqual(aa.asset_id, "AST1")
        self.assertEqual(aa.employee_id, 1)
        self.assertEqual(aa.room_id, 101)
        self.assertEqual(aa.condition, "Good")
        self.assertEqual(aa.assignment_date, start)
        self.assertEqual(aa.return_date, end)
        self.assertEqual(aa.status, 'returned')

    def test_asset_assignment_conditions(self):
        conditions = ['Good', 'Needs Repair', 'Beyond Repair']
        for cond in conditions:
            aa = AssetAssignment(asset_id="AST1", employee_id=1, room_id=101, condition=cond)
            self.assertEqual(aa.condition, cond)

    def test_assignment_auto_status_logic(self):
        # Case 1: Active assignment (no return_date)
        aa_active = AssetAssignment(asset_id="AST1", employee_id=1, room_id=101, condition="Good")
        self.assertEqual(aa_active.status, 'in_use')
        # Case 2: Returned assignment (return_date provided)
        aa_returned = AssetAssignment(asset_id="AST1", employee_id=1, room_id=101, condition="Good", 
                                      return_date=datetime.utcnow())
        self.assertEqual(aa_returned.status, 'returned')

    def test_assignment_with_custom_dates(self):
        # Test providing custom assignment_date
        past_date = datetime(2025, 1, 1)
        aa = AssetAssignment(asset_id="AST1", employee_id=1, room_id=101, condition="Good", 
                             assignment_date=past_date)
        self.assertEqual(aa.assignment_date, past_date)
