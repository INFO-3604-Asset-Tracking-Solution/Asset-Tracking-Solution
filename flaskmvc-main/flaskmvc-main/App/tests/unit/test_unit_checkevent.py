import unittest
from datetime import datetime
from App.models import CheckEvent

class CheckEventUnitTests(unittest.TestCase):

    def test_checkevent(self):
        ce = CheckEvent(audit_id="A1", asset_id="AST1", user_id=1, found_room_id=10, condition='Good', status='found')
        self.assertEqual(ce.audit_id, "A1")
        self.assertEqual(ce.asset_id, "AST1")
        self.assertEqual(ce.user_id, 1)
        self.assertEqual(ce.found_room_id, 10)
        self.assertEqual(ce.condition, 'Good')
        self.assertEqual(ce.status, 'found')

    def test_checkevent_enums_coverage(self):
        conditions = ['Good', 'Needs Repair', 'Beyond Repair']
        statuses = ['found', 'missing', 'relocated', 'pending relocation', 'lost']
        for cond in conditions:
            for stat in statuses:
                ce = CheckEvent(audit_id="A1", asset_id="AST1", user_id=1, found_room_id=10, 
                                condition=cond, status=stat)
                self.assertEqual(ce.condition, cond)
                self.assertEqual(ce.status, stat)

    def test_checkevent_with_custom_timestamp(self):
        ts = datetime(2025, 4, 1, 10, 30)
        ce = CheckEvent(audit_id="A1", asset_id="AST1", user_id=1, found_room_id=10, 
                        condition='Good', status='found', timestamp=ts)
        self.assertEqual(ce.timestamp, ts)


    def test_checkevent_get_json(self):
        ce = CheckEvent(audit_id="A2", asset_id="AST2", user_id=2, found_room_id=20, condition='Needs Repair', status='relocated')
        expected_json = {
            "check_id": ce.check_id,
            "audit_id": "A2",
            "asset_id": "AST2",
            "user_id": 2,
            "found_room_id": 20,
            "condition": 'Needs Repair',
            "status": 'relocated',
            "timestamp": ce.timestamp
        }
        self.assertDictEqual(ce.get_json(), expected_json)
