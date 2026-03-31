import unittest
from datetime import datetime
from App.models import Audit

class AuditUnitTests(unittest.TestCase):

    def test_new_audit(self):
        audit = Audit(initiator_id=1, status='PENDING')
        self.assertEqual(audit.initiator_id, 1)
        self.assertEqual(audit.status, 'PENDING')
        self.assertIsInstance(audit.start_date, datetime)
        self.assertIsNone(audit.end_date)

    def test_audit_status_coverage(self):
        statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED']
        for s in statuses:
            audit = Audit(initiator_id=1, status=s)
            self.assertEqual(audit.status, s)

    def test_audit_initiator_id_types(self):
        a = Audit(initiator_id="A1", status='PENDING')
        self.assertEqual(a.initiator_id, "A1")


    def test_audit_get_json(self):
        start = datetime(2025, 2, 1)
        audit = Audit(initiator_id=3, status='IN_PROGRESS', start_date=start)

        expected_json = {
            'audit_id': audit.audit_id,
            'initiator_id': 3,
            'start_date': start,
            'end_date': None,
            'status': 'IN_PROGRESS'
        }
        self.assertDictEqual(audit.get_json(), expected_json)
