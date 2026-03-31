import unittest
from App.models import AssetStatus

class AssetStatusUnitTests(unittest.TestCase):

    def test_new_asset_status(self):
        status = AssetStatus("Functional")
        self.assertEqual(status.status_name, "Functional")

    def test_asset_status_get_json(self):
        status = AssetStatus("Broken")
        expected_json = {
            "status_id": None,
            "status_name": "Broken",
        }
        self.assertDictEqual(status.get_json(), expected_json)
