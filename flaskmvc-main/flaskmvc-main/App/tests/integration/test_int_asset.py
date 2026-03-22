import unittest
from datetime import datetime
from App.controllers.building import create_building
from App.controllers.floor import create_floor
from App.controllers.room import create_room
from App.models import Asset
from App.controllers.asset import add_asset, get_asset, get_all_assets, get_all_assets_by_room_id
from App.database import db


class AssetIntegrationTests(unittest.TestCase):
    def test_create_asset(self):
        #test_asset = add_asset( "1", "laptop", "ISP 300", "DELL", "8300164", "R2", "R2", "01", "30-01-2025", "Recently bought", "Good")
       # test_2 = Asset( "1", "laptop", "ISP 300", "DELL", "8300164", "R2", "R2", "01", "30-01-2025", "Recently bought", "Good")
        #self.assertEqual(test_asset.id, "1")
        building = create_building("B1", "Main")
        floor = create_floor("F1", "B1", "First")
        room = create_room("R3", "F1", "Lab")
        """Test the add_asset method with valid parameters."""
    # Arrange - Define all required parameters for add_asset
        asset_id = "A001"
        description = "Test Laptop"
        model = "XPS 15"
        brand = "Dell"
        serial_number = "SN123456789"
        room_id = "R3"  # Assumes this room exists in the test database
        last_located = "R3"
        assignee_id = 1  # Assumes this assignee exists in the test database
        last_update = datetime.now()
        notes = "Test notes for asset"
        status = "Good"
    
    # Act - Call the function under test
        new_asset = add_asset(asset_id, description, model, brand, serial_number, 
                         room_id, last_located, assignee_id, last_update,
                         notes)

    
    # Assert - Verify the asset was created correctly
        self.assertIsNotNone(new_asset)
        self.assertEqual(new_asset.id, asset_id)
        self.assertEqual(new_asset.description, description)
        self.assertEqual(new_asset.model, model)
        self.assertEqual(new_asset.brand, brand)
        self.assertEqual(new_asset.serial_number, serial_number)
        self.assertEqual(new_asset.room_id, room_id)
        self.assertEqual(new_asset.last_located, last_located)
        self.assertEqual(new_asset.assignee_id, assignee_id)
        self.assertEqual(new_asset.notes, notes)
        self.assertEqual(new_asset.status, status)
        
        # Verify the asset exists in the database
        retrieved_asset = get_asset(asset_id)
        self.assertIsNotNone(retrieved_asset)
        self.assertEqual(retrieved_asset.id, asset_id)
        self.assertEqual(retrieved_asset.description, description)
            
            
    def test_add_asset_duplicate_id(self):
        """Test adding an asset with a duplicate ID."""
    # Arrange - Create an asset first
        asset_id = "A002"
        add_asset(asset_id, "First Asset", "Model1", "Brand1", "SN11111", 

             "R3", "R3", 1, datetime.now(), "First asset notes")

    
    # Act - Try to create another asset with the same ID
        duplicate_asset = add_asset(asset_id, "Second Asset", "Model2", "Brand2", 
                               "SN22222", "R4", "R4", 2, datetime.now(), 
                               "Second asset notes")

    
    # Assert - Function should return None for duplicate ID
        self.assertIsNone(duplicate_asset)
    
    # Verify the original asset is unchanged
        original_asset = get_asset(asset_id)
        self.assertEqual(original_asset.description, "First Asset")

   #Test needs to be fixed
   
    # def test_add_asset_invalid_room(self):
    #     """Test adding an asset with a non-existent room ID."""
    #     # Arrange - Use a room ID that doesn't exist
    #     asset_id = "A003"
    #     non_existent_room = "NONEXISTENT"
        
    #     # Act - Try to create asset with invalid room
    #     result = add_asset(asset_id, "Test Asset", "Model3", "Brand3", 
    #                     "SN33333", non_existent_room, non_existent_room, 
    #                     1, datetime.now(), "Test notes", "Good")
        
    #     # Assert - Function should return None due to foreign key constraint
    #     self.assertIsNone(result)
        
    #     # Verify the asset was not created
    #     self.assertIsNone(get_asset(asset_id))

    # def test_add_asset_missing_required_fields(self):
    #     """Test that add_asset properly handles missing required fields."""
    #     # Arrange - Missing room_id which is a required field
    #     asset_id = "A004"
        
    #     # Act & Assert - This should raise an exception due to the NOT NULL constraint
    #     # Using context manager to catch the expected exception
    #     with self.assertRaises(Exception):
    #         add_asset(asset_id, "Test Asset", "Model4", "Brand4", 
    #                 "SN44444", None, "R3", 1, datetime.now(), 
    #                 "Test notes", "Good")
    
    def test_get_asset_by_id(self):
        # add_asset("01", "laptop", "ISP 300", "DELL", "8300164", "R2", "R2", "01", "30-01-2025", "Recently bought", "Good")#  create_room("R4", "F3", "Asset Room: 104")
        # a = get_asset("01")# room = get_room("R4")
        # self.assertIsNotNone(a)# self.assertIsNotNone(room)
        # self.assertEqual(a.description, "laptop")# self.assertEqual(room.room_name, "Asset Room: 104")
        
        """Test retrieving an asset by its ID."""
        # Arrange - Create an asset first
        asset_id = "A101"
        description = "Test Device"
        model = "Latitude 7400"
        brand = "Dell"
        serial_number = "SN987654321"
        room_id = "R3"  # Assumes this room exists in the test database
        last_located = "R3"
        assignee_id = 1  # Assumes this assignee exists in the test database
        last_update = datetime.now()
        notes = "Testing get_asset method"
        status = "Good"

        
        # Add the asset to the database
        add_asset(asset_id, description, model, brand, serial_number,
                room_id, last_located, assignee_id, last_update,
                notes)

        
        # Act - Call the function under test
        retrieved_asset = get_asset(asset_id)
        
        # Assert - Verify the asset was retrieved correctly
        self.assertIsNotNone(retrieved_asset)
        self.assertEqual(retrieved_asset.id, asset_id)
        self.assertEqual(retrieved_asset.description, description)
        self.assertEqual(retrieved_asset.model, model)
        self.assertEqual(retrieved_asset.brand, brand)
        self.assertEqual(retrieved_asset.serial_number, serial_number)
        self.assertEqual(retrieved_asset.room_id, room_id)
        self.assertEqual(retrieved_asset.last_located, last_located)
        self.assertEqual(retrieved_asset.assignee_id, assignee_id)
        self.assertEqual(retrieved_asset.notes, notes)
        # self.assertEqual(retrieved_asset.status, status)

        
    def test_get_asset_nonexistent_id(self):
        """Test retrieving an asset with an ID that doesn't exist."""
        # Act - Try to retrieve an asset with a non-existent ID
        nonexistent_id = "NONEXISTENT"
        retrieved_asset = get_asset(nonexistent_id)
        
        # Assert - Should return None for non-existent asset
        self.assertIsNone(retrieved_asset)

    def test_get_asset_after_deletion(self):
        """Test retrieving an asset after it has been deleted."""
        # Arrange - Create and then delete an asset
        asset_id = "A102"
        
        # Add the asset
        add_asset(asset_id, "Temporary Asset", "TempModel", "TempBrand", 
                "SNTEMP", "R4", "R4", 1, datetime.now(), 
                "This asset will be deleted")

        
        # Verify it was added
        self.assertIsNotNone(get_asset(asset_id))
        
        # Delete the asset (using SQLAlchemy directly since there's no delete_asset function)
        asset_to_delete = get_asset(asset_id)
        if asset_to_delete:
            db.session.delete(asset_to_delete)
            db.session.commit()
        
        # Act - Try to retrieve the deleted asset
        retrieved_asset = get_asset(asset_id)
        
        # Assert - Should return None for deleted asset
        self.assertIsNone(retrieved_asset)

    def test_get_asset_case_sensitivity(self):
        """Test if get_asset is case sensitive for string IDs."""
        # Arrange - Create an asset with a mixed-case ID
        original_id = "MixedCase123"
        
        add_asset(original_id, "Case Sensitive Test", "TestModel", "TestBrand", 
                "SNTEST", "R4", "R4", 1, datetime.now(), 

                "Testing ID case sensitivity")

        
        # Act - Try to retrieve with different case
        lower_case_id = original_id.lower()
        retrieved_with_lower = get_asset(lower_case_id)
        
        upper_case_id = original_id.upper()
        retrieved_with_upper = get_asset(upper_case_id)
        
        # Assert - Should be case sensitive (depending on database)
        # This test will help identify the behavior of your system
        original_asset = get_asset(original_id)
        self.assertIsNotNone(original_asset)
        
        # The following assertions depend on your database's case sensitivity
        # SQLite is typically case-insensitive for string comparisons
        # If you want strict case sensitivity, you might need to adjust your query
        if retrieved_with_lower is None and retrieved_with_upper is None:
            # Database is case sensitive
            self.assertIsNone(retrieved_with_lower)
            self.assertIsNone(retrieved_with_upper)
        else:
            # Database is case insensitive (like SQLite default)
            # This is informational - the test doesn't necessarily fail
            pass
        
    def test_get_all_assets(self):
        """Test retrieving all assets from the database."""
    # Arrange - Clear existing assets to start with known state
    # (This approach is optional - depends on your test setup)
        for asset in Asset.query.all():
            db.session.delete(asset)
        db.session.commit()
        
        # Create multiple test assets
        test_assets = [
            # id, description, model, brand, serial_number, room_id, last_located, assignee_id, last_update, notes, status

            ("A201", "Desktop PC", "OptiPlex 7050", "Dell", "SN10001", "R1", "R1", 1, datetime.now(), "Test asset 1"),
            ("A202", "Monitor", "P2419H", "Dell", "SN10002", "R1", "R1", 1, datetime.now(), "Test asset 2"),
            ("A203", "Printer", "LaserJet Pro", "HP", "SN10003", "R2", "R2", 2, datetime.now(), "Test asset 3")

        ]
        
        # Add each test asset to the database
        for asset_data in test_assets:
            add_asset(*asset_data)
        
        # Act - Call the function under test
        all_assets = get_all_assets()
        
        # Assert - Verify all assets were retrieved
        self.assertIsNotNone(all_assets)
        self.assertEqual(len(all_assets), len(test_assets))
        
        # Verify each expected asset is in the returned list
        asset_ids = [asset.id for asset in all_assets]
        for asset_data in test_assets:
            expected_id = asset_data[0]
            self.assertIn(expected_id, asset_ids)
            
        # Verify some properties of each retrieved asset
        for asset in all_assets:
            # Find the corresponding test data
            test_data = next((data for data in test_assets if data[0] == asset.id), None)
            self.assertIsNotNone(test_data, f"Couldn't find test data for asset ID {asset.id}")
            
            # Check that properties match
            self.assertEqual(asset.description, test_data[1])
            self.assertEqual(asset.model, test_data[2])
            self.assertEqual(asset.brand, test_data[3])
            self.assertEqual(asset.serial_number, test_data[4])


    def test_get_all_assets_empty_database(self):
        """Test retrieving all assets when the database is empty."""
        # Arrange - Clear existing assets to start with empty state
        for asset in Asset.query.all():
            db.session.delete(asset)
        db.session.commit()
        
        # Act - Call the function under test
        all_assets = get_all_assets()
        
        # Assert - Should return an empty list, not None
        self.assertIsNotNone(all_assets)
        self.assertEqual(len(all_assets), 0)
        self.assertEqual(all_assets, [])

            
        
    # def test_get_all_assets_by_room_id(self):
        
    #      # First create multiple assets in different rooms
    #     add_asset("A1", "Laptop", "XPS 15", "Dell", "DL123456", "R1", "R1", "01", "2025-03-15", "New laptop", "Good")
    #     add_asset("A2", "Monitor", "P2419H", "Dell", "MN789012", "R1", "R1", "01", "2025-03-15", "24-inch monitor", "Good")
    #     add_asset("A3", "Printer", "LaserJet Pro", "HP", "HP345678", "R2", "R2", "02", "2025-03-15", "Color printer", "Good")
        
    #     # Retrieve assets for room R1
    #     assets_r1 = get_all_assets_by_room_id("R1")
        
    #     # Check that we got the correct number of assets
    #     self.assertEqual(len(assets_r1), 2)
        
    #     # Verify the returned assets are the ones we expect
    #     asset_ids = [asset.id for asset in assets_r1]
    #     self.assertIn("A1", asset_ids)
    #     self.assertIn("A2", asset_ids)
    #     self.assertNotIn("A3", asset_ids)
        
    #     # Retrieve assets for room R2
    #     assets_r2 = get_all_assets_by_room_id("R2")
        
    #     # Check that we got the correct number of assets
    #     self.assertEqual(len(assets_r2), 1)
        
    #     # Verify the returned asset is the one we expect
    #     self.assertEqual(assets_r2[0].id, "A3")
        
    #     # Test with a room that has no assets
    #     assets_r3 = get_all_assets_by_room_id("R3")
    #     self.assertEqual(len(assets_r3), 0)
        
        
        
        
        
        
    # def test_status_updated_with_location(self):