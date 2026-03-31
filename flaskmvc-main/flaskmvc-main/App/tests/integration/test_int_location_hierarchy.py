import unittest
from App.controllers import (
    create_building, get_building, 
    create_floor, get_floor,
    create_room, get_room, 
)
from App.models import Building, Floor, Room
from App.database import db

class LocationHierarchyIntegrationTests(unittest.TestCase):
    def setUp(self):
        db.session.query(Room).delete()
        db.session.query(Floor).delete()
        db.session.query(Building).delete()
        db.session.commit()

    def test_building_crud(self):
        b = create_building("Headquarters")
        self.assertIsNotNone(b)
        self.assertIsNotNone(b.building_id)
        
        fetched = get_building(b.building_id)
        self.assertEqual(fetched.building_name, "Headquarters")

    def test_floor_crud(self):
        b = create_building("Headquarters")
        f = create_floor(b.building_id, "Ground Floor")
        self.assertIsNotNone(f)
        self.assertEqual(f.building_id, b.building_id)
        
        fetched = get_floor(f.floor_id)
        self.assertEqual(fetched.floor_name, "Ground Floor")

    def test_room_crud(self):
        b = create_building("Headquarters")
        f = create_floor(b.building_id, "Ground Floor")
        r = create_room(f.floor_id, "Server Room")
        self.assertIsNotNone(r)
        self.assertEqual(r.floor_id, f.floor_id)
        
        fetched = get_room(r.room_id)
        self.assertEqual(fetched.room_name, "Server Room")
        