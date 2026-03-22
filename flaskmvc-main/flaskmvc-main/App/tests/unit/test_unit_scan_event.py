import unittest
from App.models import ScanEvent    


class ScanEventUnitTest(unittest.TestCase):
    def test_new_scanevent(self):
        scanevent = ScanEvent("01", "01", "01", "01", "30-12-2024", "Good", "scanned successfully", "15-09-2024", "Original owner")
        self.assertEqual(scanevent.asset_id, "01")
        self.assertEqual(scanevent.user_id, "01")
        self.assertEqual(scanevent.room_id, "01")
        self.assertEqual(scanevent.scan_time, "30-12-2024")
        self.assertEqual(scanevent.status, "Good")
        self.assertEqual(scanevent.notes, "scanned successfully")
        self.assertEqual(scanevent.last_update, "15-09-2024")
        self.assertEqual(scanevent.changeLog, "Original owner")
        
    def test_get_json(self):
        scanevent = ScanEvent("01", "02", "03", "04", "30-12-2024", "Good", "scanned successfully", "15-09-2024", "Original owner")
        expected_json = {
            'scan_id: ': "01",
            'asset_id: ': "02",
            'user_id: ': "03",
            'room_id: ': "04",
            'scan_time: ': "30-12-2024",
            'status: ': "Good",
            'notes: ': "scanned successfully",
            'last_update: ': "15-09-2024",
            'change log: ': "Original owner"
        }
        self.assertDictEqual(scanevent.get_json(), expected_json)
        
        