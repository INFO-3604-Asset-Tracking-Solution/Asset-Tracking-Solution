import unittest
from datetime import datetime
from App.models import Asset, AssetStatus
from App.controllers.assetstatus import create_asset_status
from App.controllers.asset import add_asset, get_asset, get_all_assets, delete_asset, update_asset_details
from App.database import db

class AssetIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Ensure 'Available' and 'In Use' status exist before tests run
        self.status = AssetStatus.query.filter_by(status_name="Available").first()
        if not self.status:
            self.status = create_asset_status("Available")
            
        self.status_in_use = AssetStatus.query.filter_by(status_name="In Use").first()
        if not self.status_in_use:
            self.status_in_use = create_asset_status("In Use")

    def test_create_asset(self):
        description = "Test Laptop"
        model = "XPS 15"
        brand = "Dell"
        serial_number = "SN123456789"
        cost = 1500.00
        notes = "Test notes for asset"
        
        new_asset = add_asset(description, brand, model, serial_number, cost, notes, "Available")
        
        self.assertIsNotNone(new_asset)
        self.assertIsNotNone(new_asset.asset_id)
        self.assertEqual(new_asset.description, description)
        self.assertEqual(new_asset.model, model)
        self.assertEqual(new_asset.brand, brand)
        self.assertEqual(new_asset.serial_number, serial_number)
        self.assertEqual(float(new_asset.cost), cost)
        self.assertEqual(new_asset.notes, notes)
        self.assertEqual(new_asset.status_id, self.status.status_id)

    def test_update_asset(self):
        new_asset = add_asset("Old Desc", "Brand", "Model", "SN111", 500, "Notes", "Available")
        asset_id = new_asset.asset_id
        
        updated_asset = update_asset_details(asset_id, "New Desc", "Model2", "Brand2", "SN222", 600, "New Notes", "In Use")
        self.assertIsNotNone(updated_asset)
        self.assertEqual(updated_asset.description, "New Desc")
        self.assertEqual(float(updated_asset.cost), 600)
        self.assertEqual(updated_asset.status_id, self.status_in_use.status_id)
        
    def test_get_all_assets(self):
        # Clear existing
        for asset in Asset.query.all():
            db.session.delete(asset)
        db.session.commit()
        
        add_asset("Asset 1", "Brand 1", "Model 1", "SN1", 100, "Note", "Available")
        add_asset("Asset 2", "Brand 2", "Model 2", "SN2", 200, "Note", "Available")
        
        assets = get_all_assets()
        self.assertEqual(len(assets), 2)

    def test_delete_asset(self):
        new_asset = add_asset("ToDelete", "Brand", "Model", "SN3", 100, "Note", "Available")
        asset_id = new_asset.asset_id
        
        success, msg = delete_asset(asset_id)
        self.assertTrue(success)
        
        asset = get_asset(asset_id)
        self.assertIsNone(asset)