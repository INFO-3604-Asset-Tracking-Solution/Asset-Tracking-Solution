import unittest
from datetime import datetime
from App.models import MissingDevice

class MissingDeviceUnitTests(unittest.TestCase):

    def test_new_missing_device(self):
        md = MissingDevice(audit_id="A1", assignment_id="ASG1")
        self.assertEqual(md.audit_id, "A1")
        self.assertEqual(md.assignment_id, "ASG1")
        self.assertIsInstance(md.timestamp, datetime)

    def test_missing_device_get_json(self):
        md = MissingDevice(audit_id="A2", assignment_id="ASG2")
        expected_json = {
            'missing_id': None,
            'audit_id': "A2",
            'assignment_id': "ASG2",
            'timestamp': md.timestamp,
            'found_relocation_id': None
        }
        self.assertDictEqual(md.get_json(), expected_json)
