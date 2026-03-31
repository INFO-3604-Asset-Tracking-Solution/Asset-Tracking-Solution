import unittest
from datetime import datetime
from App.models import Notification

class NotificationUnitTests(unittest.TestCase):

    def test_new_notification(self):
        notif = Notification(audit_id="A1", recipient_id=1, message="Audit started")
        self.assertEqual(notif.audit_id, "A1")
        self.assertEqual(notif.recipient_id, 1)
        self.assertEqual(notif.message, "Audit started")
        self.assertIsInstance(notif.timestamp, datetime)

    def test_notification_with_custom_timestamp(self):
        ts = datetime(2025, 3, 10, 10, 0, 0)
        notif = Notification(audit_id="A2", recipient_id=2, message="Hello", timestamp=ts)
        self.assertEqual(notif.timestamp, ts)

    def test_notification_get_json(self):
        notif = Notification(audit_id="A3", recipient_id=3, message="Test message")
        expected_json = {
            'notif_id': None,
            'audit_id': "A3",
            'recipient_id': 3,
            'message': "Test message",
            'timestamp': notif.timestamp
        }
        self.assertDictEqual(notif.get_json(), expected_json)
