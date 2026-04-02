import unittest
from datetime import datetime
from App.models import AssetAuthorization

class AssetAuthorizationUnitTests(unittest.TestCase):

    def test_asset_authorization_statuses(self):
        statuses = ['Pending', 'Approved', 'Rejected']
        for s in statuses:
            aa = AssetAuthorization(description="Item", proposing_user_id=1)
            # Need to manually set status as it defaults to 'Pending' in __init__
            aa.authorization_status = s
            self.assertEqual(aa.authorization_status, s)

    def test_asset_authorization_numeric_cost(self):
        # Test zero cost
        aa = AssetAuthorization(description="Item", proposing_user_id=1, cost=0.00)
        self.assertEqual(float(aa.cost), 0.00)
        # Test large cost
        aa2 = AssetAuthorization(description="Item", proposing_user_id=1, cost=999999)
        self.assertEqual(float(aa2.cost), 999999)
        # Test missing cost
        aa3 = AssetAuthorization(description="Item", proposing_user_id=1)
        self.assertIsNone(aa3.cost)


    def test_asset_authorization_get_json(self):
        aa = AssetAuthorization(description="Mouse", proposing_user_id=2, brand="Logitech", model="MX Master 3", serial_number="SN456", cost=99.99, notes="User broke previous one")
            
        expected_json = {
            "authorization_id": None,
            "description": "Mouse",
            "brand": "Logitech",
            "model": "MX Master 3",
            "serial_number": "SN456",
            "cost": 99.99,
            "notes": "User broke previous one",
            "proposing_user_id": 2,
            "proposal_date": None,
            "authorized_by": None,
            "authorization_date": None,
            "authorization_status": 'Pending'
        }
        self.assertDictEqual(aa.get_json(), expected_json)
