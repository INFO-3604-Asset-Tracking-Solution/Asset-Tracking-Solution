import unittest
from App.models import Building, Floor, Room

class BuildingUnitTests(unittest.TestCase):

    def test_new_building(self):
        building = Building("B1", "Main Building")
        self.assertEqual(building.building_id, "B1")
        self.assertEqual(building.building_name, "Main Building")


    def test_building_get_json(self):
        building = Building("B2", "Main Building")
        expected_json = {
            'building_id': "B2",
            'building_name': "Main Building"
        }
        self.assertDictEqual(building.get_json(), expected_json)

class FloorUnitTests(unittest.TestCase):

    def test_new_floor(self):
        floor = Floor("F1", "B1", "First Floor")
        self.assertEqual(floor.floor_id, "F1")
        self.assertEqual(floor.building_id, "B1")
        self.assertEqual(floor.floor_name, "First Floor")

    def test_floor_get_json(self):
        floor = Floor("F2", "B1", "Second Floor")
        expected_json = {
            'floor_id': "F2",
            'building_id': "B1",
            'floor_name': "Second Floor"
        }
        self.assertDictEqual(floor.get_json(), expected_json)

class RoomUnitTests(unittest.TestCase):

    def test_new_room(self):
        room = Room("R1", "F1", "Asset Room: 101")
        self.assertEqual(room.room_id, "R1")
        self.assertEqual(room.floor_id, "F1")
        self.assertEqual(room.room_name, "Asset Room: 101")

    def test_room_get_json(self):
        room = Room("R2", "F1", "Asset Room: 102")
        expected_json = {
            'room_id': "R2",
            'floor_id': "F1",
            'room_name': "Asset Room: 102"
        }
        self.assertDictEqual(room.get_json(), expected_json)