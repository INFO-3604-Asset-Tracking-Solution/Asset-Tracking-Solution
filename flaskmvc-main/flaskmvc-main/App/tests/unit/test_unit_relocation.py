import unittest
from datetime import datetime
from App.models import Relocation

class RelocationUnitTests(unittest.TestCase):

    def test_new_relocation(self):
        reloc = Relocation(check_id="CE1", found_in_id=101)
        self.assertEqual(reloc.check_id, "CE1")
        self.assertEqual(reloc.found_in_id, 101)
        self.assertIsNone(reloc.new_check_event_id)

    def test_relocation_get_json(self):
        reloc = Relocation(check_id="CE2", found_in_id=102, new_check_event_id="CE3")
        reloc.timestamp = datetime(2025, 4, 1, 12, 0, 0)
        
        expected_json = {
            'relocation_id': reloc.relocation_id,
            'check_id': "CE2",
            'found_in_id': 102,
            'new_check_event_id': "CE3",
            'timestamp': reloc.timestamp.isoformat()
        }
        self.assertDictEqual(reloc.get_json(), expected_json)
