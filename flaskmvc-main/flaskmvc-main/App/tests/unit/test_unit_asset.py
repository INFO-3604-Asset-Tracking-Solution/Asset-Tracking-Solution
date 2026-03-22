import unittest
from App.models import Asset

class AssetUnitTests(unittest.TestCase):
    def test_new_asset(self):
        asset = Asset("01", "laptop", "ISP 300", "DELL", "8300164", "R2", "R2", "01", "30-01-2025", "Recently bought", "Good")
        self.assertEqual(asset.id, "01")
        self.assertEqual(asset.description, "laptop")
        self.assertEqual(asset.model, "ISP 300")
        self.assertEqual(asset.brand, "DELL")
        self.assertEqual(asset.serial_number, "8300164")
        self.assertEqual(asset.room_id, "R2")
        self.assertEqual(asset.last_located, "R2")
        self.assertEqual(asset.assignee_id, "01")
        self.assertEqual(asset.last_update, "30-01-2025")
        self.assertEqual(asset.notes, "Recently bought")
        self.assertEqual(asset.status, "Good")
        
    def test_get_json(self):
        asset = Asset("01", "laptop", "ISP 300", "DELL", "8300164", "R2", "R2", "01", "30-01-2025", "Recently bought", "Good")
        expected_json = {
            'id': "01",
            'description': "laptop",
            'model': "ISP 300",
            'brand': "DELL",
            'serial_number': "8300164",
            'room_id': "R2",
            'last_located': "R2",
            'assignee_id': "01",
            'last_update': "30-01-2025",
            'notes': "Recently bought",
            'status': "Good"
        }
        self.assertDictEqual(asset.get_json(), expected_json)
        