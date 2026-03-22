import unittest
from App.controllers import (
    create_building, get_building, 
    create_floor, get_floor,
    create_room, get_room, 
)

class BuildingIntegrationTests (unittest.TestCase):

    def test_create_building(self):
        building = create_building("B3", "Third building")
        self.assertEqual(building.building_name, "Third building")

    def test_get_building(self):
        create_building("B1", "Main Building")
        building = get_building("B1")  
        self.assertIsNotNone(building)
        self.assertEqual(building.building_name, "Main Building")

class FloorIntegrationTests(unittest.TestCase):

    def test_create_floor(self):
        floor = create_floor("F3", "B3", "Third Floor")
        self.assertEqual(floor.floor_name, "Third Floor")

    def test_get_floor(self):
        create_floor("F4", "B3", "Fourth Floor")
        floor = get_floor("F4")
        self.assertIsNotNone(floor)
        self.assertEqual(floor.floor_name, "Fourth Floor")

class RoomIntegrationTests(unittest.TestCase):

    def test_create_room(self):
        room = create_room("R3", "F3", "Asset Room: 103")
        self.assertEqual(room.room_name, "Asset Room: 103")

    def test_get_room(self):
        create_room("R4", "F3", "Asset Room: 104")
        room = get_room("R4")
        self.assertIsNotNone(room)
        self.assertEqual(room.room_name, "Asset Room: 104")