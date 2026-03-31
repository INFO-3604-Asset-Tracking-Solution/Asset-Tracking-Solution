import unittest
from App.models import Building, Floor, Room

class BuildingUnitTests(unittest.TestCase):
    def test_new_building(self):
        building = Building("Main Building")
        self.assertEqual(building.building_name, "Main Building")

    def test_building_get_json(self):
        building = Building("Science Block")
        expected_json = {'building_id': None, 'building_name': "Science Block"}
        self.assertDictEqual(building.get_json(), expected_json)

class FloorUnitTests(unittest.TestCase):
    def test_new_floor(self):
        floor = Floor(1, "First Floor")
        self.assertEqual(floor.building_id, 1)
        self.assertEqual(floor.floor_name, "First Floor")

    def test_floor_get_json(self):
        floor = Floor(2, "Second Floor")
        expected_json = {'floor_id': None, 'building_id': 2, 'floor_name': "Second Floor"}
        self.assertDictEqual(floor.get_json(), expected_json)

class RoomUnitTests(unittest.TestCase):
    def test_new_room(self):
        room = Room(1, "Asset Room: 101")
        self.assertEqual(room.floor_id, 1)
        self.assertEqual(room.room_name, "Asset Room: 101")

    def test_room_get_json(self):
        room = Room(2, "Asset Room: 102")
        expected_json = {
            'room_id': None,
            'floor_id': 2,
            'room_name': "Asset Room: 102"
        }
        self.assertDictEqual(room.get_json(), expected_json)
