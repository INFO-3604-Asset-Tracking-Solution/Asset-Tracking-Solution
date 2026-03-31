import unittest
from App.models import Asset

class AssetUnitTests(unittest.TestCase):
    def test_new_asset(self):
        asset = Asset("laptop", "DELL", "ISP 300", "8300164", 1, 1500.00, "Recently bought")
        self.assertEqual(asset.description, "laptop")
        self.assertEqual(asset.brand, "DELL")
        self.assertEqual(asset.model, "ISP 300")
        self.assertEqual(asset.serial_number, "8300164")
        self.assertEqual(asset.status_id, 1)
        self.assertEqual(float(asset.cost), 1500.00)
        self.assertEqual(asset.notes, "Recently bought")
        
    def test_asset_cost_boundaries(self):
        # 0 cost
        a1 = Asset("0-cost laptop", cost=0.00)
        self.assertEqual(float(a1.cost), 0.00)
        # Large cost
        a2 = Asset("expensive laptop", cost=99999999.99)
        self.assertEqual(float(a2.cost), 99999999.99)
        # Negative cost (though models might not forbid it, this should be tracked)
        a3 = Asset("negative cost computer", cost=-1.50)
        self.assertEqual(float(a3.cost), -1.50)

    def test_asset_optional_fields_missing(self):
        # Test providing only the required description
        asset = Asset("simple item")
        self.assertEqual(asset.description, "simple item")
        self.assertIsNone(asset.brand)
        self.assertIsNone(asset.model)
        self.assertIsNone(asset.serial_number)
        self.assertIsNone(asset.status_id)
        self.assertIsNone(asset.cost)
        self.assertIsNone(asset.notes)
        self.assertIsNone(asset.last_update)

    def test_asset_get_json_with_missing_fields(self):
        asset = Asset("Minimal item")
        asset_json = asset.get_json()
        self.assertEqual(asset_json['brand'], None)
        self.assertEqual(asset_json['cost'], None)
        self.assertEqual(asset_json['notes'], None)


        